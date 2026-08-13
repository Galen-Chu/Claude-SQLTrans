# SQLTrans

**Bilingual README / 雙語 README** · **[繁體中文](#繁體中文)** | **[English](#english)**

---

## 繁體中文

**SQLTrans** 是一套為客服支援工程師（customer support engineer）設計的互動式 SQL 工具，協助人員在排查客戶資料庫問題時，快速**建構、轉譯與執行** SQL 查詢。

### 概述

SQLTrans 結合三項核心能力：

- **查詢建構**：以視覺化介面組裝 SELECT 查詢（WHERE 條件、多資料庫方言），即時驗證並預覽。
- **跨方言轉譯**：在 Oracle、PostgreSQL、MySQL、T-SQL 等方言間轉換 SQL，引擎為 [sqlglot](https://github.com/tobymao/sqlglot)。
- **自然語言生成與執行**：以自然語言產生 SQL（Claude），並對即時資料庫執行**唯讀**查詢、回傳結果。

所有產生或執行的 SQL，都會先經過**解析後的 AST 唯讀安全策略**把關——寫入（DML）、資料定義（DDL）、權限（DCL）、交易控制（TCL）、多語句注入與 `SELECT ... INTO`，一律在接觸使用者或資料庫之前被拒絕。模型輸出視為不可信，與任何輸入一視同仁。

### 功能特色

- 🌐 **雙介面**：終端機 UI（Textual）與網頁 GUI（FastAPI + 原生 JS）
- 🎯 **互動式查詢建構**：視覺化組裝查詢、即時驗證
- 🗄️ **多資料庫**：PostgreSQL、Oracle、MySQL、T-SQL、SQLite、Snowflake、BigQuery、DuckDB
- 🔁 **跨方言轉譯**：例如 `NVL`→`COALESCE`、`SYSDATE`→`CURRENT_TIMESTAMP`
- 🤖 **自然語言 → SQL**：Claude 生成，輸出再經同一道唯讀安全閘道驗證
- 🛡️ **唯讀安全**：AST 層級強制，加上列數上限與交易層防護
- 🚀 **免設定**：開箱即用

### 安裝

```bash
git clone https://github.com/Galen-Chu/Claude-SQLTrans.git
cd Claude-SQLTrans
pip install -e .            # 安裝
pip install -e ".[dev]"     # 含開發相依套件（測試、型別檢查、格式化）
```

> PyPI 發布（`pip install sqltrans`）規劃中。

### 快速開始

```bash
sqltrans --gui                 # 網頁 GUI（自動開啟瀏覽器）
sqltrans --tui                 # 終端機 UI
sqltrans --dialect postgresql  # 指定方言
```

### v2 功能現況（重要）

跨方言轉譯、NL→SQL、執行與 schema 探勘目前已實作於後端 HTTP API（`/api/transpile`、`/api/nl2sql`、`/api/schema`、`/api/query/execute`），但**尚未整合進 TUI／網頁 GUI**——前端目前仍只驅動 v1 查詢建構器。欲使用 v2，需直接呼叫 API（例如 `curl`）。UI 整合列為近期開發重點。

### 實用性評估

**最適合場景**：小型支援團隊、內部工具、個人查詢生產力工具；資料庫為 PostgreSQL / Oracle / MySQL 等主流方言。

**優勢**

- 解決真實痛點：非 SQL 專家需頻繁對客戶資料庫下查詢。
- sqlglot 轉譯為真實、實用的跨方言能力（非僅字串替換）。
- 唯讀 AST 安全策略是紮實且可對外暴露的安全性保證，並且每條 SQL 路徑都只把關一次。
- NL→SQL 進一步降低門檻；執行＋schema 探勘串起「問題 → 答案」的完整流程。
- 工程品質良好：模組化、型別標註、測試、文件齊全。

**限制**

- 目前為**單機、單人**工具：v1 介面使用模組層級共用狀態；每個請求皆建立新連線，不適合多使用者。
- API 無認證——僅適合本機使用，未經防護不可對外開放。
- v2 功能**尚無 UI**；NL→SQL 的即時連線路徑尚未端對端驗證。
- 具副作用的函式（如 Postgres `pg_terminate_backend`）與**查詢成本**尚未在 AST 層設限；真正最後防線是資料庫端的唯讀角色，而本工具並未強制。
- 使用者文件仍以 v1 查詢建構器為主；尚未上 PyPI／打包發布。

**結論**：作為個人／小團隊的內部工具，以及「以嚴謹安全設計為核心的 SQL 助理」範例，實用性高。但距離多人或不可信環境的正式部署仍有距離，需先補齊 UI 整合、執行強化與安全邊界（見下方開發方向）。

### 未來開發方向

- **近期**
  - 網頁「轉譯」分頁與 CLI `translate` 指令；將 NL→SQL 與執行整合進 UI。
  - 執行強化：語句逾時（per-dialect `statement_timeout`）、資料指標分頁、連線池、結果快取。
- **中期**
  - 連線管理：具名連線、金鑰保存於 vault／環境變數，而非隨請求傳遞。
  - NL→SQL 品質：各方言 few-shot 範例、「是否回答了問題」回饋迴圈。
  - 將 TUI 遷移至新引擎，移除已凍結的 v1 引擎；發布至 PyPI。
- **長期**
  - 多人使用與認證（若朝共享部署發展）。
  - 查詢審計日誌；查詢成本上限與函式允許清單。

### 文件

- [快速開始](docs/quick-start.md) · [教學](docs/tutorial.md) · [文件索引](docs/index.md) · [視覺導覽](docs/visual-walkthrough.md)
- [系統設計](SYSTEM_DESIGN.md) · [開發指南](docs/development.md) · [使用者指南](docs/user-guide.md)

### 系統需求

- Python 3.10 以上
- Windows / macOS / Linux

### 授權

MIT License—詳見 [LICENSE](LICENSE)。

---

## English

**SQLTrans** is an interactive SQL tool for customer-support engineers — build, transpile, and execute queries when troubleshooting customer database issues.

### Overview

SQLTrans unifies three capabilities:

- **Query building** — assemble SELECT queries (WHERE clauses, multi-dialect) through a visual interface with live validation and preview.
- **Cross-dialect transpilation** — convert SQL between Oracle, PostgreSQL, MySQL, T-SQL, and more, powered by [sqlglot](https://github.com/tobymao/sqlglot).
- **Natural-language generation + execution** — generate SQL from plain language (Claude) and run **read-only** queries against a live database, returning rows.

Every SQL string the system produces or runs is first gated by a **read-only safety policy enforced on the parsed AST** — writes (DML), schema changes (DDL), privilege (DCL), transaction control (TCL), multi-statement injection, and `SELECT ... INTO` are all rejected before reaching the user or the database. LLM output is treated as untrusted and validated exactly like any other input.

### Features

- 🌐 **Dual interface**: Terminal UI (Textual) and Web GUI (FastAPI + vanilla JS)
- 🎯 **Interactive builder** with real-time validation
- 🗄️ **Multi-database**: PostgreSQL, Oracle, MySQL, T-SQL, SQLite, Snowflake, BigQuery, DuckDB
- 🔁 **Cross-dialect transpilation** (e.g. `NVL`→`COALESCE`, `SYSDATE`→`CURRENT_TIMESTAMP`)
- 🤖 **Natural-language → SQL** via Claude, re-validated through the same read-only gate
- 🛡️ **Read-only safety**: AST-level enforcement, plus a row cap and transaction-layer defense
- 🚀 **Zero configuration**: works out of the box

### Installation

```bash
git clone https://github.com/Galen-Chu/Claude-SQLTrans.git
cd Claude-SQLTrans
pip install -e .            # install
pip install -e ".[dev]"     # with dev dependencies (tests, typing, formatting)
```

> A PyPI release (`pip install sqltrans`) is planned.

### Quick Start

```bash
sqltrans --gui                 # web GUI (opens a browser)
sqltrans --tui                 # terminal UI
sqltrans --dialect postgresql  # specify a dialect
```

### v2 feature status (important)

Cross-dialect transpilation, NL→SQL, execution, and schema introspection are implemented in the backend HTTP API (`/api/transpile`, `/api/nl2sql`, `/api/schema`, `/api/query/execute`), but are **not yet wired into the TUI / Web GUI** — the frontend still drives only the v1 query builder. To use v2 today you call the API directly (e.g. `curl`). UI integration is a near-term priority.

### Practicality assessment

**Best fit**: small support teams, internal tooling, a personal query-productivity tool, against PostgreSQL / Oracle / MySQL-class databases.

**Strengths**

- Solves a real pain point: non-SQL-experts who must frequently query customer databases.
- The sqlglot transpiler is genuine, useful cross-dialect power — not string replacement.
- The read-only AST policy is a solid, externally-exposable safety property, enforced exactly once per SQL path.
- NL→SQL lowers the barrier further; execution + introspection close the loop from question to answer.
- Good engineering hygiene: modular, type-hinted, tested, documented.

**Limitations**

- It is a **single-machine, single-user** tool today: the v1 UI uses module-level shared state; each request opens a new connection — not suited to concurrent multi-user use.
- The API has **no authentication** — localhost only; do not expose it unguarded.
- v2 has **no UI yet**; the NL→SQL live path has not been verified end-to-end.
- Side-effecting functions (e.g. Postgres `pg_terminate_backend`) and **query cost** are not bounded at the AST layer; the true last line of defense is a read-only database role, which the tool does not enforce.
- User-facing docs still focus on the v1 builder; no PyPI/packaged release yet.

**Verdict**: Highly practical as a personal/small-team internal tool and as a reference design for a safety-first SQL assistant. It is not yet production-ready for multi-user or untrusted environments — that needs UI integration, execution hardening, and closed safety boundaries (see roadmap below).

### Future development directions

- **Near-term**
  - A web "Translate" tab and a `translate` CLI; wire NL→SQL and execution into the UI.
  - Execution hardening: per-dialect statement timeouts, server-side cursor pagination, connection pooling, result caching.
- **Mid-term**
  - Connection management: named, stored connections with secrets in a vault / env vars rather than the request body.
  - NL→SQL quality: per-dialect few-shot examples, a "did this answer the question?" feedback loop.
  - Migrate the TUI onto the new engine and remove the frozen v1 engine; ship to PyPI.
- **Long-term**
  - Multi-user support and authentication (if moving toward shared deployment).
  - Query audit logging; query-cost caps and a function allowlist.

### Documentation

- [Quick Start](docs/quick-start.md) · [Tutorial](docs/tutorial.md) · [Documentation Index](docs/index.md) · [Visual Walkthrough](docs/visual-walkthrough.md)
- [System Design](SYSTEM_DESIGN.md) · [Development Guide](docs/development.md) · [User Guide](docs/user-guide.md)

### Requirements

- Python 3.10+
- Windows / macOS / Linux

### License

MIT License — see [LICENSE](LICENSE).
