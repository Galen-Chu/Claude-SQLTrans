# SQLTrans

Interactive SQL query builder for customer support engineers.

## Overview

SQLTrans is a command-line tool with an interactive terminal interface that helps support teams quickly construct SQL queries for troubleshooting customer database issues. Build SELECT queries with WHERE clauses for PostgreSQL, Oracle, and generic SQL without memorizing syntax.

## Features

- 🎯 **Interactive Terminal UI**: Visual interface for building queries
- 🗄️ **Multi-Database Support**: PostgreSQL, Oracle SQL, and generic ANSI SQL
- 🔍 **Query Builder**: Construct SELECT queries with WHERE clause filtering
- ✅ **Syntax Validation**: Ensures generated SQL is correct for target database
- 📋 **Quick Export**: Copy to clipboard or save to file

## Installation

### From PyPI (Coming Soon)

```bash
pip install sqltrans
```

### From Source

```bash
git clone https://github.com/sqltrans/sqltrans.git
cd sqltrans
pip install -e .
```

### Development Installation

```bash
pip install -e ".[dev]"
```

## Quick Start

Launch the interactive query builder:

```bash
sqltrans
```

Or specify a default dialect:

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

🚧 **Phase 1 Development** - Core query builder features in progress

See `.spec-workflow/specs/phase1-query-builder/` for detailed specifications.
