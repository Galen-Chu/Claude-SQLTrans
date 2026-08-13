"""Schema introspection via SQLAlchemy.

Reads the table/column layout of a live database so the UI can offer autocomplete
and the NL->SQL prompt can be schema-aware. Pure read access — never writes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from sqlalchemy import create_engine, inspect
from sqlalchemy.engine import Engine

from sqltrans.utils.logging import get_logger

logger = get_logger("sqltrans.db.introspection")


@dataclass
class ColumnSchema:
    """A single column's name, type, and nullability."""

    name: str
    type: str
    nullable: bool = True


@dataclass
class TableSchema:
    """A table and its columns."""

    name: str
    columns: List[ColumnSchema] = field(default_factory=list)


def create_db_engine(url: str, **engine_kwargs) -> Engine:
    """Create a SQLAlchemy engine for a connection URL.

    Args:
        url: SQLAlchemy connection URL (e.g. ``sqlite:///./app.db``,
            ``postgresql+psycopg://user:pass@host/db``).
        **engine_kwargs: Forwarded to ``create_engine`` (e.g. ``pool_pre_ping``).

    Returns:
        A SQLAlchemy ``Engine``. No connection is opened until first use.

    Raises:
        sqlalchemy.exc.ArgumentError: If the URL is malformed.
    """
    # ``future=True`` is the default in SQLAlchemy 2.x; kept explicit for clarity.
    return create_engine(url, future=True, **engine_kwargs)


def introspect(engine: Engine, *, schema: Optional[str] = None) -> List[TableSchema]:
    """Read the table/column layout of a database.

    Args:
        engine: A SQLAlchemy engine.
        schema: Optional schema/namespace name (e.g. ``public`` for Postgres).
            ``None`` uses the database default.

    Returns:
        List of ``TableSchema``, one per table. Views are intentionally excluded
        — only materialized tables are surfaced for query building.

    Notes:
        This is a read-only operation. It issues ``INFORMATION_SCHEMA``-style
        metadata queries only; it never touches table data.
    """
    inspector = inspect(engine)
    tables: List[TableSchema] = []

    for table_name in inspector.get_table_names(schema=schema):
        columns = [
            ColumnSchema(
                name=col["name"],
                type=str(col["type"]),
                nullable=bool(col.get("nullable", True)),
            )
            for col in inspector.get_columns(table_name, schema=schema)
        ]
        tables.append(TableSchema(name=table_name, columns=columns))

    logger.info(
        "Introspected %d tables (schema=%s)", len(tables), schema or "<default>"
    )
    return tables


def render_schema_for_prompt(tables: List[TableSchema]) -> str:
    """Render a schema as compact text for inclusion in an LLM prompt.

    Args:
        tables: Tables returned by :func:`introspect`.

    Returns:
        A human/LLM-readable schema block, or an empty string if ``tables``
        is empty.

    Example::

        Schema (table: columns):
          users: id (INTEGER), email (VARCHAR), created_at (TIMESTAMP)
          orders: id (INTEGER), user_id (INTEGER), total (NUMERIC)
    """
    if not tables:
        return ""

    lines = ["Schema (table: columns):"]
    for table in tables:
        cols = ", ".join(f"{c.name} ({c.type})" for c in table.columns)
        lines.append(f"  {table.name}: {cols}")
    return "\n".join(lines)
