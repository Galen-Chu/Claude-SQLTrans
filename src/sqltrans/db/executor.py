"""Read-only query execution against a live database.

The executor runs only SQL that has passed the engine's AST read-only policy
(see :mod:`sqltrans.sql.transpiler`). It adds two more layers of defense:

1. **Row cap.** Results are fetched with ``fetchmany(row_limit + 1)`` so memory
   is bounded regardless of result-set size; a flag reports truncation.
2. **Best-effort ``SET TRANSACTION READ ONLY``.** Where the dialect supports it
   (Postgres, MySQL, ...), the transaction is marked read-only before the query
   runs. SQLite ignores it (caught) — there the AST policy is the real backstop.

These are belt-and-suspenders on top of the AST policy, which is the load-bearing
enforcement: a statement is rejected before any connection is opened.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, List, Optional

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


@dataclass
class QueryResult:
    """The outcome of a read-only query."""

    columns: List[str] = field(default_factory=list)
    rows: List[List[Any]] = field(default_factory=list)
    truncated: bool = False
    """True if the result set had more than ``row_limit`` rows."""
    row_count: int = 0
    """Number of rows actually returned (<= row_limit)."""


def execute_read_only(
    engine: Engine,
    sql: str,
    *,
    dialect: Optional[str] = None,
    row_limit: int = DEFAULT_ROW_LIMIT,
) -> QueryResult:
    """Validate and execute a single read-only SELECT against ``engine``.

    Args:
        engine: A SQLAlchemy engine for the target database.
        sql: The SQL to run. It is parsed and policy-checked *before* any
            connection is opened.
        dialect: SQL dialect name/alias for parsing (e.g. ``"postgresql"``,
            ``"sqlite"``). ``None`` uses sqlglot's default.
        row_limit: Maximum rows to return. The query is allowed to return more;
            the excess is dropped and ``truncated`` is set.

    Returns:
        A :class:`QueryResult` with columns, the (possibly truncated) rows, and
        truncation/row-count metadata.

    Raises:
        UnsafeQueryError: If the statement is not a single read-only SELECT.
            (Raised by :func:`validate_read_only` before any DB access.)
        TranspileError: If the SQL cannot be parsed.
    """
    if row_limit <= 0:
        raise ValueError("row_limit must be positive")

    # 1. Policy gate — happens before we touch the database at all.
    validate_read_only(sql, dialect=dialect)
    logger.info(
        "Executing validated read-only query (row_limit=%d)", row_limit
    )

    with engine.connect() as conn:
        # 2. Best-effort read-only transaction. Ignore failures: SQLite and some
        #    others don't support it; the AST policy already guarantees SELECT-only.
        try:
            conn.execute(text("SET TRANSACTION READ ONLY"))
        except Exception:
            pass

        # 3. Execute and bound the result.
        result = conn.execute(text(sql))
        columns = list(result.keys())

        batch = result.fetchmany(row_limit + 1)
        truncated = len(batch) > row_limit
        rows = [list(row) for row in batch[:row_limit]]

    logger.info(
        "Query returned %d rows%s",
        len(rows),
        " (truncated)" if truncated else "",
    )
    return QueryResult(
        columns=columns,
        rows=rows,
        truncated=truncated,
        row_count=len(rows),
    )
