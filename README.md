# SQLTrans

**SQLTrans** 是一套給客服支援工程師的 SQL 工具——把 SQL **轉譯**到不同資料庫方言、用**自然語言生成** SQL，並對即時資料庫執行**唯讀**查詢。提供 CLI 與網頁 GUI 兩種介面。

**SQLTrans** is a SQL tool for customer-support engineers — **transpile** SQL between dialects, **generate** SQL from natural language, and run **read-only** queries against a live database. Exposed through a CLI and a web GUI.

## 架構 / Architecture

```mermaid
flowchart TB
    CLI[CLI<br/>sqltrans translate / nl2sql / run / schema / gui]
    WEB[網頁 GUI<br/>FastAPI + 原生 JS<br/>Translate / Ask / Run / Schema]
    API[FastAPI 路由<br/>/api/transpile · /api/nl2sql · /api/schema<br/>/api/query/execute · /api/connections]
    SAFE[唯讀安全層<br/>sqlglot AST 政策 · transpiler.py]
    NL[NL→SQL · Claude · nl2sql.py<br/>各方言 few-shot + 回饋]
    CONN[連線管理員<br/>具名連線 · 環境變數金鑰 · connections.py]
    EXEC[唯讀執行器<br/>語句逾時 · 連線池 · 分頁 · 快取 · executor.py]
    INTRO[Schema 探勘 · introspection.py]
    DB[(即時資料庫)]

    CLI --> API
    WEB --> API
    API --> SAFE
    API --> NL --> SAFE
    API --> CONN --> EXEC --> SAFE
    CONN --> INTRO
    EXEC -.唯讀.-> DB
    INTRO -.metadata.-> DB
```

所有產生或執行的 SQL，都會先經過**唯讀 AST 安全政策**把關一次——寫入、DDL、DCL、多語句注入一律在接觸資料庫前被拒絕。

Every SQL string the system produces or runs is first gated by a **read-only safety policy enforced on the parsed AST** — writes, DDL, DCL, and multi-statement injection are all rejected before reaching the database.

## 專案結構 / Project Structure

```
sqltrans/
├── src/sqltrans/            # engine, CLI, web, db, utils
│   ├── sql/                 # transpiler.py (sqlglot + read-only), nl2sql.py
│   ├── db/                  # introspection, executor, engine, connections
│   ├── web/                 # FastAPI app + static web GUI
│   ├── utils/               # config, logging
│   └── __main__.py          # CLI entry point (translate/nl2sql/run/schema/gui)
├── tests/                   # unit + integration + e2e
├── docs/                    # documentation
├── examples/                # example queries / scenarios
└── pyproject.toml
```

## 功能 / Features

- 💻 **CLI（主力）**：`translate`、`nl2sql`、`run`、`schema`、`gui` 子指令，可腳本化、可管線。
- 🌐 **網頁 GUI**：Translate（貼上 SQL 轉譯）、Ask（自然語言生成 + 回饋）、Run（唯讀執行）、Schema（探勘）四個分頁。
- 🔁 **跨方言轉譯**：PostgreSQL、Oracle、MySQL、T-SQL、SQLite、Snowflake、BigQuery、DuckDB（sqlglot）。
- 🤖 **自然語言 → SQL**：Claude 生成，輸出再經同一道唯讀閘道驗證；支援各方言 few-shot 與回饋迴圈。
- 🛡️ **唯讀執行**：AST 政策 + 語句逾時 + 列數上限 + 分頁 + 連線池 + 結果快取。
- 🔑 **具名連線**：`~/.sqltrans/connections.toml` 放 metadata，連線 URL 放環境變數（金鑰不落地）。

- 💻 **CLI (primary)**: `translate`, `nl2sql`, `run`, `schema`, `gui` subcommands — scriptable, pipe-friendly.
- 🌐 **Web GUI**: Translate (paste-and-transpile), Ask (NL→SQL + feedback), Run (read-only execute), Schema (introspect) tabs.
- 🔁 **Cross-dialect transpilation**: PostgreSQL, Oracle, MySQL, T-SQL, SQLite, Snowflake, BigQuery, DuckDB (sqlglot).
- 🤖 **Natural-language → SQL**: Claude drafts; output is re-validated through the same read-only gate; per-dialect few-shot and a feedback loop.
- 🛡️ **Read-only execution**: AST policy + statement timeout + row cap + paging + connection pool + result cache.
- 🔑 **Named connections**: metadata in `~/.sqltrans/connections.toml`, URL in an environment variable (secrets never written to disk).

## 安裝 / Installation

```bash
# 從 PyPI
pip install sqltrans

# 或從原始碼
git clone https://github.com/Galen-Chu/Claude-SQLTrans.git
cd Claude-SQLTrans
pip install -e .            # 含開發相依: pip install -e ".[dev]"
```

## 快速開始 / Quick Start

```bash
# 跨方言轉譯（Oracle → Postgres：NVL → COALESCE）
sqltrans translate --read oracle --write postgres -q "SELECT NVL(x, 0) FROM t"

# 自然語言生成 SQL（需 ANTHROPIC_API_KEY）
sqltrans nl2sql "count active users grouped by plan" --dialect postgres

# 對具名連線執行唯讀查詢
export SQLTRANS_CONN_PROD="postgresql+psycopg://ro_user:****@host/db"
sqltrans run --connection prod -q "SELECT * FROM users LIMIT 10"

# 探勘 schema
sqltrans schema --connection prod

# 啟動網頁 GUI
sqltrans gui
```

## 文件 / Documentation

- [系統設計](SYSTEM_DESIGN.md) · [開發指南](docs/development.md) · [快速開始](docs/quick-start.md) · [文件索引](docs/index.md)

- [System Design](SYSTEM_DESIGN.md) · [Development Guide](docs/development.md) · [Quick Start](docs/quick-start.md) · [Documentation Index](docs/index.md)

## 👤 作者 / Author

**Galen-Chu**

---

<div align="center">

Made with ❤️ for API testing · 用 ❤️ 為 API 測試而造

</div>
