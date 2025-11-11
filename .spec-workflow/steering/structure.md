# Project Structure

## Directory Organization

```
sqltrans/
├── src/
│   └── sqltrans/              # Main package
│       ├── __init__.py
│       ├── __main__.py        # CLI entry point
│       ├── ui/                # Terminal UI components
│       │   ├── __init__.py
│       │   ├── app.py         # Main TUI application
│       │   ├── screens/       # UI screens/views
│       │   ├── widgets/       # Reusable UI widgets
│       │   └── styles.py      # TUI styling/theming
│       ├── sql/               # SQL generation logic
│       │   ├── __init__.py
│       │   ├── builder.py     # Query builder
│       │   ├── dialects/      # Database-specific syntax
│       │   │   ├── __init__.py
│       │   │   ├── base.py    # Base dialect interface
│       │   │   ├── postgresql.py
│       │   │   ├── oracle.py
│       │   │   └── generic.py
│       │   └── formatter.py   # SQL formatting/pretty-print
│       ├── models/            # Data models
│       │   ├── __init__.py
│       │   ├── query.py       # Query state model
│       │   ├── schema.py      # Table/column models
│       │   └── filters.py     # WHERE clause models
│       ├── utils/             # Utilities
│       │   ├── __init__.py
│       │   ├── clipboard.py   # Clipboard operations
│       │   ├── config.py      # Configuration handling
│       │   └── validation.py  # Input validation
│       └── config/            # Default configs
│           └── default.toml
├── tests/                     # Test files
│   ├── __init__.py
│   ├── unit/                  # Unit tests
│   │   ├── test_builder.py
│   │   ├── test_dialects.py
│   │   └── test_models.py
│   ├── integration/           # Integration tests
│   │   └── test_ui_flow.py
│   └── fixtures/              # Test data
│       └── sample_schemas.py
├── docs/                      # Documentation
│   ├── user-guide.md
│   └── development.md
├── examples/                  # Usage examples
│   └── sample_queries.md
├── .spec-workflow/            # Spec workflow documents
├── requirements.txt           # Runtime dependencies
├── requirements-dev.txt       # Development dependencies
├── pyproject.toml             # Project metadata and build config
├── setup.py                   # Package setup (if needed)
├── README.md
├── LICENSE
└── CLAUDE.md                  # Claude Code guidance
```

## Naming Conventions

### Files
- **Modules**: `snake_case.py` (e.g., `query_builder.py`, `postgresql.py`)
- **UI Components**: Descriptive names (e.g., `table_selector.py`, `filter_editor.py`)
- **Tests**: `test_[module_name].py` (e.g., `test_builder.py`)
- **Config**: `lowercase.toml` or `lowercase.yaml`

### Code
- **Classes**: `PascalCase` (e.g., `QueryBuilder`, `PostgreSQLDialect`, `TableModel`)
- **Functions/Methods**: `snake_case` (e.g., `generate_sql()`, `add_filter()`, `validate_column_name()`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_DIALECT`, `MAX_COLUMN_LENGTH`)
- **Variables**: `snake_case` (e.g., `table_name`, `selected_columns`, `where_clause`)
- **Private members**: `_leading_underscore` (e.g., `_internal_state`, `_build_clause()`)

## Import Patterns

### Import Order
1. Standard library imports
2. Third-party library imports (Textual, Rich, SQLAlchemy, etc.)
3. Local application imports (from sqltrans package)
4. Relative imports within same module

Example:
```python
import os
import sys
from typing import List, Optional

from textual.app import App
from textual.widgets import Button
from rich.console import Console

from sqltrans.models.query import Query
from sqltrans.sql.dialects import PostgreSQLDialect
from sqltrans.utils.validation import validate_identifier

from .widgets import TableSelector
```

### Module Organization
- Use absolute imports from package root: `from sqltrans.sql.builder import QueryBuilder`
- Relative imports only within same subpackage: `from .base import BaseDialect`
- Avoid circular dependencies between modules

## Code Structure Patterns

### Module Organization
```python
"""Module docstring explaining purpose."""

# 1. Imports (grouped as above)
import os
from typing import Protocol

from textual.widget import Widget

# 2. Constants
DEFAULT_PORT = 5432
MAX_QUERY_LENGTH = 10000

# 3. Type definitions and protocols
class DialectProtocol(Protocol):
    """Protocol for SQL dialect implementations."""
    def quote_identifier(self, name: str) -> str: ...

# 4. Main classes/functions
class QueryBuilder:
    """Main query builder implementation."""
    pass

# 5. Helper functions (if not in separate utils)
def _sanitize_name(name: str) -> str:
    """Internal helper function."""
    pass

# 6. Module-level exports
__all__ = ['QueryBuilder', 'DEFAULT_PORT']
```

### Class Organization
```python
class QueryBuilder:
    """Build SQL queries programmatically."""

    # 1. Class variables
    _registry: dict = {}

    # 2. __init__ and initialization
    def __init__(self, dialect: str):
        self.dialect = dialect
        self._state = {}

    # 3. Public interface methods (alphabetical or logical grouping)
    def add_column(self, column: str) -> 'QueryBuilder':
        """Add column to SELECT clause."""
        pass

    def add_filter(self, condition: str) -> 'QueryBuilder':
        """Add WHERE condition."""
        pass

    def build(self) -> str:
        """Generate final SQL string."""
        pass

    # 4. Properties
    @property
    def column_count(self) -> int:
        """Number of columns in SELECT."""
        return len(self._columns)

    # 5. Private helper methods
    def _validate_state(self) -> None:
        """Internal validation."""
        pass

    # 6. Special methods (if any)
    def __str__(self) -> str:
        return self.build()
```

### Function Organization
- Input validation first
- Main logic in the middle
- Return statement at end
- Single responsibility per function

```python
def generate_where_clause(filters: List[Filter], dialect: Dialect) -> str:
    """Generate WHERE clause from filters.

    Args:
        filters: List of filter conditions
        dialect: SQL dialect for escaping

    Returns:
        WHERE clause string

    Raises:
        ValueError: If filters are invalid
    """
    # Validate inputs
    if not filters:
        return ""

    # Main logic
    conditions = []
    for f in filters:
        condition = f.to_sql(dialect)
        conditions.append(condition)

    # Return result
    return f"WHERE {' AND '.join(conditions)}"
```

## Code Organization Principles

1. **Single Responsibility**: Each module handles one aspect of functionality
   - `builder.py` → query construction logic
   - `formatter.py` → SQL formatting/pretty-printing
   - `validation.py` → input validation only

2. **Modularity**: Components can be tested and used independently
   - Dialects are pluggable and don't depend on UI
   - Models are pure data structures
   - UI widgets are reusable across screens

3. **Separation of Concerns**:
   - **UI Layer** (`ui/`): User interaction, display, event handling
   - **Business Logic** (`sql/`, `models/`): Query construction, validation
   - **Utilities** (`utils/`): Cross-cutting concerns (config, clipboard)

4. **Testability**: Design for easy unit testing
   - Inject dependencies (dialects, config) rather than hardcode
   - Pure functions where possible
   - Mock external dependencies (clipboard, file system)

## Module Boundaries

### Dependency Rules
- **UI** depends on **Models** and **SQL** (but not vice versa)
- **SQL** depends on **Models** (but not on UI)
- **Models** have no dependencies on other modules
- **Utils** can be used by any module but shouldn't depend on domain logic

```
┌─────────┐
│   UI    │ ← Entry point, depends on everything
└────┬────┘
     │
     ├──→ ┌─────────┐
     │    │   SQL   │ ← Business logic, depends on Models
     │    └────┬────┘
     │         │
     └────┬────┴──→ ┌─────────┐
          │         │ Models  │ ← Pure data, no dependencies
          │         └─────────┘
          │
          └──────→ ┌─────────┐
                   │  Utils  │ ← Helper functions
                   └─────────┘
```

### Public APIs vs Internal
- **Public API**: Classes and functions in `__all__` exports
- **Internal**: Modules/functions starting with `_`
- **UI Widgets**: Reusable widgets in `ui/widgets/`, screen-specific code in `ui/screens/`

## Code Size Guidelines

- **File size**: Max 500 lines per file; split larger files into submodules
- **Function/Method size**: Max 50 lines; extract helper functions for complex logic
- **Class complexity**: Max 10 public methods; consider splitting large classes
- **Nesting depth**: Max 4 levels; refactor deep nesting into functions

## Testing Standards

- Every module in `src/sqltrans/` has corresponding test in `tests/unit/`
- Test file mirrors source structure: `sqltrans/sql/builder.py` → `tests/unit/test_builder.py`
- Integration tests in `tests/integration/` for UI flows and cross-module interactions
- Fixtures in `tests/fixtures/` for reusable test data

## Documentation Standards

- All public classes and functions must have docstrings
- Use Google-style or NumPy-style docstrings consistently
- Include type hints for all function signatures (Python 3.10+ syntax)
- Complex algorithms or business logic should have inline comments explaining "why"
- README.md has installation, usage, and contribution guidelines
