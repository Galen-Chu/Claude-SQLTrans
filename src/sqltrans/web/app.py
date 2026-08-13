"""FastAPI application for SQLTrans web GUI."""

from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# Import existing business logic
from sqltrans.models.query import QueryState, VALID_DIALECTS
from sqltrans.models.filters import Filter
from sqltrans.sql.builder import QueryBuilder
from sqltrans.sql.dialects import get_dialect
from sqltrans.sql.formatter import format as format_sql
from sqltrans.sql.transpiler import (
    SUPPORTED_DIALECTS as TRANSPILER_DIALECTS,
    TranspileError,
    UnsafeQueryError,
    transpile as transpile_sql,
)
from sqltrans.sql.nl2sql import (
    DEFAULT_MODEL as NL2SQL_DEFAULT_MODEL,
    NL2SQLError,
    nl2sql,
)
from sqltrans.db import (
    DEFAULT_ROW_LIMIT,
    execute_read_only,
    introspect,
    create_db_engine,
)
from sqltrans.utils.validation import validate_identifier, validate_operator, validate_value
from sqltrans.utils.logging import get_logger

logger = get_logger("sqltrans.web")

# Initialize FastAPI app
app = FastAPI(
    title="SQLTrans Web GUI",
    description="Interactive SQL Query Builder",
    version="0.1.0",
)

# Global query state (single-user local application)
query_state = QueryState()


# Pydantic models for API requests/responses
class TableRequest(BaseModel):
    """Request model for setting table name."""

    name: str = Field(..., min_length=1, description="Table name")


class ColumnRequest(BaseModel):
    """Request model for adding a column."""

    column: str = Field(..., min_length=1, description="Column name")


class FilterRequest(BaseModel):
    """Request model for adding a filter."""

    column: str = Field(..., min_length=1, description="Column name")
    operator: str = Field(..., description="Filter operator")
    value: Optional[Any] = Field(None, description="Filter value")


class DialectRequest(BaseModel):
    """Request model for changing dialect."""

    dialect: str = Field(..., description="SQL dialect")


class TranspileRequest(BaseModel):
    """Request model for cross-dialect SQL transpilation."""

    sql: str = Field(..., min_length=1, description="Source SQL to convert")
    read: Optional[str] = Field(
        None, description="Source dialect (e.g. oracle, postgresql, mysql, tsql)"
    )
    write: Optional[str] = Field(
        None, description="Target dialect (e.g. postgres, oracle, mysql, tsql)"
    )
    pretty: bool = Field(True, description="Pretty-print the output SQL")


class NL2SQLRequest(BaseModel):
    """Request model for natural-language → SQL generation."""

    prompt: str = Field(..., min_length=1, description="Natural-language request")
    dialect: Optional[str] = Field(
        None, description="Target SQL dialect hint (e.g. postgresql, mysql)"
    )
    connection: Optional[str] = Field(
        None,
        description=(
            "Optional SQLAlchemy connection URL. If given, the live schema is "
            "introspected and included as context for schema-aware SQL. "
            "Warning: may contain credentials; never log it."
        ),
    )
    model: Optional[str] = Field(
        None, description=f"Claude model ID (default {NL2SQL_DEFAULT_MODEL})"
    )
    transpile_to: Optional[str] = Field(
        None, description="If given, transpile the validated draft to this dialect"
    )


class ExecuteRequest(BaseModel):
    """Request model for read-only query execution."""

    sql: str = Field(..., min_length=1, description="SQL to execute (must be a read-only SELECT)")
    connection: str = Field(..., description="SQLAlchemy connection URL")
    dialect: Optional[str] = Field(
        None, description="Source dialect for validation (e.g. postgresql, sqlite)"
    )
    row_limit: int = Field(
        DEFAULT_ROW_LIMIT, ge=1, description="Maximum rows to return"
    )


class QueryStateResponse(BaseModel):
    """Response model for query state."""

    table: Optional[str]
    columns: List[str]
    filters: List[Dict[str, Any]]
    dialect: str


class SQLResponse(BaseModel):
    """Response model for generated SQL."""

    sql: str
    formatted: str


class ErrorResponse(BaseModel):
    """Response model for errors."""

    error: str


# Mount static files
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/")
async def root():
    """Serve the main application page."""
    index_file = static_dir / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    return JSONResponse(
        {"error": "Frontend not found. Please ensure static files are present."},
        status_code=500,
    )


@app.get("/api/query", response_model=QueryStateResponse)
async def get_query_state():
    """Get the current query state.

    Returns:
        Current query state with table, columns, filters, and dialect
    """
    return QueryStateResponse(
        table=query_state.table,
        columns=query_state.columns,
        filters=[
            {"column": f.column, "operator": f.operator, "value": f.value}
            for f in query_state.filters
        ],
        dialect=query_state.dialect,
    )


@app.post("/api/query/table")
async def set_table(request: TableRequest):
    """Set the table name.

    Args:
        request: Table name request

    Returns:
        Updated table name

    Raises:
        HTTPException: If table name is invalid
    """
    try:
        query_state.add_table(request.name)
        logger.info(f"Table set to: {request.name}")
        return {"table": query_state.table}
    except ValueError as e:
        logger.warning(f"Invalid table name: {request.name} - {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/query/columns/add")
async def add_column(request: ColumnRequest):
    """Add a column to the SELECT clause.

    Args:
        request: Column name request

    Returns:
        Updated list of columns

    Raises:
        HTTPException: If column name is invalid
    """
    try:
        query_state.add_column(request.column)
        logger.info(f"Column added: {request.column}")
        return {"columns": query_state.columns}
    except ValueError as e:
        logger.warning(f"Invalid column name: {request.column} - {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/api/query/columns/{column}")
async def remove_column(column: str):
    """Remove a column from the SELECT clause.

    Args:
        column: Column name to remove

    Returns:
        Updated list of columns

    Raises:
        HTTPException: If column not found
    """
    try:
        query_state.remove_column(column)
        logger.info(f"Column removed: {column}")
        return {"columns": query_state.columns}
    except ValueError as e:
        logger.warning(f"Cannot remove column: {column} - {e}")
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/api/query/filters/add")
async def add_filter(request: FilterRequest):
    """Add a filter to the WHERE clause.

    Args:
        request: Filter request with column, operator, and value

    Returns:
        Updated list of filters

    Raises:
        HTTPException: If filter is invalid
    """
    try:
        # Create and validate filter
        filter_obj = Filter(
            column=request.column, operator=request.operator, value=request.value
        )
        filter_obj.validate()

        query_state.add_filter(filter_obj)
        logger.info(f"Filter added: {filter_obj}")

        return {
            "filters": [
                {"column": f.column, "operator": f.operator, "value": f.value}
                for f in query_state.filters
            ]
        }
    except ValueError as e:
        logger.warning(f"Invalid filter: {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/api/query/filters/{index}")
async def remove_filter(index: int):
    """Remove a filter from the WHERE clause.

    Args:
        index: Filter index to remove

    Returns:
        Updated list of filters

    Raises:
        HTTPException: If index is invalid
    """
    try:
        query_state.remove_filter(index)
        logger.info(f"Filter removed at index: {index}")

        return {
            "filters": [
                {"column": f.column, "operator": f.operator, "value": f.value}
                for f in query_state.filters
            ]
        }
    except (ValueError, IndexError) as e:
        logger.warning(f"Cannot remove filter at index {index}: {e}")
        raise HTTPException(status_code=404, detail=str(e))


@app.post("/api/query/dialect")
async def set_dialect(request: DialectRequest):
    """Change the SQL dialect.

    Args:
        request: Dialect request

    Returns:
        Updated dialect and regenerated SQL

    Raises:
        HTTPException: If dialect is invalid
    """
    try:
        query_state.set_dialect(request.dialect)
        logger.info(f"Dialect changed to: {request.dialect}")

        # Generate SQL with new dialect
        if query_state.table:
            dialect = get_dialect(query_state.dialect)
            builder = QueryBuilder(query_state, dialect)
            sql = builder.build_query()
            formatted = format_sql(sql)
        else:
            sql = ""
            formatted = ""

        return {"dialect": query_state.dialect, "sql": sql, "formatted": formatted}
    except ValueError as e:
        logger.warning(f"Invalid dialect: {request.dialect} - {e}")
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/query/clear")
async def clear_query():
    """Clear the entire query state.

    Returns:
        Success message
    """
    query_state.clear()
    logger.info("Query cleared")
    return {"message": "Query cleared successfully"}


@app.get("/api/query/sql", response_model=SQLResponse)
async def get_sql():
    """Generate and return the SQL query.

    Returns:
        Generated SQL (plain and formatted)

    Raises:
        HTTPException: If query is invalid or table is not set
    """
    try:
        if not query_state.table:
            return SQLResponse(
                sql="-- No table selected. Add a table to begin building your query.",
                formatted="-- No table selected. Add a table to begin building your query.",
            )

        dialect = get_dialect(query_state.dialect)
        builder = QueryBuilder(query_state, dialect)
        sql = builder.build_query()
        formatted = format_sql(sql)

        logger.debug(f"Generated SQL: {sql}")

        return SQLResponse(sql=sql, formatted=formatted)
    except Exception as e:
        logger.error(f"Error generating SQL: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error generating SQL: {str(e)}")


@app.get("/api/dialects")
async def get_dialects():
    """Get list of available SQL dialects.

    Returns:
        List of dialect names
    """
    return {"dialects": list(VALID_DIALECTS)}


@app.get("/api/transpile/dialects")
async def get_transpile_dialects():
    """List dialects supported by the transpilation engine.

    Returns:
        Sorted list of canonical dialect names. Aliases (e.g. ``postgresql``)
        are also accepted by the transpile endpoint but not listed here.
    """
    return {"dialects": sorted(TRANSPILER_DIALECTS)}


@app.post("/api/transpile")
async def transpile(request: TranspileRequest):
    """Convert a SQL statement from one dialect to another.

    The input is parsed and validated as a single read-only (SELECT-only)
    statement before conversion. Write/DDL/DCL statements, multi-statement
    input, and ``SELECT ... INTO`` are rejected with HTTP 400.

    Args:
        request: Source SQL plus optional read/write dialects.

    Returns:
        Converted SQL (plain and pretty), plus the resolved dialect names.

    Raises:
        HTTPException: 400 if the input violates the read-only policy,
            422 if it cannot be parsed, 400 for an unknown dialect.
    """
    try:
        converted = transpile_sql(
            request.sql,
            read=request.read,
            write=request.write,
            pretty=request.pretty,
        )
    except UnsafeQueryError as e:
        logger.warning("Rejected unsafe transpile request: %s", e)
        raise HTTPException(status_code=400, detail=str(e))
    except TranspileError as e:
        logger.info("Unparseable transpile request: %s", e)
        raise HTTPException(status_code=422, detail=str(e))
    except ValueError as e:
        # Unknown dialect name from normalize_dialect()
        raise HTTPException(status_code=400, detail=str(e))

    from sqltrans.sql.transpiler import normalize_dialect

    logger.info(
        "Transpiled %s -> %s",
        request.read or "default",
        request.write or "default",
    )
    return {
        "sql": converted,
        "read": normalize_dialect(request.read),
        "write": normalize_dialect(request.write),
    }


@app.post("/api/nl2sql")
async def generate_sql_from_nl(request: NL2SQLRequest):
    """Generate validated, read-only SQL from a natural-language request.

    The LLM's draft is parsed and run through the AST read-only policy before it
    is returned. If ``connection`` is given, the live schema is introspected for
    schema-aware generation.

    Args:
        request: Natural-language prompt plus optional dialect, connection, model.

    Returns:
        The generated SQL (``sql``), whether it passed validation (``validated``),
        any ``warnings``, the raw model output, and the resolved ``dialect``.

    Raises:
        HTTPException: 400 for schema-introspection failures, 502 for LLM
            call failures.
    """
    schema_ctx = None
    if request.connection:
        try:
            engine = create_db_engine(request.connection)
            schema_ctx = introspect(engine)
        except Exception as e:
            # Do not log the connection string; it may contain credentials.
            logger.warning("Schema introspection for nl2sql failed")
            raise HTTPException(
                status_code=400,
                detail=f"Could not introspect schema: {type(e).__name__}",
            )

    try:
        result = nl2sql(
            request.prompt,
            dialect=request.dialect,
            schema=schema_ctx,
            model=request.model or NL2SQL_DEFAULT_MODEL,
            transpile_to=request.transpile_to,
        )
    except NL2SQLError as e:
        logger.warning("NL→SQL LLM call failed")
        raise HTTPException(status_code=502, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "sql": result.sql,
        "validated": result.validated,
        "warnings": result.warnings,
        "dialect": result.dialect,
        "raw": result.raw,
    }


@app.get("/api/schema")
async def get_schema(connection: str, schema: Optional[str] = None):
    """List tables and columns of a database.

    Args:
        connection: SQLAlchemy connection URL.
        schema: Optional schema/namespace (e.g. ``public``).

    Returns:
        Tables with their columns (name, type, nullable).

    Raises:
        HTTPException: 400 if the database cannot be introspected.
    """
    try:
        engine = create_db_engine(connection)
        tables = introspect(engine, schema=schema)
    except Exception as e:
        logger.warning("Schema introspection failed")
        raise HTTPException(
            status_code=400,
            detail=f"Could not introspect schema: {type(e).__name__}",
        )

    return {
        "tables": [
            {
                "name": t.name,
                "columns": [
                    {"name": c.name, "type": c.type, "nullable": c.nullable}
                    for c in t.columns
                ],
            }
            for t in tables
        ]
    }


@app.post("/api/query/execute")
async def execute_query(request: ExecuteRequest):
    """Validate and execute a single read-only SELECT against a database.

    The SQL is parsed and policy-checked (SELECT-only, single statement, no
    ``SELECT ... INTO``) **before** any connection is opened. Results are
    row-capped.

    Args:
        request: SQL, connection URL, optional dialect and row limit.

    Returns:
        Columns, rows, row count, and a ``truncated`` flag.

    Raises:
        HTTPException: 400 for unsafe/non-SELECT SQL, 422 for unparseable SQL,
            400 for database/execution errors.
    """
    try:
        engine = create_db_engine(request.connection)
        result = execute_read_only(
            engine,
            request.sql,
            dialect=request.dialect,
            row_limit=request.row_limit,
        )
    except UnsafeQueryError as e:
        logger.warning("Rejected unsafe execution request")
        raise HTTPException(status_code=400, detail=str(e))
    except TranspileError as e:
        logger.info("Unparseable execution request")
        raise HTTPException(status_code=422, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Database / connection / operational errors. Do not log the connection.
        logger.warning("Query execution failed")
        raise HTTPException(
            status_code=400,
            detail=f"Execution failed: {type(e).__name__}: {e}",
        )

    return {
        "columns": result.columns,
        "rows": result.rows,
        "row_count": result.row_count,
        "truncated": result.truncated,
    }


@app.get("/health")
async def health_check():
    """Health check endpoint.

    Returns:
        Health status
    """
    return {"status": "ok", "version": "0.1.0"}


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors."""
    return JSONResponse(
        status_code=404, content={"error": "Endpoint not found"}
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle internal server errors."""
    logger.error(f"Internal server error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error. Check logs for details."},
    )
