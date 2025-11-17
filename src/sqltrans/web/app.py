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
