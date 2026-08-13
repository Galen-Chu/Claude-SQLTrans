"""FastAPI application for the SQLTrans web GUI.

Exposes the v2 engine over HTTP: cross-dialect transpilation, natural-language
→ SQL generation, schema introspection, and read-only query execution, plus
named-connection listing and NL→SQL feedback. The interactive query builder
(v1) has been removed; the frontend is a Translate/Ask/Run/Schema UI.
"""

from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from sqltrans.db import (
    DEFAULT_ROW_LIMIT,
    execute_read_only,
    get_engine,
    introspect,
    list_connections,
    resolve_url,
)
from sqltrans.sql.nl2sql import (
    DEFAULT_MODEL as NL2SQL_DEFAULT_MODEL,
    NL2SQLError,
    nl2sql,
    record_feedback,
)
from sqltrans.sql.transpiler import (
    SUPPORTED_DIALECTS as TRANSPILER_DIALECTS,
    TranspileError,
    UnsafeQueryError,
    normalize_dialect,
    transpile as transpile_sql,
)
from sqltrans.utils.logging import get_logger

logger = get_logger("sqltrans.web")

app = FastAPI(
    title="SQLTrans Web GUI",
    description="Translate, generate, and run read-only SQL",
    version="0.2.0",
)


# --------------------------------------------------------------------------- #
# Request models
# --------------------------------------------------------------------------- #


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
    connection_name: Optional[str] = Field(
        None,
        description=(
            "Named connection (from ~/.sqltrans/connections.toml) to introspect "
            "for schema-aware SQL. Its URL is read from $SQLTRANS_CONN_<NAME>."
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
    connection: Optional[str] = Field(
        None, description="SQLAlchemy connection URL (or use connection_name)"
    )
    connection_name: Optional[str] = Field(
        None,
        description=(
            "Named connection (from ~/.sqltrans/connections.toml) whose URL is "
            "read from $SQLTRANS_CONN_<NAME>."
        ),
    )
    dialect: Optional[str] = Field(
        None, description="Source dialect for validation (e.g. postgresql, sqlite)"
    )
    row_limit: int = Field(
        DEFAULT_ROW_LIMIT, ge=1, description="Maximum rows to return"
    )


class FeedbackRequest(BaseModel):
    """Request model for NL→SQL feedback ('did this answer the question?')."""

    prompt: str = Field(..., min_length=1, description="The original natural-language request")
    sql: Optional[str] = Field(None, description="The SQL that was produced, if any")
    accepted: bool = Field(..., description="True if the user accepted the result as correct")
    dialect: Optional[str] = Field(None, description="Dialect the draft targeted, if any")
    validated: bool = Field(False, description="Whether the draft passed the read-only policy")
    comment: str = Field("", description="Optional free-text note")


# --------------------------------------------------------------------------- #
# Static frontend + helpers
# --------------------------------------------------------------------------- #

static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


def _resolve_connection_url(
    connection: Optional[str], connection_name: Optional[str]
) -> Optional[str]:
    """Resolve a connection URL from an explicit URL or a named connection.

    An explicit ``connection`` URL takes precedence; otherwise the named
    connection is resolved via the connection manager (reads
    ``$SQLTRANS_CONN_<NAME>``). Returns None if neither is provided.
    """
    if connection:
        return connection
    if connection_name:
        return resolve_url(connection_name)
    return None


# --------------------------------------------------------------------------- #
# Routes
# --------------------------------------------------------------------------- #


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


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "version": "0.2.0"}


@app.get("/api/connections")
async def get_connections():
    """List registered named connections (metadata only — never URLs)."""
    conns = list_connections()
    return {
        "connections": [
            {
                "name": c.name,
                "dialect": c.dialect,
                "schema": c.schema,
                "description": c.description,
            }
            for c in conns.values()
        ]
    }


@app.get("/api/transpile/dialects")
async def get_transpile_dialects():
    """List dialects supported by the transpilation engine.

    Aliases (e.g. ``postgresql``) are also accepted by the transpile endpoint
    but not listed here.
    """
    return {"dialects": sorted(TRANSPILER_DIALECTS)}


@app.post("/api/transpile")
async def transpile(request: TranspileRequest):
    """Convert a SQL statement from one dialect to another.

    The input is parsed and validated as a single read-only (SELECT-only)
    statement before conversion. Write/DDL/DCL statements, multi-statement
    input, and ``SELECT ... INTO`` are rejected with HTTP 400.
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
        raise HTTPException(status_code=400, detail=str(e))

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
    is returned. If a connection is given, the live schema is introspected for
    schema-aware generation.
    """
    schema_ctx = None
    url = _resolve_connection_url(request.connection, request.connection_name)
    if url:
        try:
            engine = get_engine(url)
            schema_ctx = introspect(engine)
        except (KeyError, LookupError) as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception:
            logger.warning("Schema introspection for nl2sql failed")
            raise HTTPException(
                status_code=400,
                detail="Could not introspect schema",
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


@app.post("/api/nl2sql/feedback")
async def nl2sql_feedback(request: FeedbackRequest):
    """Record NL→SQL feedback ('did this answer the question?')."""
    path = record_feedback(
        prompt=request.prompt,
        sql=request.sql,
        accepted=request.accepted,
        dialect=request.dialect,
        validated=request.validated,
        comment=request.comment,
    )
    return {"recorded": True, "path": str(path)}


@app.get("/api/schema")
async def get_schema(
    connection: Optional[str] = None,
    schema: Optional[str] = None,
    connection_name: Optional[str] = None,
):
    """List tables and columns of a database."""
    url = _resolve_connection_url(connection, connection_name)
    if url is None:
        raise HTTPException(
            status_code=400,
            detail="Provide 'connection' (URL) or 'connection_name'.",
        )
    try:
        engine = get_engine(url)
        tables = introspect(engine, schema=schema)
    except (KeyError, LookupError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        logger.warning("Schema introspection failed")
        raise HTTPException(status_code=400, detail="Could not introspect schema")

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

    The SQL is parsed and policy-checked **before** any connection is opened.
    Results are row-capped.
    """
    url = _resolve_connection_url(request.connection, request.connection_name)
    if url is None:
        raise HTTPException(
            status_code=400,
            detail="Provide 'connection' (URL) or 'connection_name'.",
        )
    try:
        engine = get_engine(url)
        result = execute_read_only(
            engine,
            request.sql,
            dialect=request.dialect,
            row_limit=request.row_limit,
        )
    except (KeyError, LookupError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except UnsafeQueryError as e:
        logger.warning("Rejected unsafe execution request")
        raise HTTPException(status_code=400, detail=str(e))
    except TranspileError as e:
        logger.info("Unparseable execution request")
        raise HTTPException(status_code=422, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        # Do not echo the exception message (it may include connection details).
        logger.warning("Query execution failed")
        raise HTTPException(status_code=400, detail="Execution failed")

    return {
        "columns": result.columns,
        "rows": result.rows,
        "row_count": result.row_count,
        "truncated": result.truncated,
    }


# --------------------------------------------------------------------------- #
# Error handlers
# --------------------------------------------------------------------------- #


@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Handle 404 errors."""
    return JSONResponse(status_code=404, content={"error": "Endpoint not found"})


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Handle internal server errors."""
    logger.error("Internal server error: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error. Check logs for details."},
    )
