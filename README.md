# SQLTrans

Interactive SQL query builder for customer support engineers.

## Overview

SQLTrans is a versatile query building tool that helps support teams quickly construct SQL queries for troubleshooting customer database issues. Build SELECT queries with WHERE clauses for PostgreSQL, Oracle, and generic SQL without memorizing syntax.

Choose between **Terminal UI (TUI)** for power users or **Web GUI** for a modern browser-based experience.

## Features

- 🌐 **Dual Interface Modes**: Choose Terminal UI or Web GUI
- 🎯 **Interactive Query Building**: Visual interface for constructing queries
- 🗄️ **Multi-Database Support**: PostgreSQL, Oracle SQL, and generic ANSI SQL
- 🔍 **Smart Query Builder**: Construct SELECT queries with WHERE clause filtering
- ✅ **Real-time Validation**: Ensures generated SQL is correct for target database
- 🎨 **Syntax Highlighting**: Color-coded SQL preview
- 📋 **Quick Export**: Copy to clipboard or download to file
- 🚀 **Zero Configuration**: Works out of the box, no setup required

## Installation

### From PyPI (Coming Soon)

```bash
pip install sqltrans
```

### From Source

```bash
git clone https://github.com/Galen-Chu/Claude-SQLTrans.git
cd sqltrans
pip install -e .
```

### Development Installation

```bash
pip install -e ".[dev]"
```

## Quick Start

### Web GUI Mode (Browser-Based)

Launch the web interface (opens automatically in your default browser):

```bash
sqltrans --gui
```

### Terminal UI Mode (Command-Line)

Launch the terminal interface:

```bash
sqltrans --tui
```

Or use default mode (TUI) with a specific dialect:

```bash
sqltrans --dialect postgresql
```

## Requirements

- Python 3.10 or higher
- Terminal with keyboard support
- Works on Windows, macOS, and Linux

## Development

### Running Tests

```bash
pytest
```

### Type Checking

```bash
mypy src/sqltrans
```

### Code Formatting

```bash
black src/sqltrans tests
ruff check src/sqltrans tests
```

## License

MIT License - see LICENSE file for details

## Project Status

✅ **Phase 1 Complete** - Terminal UI query builder
✅ **Phase 2 Complete** - Web GUI mode

See `.spec-workflow/specs/` for detailed specifications and roadmap.

## Documentation

- **[Quick Start Guide](docs/quick-start.md)** - Get started in 5 minutes
- **[Tutorial](docs/tutorial.md)** - Step-by-step examples and exercises
- **[Documentation Index](docs/index.md)** - Complete documentation overview
- **[Visual Walkthrough](docs/visual-walkthrough.md)** - Screenshots and UI guide
- **[System Design](SYSTEM_DESIGN.md)** - Architecture and technical design
