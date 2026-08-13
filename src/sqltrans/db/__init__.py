"""Database integration: schema introspection, read-only execution, connections.

Connects the validated, read-only SQL produced by the engine to real databases
via SQLAlchemy, with named connections whose credentials live in the
environment rather than on disk.
"""

from sqltrans.db.introspection import (
    ColumnSchema,
    TableSchema,
    create_db_engine,
    introspect,
    render_schema_for_prompt,
)
from sqltrans.db.engine import dispose_all, get_engine
from sqltrans.db.connections import (
    ConnectionInfo,
    connections_path,
    env_var_for,
    list_connections,
    resolve_engine,
    resolve_url,
)
from sqltrans.db.executor import (
    DEFAULT_ROW_LIMIT,
    QueryResult,
    clear_result_cache,
    execute_read_only,
)

__all__ = [
    # introspection
    "ColumnSchema",
    "TableSchema",
    "create_db_engine",
    "introspect",
    "render_schema_for_prompt",
    # engine cache
    "get_engine",
    "dispose_all",
    # connections
    "ConnectionInfo",
    "connections_path",
    "env_var_for",
    "list_connections",
    "resolve_url",
    "resolve_engine",
    # execution
    "DEFAULT_ROW_LIMIT",
    "QueryResult",
    "clear_result_cache",
    "execute_read_only",
]
