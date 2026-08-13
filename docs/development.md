# SQLTrans Development Guide

How to set up a development environment, navigate the codebase, and contribute.

## Development Setup

```bash
git clone https://github.com/Galen-Chu/Claude-SQLTrans.git
cd Claude-SQLTrans
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

Verify the install:

```bash
sqltrans --version          # CLI is wired up
sqltrans translate --read oracle --write postgres -q "SELECT NVL(x,0) FROM t"
pytest                      # test suite
```

## Project Structure

```
sqltrans/
├── src/sqltrans/            # Main package
│   ├── sql/
│   │   ├── transpiler.py    # sqlglot engine + read-only AST policy
│   │   └── nl2sql.py        # Claude NL→SQL adapter (few-shot, feedback)
│   ├── db/
│   │   ├── introspection.py # schema introspection (SQLAlchemy)
│   │   ├── executor.py      # read-only execution (timeout / paging / cache)
│   │   ├── engine.py        # cached SQLAlchemy engines
│   │   └── connections.py   # named connections (env-var secrets)
│   ├── web/
│   │   ├── app.py           # FastAPI app (v2 API)
│   │   ���── launcher.py      # uvicorn launcher
│   │   └── static/          # web GUI (index.html, js/, css/, lib/)
│   ├── utils/
│   │   ├── config.py        # ~/.sqltrans/config.toml
│   │   └── logging.py       # structured logging
│   └── __main__.py          # CLI (translate / nl2sql / run / schema / gui)
├── tests/                   # unit + integration + e2e
├── docs/                    # documentation
├── examples/                # example queries / scenarios
├── scripts/                 # build scripts
├── pyproject.toml           # project config (setuptools)
└── README.md
```

## Architecture Overview

SQLTrans is built around a read-only SQL engine surfaced through a CLI and a
web GUI. Every SQL string the system produces or runs is parsed and checked
against a read-only AST policy before it reaches the user or the database.

### Layers

- **CLI** (`__main__.py`) — `translate` / `nl2sql` / `run` / `schema` / `gui`.
- **Web** (`web/`) — FastAPI router (`app.py`) + static JS GUI + uvicorn launcher.
- **Engine** (`sql/`) — `transpiler.py` (sqlglot + read-only policy) and
  `nl2sql.py` (Claude adapter, few-shot, feedback).
- **Data** (`db/`) — `introspection.py`, `executor.py` (timeouts / paging / cache),
  `engine.py` (cached engines), `connections.py` (named connections, env-var secrets).
- **Utils** (`utils/`) — `config.py`, `logging.py`.

See [SYSTEM_DESIGN.md](../SYSTEM_DESIGN.md) for the full design, the read-only
safety policy, and data-flow diagrams.

**Principles:** single responsibility per module; the parsed AST is the single
source of truth; LLM output is untrusted and validated like any other input;
secrets live in the environment, never on disk.

## The engine

SQL is handled by `sql/transpiler.py` (sqlglot-backed parse → read-only AST
policy → cross-dialect emit). Read-only safety is enforced on the parsed AST,
not on source text. Dialects are mapped by `normalize_dialect` /
`SUPPORTED_DIALECTS`; there are no per-dialect modules to edit — to support or
alias a dialect, extend those.

## Testing

```bash
pytest                                       # all tests
pytest tests/unit                            # unit only
pytest tests/unit/test_transpiler.py -k name # one test
pytest --cov=sqltrans                        # with coverage
```

Key suites: `test_transpiler`, `test_nl2sql`, `test_db`, `test_connections`,
`test_executor_hardening`, `test_nl2sql_quality`, `test_cli`. DB tests use
temp-file SQLite; the LLM client is a Protocol so tests inject a fake (no API
calls).

## Code Quality

```bash
black src/sqltrans tests            # format
ruff check src/sqltrans tests       # lint (auto-fix with --fix)
mypy src/sqltrans                   # type check
```

Configured in `pyproject.toml`: black (line-length 100), ruff, strict mypy.

## Contributing

1. Open an issue for non-trivial changes.
2. Branch from `main`; keep commits focused.
3. Add tests for new behavior; ensure `pytest`, `mypy`, `black`, and `ruff` pass.
4. For SQL changes, operate on the parsed AST and keep every code path behind
   the read-only policy.

## Resources

- **Repository:** https://github.com/Galen-Chu/Claude-SQLTrans
- **Issues:** https://github.com/Galen-Chu/Claude-SQLTrans/issues
- **System design:** [SYSTEM_DESIGN.md](../SYSTEM_DESIGN.md)
