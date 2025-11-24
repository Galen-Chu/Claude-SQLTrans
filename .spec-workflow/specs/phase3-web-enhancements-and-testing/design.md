# Design Document - Phase 3: Web GUI Enhancements & E2E Testing

## Introduction

This document describes the technical design for Phase 3 features, covering web GUI enhancements and comprehensive E2E testing infrastructure.

---

# Part A: Web GUI Enhancements - Technical Design

## 1. Query History & Persistence

### Architecture

**Storage Layer:**
```javascript
// src/sqltrans/web/static/js/storage.js
class QueryStorage {
  constructor() {
    this.storageKey = 'sqltrans_query_history';
    this.maxQueries = 50;
  }

  saveQuery(queryState, name) {
    // Save to localStorage with metadata
  }

  loadQuery(id) {
    // Load query by ID
  }

  listQueries() {
    // Return all saved queries
  }

  deleteQuery(id) {
    // Remove query from history
  }

  exportHistory() {
    // Export as JSON file
  }

  importHistory(jsonData) {
    // Import and merge queries
  }
}
```

**Data Model:**
```javascript
{
  id: "uuid-v4",
  name: "User-provided name",
  queryState: {
    table: "users",
    columns: ["id", "name"],
    filters: [...],
    dialect: "postgresql"
  },
  metadata: {
    createdAt: "2025-11-17T10:30:00Z",
    lastUsed: "2025-11-17T11:00:00Z",
    useCount: 5
  }
}
```

**UI Components:**
```html
<!-- History Sidebar -->
<aside id="history-sidebar" class="collapsed">
  <div class="sidebar-header">
    <h3>Query History</h3>
    <button id="close-sidebar">×</button>
  </div>
  <div class="sidebar-actions">
    <button id="export-history">Export</button>
    <button id="import-history">Import</button>
  </div>
  <div class="search-box">
    <input type="text" placeholder="Search queries...">
  </div>
  <ul id="history-list">
    <!-- Query items rendered here -->
  </ul>
</aside>
```

**Integration Points:**
- Auto-save on every query change (debounced 2 seconds)
- Load query replaces current state
- History sidebar toggles with Ctrl+H
- Export/import buttons in sidebar

---

## 2. Dark Mode Theme

### Architecture

**CSS Variables Approach:**
```css
/* src/sqltrans/web/static/css/themes.css */
:root {
  /* Light theme (default) */
  --color-bg-primary: #ffffff;
  --color-bg-secondary: #f5f7fa;
  --color-text-primary: #1a202c;
  --color-text-secondary: #4a5568;
  --color-border: #e2e8f0;
  --color-accent: #3b82f6;
  --color-success: #10b981;
  --color-error: #ef4444;
  --shadow-sm: rgba(0, 0, 0, 0.05);
  --shadow-md: rgba(0, 0, 0, 0.1);
}

[data-theme="dark"] {
  /* Dark theme */
  --color-bg-primary: #1a202c;
  --color-bg-secondary: #2d3748;
  --color-text-primary: #f7fafc;
  --color-text-secondary: #e2e8f0;
  --color-border: #4a5568;
  --color-accent: #60a5fa;
  --color-success: #34d399;
  --color-error: #f87171;
  --shadow-sm: rgba(0, 0, 0, 0.3);
  --shadow-md: rgba(0, 0, 0, 0.5);
}
```

**Theme Manager:**
```javascript
// src/sqltrans/web/static/js/theme.js
class ThemeManager {
  constructor() {
    this.storageKey = 'sqltrans_theme';
    this.init();
  }

  init() {
    // Detect OS preference
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    const savedTheme = localStorage.getItem(this.storageKey);
    this.setTheme(savedTheme || (prefersDark ? 'dark' : 'light'));

    // Listen for OS changes
    window.matchMedia('(prefers-color-scheme: dark)')
      .addEventListener('change', (e) => {
        if (!localStorage.getItem(this.storageKey)) {
          this.setTheme(e.matches ? 'dark' : 'light');
        }
      });
  }

  setTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem(this.storageKey, theme);
    this.updatePrismTheme(theme);
  }

  toggle() {
    const current = document.documentElement.getAttribute('data-theme');
    this.setTheme(current === 'dark' ? 'light' : 'dark');
  }

  updatePrismTheme(theme) {
    // Swap Prism CSS for dark/light syntax highlighting
  }
}
```

**UI Integration:**
```html
<button id="theme-toggle" aria-label="Toggle dark mode">
  <svg class="sun-icon">...</svg>
  <svg class="moon-icon">...</svg>
</button>
```

---

## 3. Keyboard Shortcuts

### Architecture

**Keyboard Manager:**
```javascript
// src/sqltrans/web/static/js/keyboard.js
class KeyboardManager {
  constructor(app) {
    this.app = app;
    this.shortcuts = {
      'Ctrl+Enter': () => this.app.copySQL(),
      'Ctrl+D': () => this.app.downloadSQL(),
      'Ctrl+K': () => this.app.clearQuery(),
      'Ctrl+H': () => this.app.toggleHistory(),
      'Ctrl+/': () => this.showHelp(),
      'Escape': () => this.closeModals(),
    };
    this.init();
  }

  init() {
    document.addEventListener('keydown', (e) => {
      const key = this.getKeyCombo(e);
      if (this.shortcuts[key]) {
        e.preventDefault();
        this.shortcuts[key]();
      }
    });
  }

  getKeyCombo(event) {
    const parts = [];
    if (event.ctrlKey || event.metaKey) parts.push('Ctrl');
    if (event.shiftKey) parts.push('Shift');
    if (event.altKey) parts.push('Alt');

    const key = event.key === ' ' ? 'Space' : event.key;
    parts.push(key);

    return parts.join('+');
  }

  showHelp() {
    // Display keyboard shortcuts modal
  }
}
```

**Help Modal:**
```html
<div id="shortcuts-modal" class="modal">
  <div class="modal-content">
    <h2>Keyboard Shortcuts</h2>
    <table class="shortcuts-table">
      <tr>
        <td><kbd>Ctrl</kbd> + <kbd>Enter</kbd></td>
        <td>Copy SQL to clipboard</td>
      </tr>
      <tr>
        <td><kbd>Ctrl</kbd> + <kbd>D</kbd></td>
        <td>Download SQL file</td>
      </tr>
      <!-- More shortcuts -->
    </table>
  </div>
</div>
```

---

## 4. Enhanced Export Options

### Architecture

**Export Manager:**
```javascript
// src/sqltrans/web/static/js/export.js
class ExportManager {
  constructor(app) {
    this.app = app;
  }

  exportSQL(queryState, sql) {
    const content = this.generateSQLFile(queryState, sql);
    const filename = this.generateFilename(queryState, 'sql');
    this.download(content, filename, 'text/sql');
  }

  exportJSON(queryState) {
    const content = JSON.stringify({
      version: '1.0',
      exportedAt: new Date().toISOString(),
      queryState: queryState
    }, null, 2);
    const filename = this.generateFilename(queryState, 'json');
    this.download(content, filename, 'application/json');
  }

  exportCSV(queryState) {
    // Generate CSV template with column headers
    const headers = queryState.columns.join(',');
    const content = headers + '\n';
    const filename = this.generateFilename(queryState, 'csv');
    this.download(content, filename, 'text/csv');
  }

  generateSQLFile(queryState, sql) {
    return `-- SQLTrans Query Export
-- Table: ${queryState.table}
-- Dialect: ${queryState.dialect}
-- Generated: ${new Date().toISOString()}
-- Columns: ${queryState.columns.join(', ')}

${sql}
`;
  }

  generateFilename(queryState, extension) {
    const table = queryState.table || 'query';
    const dialect = queryState.dialect;
    const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
    return `${table}_${dialect}_${timestamp}.${extension}`;
  }

  download(content, filename, mimeType) {
    const blob = new Blob([content], { type: mimeType });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  }
}
```

**UI Integration:**
```html
<div class="export-dropdown">
  <button id="export-button">Export ▼</button>
  <ul class="dropdown-menu">
    <li><button data-format="sql">SQL File</button></li>
    <li><button data-format="json">JSON (Query State)</button></li>
    <li><button data-format="csv">CSV Template</button></li>
  </ul>
</div>
```

---

## 5. Advanced Filter Groups (OR Logic)

### Architecture

**Data Model Enhancement:**
```javascript
// Enhanced filter structure
{
  filterGroups: [
    {
      id: "group-1",
      operator: "AND", // Group-level operator (between groups)
      filters: [
        { column: "status", operator: "=", value: "active" },
        { column: "age", operator: ">", value: "18" }
      ],
      groupOperator: "OR" // Within-group operator
    },
    {
      id: "group-2",
      operator: "AND",
      filters: [
        { column: "country", operator: "=", value: "US" }
      ],
      groupOperator: "AND"
    }
  ]
}

// Generates: (status = 'active' OR age > '18') AND (country = 'US')
```

**SQL Generation:**
```javascript
// Extension to QueryBuilder
class AdvancedQueryBuilder extends QueryBuilder {
  buildWhereClause(filterGroups) {
    if (filterGroups.length === 0) return '';

    const groupClauses = filterGroups.map(group => {
      if (group.filters.length === 0) return null;

      const filterClauses = group.filters.map(f =>
        this.buildFilterClause(f)
      );

      const groupClause = filterClauses.join(` ${group.groupOperator} `);
      return group.filters.length > 1 ? `(${groupClause})` : groupClause;
    }).filter(Boolean);

    return 'WHERE ' + groupClauses.join(' AND ');
  }
}
```

**UI Components:**
```html
<div class="filter-groups">
  <div class="filter-group" data-group-id="group-1">
    <div class="group-header">
      <span class="group-label">Group 1</span>
      <select class="group-operator">
        <option value="AND">AND</option>
        <option value="OR">OR</option>
      </select>
      <button class="delete-group">×</button>
    </div>
    <div class="filters-list">
      <!-- Individual filters -->
    </div>
    <button class="add-filter-to-group">+ Add Filter</button>
  </div>
  <button id="add-filter-group">+ Add OR Group</button>
</div>
```

---

## 6. Query Templates

### Architecture

**Template Data Structure:**
```javascript
// src/sqltrans/web/static/js/templates.js
const builtInTemplates = [
  {
    id: 'customer-lookup',
    name: 'Customer Lookup',
    description: 'Find customer by ID or email',
    queryState: {
      table: 'customers',
      columns: ['id', 'email', 'name', 'created_at'],
      filters: [
        { column: 'id', operator: '=', value: '{{CUSTOMER_ID}}' }
      ],
      dialect: 'postgresql'
    },
    placeholders: ['{{CUSTOMER_ID}}']
  },
  {
    id: 'recent-records',
    name: 'Recent Records',
    description: 'Records from last 7 days',
    queryState: {
      table: '{{TABLE_NAME}}',
      columns: ['*'],
      filters: [
        { column: 'created_at', operator: '>=', value: '{{START_DATE}}' }
      ],
      dialect: 'postgresql'
    },
    placeholders: ['{{TABLE_NAME}}', '{{START_DATE}}']
  },
  // More templates...
];

class TemplateManager {
  constructor() {
    this.templates = this.loadTemplates();
  }

  loadTemplates() {
    const custom = JSON.parse(localStorage.getItem('sqltrans_templates') || '[]');
    return [...builtInTemplates, ...custom];
  }

  applyTemplate(templateId, app) {
    const template = this.templates.find(t => t.id === templateId);
    if (!template) return;

    // Apply query state
    app.loadQueryState(template.queryState);

    // Highlight placeholders for user to replace
    this.highlightPlaceholders(template.placeholders);
  }

  saveAsTemplate(queryState, name, description) {
    const template = {
      id: `custom-${Date.now()}`,
      name,
      description,
      queryState,
      custom: true
    };

    const custom = JSON.parse(localStorage.getItem('sqltrans_templates') || '[]');
    custom.push(template);
    localStorage.setItem('sqltrans_templates', JSON.stringify(custom));
  }
}
```

---

## 7. Real-time SQL Validation

### Architecture

**Backend API Endpoint:**
```python
# src/sqltrans/web/app.py
@app.post("/api/query/validate")
async def validate_sql(request: ValidateRequest):
    """Validate SQL syntax for the given dialect."""
    try:
        # Parse SQL using dialect-specific parser
        dialect = get_dialect(request.dialect)
        result = dialect.validate_sql(request.sql)

        return {
            "valid": result.valid,
            "errors": result.errors,
            "warnings": result.warnings
        }
    except Exception as e:
        return {"valid": False, "errors": [str(e)]}
```

**Frontend Validator:**
```javascript
// src/sqltrans/web/static/js/validator.js
class SQLValidator {
  constructor(api) {
    this.api = api;
    this.cache = new Map();
  }

  async validate(sql, dialect) {
    const cacheKey = `${dialect}:${sql}`;
    if (this.cache.has(cacheKey)) {
      return this.cache.get(cacheKey);
    }

    try {
      const result = await this.api.validateSQL(sql, dialect);
      this.cache.set(cacheKey, result);
      return result;
    } catch (error) {
      return { valid: false, errors: [error.message] };
    }
  }

  displayValidation(result) {
    const indicator = document.getElementById('validation-indicator');
    if (result.valid) {
      indicator.classList.add('valid');
      indicator.textContent = '✓ Valid SQL';
    } else {
      indicator.classList.add('invalid');
      indicator.textContent = `✗ ${result.errors[0]}`;
    }
  }
}
```

---

# Part B: E2E Testing - Technical Design

## 8. Web GUI E2E Testing Framework

### Architecture

**Directory Structure:**
```
tests/
├── e2e/
│   ├── web/
│   │   ├── conftest.py          # Pytest fixtures
│   │   ├── pages/               # Page Object Models
│   │   │   ├── __init__.py
│   │   │   ├── query_builder.py
│   │   │   └── history_sidebar.py
│   │   ├── test_query_building.py
│   │   ├── test_filters.py
│   │   ├── test_export.py
│   │   ├── test_history.py
│   │   ├── test_dark_mode.py
│   │   └── test_keyboard_shortcuts.py
│   ├── api/
│   │   ├── conftest.py
│   │   ├── test_query_endpoints.py
│   │   └── test_validation.py
│   └── tui/
│       ├── conftest.py
│       └── test_tui_navigation.py
├── fixtures/                     # Test data
│   ├── queries.json
│   └── templates.json
└── reports/                      # Generated test reports
```

**Page Object Pattern:**
```python
# tests/e2e/web/pages/query_builder.py
from playwright.sync_api import Page, expect

class QueryBuilderPage:
    """Page Object Model for Query Builder."""

    def __init__(self, page: Page):
        self.page = page
        self.url = "http://localhost:8000"

        # Locators
        self.table_input = page.locator("#table-name")
        self.add_column_input = page.locator("#column-name")
        self.add_column_btn = page.locator("#add-column")
        self.sql_preview = page.locator("#sql-preview")
        self.dialect_select = page.locator("#dialect-select")
        self.copy_btn = page.locator("#copy-sql")

    def navigate(self):
        """Navigate to query builder page."""
        self.page.goto(self.url)

    def set_table(self, table_name: str):
        """Set the table name."""
        self.table_input.fill(table_name)
        self.table_input.press("Enter")

    def add_column(self, column_name: str):
        """Add a column to the query."""
        self.add_column_input.fill(column_name)
        self.add_column_btn.click()

    def change_dialect(self, dialect: str):
        """Change SQL dialect."""
        self.dialect_select.select_option(dialect)

    def get_sql(self) -> str:
        """Get generated SQL."""
        return self.sql_preview.text_content()

    def copy_sql(self):
        """Click copy SQL button."""
        self.copy_btn.click()
```

**Test Example:**
```python
# tests/e2e/web/test_query_building.py
import pytest
from playwright.sync_api import Page, expect
from pages.query_builder import QueryBuilderPage

def test_build_simple_query(page: Page, query_builder: QueryBuilderPage):
    """Test building a simple SELECT query."""
    # Arrange
    query_builder.navigate()

    # Act
    query_builder.set_table("users")
    query_builder.add_column("id")
    query_builder.add_column("name")

    # Assert
    sql = query_builder.get_sql()
    assert 'SELECT "id", "name"' in sql
    assert 'FROM "users"' in sql

def test_dialect_switching(page: Page, query_builder: QueryBuilderPage):
    """Test switching between SQL dialects."""
    # Arrange
    query_builder.navigate()
    query_builder.set_table("users")
    query_builder.add_column("id")

    # Act & Assert - PostgreSQL
    query_builder.change_dialect("postgresql")
    expect(query_builder.sql_preview).to_contain_text('"id"')

    # Act & Assert - Oracle
    query_builder.change_dialect("oracle")
    expect(query_builder.sql_preview).to_contain_text('"ID"')
```

**Fixtures:**
```python
# tests/e2e/web/conftest.py
import pytest
from playwright.sync_api import Page
from pages.query_builder import QueryBuilderPage

@pytest.fixture
def query_builder(page: Page) -> QueryBuilderPage:
    """Provide QueryBuilderPage instance."""
    return QueryBuilderPage(page)

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context."""
    return {
        **browser_context_args,
        "viewport": {"width": 1920, "height": 1080},
        "locale": "en-US",
    }
```

---

## 9. API Integration Testing

### Architecture

**API Test Client:**
```python
# tests/e2e/api/conftest.py
import pytest
import requests
from typing import Generator

class APIClient:
    """Test client for SQLTrans API."""

    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()

    def get_query_state(self):
        """Get current query state."""
        response = self.session.get(f"{self.base_url}/api/query")
        response.raise_for_status()
        return response.json()

    def set_table(self, name: str):
        """Set table name."""
        response = self.session.post(
            f"{self.base_url}/api/query/table",
            json={"name": name}
        )
        response.raise_for_status()
        return response.json()

    def add_column(self, column: str):
        """Add column."""
        response = self.session.post(
            f"{self.base_url}/api/query/columns/add",
            json={"column": column}
        )
        response.raise_for_status()
        return response.json()

@pytest.fixture(scope="session")
def api_client() -> Generator[APIClient, None, None]:
    """Provide API client for testing."""
    client = APIClient("http://localhost:8000")
    yield client
    # Cleanup if needed
```

**API Tests:**
```python
# tests/e2e/api/test_query_endpoints.py
import pytest
from conftest import APIClient

def test_set_table(api_client: APIClient):
    """Test setting table name via API."""
    # Act
    result = api_client.set_table("users")

    # Assert
    assert result["table"] == "users"

    # Verify state
    state = api_client.get_query_state()
    assert state["table"] == "users"

def test_add_columns(api_client: APIClient):
    """Test adding columns via API."""
    # Arrange
    api_client.set_table("users")

    # Act
    api_client.add_column("id")
    api_client.add_column("name")

    # Assert
    state = api_client.get_query_state()
    assert "id" in state["columns"]
    assert "name" in state["columns"]

def test_invalid_table_name(api_client: APIClient):
    """Test validation for invalid table name."""
    with pytest.raises(requests.HTTPError) as exc_info:
        api_client.set_table("")

    assert exc_info.value.response.status_code == 400
```

---

## 10. TUI E2E Testing

### Architecture

**TUI Test Framework:**
```python
# tests/e2e/tui/test_tui_navigation.py
import pytest
from textual.pilot import Pilot
from sqltrans.ui.app import SQLTransApp

@pytest.mark.asyncio
async def test_tui_query_building():
    """Test building query in TUI."""
    app = SQLTransApp()

    async with app.run_test() as pilot:
        # Navigate to query screen
        await pilot.press("tab")  # Focus table input
        await pilot.press(*"users")
        await pilot.press("enter")

        # Add column
        await pilot.press("tab")
        await pilot.press(*"id")
        await pilot.press("enter")

        # Verify SQL preview
        sql_widget = app.query_one("#sql-preview")
        assert "users" in sql_widget.text
        assert "id" in sql_widget.text

@pytest.mark.asyncio
async def test_tui_dialect_switching():
    """Test switching dialects in TUI."""
    app = SQLTransApp(initial_dialect="postgresql")

    async with app.run_test() as pilot:
        # Navigate to dialect selector
        await pilot.press("ctrl+d")  # Shortcut for dialect
        await pilot.press("down")
        await pilot.press("enter")

        # Verify dialect changed
        assert app.current_dialect == "oracle"
```

---

## 11. CI/CD Integration

### Architecture

**GitHub Actions Workflow:**
```yaml
# .github/workflows/tests.yml
name: Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install ruff mypy
          pip install -e ".[dev]"
      - name: Lint with ruff
        run: ruff check src/
      - name: Type check with mypy
        run: mypy src/sqltrans

  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: pip install -e ".[dev]"
      - name: Run unit tests
        run: pytest tests/unit -v --cov=src/sqltrans
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  api-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: pip install -e ".[dev]"
      - name: Run API tests
        run: pytest tests/e2e/api -v

  web-e2e-tests:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        browser: [chromium, firefox]
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -e ".[dev]"
          playwright install ${{ matrix.browser }}
      - name: Run E2E tests
        run: pytest tests/e2e/web -v --browser=${{ matrix.browser }}
      - name: Upload screenshots on failure
        if: failure()
        uses: actions/upload-artifact@v3
        with:
          name: screenshots-${{ matrix.browser }}
          path: tests/screenshots/

  tui-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: pip install -e ".[dev]"
      - name: Run TUI tests
        run: pytest tests/e2e/tui -v
```

---

## Technology Stack Summary

### Frontend (Web GUI)
- **Core**: Vanilla JavaScript (ES6+)
- **Storage**: Browser localStorage API
- **Styling**: CSS3 with CSS custom properties
- **Export**: Blob API for file downloads

### Backend
- **Framework**: FastAPI (existing)
- **Validation**: Python SQL parsers (to be added)

### Testing
- **E2E Framework**: Playwright
- **TUI Testing**: Textual testing framework
- **API Testing**: pytest + requests
- **Test Runner**: pytest
- **Coverage**: pytest-cov
- **Reports**: pytest-html

### CI/CD
- **Platform**: GitHub Actions
- **Parallelization**: pytest-xdist
- **Artifact Storage**: GitHub Actions artifacts

---

## Code Reuse Strategy

### From Phase 2
- Reuse all business logic (100%)
- Extend QueryBuilder for filter groups
- Add validation layer to existing SQL generation
- Maintain API compatibility

### New Components
- Storage layer (localStorage abstraction)
- Theme manager (CSS variables)
- Keyboard manager (event handling)
- Export manager (file generation)
- Template manager (preset queries)
- Test infrastructure (Page Objects, fixtures)

---

## Security Considerations

### Client-Side Storage
- Validate data from localStorage before use
- Implement storage quota management
- Sanitize imported data

### XSS Prevention
- Escape user input in SQL preview
- Sanitize template placeholders
- Use textContent instead of innerHTML

### Data Privacy
- No external API calls for validation (local only)
- Query history stays in browser
- Export files don't include sensitive metadata

---

## Performance Optimization

### Frontend
- Debounce auto-save operations (2s)
- Cache validation results
- Lazy load templates
- Use CSS transitions for smooth theme switching

### Testing
- Run tests in parallel (pytest-xdist)
- Cache browser installations
- Use headless mode for speed
- Skip unnecessary test setup

---

## Accessibility

### WCAG Compliance
- WCAG AA contrast ratios in dark mode
- Keyboard navigation for all features
- ARIA labels for interactive elements
- Focus indicators for keyboard users

### Screen Readers
- Semantic HTML structure
- Alt text for icons
- Status announcements for dynamic content

---

## Monitoring & Observability

### Test Metrics
- Test execution time
- Flaky test detection
- Coverage trends
- Pass/fail rates

### Application Metrics
- localStorage usage
- Theme preference distribution
- Template usage statistics
- Export format preferences

(These metrics collected locally, no telemetry sent externally)
