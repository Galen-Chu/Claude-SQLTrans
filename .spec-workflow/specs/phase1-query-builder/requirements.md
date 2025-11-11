# Requirements Document - Phase 1: SQL Query Builder

## Introduction

Phase 1 of SQLTrans delivers a command-line tool with an interactive terminal user interface (TUI) that enables customer support engineers to quickly construct SELECT queries with WHERE clauses for multiple database systems (PostgreSQL, Oracle, and generic SQL). The tool eliminates common SQL syntax errors and reduces the time needed to troubleshoot customer database issues.

## Alignment with Product Vision

This feature directly supports the core product goals outlined in product.md:
- **Speed Over Complexity**: Focuses on rapid query construction for support scenarios
- **Error Prevention**: Guides users toward correct syntax through interactive UI
- **Database Agnostic**: Generates dialect-specific SQL for PostgreSQL, Oracle, and generic SQL
- **Keyboard-First**: Optimized for terminal environment and keyboard navigation

## Requirements

### Requirement 1: Interactive Table and Column Selection

**User Story:** As a support engineer, I want to interactively select tables and columns through a visual terminal interface, so that I can build queries quickly without memorizing schema details.

#### Acceptance Criteria

1. WHEN the user launches the tool THEN the system SHALL display an interactive terminal UI with keyboard navigation
2. WHEN the user selects "Add Table" THEN the system SHALL prompt for a table name input
3. WHEN the user enters a valid table name THEN the system SHALL accept the table and allow column selection
4. WHEN the user selects "Add Column" THEN the system SHALL prompt for column names to include in SELECT clause
5. WHEN the user adds multiple columns THEN the system SHALL display all selected columns in a list view
6. WHEN the user navigates the UI THEN the system SHALL respond within 100ms to all keyboard inputs
7. IF the user provides an invalid identifier (special characters, SQL keywords) THEN the system SHALL display a validation error and prevent addition

### Requirement 2: WHERE Clause Builder

**User Story:** As a support engineer, I want to add filter conditions to my queries, so that I can retrieve specific records matching customer issue criteria.

#### Acceptance Criteria

1. WHEN the user selects "Add Filter" THEN the system SHALL display a filter creation dialog
2. WHEN creating a filter THEN the system SHALL prompt for column name, operator, and value
3. WHEN the user selects an operator THEN the system SHALL offer options: =, !=, <, >, <=, >=, LIKE, IN, IS NULL, IS NOT NULL
4. WHEN the user enters a filter value THEN the system SHALL validate the value format (string, number, list for IN)
5. WHEN multiple filters are added THEN the system SHALL combine them with AND operators
6. WHEN the user views filters THEN the system SHALL display all active filters in readable format
7. WHEN the user deletes a filter THEN the system SHALL remove it from the WHERE clause
8. IF the user enters an invalid value format THEN the system SHALL display an error and prevent adding the filter

### Requirement 3: Multi-Database SQL Generation

**User Story:** As a support engineer working with different database systems, I want to select the target database dialect, so that the generated SQL uses correct syntax for PostgreSQL, Oracle, or generic SQL.

#### Acceptance Criteria

1. WHEN the user starts the tool THEN the system SHALL prompt for target database selection (PostgreSQL, Oracle, Generic SQL)
2. WHEN the user selects PostgreSQL THEN the system SHALL generate SQL using double-quoted identifiers and PostgreSQL syntax
3. WHEN the user selects Oracle THEN the system SHALL generate SQL using Oracle-specific identifier quoting and DUAL table conventions
4. WHEN the user selects Generic SQL THEN the system SHALL generate ANSI SQL-compliant queries
5. WHEN generating SQL THEN the system SHALL properly escape identifiers based on selected dialect
6. WHEN generating SQL THEN the system SHALL properly format string literals with appropriate quoting
7. WHEN the user changes dialect mid-session THEN the system SHALL regenerate the query in the new dialect syntax

### Requirement 4: SQL Preview and Export

**User Story:** As a support engineer, I want to see the generated SQL in real-time and copy it to my clipboard, so that I can quickly paste it into database tools.

#### Acceptance Criteria

1. WHEN the user adds or modifies query elements THEN the system SHALL update the SQL preview in real-time
2. WHEN displaying SQL THEN the system SHALL apply syntax highlighting for readability
3. WHEN displaying SQL THEN the system SHALL format it with proper indentation and line breaks
4. WHEN the user selects "Copy to Clipboard" THEN the system SHALL copy the complete SQL to system clipboard
5. WHEN the user selects "Save to File" THEN the system SHALL prompt for filename and save SQL as .sql file
6. WHEN clipboard operation succeeds THEN the system SHALL display a confirmation message
7. IF clipboard operation fails THEN the system SHALL display an error and offer file save alternative

### Requirement 5: Input Validation and Error Handling

**User Story:** As a support engineer, I want clear validation and error messages, so that I understand what went wrong and how to fix it.

#### Acceptance Criteria

1. WHEN the user enters an invalid table name THEN the system SHALL display specific validation error (e.g., "Table name cannot contain special characters")
2. WHEN the user enters an invalid column name THEN the system SHALL display specific validation error
3. WHEN the user enters an SQL keyword as identifier THEN the system SHALL warn but allow if quoted
4. WHEN a system error occurs THEN the system SHALL display user-friendly error message (not stack trace)
5. WHEN an error occurs THEN the system SHALL log technical details for debugging
6. WHEN validation fails THEN the system SHALL highlight the problematic field in the UI
7. IF the user attempts invalid operation (e.g., build query without table) THEN the system SHALL prevent action and display helpful message

### Requirement 6: Query State Management

**User Story:** As a support engineer, I want to clear or reset my current query, so that I can start over without restarting the application.

#### Acceptance Criteria

1. WHEN the user selects "Clear Query" THEN the system SHALL remove all tables, columns, and filters
2. WHEN the user selects "New Query" THEN the system SHALL prompt to save current query if modified
3. WHEN clearing the query THEN the system SHALL reset to initial state while keeping dialect selection
4. WHEN the user exits the application THEN the system SHALL prompt to save unsaved queries
5. WHEN building a new query THEN the system SHALL maintain session state until explicitly cleared

## Non-Functional Requirements

### Code Architecture and Modularity
- **Single Responsibility Principle**: Each module handles one specific aspect (UI, SQL generation, models, validation)
- **Modular Design**: SQL dialect support must be pluggable - adding new dialects shouldn't require changes to core builder
- **Dependency Management**: UI components depend on models, but models must be independent of UI
- **Clear Interfaces**: Define protocols for SQL dialects to ensure consistent behavior across PostgreSQL, Oracle, and Generic SQL

### Performance
- UI response time: < 100ms for all user interactions
- SQL generation time: < 10ms for typical queries
- Application startup: < 1 second
- Memory footprint: < 50MB during operation

### Security
- SQL injection prevention: All identifiers must be properly escaped/quoted
- Input sanitization: Validate all user inputs to prevent malicious SQL construction
- No credential storage: Application must not store or transmit database credentials

### Reliability
- Graceful error handling: Application must not crash on invalid input
- Data validation: Prevent construction of syntactically invalid SQL
- Cross-platform compatibility: Must work on Windows, Linux, and macOS terminals

### Usability
- Keyboard navigation: All features accessible via keyboard shortcuts
- Visual feedback: Clear indication of current state and available actions
- Help system: Built-in help showing available commands and shortcuts
- Accessibility: Readable in standard terminal color schemes
