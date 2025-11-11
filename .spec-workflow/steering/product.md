# Product Overview

## Product Purpose

SQLTrans is a command-line tool with an interactive terminal interface designed to help customer support teams quickly construct SQL queries for troubleshooting. The tool simplifies the process of translating table and column names into proper SQL syntax, reducing errors and speeding up response times when diagnosing customer database issues.

## Target Users

**Primary Users**: Customer support engineers and technical support staff who need to:
- Query customer databases to diagnose issues
- Construct SQL queries quickly without memorizing syntax
- Work with multiple database systems (PostgreSQL, Oracle, Generic SQL)
- Avoid SQL syntax errors during time-sensitive support situations

**Pain Points**:
- Memorizing different SQL dialects and syntax variations
- Making typos in table/column names during urgent support cases
- Constructing complex WHERE clauses with proper escaping and operators
- Switching between PostgreSQL, Oracle, and other SQL databases

## Key Features

1. **Interactive Terminal UI**: Visual interface in the terminal for table/column selection
2. **Multi-Database Support**: Generate queries for PostgreSQL, Oracle SQL, and generic ANSI SQL
3. **Query Builder**: Construct SELECT queries with WHERE clause filtering
4. **Syntax Validation**: Ensure generated SQL is syntactically correct for target database
5. **Quick Export**: Copy generated SQL to clipboard or save to file

## Business Objectives

- Reduce average time to construct SQL queries during support cases by 70%
- Minimize SQL syntax errors that delay customer issue resolution
- Enable support staff with varying SQL expertise to write correct queries
- Support multiple database platforms without requiring dialect-specific knowledge

## Success Metrics

- **Query Construction Time**: < 30 seconds to build a typical SELECT query with filters
- **Error Rate**: < 5% of generated queries require manual correction
- **User Adoption**: 80% of support team uses tool for database troubleshooting
- **Support Efficiency**: 30% reduction in time spent on database-related support tickets

## Product Principles

1. **Speed Over Complexity**: Optimize for quick query construction, not comprehensive SQL features
2. **Error Prevention**: Guide users toward correct syntax rather than fixing mistakes after
3. **Database Agnostic**: Abstract away dialect differences, generate correct syntax per target DB
4. **Keyboard-First**: Design for efficient keyboard navigation in terminal environment

## Monitoring & Visibility

- **Interface Type**: Terminal-based interactive UI (TUI)
- **Real-time Feedback**: Live SQL preview as user builds query
- **Validation Indicators**: Visual feedback for valid/invalid selections
- **Export Options**: Display final SQL with syntax highlighting

## Future Vision

### Potential Enhancements
- **Query History**: Save and recall frequently used query patterns
- **JOIN Support**: Add ability to construct queries joining multiple tables
- **Schema Discovery**: Auto-detect table structures from live database connections
- **INSERT/UPDATE Support**: Expand beyond SELECT to data modification queries
- **Snippet Library**: Pre-built query templates for common support scenarios
- **Web Dashboard**: Optional web interface for team collaboration on query templates
