# SQLTrans User Guide

**Version 0.1.0**

A comprehensive guide to using SQLTrans, the interactive SQL query builder for support engineers.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Interface Overview](#interface-overview)
3. [Building Queries](#building-queries)
4. [Operators Guide](#operators-guide)
5. [Keyboard Shortcuts](#keyboard-shortcuts)
6. [Multi-Database Support](#multi-database-support)
7. [Tips & Best Practices](#tips--best-practices)
8. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Installation

#### From PyPI (Recommended)
```bash
pip install sqltrans
```

#### From Source
```bash
git clone https://github.com/sqltrans/sqltrans.git
cd sqltrans
pip install -e .
```

#### Using Standalone Executable
Download the pre-built executable for your platform from the releases page. No Python installation required!

### First Launch

```bash
sqltrans
```

Or specify a default dialect:

```bash
sqltrans --dialect postgresql
sqltrans --dialect oracle
sqltrans --dialect generic
```

### Configuration

SQLTrans creates a configuration file at `~/.sqltrans/config.toml`:

```toml
# Default SQL dialect
default_dialect = "generic"

# Syntax highlighting theme
theme = "monokai"

# Auto-format SQL
auto_format = true

# Show line numbers in preview
show_line_numbers = false
```

---

## Interface Overview

SQLTrans uses a three-panel layout:

```
┌─────────────────────────────────────────────────────────────┐
│ SQLTrans - SQL Query Builder                                │
├─────────────────────────────────────────────────────────────┤
│ Dialect: ⦿ PostgreSQL  ○ Oracle  ○ Generic SQL            │
├──────────────────┬──────────────────┬──────────────────────┤
│ LEFT PANEL       │ CENTER PANEL     │ RIGHT PANEL          │
│                  │                  │                      │
│ • Table Name     │ • Filters        │ • SQL Preview        │
│ • Columns        │   (WHERE)        │ • Copy/Save          │
│                  │                  │                      │
└──────────────────┴──────────────────┴──────────────────────┘
│ q: Quit  c: Copy  n: New  ?: Help                          │
└─────────────────────────────────────────────────────────────┘
```

### Left Panel: Table & Columns

**Table Name Input**
- Enter the name of the database table
- Real-time validation ensures valid SQL identifiers
- Red border = invalid, green border = valid

**Column List**
- Add columns to include in SELECT clause
- Leave empty for `SELECT *`
- Remove columns with the Remove button
- Columns appear in the order you add them

### Center Panel: Filters

**Filter Editor**
- Build WHERE clause conditions
- Three inputs: column name, operator, value
- Click "Add Filter" to add the condition
- Multiple filters combine with AND

### Right Panel: SQL Preview

**SQL Display**
- Shows generated SQL with syntax highlighting
- Updates automatically as you build
- Formatted for readability

**Export Buttons**
- **Copy**: Copy SQL to clipboard (or press `c`)
- **Save**: Save SQL to a file

---

## Building Queries

### Step-by-Step Workflow

#### 1. Select Your Database Dialect

At the top of the screen, choose your target database:
- **PostgreSQL** - For PostgreSQL databases
- **Oracle** - For Oracle SQL databases
- **Generic SQL** - ANSI SQL-92 compatible (works with most databases)

The dialect affects how identifiers are quoted and values are escaped.

#### 2. Enter Table Name

In the left panel, type your table name in the "Table Name" field.

**Valid identifiers:**
- Must start with letter or underscore
- Can contain letters, numbers, underscores
- No spaces or special characters

**Examples:**
- ✅ `users`
- ✅ `order_items`
- ✅ `_temp_data`
- ❌ `123table` (starts with number)
- ❌ `user-name` (contains hyphen)

#### 3. Add Columns (Optional)

Click in the column input field and type a column name, then press Enter or click "Add".

**To select specific columns:**
```
1. Type "id" → Click Add
2. Type "email" → Click Add
3. Type "created_at" → Click Add
```

**Result:** `SELECT "id", "email", "created_at"`

**To select all columns:**
Leave the column list empty → Result: `SELECT *`

#### 4. Add Filters (Optional)

Build WHERE conditions:

1. **Enter column name** - The column to filter on
2. **Select operator** - How to compare (=, <, >, LIKE, etc.)
3. **Enter value** - What to compare against
4. **Click "Add Filter"**

**Example: Find active users**
- Column: `status`
- Operator: `=`
- Value: `active`

**Example: Recent orders**
- Column: `created_at`
- Operator: `>`
- Value: `2024-01-01`

#### 5. View & Export SQL

The SQL preview updates automatically. When ready:
- Press `c` or click **Copy** to copy to clipboard
- Click **Save** to save to a file

---

## Operators Guide

### Comparison Operators

#### Equals (=)
Match exact values.

**Example:**
```sql
WHERE "status" = 'active'
```

**Use case:** Find records with specific value

#### Not Equals (!=)
Exclude specific values.

**Example:**
```sql
WHERE "status" != 'deleted'
```

**Use case:** Find all except certain values

#### Less Than (<) / Greater Than (>)
Numeric or date comparisons.

**Examples:**
```sql
WHERE "age" > 18
WHERE "price" < 100
WHERE "created_at" > '2024-01-01'
```

**Use case:** Range filtering, date ranges

#### Less or Equal (<=) / Greater or Equal (>=)
Inclusive range comparisons.

**Examples:**
```sql
WHERE "score" <= 100
WHERE "age" >= 21
```

### Pattern Matching

#### LIKE
Match text patterns with wildcards.

**Wildcards:**
- `%` - Matches any sequence of characters (including none)
- `_` - Matches exactly one character

**Examples:**
```sql
-- Find names starting with "John"
WHERE "name" LIKE 'John%'

-- Find names ending with "son"
WHERE "name" LIKE '%son'

-- Find names containing "smith"
WHERE "name" LIKE '%smith%'

-- Find three-letter codes
WHERE "code" LIKE '___'

-- Find emails at specific domain
WHERE "email" LIKE '%@example.com'
```

**Common patterns:**
- `%Smith%` - Contains "Smith"
- `A%` - Starts with A
- `%ing` - Ends with "ing"
- `J%n` - Starts with J, ends with n

### List Matching

#### IN
Match any value in a list.

**Input format:** Comma-separated values
```
1,2,3,4,5
electronics,books,toys
pending,active,processing
```

**Generated SQL:**
```sql
WHERE "id" IN (1, 2, 3, 4, 5)
WHERE "category" IN ('electronics', 'books', 'toys')
WHERE "status" IN ('pending', 'active', 'processing')
```

**Use case:** Match multiple specific values

### Null Checks

#### IS NULL
Find records where field is NULL.

**Example:**
```sql
WHERE "deleted_at" IS NULL
```

**No value input needed** - The value field is disabled for NULL operators.

**Use case:** Find records with missing data, find active records (not deleted)

#### IS NOT NULL
Find records where field has a value.

**Example:**
```sql
WHERE "verified_at" IS NOT NULL
```

**Use case:** Find records with data present, find verified users

---

## Keyboard Shortcuts

Master these shortcuts for maximum efficiency:

| Key | Action | Description |
|-----|--------|-------------|
| `q` | **Quit** | Exit SQLTrans |
| `c` | **Copy** | Copy SQL to clipboard |
| `n` | **New** | Clear all and start new query |
| `?` | **Help** | Show help screen |
| `Tab` | **Navigate** | Move between fields |
| `Enter` | **Submit** | Activate button/submit input |
| `Esc` | **Close** | Close dialogs/help |

### Pro Tips

- Use `Tab` to navigate without touching the mouse
- Press `c` immediately after building to copy
- Press `n` to quickly clear and start fresh
- Press `?` anytime you need help

---

## Multi-Database Support

SQLTrans generates correct SQL for three database systems:

### PostgreSQL

**Identifier Quoting:** Double quotes `"users"`
**String Literals:** Single quotes with `''` escaping
**Features:** Full support for PostgreSQL syntax

**Example:**
```sql
SELECT "id", "email"
FROM "customers"
WHERE "name" = 'O''Reilly'
```

### Oracle SQL

**Identifier Quoting:** Double quotes `"USERS"` (case-sensitive)
**String Literals:** Single quotes with `''` escaping
**Case Handling:** Preserves case in quoted identifiers

**Example:**
```sql
SELECT "id", "email"
FROM "Orders"
WHERE "status" = 'PENDING'
```

### Generic SQL

**Standard:** ANSI SQL-92 compatible
**Compatibility:** Works with MySQL, SQLite, SQL Server, and more
**Conservative:** Avoids database-specific features

**Example:**
```sql
SELECT "id", "email"
FROM "users"
WHERE "active" = 1
```

### Switching Dialects

Change dialect anytime:
1. Click different dialect at top
2. SQL regenerates automatically
3. Same query, different syntax

**Use case:** Supporting customers on different databases

---

## Tips & Best Practices

### Query Building

**Start Simple**
- Begin with table and one column
- Add complexity incrementally
- Test at each step

**Use SELECT ***
- Leave columns empty initially
- See all data first
- Then select specific columns

**Build Filters Gradually**
- Start with one filter
- Add more as needed
- Each filter narrows results

### Validation

**Watch for Visual Feedback**
- Red border = invalid input
- Green border = valid input
- Error messages appear inline

**Common Validation Errors**
- Identifiers starting with numbers
- Special characters in names
- Empty values for non-NULL operators

### Performance

**Date Filters**
- Use `>` or `>=` for recent records
- More efficient than LIKE on dates

**LIKE Patterns**
- `%term%` searches anywhere (slower)
- `term%` searches prefix (faster)
- Use specific patterns when possible

### Security

**SQLTrans Protects You**
- All inputs validated
- SQL injection prevented
- Dangerous patterns blocked

**Still Be Careful**
- Verify generated SQL before running
- Use read-only database accounts when possible
- Test on dev/staging first

---

## Troubleshooting

### Clipboard Issues

**Problem:** Copy button doesn't work

**Solutions:**
```bash
# Linux - Install clipboard utilities
sudo apt-get install xclip
# or
sudo apt-get install xsel

# macOS - Should work out of box

# Windows - Should work out of box

# If still failing, use Save instead
```

### Application Won't Start

**Problem:** Application crashes on startup

**Check:**
1. Python version: `python --version` (need 3.10+)
2. Dependencies: `pip install -r requirements.txt`
3. Logs: `~/.sqltrans/logs/sqltrans.log`

### Terminal Display Issues

**Problem:** Unicode characters display incorrectly

**Solutions:**
```bash
# Set UTF-8 encoding
export PYTHONIOENCODING=utf-8

# Use modern terminal emulator
# - Windows Terminal (Windows)
# - iTerm2 (macOS)
# - GNOME Terminal (Linux)
```

### Validation Errors

**Problem:** Valid identifier rejected

**Check:**
- Starts with letter or underscore?
- Only contains letters, numbers, underscore?
- Not a SQL keyword?
- Not too long? (usually 64 char limit)

**Keywords** like `SELECT`, `FROM`, `WHERE` will show a warning but are allowed.

### Generated SQL Looks Wrong

**Problem:** SQL doesn't match expectations

**Check:**
1. Correct dialect selected?
2. Review each filter
3. Check operator types
4. Verify value formatting

**Remember:**
- Different dialects quote differently
- String values need quotes, numbers don't
- NULL operators don't use values

### Performance

**Problem:** Application feels slow

**Solutions:**
- Close other terminal applications
- Reduce terminal size if very large
- Check system resources
- Review log file for errors

---

## Getting Help

### In-App Help
Press `?` to see the help screen with all shortcuts and guides.

### Documentation
- **User Guide:** This document
- **Development Guide:** `docs/development.md`
- **README:** Project root
- **Quick Start:** `QUICKSTART.md`

### Support
- **Issues:** https://github.com/sqltrans/sqltrans/issues
- **Discussions:** GitHub Discussions
- **Logs:** `~/.sqltrans/logs/sqltrans.log`

---

## What's Next?

### Learn More
- Explore `examples/` directory for query samples
- Read `.spec-workflow/specs/` for detailed specifications
- Try different dialects to see differences

### Advanced Usage
- Create custom config in `~/.sqltrans/config.toml`
- Integrate into support workflows
- Share generated queries with team

### Contributing
- Report bugs and request features
- Contribute code improvements
- Improve documentation

---

**SQLTrans - Build SQL queries faster, safer, easier**
