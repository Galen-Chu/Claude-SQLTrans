"""SQL engine: cross-dialect transpilation with a read-only safety policy.

The interactive query builder (v1) has been removed. This package now exposes
the sqlglot-backed transpiler (parse → AST read-only policy → emit in any
dialect) and, via :mod:`sqltrans.sql.nl2sql`, the natural-language → SQL
adapter.
"""

from sqltrans.sql.transpiler import (
    SUPPORTED_DIALECTS,
    TranspileError,
    UnsafeQueryError,
    enforce_read_only,
    normalize_dialect,
    parse_one_statement,
    transpile,
    validate_read_only,
)

__all__ = [
    "SUPPORTED_DIALECTS",
    "TranspileError",
    "UnsafeQueryError",
    "enforce_read_only",
    "normalize_dialect",
    "parse_one_statement",
    "transpile",
    "validate_read_only",
]
