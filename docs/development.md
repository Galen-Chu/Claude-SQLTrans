# SQLTrans Development Guide

**Version 0.1.0**

Guide for developers contributing to SQLTrans.

---

## Table of Contents

1. [Development Setup](#development-setup)
2. [Project Structure](#project-structure)
3. [Architecture Overview](#architecture-overview)
4. [Development Workflow](#development-workflow)
5. [Testing](#testing)
6. [Code Quality](#code-quality)
7. [Adding Features](#adding-features)
8. [Contributing](#contributing)

---

## Development Setup

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)
- git

### Clone and Install

```bash
# Clone the repository
git clone https://github.com/sqltrans/sqltrans.git
cd sqltrans

# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows

# Install in development mode with dev dependencies
pip install -e ".[dev]"
```

### Verify Installation

```bash
# Run the application
python -m sqltrans

# Run tests
pytest

# Check types
mypy src/sqltrans

# Format code
black src/sqltrans tests
ruff check src/sqltrans tests
```

---

## Project Structure

```
sqltrans/
├── src/sqltrans/          # Main package
│   ├── models/            # Data models
│   │   ├── filters.py     # Filter model
│   │   ├── query.py       # QueryState model
│   │   └── schema.py      # Table/Column models
│   ├── sql/               # SQL generation
│   │   ├── dialects/      # Database dialects
│   │   │   ├── base.py    # BaseDialect protocol
│   │   │   ├── postgresql.py
│   │   │   ├── oracle.py
│   │   │   └── generic.py
│   │   ├── builder.py     # QueryBuilder
│   │   └── formatter.py   # SQL formatting
│   ├── ui/                # User interface
│   │   ├── screens/       # Textual screens
│   │   │   ├── query_builder.py
│   │   │   └── help_screen.py
│   │   ├── widgets/       # Custom widgets
│   │   │   ├── dialect_selector.py
│   │   │   ├── table_input.py
│   │   │   ├── column_list.py
│   │   │   ├── filter_editor.py
│   │   │   └── sql_preview.py
│   │   └── app.py         # Main app
│   ├── utils/             # Utilities
│   │   ├── validation.py  # Input validation
│   │   ├── clipboard.py   # Clipboard operations
│   │   ├── config.py      # Configuration
│   │   └── logging.py     # Logging setup
│   └── __main__.py        # CLI entry point
├── tests/                 # Test suite
│   ├── unit/              # Unit tests
│   ├── integration/       # Integration tests
│   └── e2e/               # End-to-end tests
├── docs/                  # Documentation
├── examples/              # Example queries
├── scripts/               # Build scripts
├── .spec-workflow/        # Specification workflow
│   ├── specs/             # Feature specs
│   └── steering/          # Project guidance
├── pyproject.toml         # Project configuration
└── README.md
```

---

## Architecture Overview

### Design Principles

**Modular Architecture**
- Each module has a single, clear responsibility
- Loose coupling between components
- Easy to test and maintain

**Specification-Driven Development**
- Requirements documented before implementation
- Design aligned with technical standards
- Tasks provide clear implementation path

**Layered Architecture**
```
┌─────────────────────────┐
│    UI Layer (Textual)   │  User interaction
├─────────────────────────┤
│   Business Logic Layer  │  Query building, validation
├─────────────────────────┤
│    Data Model Layer     │  QueryState, Filter, etc.
├─────────────────────────┤
│    SQL Generation Layer │  Dialects, builder
└─────────────────────────┘
```

### Key Components

#### Models (`models/`)

**Purpose:** Define data structures
- `schema.py` - Table and Column definitions
- `filters.py` - Filter conditions for WHERE clauses
- `query.py` - QueryState managing entire query

**Pattern:** Dataclasses with validation

#### SQL Generation (`sql/`)

**Purpose:** Generate dialect-specific SQL
- `dialects/base.py` - Protocol defining dialect interface
- `dialects/postgresql.py` - PostgreSQL implementation
- `dialects/oracle.py` - Oracle implementation
- `dialects/generic.py` - ANSI SQL implementation
- `builder.py` - Orchestrates SQL generation
- `formatter.py` - Formats and highlights SQL

**Pattern:** Protocol-based polymorphism

#### UI (`ui/`)

**Purpose:** Terminal user interface
- `app.py` - Main Textual application
- `screens/` - Full-screen views
- `widgets/` - Reusable UI components

**Pattern:** Event-driven with Textual framework

#### Utils (`utils/`)

**Purpose:** Cross-cutting concerns
- `validation.py` - Input validation
- `clipboard.py` - System clipboard integration
- `config.py` - Configuration management
- `logging.py` - Structured logging

**Pattern:** Utility modules with pure functions

---

## Development Workflow

### Specification-Driven Process

1. **Read Steering Documents**
   ```bash
   cat .spec-workflow/steering/product.md
   cat .spec-workflow/steering/tech.md
   cat .spec-workflow/steering/structure.md
   ```

2. **Review Feature Spec**
   ```bash
   # For a new feature
   cat .spec-workflow/specs/[feature]/requirements.md
   cat .spec-workflow/specs/[feature]/design.md
   cat .spec-workflow/specs/[feature]/tasks.md
   ```

3. **Implement Tasks Sequentially**
   - Each task is self-contained
   - Includes files to modify
   - Lists existing code to leverage
   - Provides implementation prompt

4. **Test as You Go**
   - Run unit tests: `pytest tests/unit/`
   - Run specific test: `pytest tests/unit/test_builder.py -k test_name`

### Making Changes

#### Adding a New SQL Dialect

1. **Create dialect file** in `src/sqltrans/sql/dialects/`
```python
"""MyDB SQL dialect."""
from sqltrans.sql.dialects.base import BaseDialect

class MyDBDialect(BaseDialect):
    def quote_identifier(self, name: str) -> str:
        # Implement quoting
        return f"`{name}`"

    def format_string_literal(self, value: str) -> str:
        # Implement escaping
        escaped = value.replace("'", "''")
        return f"'{escaped}'"

    # ... implement other methods
```

2. **Add tests** in `tests/unit/test_dialects.py`
3. **Register in app** - Add to `QueryBuilderScreen.dialect_map`
4. **Update docs** - Document dialect-specific behavior

#### Adding a New Widget

1. **Create widget file** in `src/sqltrans/ui/widgets/`
2. **Extend Textual widget** (Container, Vertical, etc.)
3. **Define CSS** in `DEFAULT_CSS` class variable
4. **Emit messages** for events
5. **Add to screen** in `query_builder.py`

#### Adding a New Operator

1. **Add to `VALID_OPERATORS`** in `models/filters.py`
2. **Update validation** in `Filter.validate()`
3. **Implement SQL generation** in `Filter.to_sql()`
4. **Add to filter editor** in `ui/widgets/filter_editor.py`
5. **Write tests** in `tests/unit/test_models.py`

---

## Testing

### Test Organization

```
tests/
├── unit/              # Fast, isolated tests
│   ├── test_models.py
│   ├── test_validation.py
│   ├── test_dialects.py
│   ├── test_builder.py
│   └── test_formatter.py
├── integration/       # UI flow tests
│   └── test_ui_flow.py
└── e2e/              # Real-world scenarios
    └── test_scenarios.py
```

### Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/unit/test_builder.py

# Specific test
pytest tests/unit/test_builder.py::TestQueryBuilder::test_build_query

# With coverage
pytest --cov=sqltrans --cov-report=html

# Fast (unit only)
pytest tests/unit/

# Verbose
pytest -v

# Show print statements
pytest -s
```

### Writing Tests

**Unit Test Example:**
```python
def test_filter_validation():
    """Test filter validates correctly."""
    # Arrange
    filter_obj = Filter(column="age", operator=">", value=18)

    # Act
    result = filter_obj.validate()

    # Assert
    assert result is True
```

**E2E Test Example:**
```python
def test_customer_lookup_scenario():
    """Test finding customer by email."""
    # Arrange
    query_state = QueryState(dialect="postgresql")
    query_state.add_table("customers")
    query_state.add_filter(Filter("email", "=", "test@example.com"))

    # Act
    dialect = PostgreSQLDialect()
    builder = QueryBuilder(query_state, dialect)
    sql = builder.build_query()

    # Assert
    assert 'FROM "customers"' in sql
    assert '"email" = ' in sql
    assert 'test@example.com' in sql
```

### Test Coverage Goals

- Unit tests: >95% coverage
- All public methods tested
- Edge cases covered
- Error conditions tested

---

## Code Quality

### Type Checking

**MyPy** enforces static typing:

```bash
# Check all code
mypy src/sqltrans

# Check specific file
mypy src/sqltrans/sql/builder.py
```

**Type hints required:**
```python
def build_query(state: QueryState) -> str:
    """Build query with type hints."""
    pass
```

### Code Formatting

**Black** formats code automatically:

```bash
# Format all code
black src/sqltrans tests

# Check without modifying
black --check src/sqltrans tests
```

**Configuration:** `pyproject.toml`
```toml
[tool.black]
line-length = 100
target-version = ['py310', 'py311', 'py312']
```

### Linting

**Ruff** checks for issues:

```bash
# Check all code
ruff check src/sqltrans tests

# Auto-fix issues
ruff check --fix src/sqltrans tests
```

### Pre-Commit Workflow

Before committing:
```bash
# 1. Format
black src/sqltrans tests

# 2. Lint
ruff check --fix src/sqltrans tests

# 3. Type check
mypy src/sqltrans

# 4. Test
pytest

# 5. Coverage (optional)
pytest --cov=sqltrans
```

---

## Adding Features

### Feature Development Process

1. **Create Specification**
   - Document requirements in `.spec-workflow/specs/[feature]/requirements.md`
   - Design architecture in `design.md`
   - Break down into tasks in `tasks.md`

2. **Implement Incrementally**
   - Follow tasks.md order
   - Write tests first (TDD) or alongside
   - Leverage existing code (noted in tasks)

3. **Test Thoroughly**
   - Unit tests for logic
   - Integration tests for UI flows
   - E2E tests for user scenarios

4. **Document**
   - Update user guide
   - Add examples
   - Update README if needed

### Example: Adding BETWEEN Operator

**1. Requirements:**
```markdown
As a support engineer, I want to filter by value ranges
so that I can find records within date or numeric ranges.

Acceptance Criteria:
- BETWEEN operator available in filter editor
- Accepts two values (min and max)
- Generates correct SQL: `col BETWEEN val1 AND val2`
```

**2. Design:**
- Modify Filter model to accept range values
- Add BETWEEN to VALID_OPERATORS
- Update filter editor UI for two value inputs
- Implement SQL generation

**3. Implementation:**

```python
# In models/filters.py
VALID_OPERATORS = [
    "=", "!=", "<", ">", "<=", ">=",
    "LIKE", "IN", "IS NULL", "IS NOT NULL",
    "BETWEEN"  # Add new operator
]

# Update Filter dataclass
@dataclass
class Filter:
    column: str
    operator: str
    value: Any = None
    value2: Any = None  # For BETWEEN

    def validate(self) -> bool:
        # ... existing validation

        if self.operator == "BETWEEN":
            if self.value is None or self.value2 is None:
                raise ValueError("BETWEEN requires two values")

        return True

    def to_sql(self, dialect: BaseDialect) -> str:
        # ... existing cases

        elif self.operator == "BETWEEN":
            col = dialect.quote_identifier(self.column)
            val1 = self._format_value(self.value, dialect)
            val2 = self._format_value(self.value2, dialect)
            return f"{col} BETWEEN {val1} AND {val2}"
```

**4. Test:**
```python
def test_between_operator():
    """Test BETWEEN operator."""
    f = Filter("age", "BETWEEN", 18, 65)
    assert f.validate()

    sql = f.to_sql(GenericDialect())
    assert 'BETWEEN' in sql
    assert '18' in sql
    assert '65' in sql
```

---

## Contributing

### Getting Started

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

### Contribution Guidelines

**Code Style**
- Follow existing patterns
- Use type hints
- Write docstrings
- Format with Black

**Testing**
- Add tests for new features
- Maintain >90% coverage
- All tests must pass

**Documentation**
- Update user guide for user-facing changes
- Update development guide for architecture changes
- Add examples for new features

**Commits**
- Write clear commit messages
- Reference issues in commits
- Small, focused commits

### Pull Request Process

1. **Create PR** with clear description
2. **Link related issues**
3. **Ensure CI passes** (tests, linting, type checking)
4. **Request review** from maintainers
5. **Address feedback**
6. **Merge** when approved

### Community

- **Report bugs:** GitHub Issues
- **Request features:** GitHub Issues with "enhancement" label
- **Ask questions:** GitHub Discussions
- **Chat:** Discord (link in README)

---

## Useful Commands

### Development
```bash
# Run application
python -m sqltrans

# Run with specific dialect
python -m sqltrans --dialect postgresql

# Run tests
pytest
pytest -v  # verbose
pytest -k test_name  # specific test
pytest --lf  # last failed

# Code quality
black src/sqltrans tests
ruff check src/sqltrans tests
mypy src/sqltrans

# Coverage
pytest --cov=sqltrans --cov-report=html
open htmlcov/index.html

# Build executable
python scripts/build_exe.py

# Build package
python -m build
```

### Debugging
```bash
# Run with debug logging
python -m sqltrans --debug

# Check logs
tail -f ~/.sqltrans/logs/sqltrans.log

# Interactive debugging
python -m pdb -m sqltrans
```

---

## Resources

### Documentation
- [Textual Documentation](https://textual.textualize.io/)
- [Rich Documentation](https://rich.readthedocs.io/)
- [Python Type Hints](https://docs.python.org/3/library/typing.html)

### Project
- **Repository:** https://github.com/sqltrans/sqltrans
- **Issues:** https://github.com/sqltrans/sqltrans/issues
- **Specifications:** `.spec-workflow/specs/`

---

**Happy coding! 🚀**
