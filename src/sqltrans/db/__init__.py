"""Database integration: schema introspection and read-only execution.

Phase 4 of the v2 architecture. Connects the validated, read-only SQL produced
by the engine to real databases via SQLAlchemy.
"""

from sqltrans.db.introspection import (
    ColumnSchema,
    TableSchema,
    create_db_engine,
    introspect,
    render_schema_for_prompt,
)
from sqltrans.db.executor import (
    DEFAULT_ROW_LIMIT,
    QueryResult,
    execute_read_only,
)

__all__ = [
    "ColumnSchema",
    "TableSchema",
    "create_db_engine",
    "introspect",
    "render_schema_for_prompt",
    "DEFAULT_ROW_LIMIT",
    "QueryResult",
    "execute_read_only",
]
