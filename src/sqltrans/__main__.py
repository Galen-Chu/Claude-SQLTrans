"""SQLTrans CLI — translate, generate, and run read-only SQL.

Subcommands:
  translate  Transpile SQL between dialects.
  nl2sql     Generate SQL from a natural-language request (Claude).
  run        Execute a read-only SELECT against a named connection or URL.
  schema     List tables/columns of a database.
  gui        Launch the web GUI.

SQL for ``translate``/``run`` is read from ``-q``/``--query``, ``--file``,
or stdin (when piped). Output SQL is syntax-highlighted with ``rich`` when
available; result rows render as a table.
"""

from __future__ import annotations

import argparse
import sys
from importlib.metadata import PackageNotFoundError, version as pkg_version
from pathlib import Path

from sqltrans.db import DEFAULT_ROW_LIMIT, execute_read_only, introspect
from sqltrans.db.executor import DEFAULT_STATEMENT_TIMEOUT_MS
from sqltrans.db.connections import resolve_engine
from sqltrans.sql.nl2sql import DEFAULT_MODEL, NL2SQLError, nl2sql
from sqltrans.sql.transpiler import (
    TranspileError,
    UnsafeQueryError,
    transpile,
)
from sqltrans.utils.logging import get_logger, setup_logging

logger = get_logger("sqltrans.main")


def _version() -> str:
    try:
        return pkg_version("sqltrans")
    except PackageNotFoundError:  # pragma: no cover - not installed
        return "0.0.0+unknown"


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #


def _read_sql(args: argparse.Namespace) -> str:
    """Read SQL from --query, --file, or stdin (when piped)."""
    if getattr(args, "query", None):
        return args.query
    if getattr(args, "file", None):
        return Path(args.file).read_text(encoding="utf-8")
    if not sys.stdin.isatty():
        return sys.stdin.read()
    sys.stderr.write("error: provide SQL via -q/--query, --file, or stdin\n")
    sys.exit(2)


def _resolve_engine(args: argparse.Namespace):
    """Resolve a connection name or explicit URL to a cached engine."""
    from sqltrans.db import get_engine

    if getattr(args, "connection", None):
        return resolve_engine(args.connection)
    if getattr(args, "url", None):
        return get_engine(args.url)
    sys.stderr.write("error: --connection or --url is required\n")
    sys.exit(2)


def _print_sql(sql: str) -> None:
    try:
        from rich.console import Console
        from rich.syntax import Syntax

        Console().print(Syntax(sql, "sql", theme="ansi_dark"))
    except Exception:  # pragma: no cover - rich unavailable
        print(sql)


def _print_table(result) -> None:
    try:
        from rich.console import Console
        from rich.table import Table

        table = Table(show_header=True)
        for column in result.columns:
            table.add_column(column)
        for row in result.rows:
            table.add_row(*[str(v) for v in row])
        Console().print(table)
    except Exception:  # pragma: no cover - rich unavailable
        print("\t".join(result.columns))
        for row in result.rows:
            print("\t".join(str(v) for v in row))


def _die(message: str, code: int = 1) -> None:
    sys.stderr.write(f"{message}\n")
    sys.exit(code)


# --------------------------------------------------------------------------- #
# Subcommands
# --------------------------------------------------------------------------- #


def cmd_translate(args: argparse.Namespace) -> None:
    """sqltrans translate [--read D] [--write D] [-q SQL | --file F | stdin]."""
    sql = _read_sql(args)
    try:
        out = transpile(sql, read=args.read, write=args.write, pretty=True)
    except UnsafeQueryError as e:
        _die(f"rejected (not read-only): {e}")
    except TranspileError as e:
        _die(f"parse error: {e}")
    except ValueError as e:
        _die(f"error: {e}")
    _print_sql(out)


def cmd_nl2sql(args: argparse.Namespace) -> None:
    """sqltrans nl2sql PROMPT [--dialect D] [--connection N | --url U] ..."""
    schema_ctx = None
    if args.connection or args.url:
        try:
            engine = _resolve_engine(args)
            schema_ctx = introspect(engine)
        except (KeyError, LookupError) as e:
            _die(f"connection error: {e}")
        except Exception as e:  # pragma: no cover - introspect failure
            _die(f"schema introspection failed: {type(e).__name__}")

    try:
        result = nl2sql(
            args.prompt,
            dialect=args.dialect,
            schema=schema_ctx,
            model=args.model,
            transpile_to=args.transpile_to,
        )
    except NL2SQLError as e:
        _die(f"LLM error: {e}")
    except ValueError as e:
        _die(f"error: {e}")

    if result.sql:
        _print_sql(result.sql)
        for warning in result.warnings:
            sys.stderr.write(f"warning: {warning}\n")
        sys.stderr.write(f"(validated={result.validated})\n")
    else:
        sys.stderr.write("no SQL generated\n")
        for warning in result.warnings:
            sys.stderr.write(f"  {warning}\n")
        sys.exit(1)


def cmd_run(args: argparse.Namespace) -> None:
    """sqltrans run (--connection N | --url U) [-q SQL | --file F | stdin]."""
    sql = _read_sql(args)
    try:
        engine = _resolve_engine(args)
        result = execute_read_only(
            engine,
            sql,
            dialect=args.dialect,
            row_limit=args.row_limit,
            statement_timeout_ms=args.timeout,
        )
    except (KeyError, LookupError) as e:
        _die(f"connection error: {e}")
    except UnsafeQueryError as e:
        _die(f"rejected (not read-only): {e}")
    except TranspileError as e:
        _die(f"parse error: {e}")
    except ValueError as e:
        _die(f"error: {e}")
    except Exception as e:
        # Do not echo the exception message (it may include connection details).
        _die(f"execution failed: {type(e).__name__}")

    _print_table(result)
    if result.truncated:
        sys.stderr.write(f"(truncated to {result.row_count} rows)\n")


def cmd_schema(args: argparse.Namespace) -> None:
    """sqltrans schema (--connection N | --url U) [--schema S]."""
    try:
        engine = _resolve_engine(args)
        tables = introspect(engine, schema=args.schema)
    except (KeyError, LookupError) as e:
        _die(f"connection error: {e}")
    except Exception as e:  # pragma: no cover - introspect failure
        _die(f"introspection failed: {type(e).__name__}")

    for table in tables:
        print(f"{table.name}:")
        for column in table.columns:
            nullable = " NULL" if column.nullable else " NOT NULL"
            print(f"  {column.name} ({column.type}){nullable}")


def cmd_gui(args: argparse.Namespace) -> None:
    """sqltrans gui [--dialect D] — launch the web GUI."""
    from sqltrans.web.launcher import launch_web_gui

    launch_web_gui(initial_dialect=args.dialect or "generic")


# --------------------------------------------------------------------------- #
# Argument parsing
# --------------------------------------------------------------------------- #


def _add_sql_input(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("-q", "--query", help="SQL string")
    parser.add_argument("-f", "--file", help="File containing SQL")


def build_parser() -> argparse.ArgumentParser:
    """Build the top-level argument parser with subcommands."""
    parser = argparse.ArgumentParser(
        prog="sqltrans",
        description="SQLTrans — translate, generate, and run read-only SQL.",
    )
    parser.add_argument(
        "--version", "-v", action="version", version=f"SQLTrans {_version()}"
    )
    sub = parser.add_subparsers(dest="command", metavar="{translate,nl2sql,run,schema,gui}")

    # translate
    sp = sub.add_parser("translate", help="Transpile SQL between dialects")
    sp.add_argument("--read", "-r", help="Source dialect (e.g. oracle, postgresql)")
    sp.add_argument("--write", "-w", help="Target dialect")
    _add_sql_input(sp)
    sp.set_defaults(func=cmd_translate)

    # nl2sql
    sp = sub.add_parser("nl2sql", help="Generate SQL from a natural-language request")
    sp.add_argument("prompt", help="Natural-language request")
    sp.add_argument("--dialect", "-d", help="Target dialect")
    sp.add_argument("--connection", help="Named connection for schema context")
    sp.add_argument("--url", help="Connection URL for schema context")
    sp.add_argument(
        "--model", default=DEFAULT_MODEL, help=f"Claude model ID (default {DEFAULT_MODEL})"
    )
    sp.add_argument(
        "--transpile-to", dest="transpile_to", help="Transpile the draft to this dialect"
    )
    sp.set_defaults(func=cmd_nl2sql)

    # run
    sp = sub.add_parser("run", help="Execute a read-only SELECT")
    conn = sp.add_mutually_exclusive_group(required=True)
    conn.add_argument("--connection", help="Named connection")
    conn.add_argument("--url", help="Connection URL")
    _add_sql_input(sp)
    sp.add_argument("--dialect", "-d", help="Source dialect for validation")
    sp.add_argument("--row-limit", type=int, default=DEFAULT_ROW_LIMIT)
    sp.add_argument(
        "--timeout",
        type=int,
        default=DEFAULT_STATEMENT_TIMEOUT_MS,
        help="Per-statement timeout in milliseconds (postgres/mysql)",
    )
    sp.set_defaults(func=cmd_run)

    # schema
    sp = sub.add_parser("schema", help="List tables/columns of a database")
    conn = sp.add_mutually_exclusive_group(required=True)
    conn.add_argument("--connection", help="Named connection")
    conn.add_argument("--url", help="Connection URL")
    sp.add_argument("--schema", help="Schema/namespace (e.g. public)")
    sp.set_defaults(func=cmd_schema)

    # gui
    sp = sub.add_parser("gui", help="Launch the web GUI")
    sp.add_argument("--dialect", "-d", default="generic")
    sp.set_defaults(func=cmd_gui)

    return parser


def main() -> None:
    """Entry point for the SQLTrans CLI."""
    setup_logging(log_level="INFO", console_level="WARNING")
    parser = build_parser()
    args = parser.parse_args()
    if not getattr(args, "func", None):
        parser.print_help()
        sys.exit(0)
    args.func(args)


if __name__ == "__main__":
    main()
