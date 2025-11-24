# Tasks Document - Phase 3: Web GUI Enhancements & E2E Testing

## Overview

This document outlines the implementation tasks for Phase 3, divided into two parts:
- **Part A: Web GUI Enhancements** (Tasks 1-7)
- **Part B: E2E Testing** (Tasks 8-11)

Each task is designed to be modular and follows the spec-workflow methodology.

---

## Task Completion Status

### Part A: Web GUI Enhancements
⬜ **Task 1**: Query History & LocalStorage
⬜ **Task 2**: Dark Mode Theme System
⬜ **Task 3**: Keyboard Shortcuts Manager
⬜ **Task 4**: Enhanced Export Options
⬜ **Task 5**: Query Templates System
⬜ **Task 6**: Advanced Filter Groups (OR Logic)
⬜ **Task 7**: Real-time SQL Validation

### Part B: E2E Testing
⬜ **Task 8**: E2E Testing Framework Setup
⬜ **Task 9**: Web GUI E2E Tests
⬜ **Task 10**: API Integration Tests
⬜ **Task 11**: TUI E2E Tests
⬜ **Task 12**: CI/CD Pipeline Integration

---

# Part A: Web GUI Enhancements

## Task 1: Query History & LocalStorage

**Files**:
- `src/sqltrans/web/static/js/storage.js` (new)
- `src/sqltrans/web/static/index.html` (modify - add history sidebar)
- `src/sqltrans/web/static/js/app.js` (modify - integrate storage)
- `src/sqltrans/web/static/css/main.css` (modify - sidebar styles)

**Purpose**: Implement query persistence using browser localStorage with save/load/export/import functionality

**Status**: ⬜ Not Started

**Implementation Details**:

### storage.js - Storage Manager
```javascript
class QueryStorage {
  constructor() {
    this.storageKey = 'sqltrans_query_history';
    this.maxQueries = 50;
  }

  // Core methods
  saveQuery(queryState, name) { }
  loadQuery(id) { }
  listQueries() { }
  deleteQuery(id) { }
  exportHistory() { }
  importHistory(jsonData) { }

  // Helper methods
  _generateId() { }
  _pruneOldQueries() { }
  _getStorage() { }
  _setStorage(data) { }
}
```

### HTML Sidebar Structure
```html
<aside id="history-sidebar" class="sidebar collapsed">
  <div class="sidebar-header">
    <h3>Query History</h3>
    <button class="close-btn">×</button>
  </div>
  <div class="sidebar-actions">
    <button id="export-history-btn">Export</button>
    <button id="import-history-btn">Import</button>
  </div>
  <input type="text" id="history-search" placeholder="Search queries...">
  <ul id="history-list"></ul>
</aside>
```

### Integration Points
- Auto-save on query change (debounced 2 seconds)
- Ctrl+H keyboard shortcut to toggle sidebar
- Click query to load
- Delete with confirmation modal

**Requirements Covered**: Requirement 1 (Query History & Persistence)

**AI Implementation Prompt**:
```
Role: You are a frontend JavaScript developer implementing localStorage-based data persistence.

Task: Create a QueryStorage class that manages query history in browser localStorage:
1. Implement CRUD operations (save, load, list, delete)
2. Add auto-pruning when history exceeds 50 items
3. Add export/import functionality (JSON format)
4. Include search/filter capability
5. Store metadata (createdAt, lastUsed, useCount)
6. Integrate with existing app.js

Restrictions:
- Use vanilla JavaScript (no frameworks)
- Handle localStorage quota exceeded errors gracefully
- Validate imported data structure
- Debounce auto-save to avoid excessive writes

Success: History sidebar works, queries persist across sessions, export/import functions correctly
```

---

## Task 2: Dark Mode Theme System

**Files**:
- `src/sqltrans/web/static/js/theme.js` (new)
- `src/sqltrans/web/static/css/themes.css` (new)
- `src/sqltrans/web/static/css/main.css` (modify - use CSS variables)
- `src/sqltrans/web/static/css/prism-dark.css` (new - dark syntax theme)
- `src/sqltrans/web/static/index.html` (modify - add theme toggle button)

**Purpose**: Implement light/dark theme switching with OS preference detection

**Status**: ⬜ Not Started

**Implementation Details**:

### CSS Variables Structure
```css
/* themes.css */
:root {
  /* Light theme (default) */
  --color-bg-primary: #ffffff;
  --color-bg-secondary: #f5f7fa;
  --color-text-primary: #1a202c;
  --color-accent: #3b82f6;
  /* ... more variables */
}

[data-theme="dark"] {
  /* Dark theme overrides */
  --color-bg-primary: #1a202c;
  --color-bg-secondary: #2d3748;
  --color-text-primary: #f7fafc;
  --color-accent: #60a5fa;
  /* ... more variables */
}
```

### ThemeManager Class
```javascript
class ThemeManager {
  constructor() {
    this.storageKey = 'sqltrans_theme';
  }

  init() {
    // Detect OS preference
    // Load saved preference
    // Listen for OS changes
  }

  setTheme(theme) { }
  toggle() { }
  updatePrismTheme(theme) { }
}
```

### UI Integration
- Theme toggle button in header
- Smooth transitions (200ms)
- Sun/moon icon swap
- Preserve preference in localStorage

**Requirements Covered**: Requirement 2 (Dark Mode Theme)

**AI Implementation Prompt**:
```
Role: You are a frontend developer implementing dark mode with CSS custom properties.

Task: Create a dark mode theme system:
1. Define CSS variables for all colors in themes.css
2. Create ThemeManager class to handle switching
3. Detect OS dark mode preference on load
4. Save user preference to localStorage
5. Swap Prism.js CSS for syntax highlighting
6. Ensure WCAG AA contrast ratios in dark mode
7. Add smooth transitions between themes

Restrictions:
- Use CSS custom properties (no CSS-in-JS)
- Support prefers-color-scheme media query
- No flashing during theme switch
- All interactive elements must be visible in both themes

Success: Theme switches smoothly, preference persists, meets accessibility standards
```

---

## Task 3: Keyboard Shortcuts Manager

**Files**:
- `src/sqltrans/web/static/js/keyboard.js` (new)
- `src/sqltrans/web/static/index.html` (modify - add shortcuts modal)
- `src/sqltrans/web/static/css/main.css` (modify - modal styles)
- `src/sqltrans/web/static/js/app.js` (modify - integrate keyboard manager)

**Purpose**: Implement keyboard shortcuts for power users with help modal

**Status**: ⬜ Not Started

**Implementation Details**:

### Keyboard Shortcuts Map
```javascript
const shortcuts = {
  'Ctrl+Enter': 'Copy SQL to clipboard',
  'Ctrl+D': 'Download SQL file',
  'Ctrl+K': 'Clear query',
  'Ctrl+H': 'Toggle query history',
  'Ctrl+/': 'Show keyboard shortcuts',
  'Escape': 'Close modals'
};
```

### KeyboardManager Class
```javascript
class KeyboardManager {
  constructor(app) {
    this.app = app;
    this.shortcuts = { ... };
  }

  init() {
    document.addEventListener('keydown', this.handleKeyPress.bind(this));
  }

  handleKeyPress(event) { }
  getKeyCombo(event) { }
  showHelp() { }
  executeShortcut(action) { }
}
```

### Help Modal
```html
<div id="shortcuts-modal" class="modal">
  <div class="modal-content">
    <h2>Keyboard Shortcuts</h2>
    <table class="shortcuts-table">
      <!-- Shortcuts listed here -->
    </table>
    <button class="close-modal">Close</button>
  </div>
</div>
```

**Requirements Covered**: Requirement 3 (Keyboard Shortcuts)

**AI Implementation Prompt**:
```
Role: You are a frontend developer implementing keyboard shortcuts with accessibility in mind.

Task: Create a KeyboardManager class:
1. Listen for keyboard events globally
2. Handle Ctrl/Cmd key combinations
3. Prevent default browser behavior for shortcuts
4. Show toast confirmation when shortcuts are used
5. Create help modal showing all shortcuts (Ctrl+/)
6. Handle Escape key to close modals
7. Integrate with app actions (copy, download, clear, etc.)

Restrictions:
- Support both Ctrl (Windows/Linux) and Cmd (Mac)
- Don't interfere with browser shortcuts (Ctrl+T, Ctrl+W, etc.)
- Ensure shortcuts work when focus is in input fields
- Show visual feedback for each action

Success: All shortcuts work reliably, help modal is clear, user gets confirmation feedback
```

---

## Task 4: Enhanced Export Options

**Files**:
- `src/sqltrans/web/static/js/export.js` (new)
- `src/sqltrans/web/static/index.html` (modify - add export dropdown)
- `src/sqltrans/web/static/css/main.css` (modify - dropdown styles)
- `src/sqltrans/web/static/js/app.js` (modify - integrate export manager)

**Purpose**: Add multiple export formats (SQL, JSON, CSV) with metadata

**Status**: ⬜ Not Started

**Implementation Details**:

### ExportManager Class
```javascript
class ExportManager {
  constructor(app) {
    this.app = app;
  }

  exportSQL(queryState, sql) { }
  exportJSON(queryState) { }
  exportCSV(queryState) { }

  generateFilename(queryState, extension) {
    // Format: table_dialect_timestamp.ext
  }

  download(content, filename, mimeType) {
    // Use Blob API
  }
}
```

### Export Formats
**SQL**: Include comments with metadata
```sql
-- SQLTrans Query Export
-- Table: users
-- Dialect: postgresql
-- Generated: 2025-11-17T10:30:00Z
-- Columns: id, name, email

SELECT "id", "name", "email" FROM "users" WHERE "status" = 'active';
```

**JSON**: Full query state
```json
{
  "version": "1.0",
  "exportedAt": "2025-11-17T10:30:00Z",
  "queryState": {
    "table": "users",
    "columns": ["id", "name"],
    "filters": [...],
    "dialect": "postgresql"
  }
}
```

**CSV**: Column headers template
```csv
id,name,email
```

### UI Integration
- Export dropdown button
- Format selection menu
- Descriptive filenames
- Success notification

**Requirements Covered**: Requirement 4 (Enhanced Export Options)

**AI Implementation Prompt**:
```
Role: You are a frontend developer implementing file export functionality.

Task: Create an ExportManager class with multiple export formats:
1. Export SQL with metadata comments (table, dialect, timestamp, columns)
2. Export JSON with full query state structure
3. Export CSV with column headers only (data template)
4. Generate descriptive filenames (table_dialect_timestamp.ext)
5. Use Blob API for downloads
6. Show success notification after export

Restrictions:
- Use vanilla JavaScript (no libraries)
- Handle missing data gracefully (no table name, etc.)
- Format timestamps in ISO 8601
- Ensure downloads work in all modern browsers

Success: All three formats export correctly with proper filenames and content
```

---

## Task 5: Query Templates System

**Files**:
- `src/sqltrans/web/static/js/templates.js` (new)
- `src/sqltrans/web/static/index.html` (modify - add templates dropdown)
- `src/sqltrans/web/static/css/main.css` (modify - template UI styles)
- `src/sqltrans/web/static/js/app.js` (modify - integrate templates)

**Purpose**: Provide pre-built query templates for common scenarios

**Status**: ⬜ Not Started

**Implementation Details**:

### Built-in Templates
1. **Customer Lookup**: Find customer by ID or email
2. **Recent Records**: Records from last N days
3. **Null Check**: Find records with null values
4. **Pattern Match**: LIKE operator with wildcards
5. **Range Query**: BETWEEN operator for dates/numbers

### TemplateManager Class
```javascript
class TemplateManager {
  constructor() {
    this.builtInTemplates = [...];
    this.customTemplates = this.loadCustom();
  }

  loadTemplates() { }
  applyTemplate(templateId, app) { }
  saveAsTemplate(queryState, name, description) { }
  deleteTemplate(id) { }
  highlightPlaceholders(placeholders) { }
}
```

### Template Structure
```javascript
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
  placeholders: ['{{CUSTOMER_ID}}'],
  category: 'common'
}
```

### UI Integration
- Templates dropdown in toolbar
- Preview on hover
- Highlight placeholders after load
- "Save as Template" button
- Custom template management

**Requirements Covered**: Requirement 6 (Query Templates)

**AI Implementation Prompt**:
```
Role: You are a frontend developer creating a template system for common queries.

Task: Create a TemplateManager class with built-in and custom templates:
1. Define 5 built-in templates for common patterns
2. Support placeholders ({{TABLE_NAME}}, {{VALUE}}, etc.)
3. Highlight placeholders after template is applied
4. Allow users to save current query as custom template
5. Store custom templates in localStorage
6. Provide template search/filter
7. Show template preview on hover

Restrictions:
- Templates should work across all dialects
- Validate template structure before applying
- Don't overwrite current query without confirmation
- Make placeholders visually distinct

Success: Templates load correctly, placeholders are highlighted, users can create custom templates
```

---

## Task 6: Advanced Filter Groups (OR Logic)

**Files**:
- `src/sqltrans/web/app.py` (modify - update API for filter groups)
- `src/sqltrans/models/query.py` (modify - support filter groups)
- `src/sqltrans/sql/builder.py` (modify - generate OR clauses)
- `src/sqltrans/web/static/js/app.js` (modify - filter groups UI)
- `src/sqltrans/web/static/index.html` (modify - filter groups structure)
- `src/sqltrans/web/static/css/main.css` (modify - group styling)

**Purpose**: Enable complex WHERE clauses with OR groups and proper parentheses

**Status**: ⬜ Not Started

**Implementation Details**:

### Data Model Extension
```python
# models/query.py
class FilterGroup(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    filters: List[Filter] = []
    group_operator: Literal["AND", "OR"] = "AND"  # Within group

class QueryState(BaseModel):
    table: Optional[str] = None
    columns: List[str] = []
    filter_groups: List[FilterGroup] = []  # New field
    dialect: str = "generic"
```

### SQL Generation
```python
# sql/builder.py
def build_where_clause(self, filter_groups: List[FilterGroup]) -> str:
    if not filter_groups:
        return ""

    group_clauses = []
    for group in filter_groups:
        if not group.filters:
            continue

        # Build filter clauses within group
        filter_clauses = [self.build_filter(f) for f in group.filters]

        # Join with group operator
        group_clause = f" {group.group_operator} ".join(filter_clauses)

        # Add parentheses if multiple filters
        if len(group.filters) > 1:
            group_clause = f"({group_clause})"

        group_clauses.append(group_clause)

    # Join groups with AND
    return "WHERE " + " AND ".join(group_clauses)
```

### Frontend UI
```html
<div class="filter-groups-container">
  <div class="filter-group" data-group-id="group-1">
    <div class="group-header">
      <span class="group-badge">Group 1</span>
      <select class="group-operator">
        <option value="AND">AND</option>
        <option value="OR">OR</option>
      </select>
      <button class="delete-group">Delete Group</button>
    </div>
    <div class="filters-list">
      <!-- Individual filters here -->
    </div>
    <button class="add-filter-btn">+ Add Filter</button>
  </div>
  <button id="add-group-btn">+ Add OR Group</button>
</div>
```

### API Endpoints (New/Modified)
```python
@app.post("/api/query/filter-groups")
async def set_filter_groups(request: FilterGroupsRequest):
    """Set filter groups with OR logic."""
    pass

@app.post("/api/query/filter-groups/{group_id}/filters/add")
async def add_filter_to_group(group_id: str, request: FilterRequest):
    """Add filter to specific group."""
    pass
```

**Requirements Covered**: Requirement 5 (Advanced Filter Groups)

**AI Implementation Prompt**:
```
Role: You are a full-stack developer implementing complex SQL WHERE clause generation.

Task: Extend the filter system to support OR groups:
1. Backend: Update QueryState model to support filter groups
2. Backend: Modify QueryBuilder to generate (filter1 OR filter2) AND (filter3)
3. Backend: Add API endpoints for group management
4. Frontend: Create visual group containers with operator selector
5. Frontend: Allow drag-and-drop to reorder groups
6. Frontend: Show SQL preview with correct parentheses
7. Ensure backward compatibility with simple filters

Restrictions:
- Maintain clean SQL with proper parentheses
- Validate that groups have at least one filter
- Groups are always combined with AND
- Within group: user chooses AND or OR

Success: Complex WHERE clauses generate correctly, UI clearly shows grouping, SQL is valid
```

---

## Task 7: Real-time SQL Validation

**Files**:
- `src/sqltrans/web/app.py` (modify - add validation endpoint)
- `src/sqltrans/sql/validator.py` (new - SQL validation logic)
- `src/sqltrans/web/static/js/validator.js` (new)
- `src/sqltrans/web/static/index.html` (modify - add validation indicator)
- `src/sqltrans/web/static/css/main.css` (modify - validation styles)

**Purpose**: Validate generated SQL syntax in real-time with visual feedback

**Status**: ⬜ Not Started

**Implementation Details**:

### Backend Validation
```python
# sql/validator.py
from typing import List, Dict
import sqlparse

class SQLValidator:
    """Validate SQL syntax for different dialects."""

    def __init__(self, dialect: str):
        self.dialect = dialect

    def validate(self, sql: str) -> Dict:
        """Validate SQL and return errors/warnings."""
        try:
            # Parse SQL
            parsed = sqlparse.parse(sql)
            if not parsed:
                return {"valid": False, "errors": ["Empty SQL"]}

            # Check syntax
            errors = self._check_syntax(parsed[0])
            warnings = self._check_warnings(parsed[0])

            return {
                "valid": len(errors) == 0,
                "errors": errors,
                "warnings": warnings
            }
        except Exception as e:
            return {"valid": False, "errors": [str(e)]}

# API endpoint
@app.post("/api/query/validate")
async def validate_sql(request: ValidateRequest):
    """Validate SQL syntax."""
    validator = SQLValidator(request.dialect)
    result = validator.validate(request.sql)
    return result
```

### Frontend Validator
```javascript
// validator.js
class SQLValidator {
  constructor(api) {
    this.api = api;
    this.cache = new Map();
    this.debounceTimer = null;
  }

  async validate(sql, dialect) {
    // Check cache
    // Debounce validation
    // Call API
    // Update UI
  }

  displayResult(result) {
    const indicator = document.getElementById('validation-indicator');
    if (result.valid) {
      indicator.className = 'valid';
      indicator.innerHTML = '✓ Valid SQL';
    } else {
      indicator.className = 'invalid';
      indicator.innerHTML = `✗ ${result.errors[0]}`;
    }
  }
}
```

### UI Integration
- Validation indicator next to SQL preview
- Green checkmark for valid SQL
- Red X with error message for invalid
- Disable export buttons when invalid
- Real-time validation (debounced 500ms)

**Requirements Covered**: Requirement 7 (Real-time SQL Validation)

**Dependencies**:
- `sqlparse>=0.4.4` (SQL parsing library)

**AI Implementation Prompt**:
```
Role: You are a full-stack developer implementing SQL validation.

Task: Add real-time SQL validation:
1. Backend: Create SQLValidator class using sqlparse library
2. Backend: Add /api/query/validate endpoint
3. Backend: Detect syntax errors and common issues
4. Frontend: Create SQLValidator class that calls API
5. Frontend: Debounce validation (500ms delay)
6. Frontend: Cache validation results
7. Frontend: Show validation status with clear visual feedback
8. Disable export buttons when SQL is invalid

Restrictions:
- Validation must be fast (< 100ms)
- Handle parse errors gracefully
- Don't spam API with requests (debounce)
- Show specific error messages, not generic ones

Success: Validation shows immediately, errors are clear, export is blocked for invalid SQL
```

---

# Part B: E2E Testing

## Task 8: E2E Testing Framework Setup

**Files**:
- `tests/e2e/conftest.py` (new - pytest configuration)
- `tests/e2e/web/conftest.py` (new - web test fixtures)
- `tests/e2e/web/pages/__init__.py` (new)
- `tests/e2e/web/pages/base_page.py` (new - base page object)
- `tests/e2e/web/pages/query_builder.py` (new - main page object)
- `pytest.ini` (modify - add E2E test markers)
- `requirements.txt` (modify - add test dependencies)
- `.github/workflows/tests.yml` (new - CI configuration)

**Purpose**: Set up Playwright-based E2E testing framework with Page Object Model

**Status**: ⬜ Not Started

**Implementation Details**:

### Project Structure
```
tests/
├── e2e/
│   ├── conftest.py              # Root fixtures
│   ├── web/
│   │   ├── conftest.py          # Web-specific fixtures
│   │   ├── pages/
│   │   │   ├── __init__.py
│   │   │   ├── base_page.py     # Base page class
│   │   │   ├── query_builder.py
│   │   │   └── history_sidebar.py
│   │   └── test_*.py            # Test files
│   ├── api/
│   │   ├── conftest.py
│   │   └── test_*.py
│   └── tui/
│       ├── conftest.py
│       └── test_*.py
├── fixtures/
│   ├── queries.json
│   └── templates.json
└── reports/
```

### Base Page Object
```python
# pages/base_page.py
from playwright.sync_api import Page, expect

class BasePage:
    """Base page object with common functionality."""

    def __init__(self, page: Page):
        self.page = page

    def navigate(self, path: str = "/"):
        """Navigate to page."""
        self.page.goto(f"http://localhost:8000{path}")

    def wait_for_load(self):
        """Wait for page to be fully loaded."""
        self.page.wait_for_load_state("networkidle")

    def screenshot(self, name: str):
        """Take screenshot."""
        self.page.screenshot(path=f"tests/screenshots/{name}.png")
```

### Root Conftest
```python
# tests/e2e/conftest.py
import pytest
import subprocess
import time
from playwright.sync_api import sync_playwright

@pytest.fixture(scope="session")
def server():
    """Start SQLTrans web server for testing."""
    process = subprocess.Popen(
        ["python", "-m", "uvicorn", "sqltrans.web.app:app", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # Wait for server to start
    time.sleep(2)

    yield process

    # Cleanup
    process.terminate()
    process.wait()

@pytest.fixture(scope="session")
def browser_type_launch_args():
    """Configure browser launch arguments."""
    return {
        "headless": True,
        "slow_mo": 50  # Slow down by 50ms for stability
    }
```

### pytest.ini Configuration
```ini
[pytest]
markers =
    e2e: End-to-end tests
    web: Web GUI tests
    api: API integration tests
    tui: TUI tests
    slow: Slow-running tests
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
```

**Requirements Covered**: Requirement 8 (Web GUI E2E Testing Framework)

**Dependencies Added**:
```txt
# Testing dependencies
playwright>=1.40.0
pytest-playwright>=0.4.0
pytest-asyncio>=0.23.0
pytest-html>=4.1.0
pytest-cov>=4.1.0
pytest-xdist>=3.5.0
```

**AI Implementation Prompt**:
```
Role: You are a QA automation engineer setting up an E2E testing framework.

Task: Set up Playwright-based E2E testing infrastructure:
1. Install Playwright and pytest-playwright
2. Create directory structure (tests/e2e/web, api, tui)
3. Implement BasePage class with common functionality
4. Create conftest.py with server fixture (starts web server)
5. Configure pytest.ini with markers (e2e, web, api, tui)
6. Add browser fixture with proper configuration
7. Set up screenshot capture on test failure

Restrictions:
- Use pytest fixtures for all setup/teardown
- Tests should be independent (no shared state)
- Use Page Object Model pattern
- Run in headless mode by default

Success: Framework ready, tests can start server, Page Objects work, screenshots captured on failure
```

---

## Task 9: Web GUI E2E Tests

**Files**:
- `tests/e2e/web/pages/query_builder.py` (Page Object)
- `tests/e2e/web/test_query_building.py` (new)
- `tests/e2e/web/test_filters.py` (new)
- `tests/e2e/web/test_export.py` (new)
- `tests/e2e/web/test_history.py` (new)
- `tests/e2e/web/test_dark_mode.py` (new)
- `tests/e2e/web/test_keyboard_shortcuts.py` (new)
- `tests/e2e/web/test_templates.py` (new)

**Purpose**: Comprehensive E2E tests covering all web GUI functionality

**Status**: ⬜ Not Started

**Implementation Details**:

### Query Builder Page Object
```python
# pages/query_builder.py
from playwright.sync_api import Page, expect
from .base_page import BasePage

class QueryBuilderPage(BasePage):
    """Page Object for Query Builder."""

    def __init__(self, page: Page):
        super().__init__(page)
        # Locators
        self.table_input = page.locator("#table-name")
        self.add_column_input = page.locator("#column-name")
        self.add_column_btn = page.locator("#add-column")
        self.sql_preview = page.locator("#sql-preview")
        self.dialect_select = page.locator("#dialect-select")
        self.copy_btn = page.locator("#copy-sql")
        self.download_btn = page.locator("#download-sql")

    def set_table(self, table_name: str):
        """Set table name."""
        self.table_input.fill(table_name)
        self.table_input.press("Enter")

    def add_column(self, column_name: str):
        """Add column."""
        self.add_column_input.fill(column_name)
        self.add_column_btn.click()

    def add_filter(self, column: str, operator: str, value: str):
        """Add filter."""
        # Implementation

    def change_dialect(self, dialect: str):
        """Change SQL dialect."""
        self.dialect_select.select_option(dialect)

    def get_sql(self) -> str:
        """Get generated SQL."""
        return self.sql_preview.text_content()
```

### Test Examples
```python
# test_query_building.py
def test_simple_query(page, query_builder):
    """Test building a simple SELECT query."""
    query_builder.navigate()
    query_builder.set_table("users")
    query_builder.add_column("id")
    query_builder.add_column("name")

    sql = query_builder.get_sql()
    assert 'SELECT "id", "name"' in sql
    assert 'FROM "users"' in sql

def test_dialect_switching(page, query_builder):
    """Test switching between dialects."""
    query_builder.navigate()
    query_builder.set_table("users")
    query_builder.add_column("id")

    # PostgreSQL
    query_builder.change_dialect("postgresql")
    expect(query_builder.sql_preview).to_contain_text('"id"')

    # Oracle
    query_builder.change_dialect("oracle")
    expect(query_builder.sql_preview).to_contain_text('"ID"')

# test_filters.py
def test_add_filter_equals(page, query_builder):
    """Test adding filter with equals operator."""
    query_builder.navigate()
    query_builder.set_table("users")
    query_builder.add_column("id")
    query_builder.add_filter("status", "=", "active")

    sql = query_builder.get_sql()
    assert "WHERE" in sql
    assert "status" in sql
    assert "active" in sql

# test_keyboard_shortcuts.py
def test_copy_shortcut(page, query_builder):
    """Test Ctrl+Enter to copy SQL."""
    query_builder.navigate()
    query_builder.set_table("users")
    query_builder.add_column("id")

    # Press Ctrl+Enter
    page.keyboard.press("Control+Enter")

    # Verify toast notification
    toast = page.locator(".toast.success")
    expect(toast).to_be_visible()
    expect(toast).to_contain_text("Copied")
```

**Test Coverage Areas**:
1. Query building (table, columns, filters)
2. Dialect switching
3. SQL generation
4. Export functionality (all formats)
5. Query history (save, load, delete)
6. Dark mode toggle
7. Keyboard shortcuts
8. Templates (load, save custom)
9. Filter groups (OR logic)
10. Validation feedback

**Requirements Covered**: Requirement 8 (Web GUI E2E Testing)

**AI Implementation Prompt**:
```
Role: You are a QA automation engineer writing Playwright E2E tests.

Task: Create comprehensive E2E tests for the web GUI:
1. Create QueryBuilderPage with all locators and actions
2. Write tests for query building (table, columns, filters)
3. Test dialect switching and SQL generation
4. Test export functionality (SQL, JSON, CSV)
5. Test query history (save, load, delete, search)
6. Test dark mode toggle
7. Test all keyboard shortcuts (Ctrl+Enter, Ctrl+D, etc.)
8. Test template loading and custom template creation
9. Test filter groups with OR logic
10. Use assertions from Playwright's expect API

Restrictions:
- Each test should be independent (clear state between tests)
- Use Page Object Model pattern
- Add meaningful test names and docstrings
- Take screenshots on failure
- Aim for >90% code coverage

Success: All tests pass, cover major workflows, catch regressions
```

---

## Task 10: API Integration Tests

**Files**:
- `tests/e2e/api/conftest.py` (new - API test fixtures)
- `tests/e2e/api/test_query_endpoints.py` (new)
- `tests/e2e/api/test_filter_endpoints.py` (new)
- `tests/e2e/api/test_validation.py` (new)
- `tests/e2e/api/test_error_handling.py` (new)

**Purpose**: Test all API endpoints with proper validation and error handling

**Status**: ⬜ Not Started

**Implementation Details**:

### API Test Client
```python
# tests/e2e/api/conftest.py
import pytest
import requests

class APIClient:
    """Test client for SQLTrans API."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()

    def get_query_state(self):
        """GET /api/query"""
        response = self.session.get(f"{self.base_url}/api/query")
        response.raise_for_status()
        return response.json()

    def set_table(self, name: str):
        """POST /api/query/table"""
        response = self.session.post(
            f"{self.base_url}/api/query/table",
            json={"name": name}
        )
        response.raise_for_status()
        return response.json()

    # More methods...

@pytest.fixture
def api_client(server):
    """Provide API client."""
    return APIClient()

@pytest.fixture(autouse=True)
def reset_query_state(api_client):
    """Reset query state before each test."""
    api_client.clear_query()
    yield
```

### Test Examples
```python
# test_query_endpoints.py
def test_get_initial_state(api_client):
    """Test getting initial query state."""
    state = api_client.get_query_state()
    assert state["table"] is None
    assert state["columns"] == []
    assert state["filters"] == []
    assert state["dialect"] == "generic"

def test_set_table(api_client):
    """Test setting table name."""
    result = api_client.set_table("users")
    assert result["table"] == "users"

    # Verify state persists
    state = api_client.get_query_state()
    assert state["table"] == "users"

def test_add_columns(api_client):
    """Test adding multiple columns."""
    api_client.set_table("users")
    api_client.add_column("id")
    api_client.add_column("name")

    state = api_client.get_query_state()
    assert "id" in state["columns"]
    assert "name" in state["columns"]

# test_error_handling.py
def test_invalid_table_name(api_client):
    """Test validation for invalid table name."""
    with pytest.raises(requests.HTTPError) as exc:
        api_client.set_table("")

    assert exc.value.response.status_code == 400
    error = exc.value.response.json()
    assert "detail" in error

def test_invalid_operator(api_client):
    """Test validation for invalid operator."""
    api_client.set_table("users")

    with pytest.raises(requests.HTTPError) as exc:
        api_client.add_filter("id", "INVALID_OP", "123")

    assert exc.value.response.status_code == 400
```

**Test Coverage Areas**:
1. Query state endpoints (GET, POST, DELETE)
2. Table operations
3. Column operations (add, remove)
4. Filter operations (add, remove)
5. Dialect switching
6. SQL generation
7. Validation endpoints
8. Error responses (400, 404, 500)
9. Response schema validation

**Requirements Covered**: Requirement 9 (API Integration Testing)

**AI Implementation Prompt**:
```
Role: You are a backend QA engineer writing API integration tests.

Task: Create comprehensive API tests:
1. Create APIClient class wrapping all endpoints
2. Add fixture to reset state between tests
3. Test all GET/POST/DELETE endpoints
4. Test successful operations with assertions
5. Test error cases (400, 404, 500)
6. Validate response schemas (correct JSON structure)
7. Test API contract (required fields, types)
8. Test state persistence across requests

Restrictions:
- Use requests library for HTTP calls
- Each test should be independent
- Clear query state between tests
- Verify both response and side effects (GET after POST)
- Handle both success and error cases

Success: All API endpoints tested, >95% coverage, error handling verified
```

---

## Task 11: TUI E2E Tests

**Files**:
- `tests/e2e/tui/conftest.py` (new - TUI test fixtures)
- `tests/e2e/tui/test_navigation.py` (new)
- `tests/e2e/tui/test_query_building.py` (new)
- `tests/e2e/tui/test_export.py` (new)

**Purpose**: Test terminal UI functionality using Textual's testing framework

**Status**: ⬜ Not Started

**Implementation Details**:

### TUI Test Setup
```python
# tests/e2e/tui/conftest.py
import pytest
from textual.pilot import Pilot
from sqltrans.ui.app import SQLTransApp

@pytest.fixture
def app():
    """Provide SQLTransApp instance."""
    return SQLTransApp(initial_dialect="postgresql")
```

### Test Examples
```python
# test_query_building.py
import pytest
from sqltrans.ui.app import SQLTransApp

@pytest.mark.asyncio
async def test_build_query():
    """Test building query in TUI."""
    app = SQLTransApp()

    async with app.run_test() as pilot:
        # Set table
        await pilot.click("#table-input")
        await pilot.press(*"users")
        await pilot.press("enter")

        # Add column
        await pilot.click("#column-input")
        await pilot.press(*"id")
        await pilot.press("enter")

        # Verify SQL preview
        sql_widget = app.query_one("#sql-preview")
        assert "users" in sql_widget.text
        assert "id" in sql_widget.text

@pytest.mark.asyncio
async def test_dialect_switching():
    """Test switching dialects in TUI."""
    app = SQLTransApp(initial_dialect="postgresql")

    async with app.run_test() as pilot:
        # Open dialect selector
        await pilot.press("f2")  # Assuming F2 opens dialect menu

        # Select Oracle
        await pilot.press("down")
        await pilot.press("enter")

        # Verify dialect changed
        assert app.current_dialect == "oracle"

# test_navigation.py
@pytest.mark.asyncio
async def test_tab_navigation():
    """Test keyboard navigation between widgets."""
    app = SQLTransApp()

    async with app.run_test() as pilot:
        # Navigate with Tab
        await pilot.press("tab")
        focused = app.focused
        assert focused.id == "table-input"

        await pilot.press("tab")
        focused = app.focused
        assert focused.id == "column-input"
```

**Test Coverage Areas**:
1. Navigation between screens
2. Query building (table, columns, filters)
3. Keyboard shortcuts
4. SQL preview updates
5. Export functionality
6. Dialect switching
7. Error handling

**Requirements Covered**: Requirement 10 (TUI E2E Testing)

**AI Implementation Prompt**:
```
Role: You are a QA engineer writing tests for a Textual TUI application.

Task: Create E2E tests for the Terminal UI:
1. Use Textual's testing framework (run_test, Pilot)
2. Test keyboard navigation (Tab, Arrow keys, Enter)
3. Test query building workflow
4. Test SQL preview updates
5. Test export functionality
6. Test dialect switching
7. Simulate real user interactions

Restrictions:
- Use async/await with pytest-asyncio
- Tests should run without display (headless)
- Verify widget states after actions
- Handle timing issues (use pilot.pause())
- Aim for >80% coverage of TUI code

Success: TUI tests pass, cover main workflows, run reliably in CI
```

---

## Task 12: CI/CD Pipeline Integration

**Files**:
- `.github/workflows/tests.yml` (new)
- `.github/workflows/deploy.yml` (new - future)
- `pyproject.toml` (modify - add test scripts)
- `Makefile` (new - test commands)

**Purpose**: Automate testing on every commit with GitHub Actions

**Status**: ⬜ Not Started

**Implementation Details**:

### GitHub Actions Workflow
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
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install ruff mypy
          pip install -e ".[dev]"
      - name: Lint
        run: ruff check src/
      - name: Type check
        run: mypy src/sqltrans

  unit-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: pip install -e ".[dev]"
      - name: Run unit tests
        run: pytest tests/unit -v --cov=src/sqltrans --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./coverage.xml

  api-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: pip install -e ".[dev]"
      - name: Run API tests
        run: pytest tests/e2e/api -v --html=reports/api-report.html
      - name: Upload report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: api-test-report
          path: reports/

  web-e2e-tests:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        browser: [chromium, firefox]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: |
          pip install -e ".[dev]"
          playwright install ${{ matrix.browser }}
      - name: Run E2E tests
        run: |
          pytest tests/e2e/web -v \
            --browser=${{ matrix.browser }} \
            --html=reports/e2e-${{ matrix.browser }}.html \
            --screenshot=on
      - name: Upload artifacts
        if: failure()
        uses: actions/upload-artifact@v3
        with:
          name: e2e-${{ matrix.browser }}-failure
          path: |
            reports/
            tests/screenshots/

  tui-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - name: Install dependencies
        run: pip install -e ".[dev]"
      - name: Run TUI tests
        run: pytest tests/e2e/tui -v

  all-tests-passed:
    runs-on: ubuntu-latest
    needs: [lint, unit-tests, api-tests, web-e2e-tests, tui-tests]
    if: always()
    steps:
      - name: Check test results
        run: |
          if [ "${{ needs.lint.result }}" != "success" ] || \
             [ "${{ needs.unit-tests.result }}" != "success" ] || \
             [ "${{ needs.api-tests.result }}" != "success" ] || \
             [ "${{ needs.web-e2e-tests.result }}" != "success" ] || \
             [ "${{ needs.tui-tests.result }}" != "success" ]; then
            echo "Tests failed"
            exit 1
          fi
```

### Makefile
```makefile
# Makefile
.PHONY: test test-unit test-api test-e2e test-tui lint format install

install:
	pip install -e ".[dev]"
	playwright install

lint:
	ruff check src/
	mypy src/sqltrans

format:
	black src/ tests/
	ruff check --fix src/

test-unit:
	pytest tests/unit -v --cov=src/sqltrans

test-api:
	pytest tests/e2e/api -v

test-e2e:
	pytest tests/e2e/web -v --browser=chromium

test-tui:
	pytest tests/e2e/tui -v

test: test-unit test-api test-e2e test-tui
	@echo "All tests passed!"

test-parallel:
	pytest tests/ -v -n auto

ci:
	make lint
	make test
```

**Requirements Covered**: Requirement 11 (CI/CD Integration)

**AI Implementation Prompt**:
```
Role: You are a DevOps engineer setting up CI/CD pipeline.

Task: Create GitHub Actions workflow for automated testing:
1. Create jobs for: lint, unit tests, API tests, E2E tests, TUI tests
2. Run E2E tests in parallel across browsers (Chrome, Firefox)
3. Generate and upload test reports (HTML, coverage)
4. Upload screenshots/videos on test failure
5. Block PR merge if tests fail
6. Add status badges to README
7. Create Makefile with test commands for local development

Restrictions:
- All tests must pass before merge
- Run tests in parallel where possible
- Set timeout for E2E tests (10 minutes)
- Use GitHub Actions caching for dependencies
- Generate coverage reports for Codecov

Success: Pipeline runs on every push, tests run reliably, failures are caught
```

---

## Testing & Verification

### Part A: Web GUI Enhancements
- ✅ Query history saves and loads correctly
- ✅ Dark mode switches smoothly and persists
- ✅ All keyboard shortcuts work
- ✅ Export formats (SQL, JSON, CSV) generate correctly
- ✅ Templates load and apply correctly
- ✅ Filter groups generate correct SQL with parentheses
- ✅ SQL validation shows real-time feedback

### Part B: E2E Testing
- ✅ All E2E tests pass reliably
- ✅ Coverage >90% for web module
- ✅ Coverage >95% for API
- ✅ Coverage >80% for TUI
- ✅ CI pipeline runs on every commit
- ✅ Test reports generated and uploaded

---

## Final Phase 3 Deliverables

### Web GUI Enhancements
1. ✅ Query history with save/load/export/import
2. ✅ Dark mode with OS preference detection
3. ✅ Keyboard shortcuts for all actions
4. ✅ Multiple export formats (SQL, JSON, CSV)
5. ✅ Pre-built and custom templates
6. ✅ Advanced filter groups with OR logic
7. ✅ Real-time SQL validation

### E2E Testing
1. ✅ Playwright E2E framework with Page Objects
2. ✅ Comprehensive web GUI tests
3. ✅ API integration tests
4. ✅ TUI functional tests
5. ✅ CI/CD pipeline with GitHub Actions
6. ✅ Test reports and coverage metrics

---

## Success Metrics

**Web GUI Enhancements:**
- All features functional and user-tested
- Performance within specified limits
- LocalStorage under 5MB
- WCAG AA compliance for dark mode

**E2E Testing:**
- Test suite passes consistently (zero flaky tests)
- >90% code coverage for web module
- >95% coverage for API
- >80% coverage for TUI
- CI pipeline completes in <10 minutes
- All tests run in parallel

---

## Phase 3 Timeline

**Total Estimated Time: 8 weeks (40 working days)**

### Sprint 1 (Days 1-10): Essential Features
- Task 1: Query History (4 days)
- Task 2: Dark Mode (3 days)
- Task 3: Keyboard Shortcuts (3 days)

### Sprint 2 (Days 11-20): Advanced Features
- Task 4: Enhanced Export (3 days)
- Task 5: Query Templates (4 days)
- Task 7: SQL Validation (3 days)

### Sprint 3 (Days 21-25): Complex Features
- Task 6: Filter Groups (5 days)

### Sprint 4 (Days 26-35): E2E Framework & Tests
- Task 8: Framework Setup (3 days)
- Task 9: Web GUI Tests (5 days)
- Task 10: API Tests (2 days)

### Sprint 5 (Days 36-40): Final Testing & CI
- Task 11: TUI Tests (2 days)
- Task 12: CI/CD Integration (2 days)
- Final testing and bug fixes (1 day)

---

## Dependencies Summary

**New Python Packages:**
```txt
# SQL Validation
sqlparse>=0.4.4

# E2E Testing
playwright>=1.40.0
pytest-playwright>=0.4.0
pytest-asyncio>=0.23.0
pytest-html>=4.1.0
pytest-cov>=4.1.0
pytest-xdist>=3.5.0
```

**No New Frontend Dependencies** (pure JavaScript/CSS)

---

## Risk Mitigation

### Technical Risks
- **Risk**: Filter groups SQL generation complex
  - **Mitigation**: Start with simple cases, add complexity incrementally

- **Risk**: E2E tests may be flaky
  - **Mitigation**: Use proper waits, retries, and Page Object pattern

- **Risk**: LocalStorage quota exceeded
  - **Mitigation**: Implement auto-pruning and graceful degradation

### Schedule Risks
- **Risk**: Feature creep
  - **Mitigation**: Stick to requirements, defer nice-to-haves to Phase 4

- **Risk**: Testing takes longer than expected
  - **Mitigation**: Start testing framework early, write tests incrementally

---

## Notes

- All web enhancements use vanilla JavaScript (no framework dependencies)
- Maintain 100% code reuse of business logic
- E2E tests run in CI on every commit
- Phase 3 focuses on production readiness and quality assurance
- Documentation updated as features are completed
