# SQLTrans Quick Start

Install, then translate, generate, or run SQL from the CLI or the web GUI.

## Install

```bash
pip install sqltrans          # from PyPI
# or from source:
pip install -e .
```

Requires Python 3.10+.

## CLI

```bash
# Transpile between dialects (Oracle -> Postgres: NVL -> COALESCE)
sqltrans translate --read oracle --write postgres -q "SELECT NVL(x, 0) FROM t"

# Generate SQL from a natural-language request (requires ANTHROPIC_API_KEY)
sqltrans nl2sql "count active users grouped by plan" --dialect postgres

# Run a read-only query against a named connection
export SQLTRANS_CONN_PROD="postgresql+psycopg://ro_user:****@host/db"
sqltrans run --connection prod -q "SELECT * FROM users LIMIT 10"

# Introspect a schema
sqltrans schema --connection prod
```

SQL can be passed with `-q`, read from `--file`, or piped via stdin.

## Named connections

Register metadata in `~/.sqltrans/connections.toml`:

```toml
[connections.prod]
dialect = "postgres"
schema = "public"
```

…then provide the connection URL out of band, so the secret is never stored on
disk by SQLTrans:

```bash
export SQLTRANS_CONN_PROD="postgresql+psycopg://ro_user:****@host/db"
```

## Web GUI

```bash
sqltrans gui
```

Opens a browser with four tabs:

- **Translate** — paste SQL, transpile to another dialect.
- **Ask** — describe a query in plain language; review and give feedback.
- **Run** — execute a read-only SELECT against a connection.
- **Schema** — introspect a database's tables and columns.

## Safety

Every SQL string is parsed and checked against a read-only AST policy before it
is transpiled or executed — writes, DDL, and multi-statement input are rejected.
For live execution, use a **read-only database role**: it is the last line of
defense. See the [System Design](../SYSTEM_DESIGN.md) for the details.
