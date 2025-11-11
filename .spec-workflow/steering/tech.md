# Technology Stack

## Project Type

Command-line application with terminal-based user interface (TUI) for interactive SQL query construction

## Core Technologies

### Primary Language(s)
- **Language**: Python 3.10+
- **Runtime**: CPython interpreter
- **Package Management**: pip with requirements.txt and/or pyproject.toml

**Rationale**: Python provides excellent libraries for TUI development, SQL parsing, and cross-platform CLI tools. Quick development cycle suitable for support tooling.

### Key Dependencies/Libraries

**Terminal UI Framework**:
- **Textual** or **Rich**: Modern Python TUI frameworks with good UX
  - Textual for full reactive UI with widgets
  - Rich for styled terminal output and simple interactions

**SQL Generation**:
- **SQLAlchemy Core** (optional): For dialect-aware SQL generation
- **pyparsing** or custom builders: For constructing SQL syntax trees

**Database Dialect Support**:
- PostgreSQL dialect module
- Oracle SQL dialect module
- Generic ANSI SQL support

**Utility Libraries**:
- **pyperclip**: Clipboard integration for copying generated SQL
- **click** or **typer**: CLI argument parsing and command structure

### Application Architecture

**Interactive TUI Application**:
- Event-driven UI with keyboard navigation
- Model-View-Controller pattern:
  - **Model**: Query state (tables, columns, filters)
  - **View**: Terminal UI widgets and layout
  - **Controller**: User input handlers and SQL generation logic
- Pluggable SQL dialect system for multi-database support

### Data Storage

- **Primary storage**: In-memory (query state during session)
- **Configuration**: Local config file (YAML/TOML) for user preferences
- **Query History** (future): SQLite database for saved queries
- **Data formats**: SQL text output, JSON for config

### External Integrations

- **Clipboard**: System clipboard integration for SQL export
- **Database Connections** (future phase): Optional connection to inspect schemas
- **APIs**: None required for phase 1

## Development Environment

### Build & Development Tools
- **Package Management**: pip, pip-tools for dependency management
- **Virtual Environments**: venv or virtualenv for isolated development
- **Development workflow**:
  - Hot reload during development (if supported by TUI framework)
  - Manual testing in terminal

### Code Quality Tools
- **Static Analysis**: pylint or ruff for code quality
- **Type Checking**: mypy for type safety (Python 3.10+ type hints)
- **Formatting**: black for consistent code style
- **Testing Framework**: pytest for unit and integration tests
- **Documentation**: docstrings (Google or NumPy style), Sphinx for API docs

### Version Control & Collaboration
- **VCS**: Git
- **Branching Strategy**: GitHub Flow (main + feature branches)
- **Code Review Process**: Pull requests with spec alignment review

## Deployment & Distribution

- **Target Platform(s)**: Cross-platform (Windows, Linux, macOS)
- **Distribution Method**:
  - PyPI package for pip install
  - Standalone executable (PyInstaller) for non-Python users
- **Installation Requirements**:
  - Python 3.10+ (if installed via pip)
  - No dependencies for standalone executable
- **Update Mechanism**: pip upgrade or manual download of new executable

## Technical Requirements & Constraints

### Performance Requirements
- **Startup time**: < 1 second to launch TUI
- **Response time**: < 100ms for UI interactions
- **Memory usage**: < 50MB for typical query construction
- **Query generation**: < 10ms to generate SQL from current state

### Compatibility Requirements
- **Platform Support**: Windows 10+, Linux (major distros), macOS 11+
- **Terminal Support**: Must work in common terminals (Windows Terminal, iTerm2, GNOME Terminal, etc.)
- **Python Version**: Minimum Python 3.10
- **Standards Compliance**: Generate ANSI SQL-compliant queries, with dialect-specific extensions

### Security & Compliance
- **No Credentials Storage**: Tool does not store or handle database credentials in phase 1
- **SQL Injection Prevention**: Generate parameterized queries or properly escaped SQL
- **Input Validation**: Sanitize table/column names to prevent malicious input
- **Data Privacy**: No query logging or telemetry without user consent

### Scalability & Reliability
- **Expected Load**: Single-user tool, lightweight operation
- **Availability Requirements**: Offline-first, no external dependencies for core functionality
- **Error Handling**: Graceful degradation, clear error messages in UI

## Technical Decisions & Rationale

### Decision Log

1. **Python over Go/Rust**: Python chosen for rapid development, excellent TUI libraries (Textual/Rich), and familiarity for support teams who may extend the tool. Go/Rust would be faster but longer development cycle.

2. **Textual/Rich over Curses**: Modern Python TUI frameworks provide better UX, cross-platform compatibility, and easier development compared to raw ncurses. Textual offers reactive UI similar to web frameworks.

3. **SQL Generation vs ORM**: Focus on SQL text generation rather than ORM approach. Support teams need readable SQL they can understand and modify, not abstracted query objects.

4. **No Database Connection in Phase 1**: Simplify initial release by having users manually input table/column names. Schema introspection can be added later without changing core architecture.

## Known Limitations

- **No JOIN Support (Phase 1)**: Initial release focuses on single-table SELECT queries with WHERE clauses. Multi-table joins planned for future release.

- **Limited SQL Features**: Phase 1 supports SELECT and WHERE only. INSERT/UPDATE/DELETE, aggregations, subqueries, and CTEs are out of scope.

- **Manual Schema Input**: Users must know table and column names. Auto-discovery from database connections is future enhancement.

- **Terminal Dependency**: Requires terminal environment; no GUI version. May limit usage on systems with poor terminal support.
