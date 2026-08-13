"""Read-only query execution against a live database.

The executor runs only SQL that has passed the engine's AST read-only policy
(see :mod:`sqltrans.sql.transpiler`). It adds further layers of defense:

1. **Per-dialect statement timeout.** Where supported (Postgres, MySQL), a
   wall-clock ``statement_timeout`` / ``MAX_EXECUTION_TIME`` is set before the
   query so an expensive SELECT cannot peg the database indefinitely.
2. **Row cap + offset.** Results are fetched with ``fetchmany`` (bounded memory)
   and a ``truncated`` flag reports overflow; ``offset`` enables paging.
3. **Best-effort ``SET TRANSACTION READ ONLY``.** Where the dialect supports it;
   SQLite ignores it. The AST policy is the load-bearing backstop.
4. **Optional result cache.** A small in-process LRU keyed by query, so repeated
   identical reads in an interactive session skip the database. Off by default.

A statement is rejected by the AST policy before any connection is opened.
"""

from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import text
from sqlalchemy.engine import Engine

from sqltrans.sql.transpiler import (
    TranspileError,
    UnsafeQueryError,
    validate_read_only,
)
from sqltrans.utils.logging import get_logger

logger = get_logger("sqltrans.db.executor")

# Default ceiling on rows returned in one call. Generous for interactive support
# work, small enough to keep responses fast and memory bounded.
DEFAULT_ROW_LIMIT = 1000

# Default per-statement wall-clock cap (milliseconds). 0 disables it.
DEFAULT_STATEMENT_TIMEOUT_MS = 30_000

# Upper bound on cached result sets (LRU eviction once exceeded).
_CACHE_MAX = 64


@dataclass
class QueryResult:
    """The outcome of a read-only query."""

    columns: List[str] = field(default_factory=list)
    rows: List[List[Any]] = field(default_factory=list)
    truncated: bool = False
    """True if the result set had more than ``row_limit`` rows."""
    row_count: int = 0
    """Number of rows actually returned (<= row_limit)."""


# In-process LRU cache: key -> QueryResult. Keys never contain credentials
# (they use the engine's id() rather than its URL).
_result_cache: "OrderedDict[Tuple[int, str, int, int], QueryResult]" = OrderedDict()


def _cache_get(key: Tuple[int, str, int, int]) -> Optional[QueryResult]:
    result = _result_cache.get(key)
    if result is not None:
        _result_cache.move_to_end(key)
    return result


def _cache_put(key: Tuple[int, str, int, int], result: QueryResult) -> None:
    _result_cache[key] = result
    _result_cache.move_to_end(key)
    while len(_result_cache) > _CACHE_MAX:
        _result_cache.popitem(last=False)


def clear_result_cache() -> None:
    """Drop all cached query results (e.g. between test runs)."""
    _result_cache.clear()


def _apply_statement_timeout(conn, backend: str, ms: int) -> None:
    """Best-effort per-statement timeout. Silently skips unsupported dialects."""
    try:
        if backend == "postgresql":
            conn.execute(text(f"SET LOCAL statement_timeout = {int(ms)}"))
        elif backend == "mysql":
            # MAX_EXECUTION_TIME is in milliseconds and applies to SELECT.
            conn.execute(text(f"SET SESSION MAX_EXECUTION_TIME = {int(ms)}"))
        else:
            logger.debug("No statement_timeout mapping for backend %s", backend)
    except Exception:
        logger.debug("statement_timeout not applied (backend=%s)", backend)


def _skip(result, offset: int) -> None:
    """Advance the cursor by ``offset`` rows in bounded chunks."""
    remaining = offset
    while remaining > 0:
        chunk = result.fetchmany(min(remaining, 1000))
        if not chunk:
            break
        remaining -= len(chunk)


def execute_read_only(
    engine: Engine,
    sql: str,
    *,
    dialect: Optional[str] = None,
    row_limit: int = DEFAULT_ROW_LIMIT,
    statement_timeout_ms: Optional[int] = DEFAULT_STATEMENT_TIMEOUT_MS,
    offset: int = 0,
    use_cache: bool = False,
) -> QueryResult:
    """Validate and execute a single read-only SELECT against ``engine``.

    Args:
        engine: A SQLAlchemy engine for the target database.
        sql: The SQL to run. Parsed and policy-checked *before* any connection
            is opened.
        dialect: SQL dialect name/alias for parsing (e.g. ``"postgresql"``,
            ``"sqlite"``). ``None`` uses sqlglot's default.
        row_limit: Maximum rows to return; the excess is dropped and
            ``truncated`` is set.
        statement_timeout_ms: Per-statement wall-clock cap in milliseconds
            (Postgres/MySQL). ``None`` or ``0`` disables it.
        offset: Number of leading rows to skip (for paging).
        use_cache: If True, return a cached result for an identical
            (engine, sql, row_limit, offset) call, when available.

    Returns:
        A :class:`QueryResult` with columns, the (possibly truncated) rows, and
        truncation/row-count metadata.

    Raises:
        ValueError: If ``row_limit`` is non-positive or ``offset`` is negative.
        UnsafeQueryError: If the statement is not a single read-only SELECT
            (raised before any DB access).
        TranspileError: If the SQL cannot be parsed.
    """
    if row_limit <= 0:
        raise ValueError("row_limit must be positive")
    if offset < 0:
        raise ValueError("offset must be non-negative")

    # 1. Policy gate — before any connection is opened.
    validate_read_only(sql, dialect=dialect)
    logger.info(
        "Executing validated read-only query (row_limit=%d, offset=%d)",
        row_limit,
        offset,
    )

    cache_key: Optional[Tuple[int, str, int, int]] = None
    if use_cache:
        cache_key = (id(engine), sql.strip(), row_limit, offset)
        cached = _cache_get(cache_key)
        if cached is not None:
            logger.info("Query result cache hit")
            return cached

    backend = engine.url.get_backend_name()
    with engine.connect() as conn:
        # 2. Best-effort read-only transaction.
        try:
            conn.execute(text("SET TRANSACTION READ ONLY"))
        except Exception:
            pass

        # 3. Per-statement timeout.
        if statement_timeout_ms:
            _apply_statement_timeout(conn, backend, statement_timeout_ms)

        # 4. Execute and bound the result.
        result = conn.execute(text(sql))
        columns = list(result.keys())

        if offset:
            _skip(result, offset)

        batch = result.fetchmany(row_limit + 1)
        truncated = len(batch) > row_limit
        rows = [list(row) for row in batch[:row_limit]]

    logger.info(
        "Query returned %d rows%s",
        len(rows),
        " (truncated)" if truncated else "",
    )
    query_result = QueryResult(
        columns=columns,
        rows=rows,
        truncated=truncated,
        row_count=len(rows),
    )

    if cache_key is not None:
        _cache_put(cache_key, query_result)

    return query_result
