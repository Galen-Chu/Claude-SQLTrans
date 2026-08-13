"""SQL transpilation engine built on sqlglot, with read-only enforcement.

This module is the SQL engine: it *parses* any SQL string and *transpiles* it
between dialects (Oracle, Postgres, MySQL, T-SQL, ...). The hard work is
delegated to `sqlglot`; what this module adds is a strict read-only safety
policy so the engine is safe to expose behind the web API and to run against
live databases.

Public surface:

- ``transpile(sql, read, write)`` — convert a SQL string between dialects.
- ``validate_read_only(sql, dialect)`` — parse + enforce SELECT-only, return AST.
- ``SUPPORTED_DIALECTS`` / ``normalize_dialect()`` — dialect discovery & aliasing.
- ``TranspileError`` / ``UnsafeQueryError`` — error hierarchy.

Read-only policy
----------------
A statement is accepted only when **all** hold:

1. It parses to exactly **one** statement (multi-statement input is rejected,
   so ``SELECT 1; DROP TABLE t;`` never slips through).
2. No node in the tree is a write/DDL/DCL/TCL/vendor-command type
   (INSERT, UPDATE, DELETE, MERGE, CREATE, DROP, ALTER, TRUNCATE, GRANT,
   REVOKE, COMMIT, ROLLBACK, USE, BEGIN/TRANSACTION, or a catch-all Command).
3. The root is a SELECT-family statement (Select, Union, Intersect, Except,
   Subquery) — this also rejects BEGIN/COMMIT/SET etc. by omission.
4. It is not ``SELECT ... INTO`` (table creation).

The policy is enforced on the parsed AST, not by regex on the source text.
"""

from __future__ import annotations

from typing import Optional

import sqlglot
from sqlglot import exp

from sqltrans.utils.logging import get_logger

logger = get_logger("sqltrans.sql.transpiler")


# --------------------------------------------------------------------------- #
# Dialect handling
# --------------------------------------------------------------------------- #

# sqlglot supports ~20 dialects; we surface a useful, tested subset. The rest of
# sqlglot's dialects still work if passed directly, but only these are advertised
# through the API.
SUPPORTED_DIALECTS = frozenset(
    {
        "postgres",
        "oracle",
        "mysql",
        "tsql",
        "sqlite",
        "snowflake",
        "bigquery",
        "duckdb",
    }
)

# Human-friendly aliases -> canonical sqlglot dialect names. This lets the API
# accept the v1 project's spelling ("postgresql") and common shorthands.
_DIALECT_ALIASES = {
    "postgresql": "postgres",
    "postgres": "postgres",
    "pg": "postgres",
    "oracle": "oracle",
    "ora": "oracle",
    "mysql": "mysql",
    "mariadb": "mysql",
    "tsql": "tsql",
    "mssql": "tsql",
    "sqlserver": "tsql",
    "sqlite": "sqlite",
    "snowflake": "snowflake",
    "bigquery": "bigquery",
    "duckdb": "duckdb",
}


def normalize_dialect(dialect: Optional[str]) -> Optional[str]:
    """Normalize a dialect name to sqlglot's canonical form.

    Args:
        dialect: Dialect name or alias (case-insensitive), or None.

    Returns:
        Canonical dialect name, or None if input is None.

    Raises:
        ValueError: If the dialect is not recognized.
    """
    if dialect is None:
        return None
    key = dialect.strip().lower()
    canonical = _DIALECT_ALIASES.get(key)
    if canonical is None:
        raise ValueError(
            f"Unknown dialect: {dialect!r}. "
            f"Supported: {', '.join(sorted(SUPPORTED_DIALECTS))} "
            f"(plus aliases like 'postgresql', 'mssql')."
        )
    return canonical


# --------------------------------------------------------------------------- #
# Errors
# --------------------------------------------------------------------------- #


class TranspileError(Exception):
    """Base class for transpilation failures (parse errors, empty input, ...)."""


class UnsafeQueryError(TranspileError):
    """Raised when input violates the read-only (SELECT-only) policy.

    This is a *security* signal: callers should treat it as a rejected request,
    not a transient failure.
    """


# --------------------------------------------------------------------------- #
# Read-only policy
# --------------------------------------------------------------------------- #

# Root node types permitted for a top-level statement. Anything else (BEGIN,
# COMMIT, SET, a bare expression, ...) is rejected by omission.
_SELECT_ROOTS = (
    exp.Select,
    exp.Union,
    exp.Intersect,
    exp.Except,
    exp.Subquery,
)


def _denied_nodes() -> tuple[type[exp.Expression], ...]:
    """Node types that must never appear in a read-only query, anywhere.

    Built defensively so a missing attribute on some sqlglot version does not
    crash the validator — it just omits that one type (the root whitelist and
    INTO check still backstop the policy).
    """
    names = (
        # DML
        "Insert",
        "Update",
        "Delete",
        "Merge",
        # DDL
        "Create",
        "Drop",
        "Alter",
        "TruncateTable",
        # DCL
        "Grant",
        "Revoke",
        # TCL
        "Commit",
        "Rollback",
        "Transaction",
        "Begin",
        # Session / vendor commands (Command is sqlglot's catch-all fallback)
        "Command",
        "Use",
    )
    return tuple(getattr(exp, n) for n in names if hasattr(exp, n))


def parse_one_statement(
    sql: str, dialect: Optional[str] = None
) -> exp.Expression:
    """Parse a SQL string into exactly one AST root.

    Args:
        sql: SQL source text.
        dialect: Source dialect (name or alias), or None for sqlglot's default.

    Returns:
        The parsed AST root.

    Raises:
        TranspileError: If the input is empty or cannot be parsed.
        UnsafeQueryError: If the input contains more than one statement
            (e.g. ``SELECT 1; DROP TABLE t;``).
    """
    if sql is None or not sql.strip():
        raise TranspileError("SQL input is empty")

    read = normalize_dialect(dialect)
    try:
        statements = sqlglot.parse(sql, read=read)
    except Exception as e:  # sqlglot raises a variety of exception types
        raise TranspileError(f"Failed to parse SQL: {e}") from e

    # sqlglot may emit None entries for stray semicolons; drop them before counting.
    statements = [s for s in statements if s is not None]
    if len(statements) != 1:
        raise UnsafeQueryError(
            f"Expected exactly one statement, got {len(statements)}. "
            "Multi-statement input is not allowed."
        )
    return statements[0]


def enforce_read_only(ast: exp.Expression) -> exp.Expression:
    """Enforce the read-only policy on a parsed AST.

    Args:
        ast: Parsed statement root.

    Returns:
        The same AST, unchanged, if it passes the policy.

    Raises:
        UnsafeQueryError: If the statement is not a single read-only SELECT.
    """
    # 1. No dangerous node types anywhere in the tree.
    denied = next(ast.find_all(*_denied_nodes()), None)
    if denied is not None:
        raise UnsafeQueryError(
            "Read-only policy violated: "
            f"'{type(denied).__name__}' is not permitted in a read-only query."
        )

    # 2. Root must be SELECT-family.
    if not isinstance(ast, _SELECT_ROOTS):
        raise UnsafeQueryError(
            "Only SELECT statements are allowed "
            f"(got root type '{type(ast).__name__}')."
        )

    # 3. Reject SELECT ... INTO (Postgres table creation).
    if isinstance(ast, exp.Select) and ast.args.get("into") is not None:
        raise UnsafeQueryError(
            "SELECT ... INTO is not allowed: it creates a table."
        )

    return ast


def validate_read_only(
    sql: str, dialect: Optional[str] = None
) -> exp.Expression:
    """Parse SQL and enforce the read-only policy.

    Convenience wrapper: ``parse_one_statement`` then ``enforce_read_only``.

    Args:
        sql: SQL source text.
        dialect: Source dialect (name or alias), or None.

    Returns:
        The validated AST root.

    Raises:
        TranspileError: On parse failure or empty input.
        UnsafeQueryError: If the statement is not a single read-only SELECT.
    """
    ast = parse_one_statement(sql, dialect=dialect)
    return enforce_read_only(ast)


# --------------------------------------------------------------------------- #
# Transpilation
# --------------------------------------------------------------------------- #


def transpile(
    sql: str,
    read: Optional[str] = None,
    write: Optional[str] = None,
    pretty: bool = True,
    validate: bool = True,
) -> str:
    """Convert a SQL string from one dialect to another.

    Args:
        sql: Source SQL.
        read: Source dialect (name or alias), or None for sqlglot's default.
        write: Target dialect (name or alias), or None for sqlglot's default.
        pretty: If True, pretty-print the output.
        validate: If True (default), enforce the read-only policy before
            converting. Set to False only for trusted, internal use.

    Returns:
        The converted SQL string.

    Raises:
        TranspileError: On parse failure or empty input.
        UnsafeQueryError: If ``validate`` is True and the statement is not a
            single read-only SELECT.
        ValueError: If a dialect name is unrecognized.

    Example:
        >>> transpile("SELECT NVL(x, 0) FROM t", read="oracle", write="postgres")
        "SELECT COALESCE(x, 0) FROM t"
    """
    read_dialect = normalize_dialect(read)
    write_dialect = normalize_dialect(write)

    ast = parse_one_statement(sql, dialect=read_dialect)
    if validate:
        enforce_read_only(ast)

    result = ast.sql(dialect=write_dialect, pretty=pretty)
    logger.info(
        "Transpiled %s -> %s (%d -> %d chars)",
        read_dialect or "default",
        write_dialect or "default",
        len(sql),
        len(result),
    )
    return result
