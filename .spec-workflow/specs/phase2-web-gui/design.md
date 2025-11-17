# Design Document - Phase 2: Web GUI Mode

## Architecture Overview

The web GUI mode extends SQLTrans with a local web server and browser-based interface while reusing 100% of the existing business logic. The architecture follows a clean separation between layers:

```
┌─────────────────────────────────────────┐
│         Web Browser (Frontend)           │
│   HTML + CSS + Vanilla JavaScript       │
│   - Query Builder UI                    │
│   - Real-time SQL Preview               │
│   - Syntax Highlighting                 │
└─────────────────┬───────────────────────┘
                  │ HTTP/JSON
                  │ REST API
┌─────────────────▼───────────────────────┐
│    FastAPI Backend (src/sqltrans/web)   │
│   - API Endpoints (/api/*)              │
│   - Static File Serving                 │
│   - Request Validation                  │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│   Existing Business Logic (Reused)      │
│   - models/query.py (QueryState)        │
│   - sql/builder.py (QueryBuilder)       │
│   - sql/dialects/* (SQL Generation)     │
│   - utils/validation.py (Validation)    │
└──────────────────────────────────────────┘
```

## Technology Stack

### Backend
- **Framework**: FastAPI 0.104+ (async, fast, OpenAPI docs)
- **Server**: Uvicorn (ASGI server)
- **Dependencies**: Minimal additions to existing requirements

### Frontend
- **HTML5**: Semantic markup
- **CSS3**: Modern styling with Flexbox/Grid
- **JavaScript**: Vanilla ES6+ (no framework overhead)
- **Syntax Highlighting**: Prism.js or Highlight.js for SQL

### Integration
- **Launcher**: Modified `__main__.py` with --gui/--tui flags
- **Browser**: Python `webbrowser` module for auto-open

## Component Design

### 1. FastAPI Web Application (`src/sqltrans/web/app.py`)

```python
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

# Reuse existing components
from sqltrans.models.query import QueryState
from sqltrans.sql.builder import QueryBuilder
from sqltrans.sql.dialects import get_dialect
from sqltrans.sql.formatter import format_sql, highlight_to_html

app = FastAPI(title="SQLTrans Web GUI")

# Global state (single-user local app)
query_state = QueryState()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# API endpoints (see API Design section below)
```

**Key Design Decisions:**
- Single global `QueryState` instance (local single-user app)
- Synchronous business logic calls (existing code is sync)
- Static file serving for frontend assets
- CORS disabled (localhost only)

### 2. REST API Design

#### Query State Management

**GET /api/query**
```json
Response 200:
{
  "table": "users",
  "columns": ["id", "name", "email"],
  "filters": [
    {"column": "status", "operator": "=", "value": "active"}
  ],
  "dialect": "postgresql"
}
```

**POST /api/query/table**
```json
Request: {"name": "users"}
Response 200: {"table": "users"}
Response 400: {"error": "Invalid identifier"}
```

**POST /api/query/columns/add**
```json
Request: {"column": "email"}
Response 200: {"columns": ["id", "name", "email"]}
```

**DELETE /api/query/columns/{column}**
```json
Response 200: {"columns": ["id", "name"]}
```

**POST /api/query/filters/add**
```json
Request: {
  "column": "status",
  "operator": "=",
  "value": "active"
}
Response 200: {"filters": [...]}
Response 400: {"error": "Invalid filter"}
```

**DELETE /api/query/filters/{index}**
```json
Response 200: {"filters": [...]}
```

**POST /api/query/dialect**
```json
Request: {"dialect": "postgresql"}
Response 200: {"dialect": "postgresql", "sql": "..."}
```

**POST /api/query/clear**
```json
Response 200: {"message": "Query cleared"}
```

**GET /api/query/sql**
```json
Response 200: {
  "sql": "SELECT \"id\", \"name\" FROM \"users\" WHERE \"status\" = 'active'",
  "formatted": "...",  // With line breaks
  "html": "..."        // With syntax highlighting
}
```

**GET /api/dialects**
```json
Response 200: {
  "dialects": ["postgresql", "oracle", "generic"]
}
```

### 3. Frontend Structure (`src/sqltrans/web/static/`)

```
static/
├── index.html          # Main application page
├── css/
│   ├── main.css       # Core styles
│   ├── query-builder.css  # Query builder components
│   └── syntax-highlight.css  # SQL syntax highlighting
├── js/
│   ├── app.js         # Main application logic
│   ├── api.js         # API client (fetch wrapper)
│   ├── query-builder.js  # Query builder UI component
│   └── sql-preview.js    # SQL preview component
└── lib/
    └── prism.min.js   # Syntax highlighting library
```

### 4. Frontend Architecture

#### App Initialization (`js/app.js`)
```javascript
class SQLTransApp {
  constructor() {
    this.api = new APIClient();
    this.queryBuilder = new QueryBuilder();
    this.sqlPreview = new SQLPreview();
    this.init();
  }

  async init() {
    // Load initial state
    // Set up event listeners
    // Initialize components
  }
}

document.addEventListener('DOMContentLoaded', () => {
  new SQLTransApp();
});
```

#### API Client (`js/api.js`)
```javascript
class APIClient {
  constructor(baseURL = '/api') {
    this.baseURL = baseURL;
  }

  async getQueryState() { /* ... */ }
  async setTable(name) { /* ... */ }
  async addColumn(column) { /* ... */ }
  async removeColumn(column) { /* ... */ }
  async addFilter(filter) { /* ... */ }
  async removeFilter(index) { /* ... */ }
  async setDialect(dialect) { /* ... */ }
  async clearQuery() { /* ... */ }
  async getSQL() { /* ... */ }
}
```

#### Query Builder Component (`js/query-builder.js`)
```javascript
class QueryBuilder {
  constructor() {
    this.elements = {
      dialectSelect: document.getElementById('dialect-select'),
      tableInput: document.getElementById('table-input'),
      columnList: document.getElementById('column-list'),
      filterList: document.getElementById('filter-list'),
      // ...
    };
    this.attachEventListeners();
  }

  async handleTableChange() { /* ... */ }
  async handleAddColumn() { /* ... */ }
  async handleAddFilter() { /* ... */ }
  render() { /* ... */ }
}
```

#### SQL Preview Component (`js/sql-preview.js`)
```javascript
class SQLPreview {
  constructor() {
    this.container = document.getElementById('sql-preview');
    this.copyBtn = document.getElementById('copy-btn');
    this.downloadBtn = document.getElementById('download-btn');
    this.attachEventListeners();
  }

  async update() {
    const data = await api.getSQL();
    this.render(data.html);
  }

  async copyToClipboard() { /* ... */ }
  downloadSQL() { /* ... */ }
}
```

### 5. UI Layout Design

```html
<!DOCTYPE html>
<html>
<head>
  <title>SQLTrans - Query Builder</title>
  <link rel="stylesheet" href="/static/css/main.css">
</head>
<body>
  <div class="app-container">
    <!-- Header -->
    <header class="header">
      <h1>SQLTrans Query Builder</h1>
      <div class="dialect-selector">
        <label>Dialect:</label>
        <select id="dialect-select">
          <option value="generic">Generic SQL</option>
          <option value="postgresql">PostgreSQL</option>
          <option value="oracle">Oracle</option>
        </select>
      </div>
    </header>

    <!-- Main Content -->
    <main class="main-content">
      <!-- Left Panel: Query Builder -->
      <aside class="query-builder">
        <!-- Table Selection -->
        <section class="section">
          <h2>Table</h2>
          <input type="text" id="table-input" placeholder="Enter table name">
          <span class="validation-error" id="table-error"></span>
        </section>

        <!-- Column Selection -->
        <section class="section">
          <h2>Columns</h2>
          <div class="input-group">
            <input type="text" id="column-input" placeholder="Column name">
            <button id="add-column-btn">Add Column</button>
          </div>
          <ul id="column-list" class="item-list"></ul>
          <span class="help-text">Leave empty for SELECT *</span>
        </section>

        <!-- Filter Builder -->
        <section class="section">
          <h2>Filters (WHERE)</h2>
          <div class="filter-form">
            <input type="text" id="filter-column" placeholder="Column">
            <select id="filter-operator">
              <option value="=">=</option>
              <option value="!=">!=</option>
              <option value="<"><</option>
              <option value=">">></option>
              <option value="<="><=</option>
              <option value=">=">>=</option>
              <option value="LIKE">LIKE</option>
              <option value="IN">IN</option>
              <option value="IS NULL">IS NULL</option>
              <option value="IS NOT NULL">IS NOT NULL</option>
            </select>
            <input type="text" id="filter-value" placeholder="Value">
            <button id="add-filter-btn">Add Filter</button>
          </div>
          <ul id="filter-list" class="item-list"></ul>
        </section>

        <!-- Actions -->
        <section class="section actions">
          <button id="clear-query-btn" class="btn-secondary">Clear Query</button>
        </section>
      </aside>

      <!-- Right Panel: SQL Preview -->
      <section class="sql-panel">
        <div class="panel-header">
          <h2>Generated SQL</h2>
          <div class="panel-actions">
            <button id="copy-btn" class="btn-primary">Copy to Clipboard</button>
            <button id="download-btn" class="btn-secondary">Download</button>
          </div>
        </div>
        <div id="sql-preview" class="sql-display">
          <pre><code class="language-sql">-- Build your query using the form on the left</code></pre>
        </div>
      </section>
    </main>
  </div>

  <!-- Toast Notifications -->
  <div id="toast-container"></div>

  <script src="/static/js/api.js"></script>
  <script src="/static/js/query-builder.js"></script>
  <script src="/static/js/sql-preview.js"></script>
  <script src="/static/js/app.js"></script>
  <script src="/static/lib/prism.min.js"></script>
</body>
</html>
```

### 6. Styling Approach

**Color Scheme** (Professional, modern):
```css
:root {
  --primary-color: #2563eb;      /* Blue */
  --secondary-color: #64748b;    /* Slate */
  --success-color: #10b981;      /* Green */
  --error-color: #ef4444;        /* Red */
  --background: #f8fafc;         /* Light gray */
  --surface: #ffffff;            /* White */
  --border: #e2e8f0;            /* Light border */
  --text-primary: #1e293b;      /* Dark gray */
  --text-secondary: #64748b;    /* Medium gray */
  --code-bg: #1e293b;           /* Dark for code */
  --code-text: #e2e8f0;         /* Light for code */
}
```

**Layout Principles**:
- Two-column layout: Query builder (left) + SQL preview (right)
- Responsive: Stack vertically on smaller screens
- Fixed header with dialect selector
- Scrollable sections for long content
- Card-based sections with subtle shadows

### 7. Modified Launcher (`src/sqltrans/__main__.py`)

```python
def main() -> None:
    parser = argparse.ArgumentParser(...)
    
    # Add mode selection
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--gui",
        action="store_true",
        help="Launch web GUI mode in browser"
    )
    mode_group.add_argument(
        "--tui",
        action="store_true",
        help="Launch terminal UI mode (default)"
    )
    
    # ... existing arguments ...
    
    args = parser.parse_args()
    
    # Determine mode
    if args.gui:
        from sqltrans.web.launcher import launch_web_gui
        launch_web_gui(initial_dialect=initial_dialect)
    else:
        # Launch TUI (existing code)
        from sqltrans.ui.app import SQLTransApp
        app = SQLTransApp(initial_dialect=initial_dialect)
        app.run()
```

### 8. Web Server Launcher (`src/sqltrans/web/launcher.py`)

```python
import webbrowser
import uvicorn
from threading import Timer

def find_free_port(start_port=8000, max_attempts=10):
    """Find an available port starting from start_port."""
    # Implementation...

def open_browser(url):
    """Open browser after server starts."""
    webbrowser.open(url)

def launch_web_gui(initial_dialect="generic", port=None):
    """Launch the web GUI server and open browser."""
    if port is None:
        port = find_free_port()
    
    url = f"http://127.0.0.1:{port}"
    print(f"Starting SQLTrans Web GUI on {url}")
    print("Press Ctrl+C to stop the server")
    
    # Open browser after 1 second delay
    Timer(1.0, open_browser, args=[url]).start()
    
    # Start server (blocks until Ctrl+C)
    uvicorn.run(
        "sqltrans.web.app:app",
        host="127.0.0.1",
        port=port,
        log_level="warning"
    )
```

## Code Reuse Strategy

### Reused Components (100% reuse)
- ✅ `models/query.py` - QueryState class
- ✅ `models/filters.py` - Filter class
- ✅ `models/schema.py` - Table, Column classes
- ✅ `sql/builder.py` - QueryBuilder class
- ✅ `sql/dialects/*` - All dialect implementations
- ✅ `sql/formatter.py` - SQL formatting (extend for HTML output)
- ✅ `utils/validation.py` - All validation functions
- ✅ `utils/config.py` - Configuration loading

### New Components
- `web/app.py` - FastAPI application
- `web/launcher.py` - Web server launcher
- `web/static/*` - Frontend files (HTML, CSS, JS)

### Modified Components
- `__main__.py` - Add --gui/--tui flags
- `sql/formatter.py` - Add `highlight_to_html()` function for web

## Error Handling Strategy

### Backend Errors
- Validation errors → 400 Bad Request with error details
- Internal errors → 500 Internal Server Error with generic message
- Logging all errors to file for debugging

### Frontend Errors
- API errors → Toast notifications with user-friendly messages
- Validation errors → Inline error messages near inputs
- Network errors → Retry suggestion + fallback message

### Graceful Degradation
- If syntax highlighting fails → Show plain SQL
- If clipboard API unavailable → Provide download option
- If browser doesn't auto-open → Show URL in console

## Performance Considerations

### Backend
- No database → Instant responses
- Lightweight state → Minimal memory usage
- Async FastAPI → Non-blocking I/O

### Frontend
- Vanilla JS → No framework overhead
- Debouncing → Avoid excessive API calls
- Lazy loading → Load syntax highlighter only when needed

## Security Considerations

### Localhost Only
- Server binds to 127.0.0.1 (not 0.0.0.0)
- No external network access
- No authentication needed

### Input Validation
- Double validation (frontend + backend)
- SQL injection prevention (reused from existing code)
- No arbitrary code execution

## Testing Strategy

### Backend Tests
- API endpoint tests using FastAPI TestClient
- Reuse existing business logic tests
- Integration tests for API + business logic

### Frontend Tests
- Manual testing in major browsers
- API integration testing
- User flow testing (add table, columns, filters, export)

### E2E Tests
- Launch server programmatically
- Use Selenium/Playwright for browser automation
- Test complete workflows

## Deployment Considerations

### Package Distribution
- FastAPI and Uvicorn added to requirements.txt
- Static files included in package (pyproject.toml)
- No additional setup needed by users

### Cross-Platform
- Uvicorn works on Windows, Mac, Linux
- Browser auto-open works cross-platform
- Port selection handles conflicts automatically

## Future Enhancements

- **Multiple Tabs**: Support multiple concurrent queries
- **Query History**: Save and load previous queries
- **Dark Mode**: Toggle between light/dark themes
- **Export Options**: Additional formats (JSON, CSV)
- **Keyboard Shortcuts**: Power user features
- **Templates**: Pre-built query templates
