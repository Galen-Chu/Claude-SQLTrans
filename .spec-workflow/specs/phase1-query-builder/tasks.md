# Tasks Document - Phase 1: SQL Query Builder

## Phase 1A: Core Models and Validation (Foundation)

- [ ] 1. Set up project structure and dependencies
  - Files: pyproject.toml, requirements.txt, src/sqltrans/__init__.py
  - Create directory structure: src/sqltrans/{models,sql,ui,utils}
  - Set up package metadata and dependencies (Textual, Rich, pyperclip, pytest)
  - Purpose: Establish Python package foundation
  - _Leverage: N/A (initial setup)_
  - _Requirements: All non-functional requirements (Python 3.10+, cross-platform)_
  - _Prompt: Role: Python DevOps Engineer with expertise in package management and project structure | Task: Set up a Python 3.10+ project structure for SQLTrans following modern best practices with pyproject.toml, requirements.txt for dependencies (textual, rich, pyperclip, pytest), and create the src/sqltrans package layout with models/, sql/, ui/, utils/ subdirectories as specified in structure.md | Restrictions: Must use src-layout pattern, include type checking configuration for mypy, ensure cross-platform compatibility | Success: Project structure matches structure.md, dependencies install cleanly, package is importable, mypy configuration is present_

- [ ] 2. Implement data models in models/schema.py
  - File: src/sqltrans/models/schema.py
  - Define Column and Table dataclasses
  - Add type hints and validation
  - Purpose: Represent table and column metadata for future schema discovery
  - _Leverage: Python dataclasses, typing module_
  - _Requirements: Requirement 1 (table/column selection foundation)_
  - _Prompt: Role: Python Developer specializing in data modeling and type systems | Task: Implement Column and Table dataclasses in models/schema.py with full type hints (Python 3.10+), representing database schema objects with name and optional data_type fields, include __str__ and __repr__ methods for debugging | Restrictions: Use @dataclass decorator, all fields must have type hints, no external dependencies beyond stdlib, keep models pure data structures | Success: Dataclasses are defined with proper types, have good string representations, mypy passes with no errors_

- [ ] 3. Implement Filter model in models/filters.py
  - File: src/sqltrans/models/filters.py
  - Create Filter dataclass with column, operator, value
  - Implement to_sql() method signature (implementation comes later)
  - Implement validate() method for filter validation
  - Purpose: Represent WHERE clause conditions
  - _Leverage: Python dataclasses, typing module_
  - _Requirements: Requirement 2 (WHERE clause builder)_
  - _Prompt: Role: Python Developer with expertise in data modeling and validation logic | Task: Implement Filter dataclass in models/filters.py representing a WHERE clause condition with column (str), operator (str from =, !=, <, >, <=, >=, LIKE, IN, IS NULL, IS NOT NULL), and optional value (Any), include validate() method that checks operator validity and value requirements (IS NULL/IS NOT NULL need no value, IN needs list, etc.), add to_sql() method stub that raises NotImplementedError | Restrictions: Use @dataclass, validate all operator/value combinations, no SQL generation yet (just validation), type hints required | Success: Filter validates correctly for all operator types, invalid combinations raise clear errors, to_sql stub is present for future implementation_

- [ ] 4. Implement QueryState model in models/query.py
  - File: src/sqltrans/models/query.py
  - Create QueryState dataclass with table, columns, filters, dialect
  - Implement add_table(), add_column(), add_filter(), set_dialect(), clear()
  - Add to_dict() and from_dict() for serialization
  - Purpose: Manage the state of the query being built
  - _Leverage: models/filters.py, models/schema.py, Python dataclasses_
  - _Requirements: Requirements 1, 2, 3 (query state management)_
  - _Prompt: Role: Python Developer specializing in state management and data structures | Task: Implement QueryState dataclass in models/query.py with fields for table (Optional[str]), columns (List[str]), filters (List[Filter]), dialect (str defaulting to 'generic'), implement methods add_table(), add_column(), add_filter(), set_dialect(), clear() for state mutation, add to_dict()/from_dict() for serialization, ensure all methods maintain valid state | Restrictions: Use @dataclass with field defaults, import Filter from models/filters, validate dialect is one of 'postgresql'/'oracle'/'generic', type hints required | Success: QueryState manages all query elements, serialization works bidirectionally, state transitions are valid, mypy passes_

- [ ] 5. Implement validation utilities in utils/validation.py
  - File: src/sqltrans/utils/validation.py
  - Implement validate_identifier() - check SQL identifier validity
  - Implement validate_operator() - check operator is allowed
  - Implement validate_value() - parse and validate filter values
  - Implement is_sql_keyword() - check for reserved keywords
  - Purpose: Centralize all input validation logic
  - _Leverage: Standard library re module for pattern matching_
  - _Requirements: Requirement 5 (input validation and error handling)_
  - _Prompt: Role: Security-focused Python Developer with expertise in SQL and input validation | Task: Implement validation utilities in utils/validation.py including validate_identifier(name: str) -> Tuple[bool, str] checking if name is valid SQL identifier (alphanumeric, underscore, not starting with digit), validate_operator(op: str) -> bool checking against allowed operators list, validate_value(value: str, value_type: str) -> Tuple[bool, Any, str] parsing string/number/list values, is_sql_keyword(name: str) -> bool checking SQL reserved words, all functions return success status and error message | Restrictions: Use regex for identifier validation, no SQL execution, return detailed error messages, handle edge cases (empty strings, special characters), prevent SQL injection patterns | Success: All validators work correctly, SQL keywords detected, invalid inputs rejected with clear messages, no false positives/negatives_

- [ ] 6. Write unit tests for models in tests/unit/test_models.py
  - File: tests/unit/test_models.py
  - Test QueryState operations (add, remove, clear, serialization)
  - Test Filter validation with valid and invalid inputs
  - Test Table and Column models
  - Purpose: Ensure models work correctly in isolation
  - _Leverage: pytest framework_
  - _Requirements: All model-related requirements_
  - _Prompt: Role: QA Engineer with expertise in Python unit testing and pytest | Task: Write comprehensive unit tests in tests/unit/test_models.py for QueryState (test all methods, edge cases, serialization round-trips), Filter (test validation for all operators, edge cases like NULL values, IN lists), Table and Column models, use pytest fixtures for common test data, aim for 100% code coverage of models package | Restrictions: No external dependencies in tests (mock everything), use pytest conventions, test both success and failure paths, clear test names describing what is tested | Success: All model code is tested, coverage >95%, tests run fast (<1s), all edge cases covered_

- [ ] 7. Write unit tests for validation in tests/unit/test_validation.py
  - File: tests/unit/test_validation.py
  - Test validate_identifier() with valid/invalid identifiers, SQL keywords
  - Test validate_operator() with all supported operators
  - Test validate_value() with strings, numbers, lists, nulls
  - Test edge cases and SQL injection attempts
  - Purpose: Ensure validation prevents invalid and malicious inputs
  - _Leverage: pytest framework_
  - _Requirements: Requirement 5 (input validation)_
  - _Prompt: Role: Security-focused QA Engineer with expertise in SQL injection testing and validation | Task: Write comprehensive unit tests in tests/unit/test_validation.py testing validate_identifier with valid names, invalid characters, SQL keywords, reserved words, validate_operator with all supported operators and invalid ones, validate_value with various data types (strings with quotes, numbers, comma-separated lists, null), include SQL injection attempts (quotes, semicolons, comments) to ensure they're caught, aim for 100% coverage | Restrictions: Test all edge cases, use parameterized tests for multiple inputs, no actual SQL execution, clear test names | Success: All validation logic tested, SQL injection patterns rejected, coverage >95%, security edge cases covered_

## Phase 1B: SQL Generation (Business Logic)

- [ ] 8. Implement BaseDialect protocol in sql/dialects/base.py
  - File: src/sqltrans/sql/dialects/base.py
  - Define BaseDialect protocol with required methods
  - Add method signatures: quote_identifier(), format_string_literal(), format_number_literal(), get_null_keyword()
  - Add supports_feature() for dialect capability checking
  - Purpose: Define interface that all SQL dialects must implement
  - _Leverage: Python Protocol (typing module)_
  - _Requirements: Requirement 3 (multi-database SQL generation)_
  - _Prompt: Role: Software Architect specializing in plugin architectures and Python protocols | Task: Define BaseDialect protocol in sql/dialects/base.py using typing.Protocol, include abstract methods quote_identifier(name: str) -> str for escaping identifiers, format_string_literal(value: str) -> str for escaping strings, format_number_literal(value: Union[int, float]) -> str for numbers, get_null_keyword() -> str for NULL, supports_feature(feature: str) -> bool for capability checking, add comprehensive docstrings explaining each method's purpose | Restrictions: Use Protocol not ABC, all methods must have type hints, no implementation (protocol only), document expected behavior in docstrings | Success: Protocol is well-defined, type hints are correct, mypy recognizes it as protocol, clear documentation for implementers_

- [ ] 9. Implement PostgreSQL dialect in sql/dialects/postgresql.py
  - File: src/sqltrans/sql/dialects/postgresql.py
  - Implement BaseDialect protocol for PostgreSQL
  - Use double-quoted identifiers, PostgreSQL string escaping
  - Handle PostgreSQL-specific features
  - Purpose: Generate PostgreSQL-compatible SQL
  - _Leverage: sql/dialects/base.py protocol_
  - _Requirements: Requirement 3 (PostgreSQL support)_
  - _Prompt: Role: Database Developer with PostgreSQL expertise and Python experience | Task: Implement PostgreSQLDialect class in sql/dialects/postgresql.py implementing BaseDialect protocol, use double quotes for identifiers ("table_name"), single quotes for strings with proper escaping ('' for embedded quotes), standard number formatting, 'NULL' keyword, implement quote_identifier to handle special characters and case sensitivity, format_string_literal to escape quotes and backslashes safely | Restrictions: Must implement all protocol methods, follow PostgreSQL SQL standard, prevent SQL injection in escaping logic, handle edge cases (empty strings, special characters) | Success: All protocol methods implemented correctly, generates valid PostgreSQL SQL, string escaping is injection-proof, mypy confirms protocol compliance_

- [ ] 10. Implement Oracle dialect in sql/dialects/oracle.py
  - File: src/sqltrans/sql/dialects/oracle.py
  - Implement BaseDialect protocol for Oracle SQL
  - Use Oracle-specific identifier quoting and conventions
  - Handle Oracle string literal syntax
  - Purpose: Generate Oracle-compatible SQL
  - _Leverage: sql/dialects/base.py protocol_
  - _Requirements: Requirement 3 (Oracle support)_
  - _Prompt: Role: Database Developer with Oracle SQL expertise and Python experience | Task: Implement OracleDialect class in sql/dialects/oracle.py implementing BaseDialect protocol, use double quotes for case-sensitive identifiers (Oracle defaults to uppercase unquoted), single quotes for strings with '' escaping, standard number formatting, 'NULL' keyword, handle Oracle-specific conventions (DUAL table reference if needed in future), implement all quoting and escaping methods safely | Restrictions: Must implement all protocol methods, follow Oracle SQL standards, prevent SQL injection, handle case sensitivity correctly | Success: All protocol methods implemented, generates valid Oracle SQL, identifier quoting handles case correctly, injection-proof escaping_

- [ ] 11. Implement Generic SQL dialect in sql/dialects/generic.py
  - File: src/sqltrans/sql/dialects/generic.py
  - Implement BaseDialect protocol for ANSI SQL
  - Use conservative SQL-92 compatible syntax
  - Avoid database-specific features
  - Purpose: Generate portable ANSI SQL queries
  - _Leverage: sql/dialects/base.py protocol_
  - _Requirements: Requirement 3 (generic SQL support)_
  - _Prompt: Role: Database Developer with broad SQL knowledge and standards expertise | Task: Implement GenericDialect class in sql/dialects/generic.py implementing BaseDialect protocol, use ANSI SQL-92 standard syntax with double quotes for identifiers, single quotes for strings with '' escaping, standard number formatting, 'NULL' keyword, avoid any database-specific extensions, conservative approach favoring compatibility over features | Restrictions: Must implement all protocol methods, strictly follow ANSI SQL-92 standard, no vendor-specific features, injection-proof escaping | Success: Generates valid ANSI SQL-92 compatible queries, works across major databases, protocol fully implemented_

- [ ] 12. Implement QueryBuilder in sql/builder.py
  - File: src/sqltrans/sql/builder.py
  - Create QueryBuilder class with build_select(), build_from(), build_where(), build_query()
  - Integrate with QueryState model and dialect system
  - Implement complete SQL generation logic
  - Purpose: Orchestrate SQL generation from query state
  - _Leverage: models/query.py, models/filters.py, sql/dialects/base.py_
  - _Requirements: Requirements 1, 2, 3 (query building and SQL generation)_
  - _Prompt: Role: Backend Developer with SQL expertise and Python experience | Task: Implement QueryBuilder class in sql/builder.py taking QueryState and BaseDialect in constructor, implement build_select() generating SELECT clause with quoted columns, build_from() generating FROM clause with quoted table, build_where() generating WHERE clause by calling filter.to_sql() for each filter and joining with AND, build_query() assembling complete SQL statement, handle edge cases (no columns = SELECT *, no filters = no WHERE), use dialect methods for all quoting | Restrictions: Must use dialect for all identifier quoting, validate state before building (need table), handle empty cases gracefully, no SQL injection vulnerabilities | Success: Generates correct SQL for all query combinations, uses dialect correctly, handles edge cases, validates state_

- [ ] 13. Implement Filter.to_sql() method in models/filters.py
  - File: src/sqltrans/models/filters.py (modify existing)
  - Implement the to_sql() method stub created earlier
  - Generate SQL condition strings for all operators
  - Use dialect for proper escaping
  - Purpose: Convert Filter objects to SQL WHERE conditions
  - _Leverage: sql/dialects/base.py protocol_
  - _Requirements: Requirement 2 (WHERE clause generation)_
  - _Prompt: Role: Backend Developer with SQL and Python expertise | Task: Implement Filter.to_sql(dialect: BaseDialect) method in models/filters.py, generate SQL conditions for all operators (=, !=, <, >, <=, >=, LIKE, IN, IS NULL, IS NOT NULL), use dialect.quote_identifier() for column names, dialect.format_string_literal() for string values, dialect.format_number_literal() for numbers, handle IS NULL/IS NOT NULL without values, handle IN with list of values, return properly formatted condition string | Restrictions: Must use dialect methods for escaping, handle all operator types, support strings/numbers/lists for values, no SQL injection possible | Success: Generates correct SQL for all operators and value types, uses dialect correctly, injection-proof, handles edge cases_

- [ ] 14. Implement SQL formatter in sql/formatter.py
  - File: src/sqltrans/sql/formatter.py
  - Create format() function for pretty-printing SQL
  - Create highlight() function for syntax highlighting using Rich
  - Add indentation and line breaks for readability
  - Purpose: Make generated SQL readable and visually appealing
  - _Leverage: Rich library for terminal styling_
  - _Requirements: Requirement 4 (SQL preview)_
  - _Prompt: Role: Frontend/CLI Developer with expertise in text formatting and Rich library | Task: Implement SQL formatting functions in sql/formatter.py, create format(sql: str, style: str = 'default') -> str that adds proper indentation (2-4 spaces), line breaks after major clauses (SELECT, FROM, WHERE), and alignment, create highlight(sql: str) -> RichText using Rich library to syntax highlight SQL keywords (blue), strings (green), identifiers (white), operators (yellow), test with various query lengths | Restrictions: Use Rich's syntax highlighting features, keep formatting simple and readable, preserve SQL correctness, handle long lines gracefully | Success: SQL is formatted with proper indentation, syntax highlighting works in terminal, improves readability significantly_

- [ ] 15. Write unit tests for dialects in tests/unit/test_dialects.py
  - File: tests/unit/test_dialects.py
  - Test each dialect's quoting and escaping methods
  - Test SQL injection prevention
  - Test edge cases (empty strings, special characters, keywords)
  - Purpose: Ensure dialects generate safe, correct SQL
  - _Leverage: pytest, parameterized tests_
  - _Requirements: Requirement 3 (multi-database support), Requirement 5 (security)_
  - _Prompt: Role: Security-focused QA Engineer with database and SQL injection testing expertise | Task: Write comprehensive unit tests in tests/unit/test_dialects.py for PostgreSQLDialect, OracleDialect, and GenericDialect, test quote_identifier with normal names, SQL keywords, special characters, test format_string_literal with quotes, backslashes, semicolons, SQL injection attempts ('; DROP TABLE, --, /**/, etc.), test format_number_literal with ints/floats/edge cases, use pytest.mark.parametrize for testing multiple inputs per dialect | Restrictions: Test all three dialects thoroughly, include SQL injection test cases, verify output is valid SQL, no actual database connections | Success: All dialects tested, SQL injection attempts are safely escaped, edge cases handled, coverage >95%_

- [ ] 16. Write unit tests for QueryBuilder in tests/unit/test_builder.py
  - File: tests/unit/test_builder.py
  - Test SELECT, FROM, WHERE clause generation
  - Test complete query generation for each dialect
  - Test edge cases (no columns, no filters, empty query)
  - Purpose: Ensure QueryBuilder generates correct SQL
  - _Leverage: pytest, mocked dialects_
  - _Requirements: Requirements 1, 2, 3 (query building and generation)_
  - _Prompt: Role: QA Engineer with SQL and unit testing expertise | Task: Write comprehensive unit tests in tests/unit/test_builder.py for QueryBuilder, test build_select() with various column combinations (including SELECT *), build_from() with table names, build_where() with single and multiple filters, build_query() for complete SQL with all three dialects, test edge cases (missing table, no columns, no filters), use fixtures for QueryState and dialect instances, mock dialect methods to verify they're called correctly | Restrictions: Test all public methods, use mocks to isolate QueryBuilder, test with all three dialects, clear test names | Success: QueryBuilder fully tested, all clause types verified, dialect integration confirmed, coverage >95%_

## Phase 1C: TUI Application (User Interface)

- [ ] 17. Implement main Textual app in ui/app.py
  - File: src/sqltrans/ui/app.py
  - Create SQLTransApp class extending Textual App
  - Define app structure, CSS styling, key bindings
  - Set up basic navigation and screen management
  - Purpose: Main entry point for TUI application
  - _Leverage: Textual framework_
  - _Requirements: Requirement 1 (interactive terminal UI)_
  - _Prompt: Role: Frontend Developer specializing in Textual TUI framework | Task: Create SQLTransApp class in ui/app.py extending textual.app.App, define CSS styling for consistent look, set up key bindings for quit (q), help (h), copy (c), define install_screen to show QueryBuilderScreen, implement on_mount to initialize app state, add basic navigation and reactive variables for tracking query state | Restrictions: Use Textual best practices, define CSS in separate string or file, use reactive variables for state, implement proper app lifecycle methods | Success: App runs and displays, CSS styling works, key bindings respond, screen navigation functional, follows Textual patterns_

- [ ] 18. Create query builder screen in ui/screens/query_builder.py
  - File: src/sqltrans/ui/screens/query_builder.py
  - Implement QueryBuilderScreen with layout of all widgets
  - Set up reactive state connection to QueryState model
  - Implement update_preview() to regenerate SQL on changes
  - Purpose: Main UI screen for building queries
  - _Leverage: Textual Screen, QueryState model, QueryBuilder_
  - _Requirements: Requirements 1-4 (all interactive features)_
  - _Prompt: Role: Frontend Developer with Textual framework expertise | Task: Implement QueryBuilderScreen in ui/screens/query_builder.py extending textual.screen.Screen, create compose() method laying out widgets in containers (header with dialect selector, left panel with table/column inputs, center panel with filter editor, right panel with SQL preview), maintain QueryState instance as reactive state, implement update_preview() method that creates QueryBuilder and regenerates SQL on any change, connect widget events to state updates | Restrictions: Use Textual containers for layout, implement reactive pattern, update preview on every state change, use proper widget composition | Success: Screen layout is functional and organized, reactive updates work, preview refreshes automatically, widgets are properly composed_

- [ ] 19. Implement DialectSelector widget in ui/widgets/dialect_selector.py
  - File: src/sqltrans/ui/widgets/dialect_selector.py
  - Create widget with radio buttons for PostgreSQL, Oracle, Generic
  - Emit event when dialect changes
  - Update QueryState dialect on selection
  - Purpose: Allow user to select target database
  - _Leverage: Textual RadioButton or Select widget_
  - _Requirements: Requirement 3 (multi-database selection)_
  - _Prompt: Role: Frontend Developer with Textual widget development experience | Task: Create DialectSelector widget in ui/widgets/dialect_selector.py extending Textual widget, use RadioButton or Select to offer PostgreSQL, Oracle, Generic SQL options, default to Generic, emit custom event DialectChanged when selection changes, provide on_dialect_changed handler that updates QueryState, style widget for visual clarity | Restrictions: Use Textual built-in widgets, emit events for parent to handle, keep widget self-contained, add proper styling | Success: Widget displays three options, selection works, events emit correctly, integrates with QueryState_

- [ ] 20. Implement TableInput widget in ui/widgets/table_input.py
  - File: src/sqltrans/ui/widgets/table_input.py
  - Create input field for table name with validation
  - Show validation errors inline
  - Update QueryState table on valid input
  - Purpose: Accept and validate table name input
  - _Leverage: Textual Input widget, validation utilities_
  - _Requirements: Requirement 1 (table selection), Requirement 5 (validation)_
  - _Prompt: Role: Frontend Developer with form validation experience | Task: Create TableInput widget in ui/widgets/table_input.py using Textual Input widget, implement on_input_changed handler that calls validate_identifier from utils/validation, show validation errors below input in red text, emit TableChanged event on valid input, update QueryState.table on success, provide visual feedback for valid/invalid state (green/red border or icon) | Restrictions: Use validation utilities, show clear error messages, don't update state with invalid input, use Textual styling for feedback | Success: Input validates table names, shows clear errors, only accepts valid identifiers, updates state correctly_

- [ ] 21. Implement ColumnList widget in ui/widgets/column_list.py
  - File: src/sqltrans/ui/widgets/column_list.py
  - Create scrollable list of selected columns
  - Add button to add new columns with validation
  - Add remove button for each column
  - Purpose: Manage list of columns in SELECT clause
  - _Leverage: Textual ListView, Input, Button, validation utilities_
  - _Requirements: Requirement 1 (column selection)_
  - _Prompt: Role: Frontend Developer with list management and Textual expertise | Task: Create ColumnList widget in ui/widgets/column_list.py displaying selected columns in ListView, add Input and Button for adding new columns with validation using validate_identifier, show each column with remove button, implement add_column method that validates and updates QueryState.columns, implement remove_column method, emit ColumnListChanged event on modifications, show "No columns (SELECT *)" when list is empty | Restrictions: Validate column names before adding, prevent duplicates, use Textual list widgets, clear error display | Success: Can add/remove columns, validation works, displays current columns, updates state, handles empty state_

- [ ] 22. Implement FilterEditor widget in ui/widgets/filter_editor.py
  - File: src/sqltrans/ui/widgets/filter_editor.py
  - Create form for adding filters: column, operator selector, value input
  - Display list of current filters with remove buttons
  - Validate filter inputs before adding
  - Purpose: Build WHERE clause conditions
  - _Leverage: Textual widgets, Filter model, validation utilities_
  - _Requirements: Requirement 2 (WHERE clause builder), Requirement 5 (validation)_
  - _Prompt: Role: Frontend Developer with complex form development experience | Task: Create FilterEditor widget in ui/widgets/filter_editor.py with Input for column name, Select for operator (=, !=, <, >, <=, >=, LIKE, IN, IS NULL, IS NOT NULL), Input for value (disabled for IS NULL/IS NOT NULL), Add Filter button, ListView showing current filters with remove buttons, implement add_filter validating inputs using validate_identifier and validate_value, create Filter instance and update QueryState.filters, emit FiltersChanged event, handle operator-specific validation (IN requires list, NULL operators need no value) | Restrictions: Validate all inputs, show clear errors, disable value input for NULL operators, use Filter model, prevent invalid filters | Success: Can add/remove filters, all operators work, validation prevents errors, displays filter list, updates state correctly_

- [ ] 23. Implement SQLPreview widget in ui/widgets/sql_preview.py
  - File: src/sqltrans/ui/widgets/sql_preview.py
  - Create read-only text display for SQL with syntax highlighting
  - Update when query state changes
  - Add copy to clipboard button
  - Add save to file button
  - Purpose: Display generated SQL with export options
  - _Leverage: Textual Static, Rich syntax highlighting, formatter_
  - _Requirements: Requirement 4 (SQL preview and export)_
  - _Prompt: Role: Frontend Developer with text display and Textual expertise | Task: Create SQLPreview widget in ui/widgets/sql_preview.py using Textual Static for read-only SQL display, accept SQL string and use formatter.highlight() to syntax highlight, provide update_sql(sql: str) method to refresh display, add Copy and Save buttons, implement on_copy using clipboard utility with success/error feedback, implement on_save prompting for filename and writing SQL, show line numbers optionally, auto-scroll for long queries | Restrictions: Read-only display, use syntax highlighting from formatter, handle clipboard errors gracefully, use file dialog for save path | Success: Displays SQL with highlighting, copy to clipboard works, save to file works, updates reactively, handles errors well_

- [ ] 24. Implement clipboard utility in utils/clipboard.py
  - File: src/sqltrans/utils/clipboard.py
  - Implement copy_to_clipboard() using pyperclip
  - Implement is_clipboard_available() for capability checking
  - Handle clipboard access errors gracefully
  - Purpose: Enable copying SQL to system clipboard
  - _Leverage: pyperclip library_
  - _Requirements: Requirement 4 (clipboard export)_
  - _Prompt: Role: Python Developer with cross-platform clipboard experience | Task: Implement clipboard utilities in utils/clipboard.py, create copy_to_clipboard(text: str) -> bool using pyperclip.copy with try/except for clipboard errors, create is_clipboard_available() -> bool checking if pyperclip works on current system, return True/False indicating success, log errors but don't raise exceptions, handle environments without clipboard (SSH, headless) | Restrictions: Use pyperclip library, handle all exceptions gracefully, return success boolean, log errors for debugging, work cross-platform | Success: Copies text to clipboard when available, returns False when unavailable, never crashes, works on Windows/Mac/Linux_

- [ ] 25. Implement configuration handling in utils/config.py
  - File: src/sqltrans/utils/config.py
  - Load configuration from ~/.sqltrans/config.toml
  - Support default dialect, color scheme preferences
  - Create default config if none exists
  - Purpose: Manage user preferences and settings
  - _Leverage: Python tomllib (3.10+) or tomli for reading TOML_
  - _Requirements: Non-functional requirements (configuration)_
  - _Prompt: Role: Python Developer with configuration management expertise | Task: Implement configuration utilities in utils/config.py, create Config dataclass for settings (default_dialect, color_scheme, etc.), implement load_config() reading from ~/.sqltrans/config.toml using tomllib (Python 3.11+) or tomli fallback, implement save_config() writing TOML, implement get_default_config() with sensible defaults, create config file on first run, handle missing/corrupted config gracefully with defaults | Restrictions: Use TOML format, store in user home directory, handle file errors, provide defaults, type hints required | Success: Loads config from TOML, creates default config if missing, handles errors gracefully, saves config correctly_

- [ ] 26. Implement __main__.py entry point in ui/__main__.py
  - File: src/sqltrans/__main__.py
  - Create CLI entry point using Click or Typer
  - Parse command-line arguments (--dialect, --help, --version)
  - Launch SQLTransApp
  - Purpose: Make package executable with python -m sqltrans
  - _Leverage: Click/Typer, ui/app.py_
  - _Requirements: All requirements (application entry point)_
  - _Prompt: Role: Python CLI Developer with Click/Typer expertise | Task: Create CLI entry point in __main__.py, use Click or Typer to define command-line interface, add options for --dialect (postgresql/oracle/generic), --version showing version, --help showing usage, implement main() function that loads config, creates SQLTransApp with initial dialect, runs app.run(), handle KeyboardInterrupt gracefully, add console script entry point in pyproject.toml for sqltrans command | Restrictions: Use Click or Typer, provide helpful --help, handle errors gracefully, clean exit on Ctrl+C | Success: App launches with python -m sqltrans and sqltrans command, CLI args work, help is clear, handles interrupts_

## Phase 1D: Integration and Testing

- [ ] 27. Write integration tests in tests/integration/test_ui_flow.py
  - File: tests/integration/test_ui_flow.py
  - Test complete query building flow from start to finish
  - Test dialect switching and SQL regeneration
  - Test export operations (clipboard, file)
  - Purpose: Verify UI and business logic work together
  - _Leverage: pytest, Textual test utilities_
  - _Requirements: All functional requirements_
  - _Prompt: Role: QA Engineer with integration testing and Textual testing expertise | Task: Write integration tests in tests/integration/test_ui_flow.py using Textual's test harness and pytest, test scenario 1: add table, columns, filters and verify SQL is generated, test scenario 2: switch dialect mid-session and verify SQL changes, test scenario 3: copy to clipboard and save to file, test scenario 4: validation errors appear and prevent invalid operations, test scenario 5: clear query and start over, use Textual test utilities to simulate user input and verify UI state | Restrictions: Use Textual's testing framework, test realistic user flows, verify both UI state and underlying models, no actual clipboard/file ops (mock them) | Success: Complete user workflows tested, UI interactions verified, state synchronization confirmed, tests cover happy paths and errors_

- [ ] 28. Write end-to-end scenario tests in tests/e2e/test_scenarios.py
  - File: tests/e2e/test_scenarios.py
  - Test real-world support scenarios
  - Test complex queries with multiple filters
  - Test edge cases and error recovery
  - Purpose: Validate tool meets real user needs
  - _Leverage: pytest, full application stack_
  - _Requirements: All requirements (end-to-end validation)_
  - _Prompt: Role: QA Engineer with E2E testing and real-world scenario design | Task: Write end-to-end tests in tests/e2e/test_scenarios.py simulating real support engineer workflows, scenario 1: "Find customer by email" (SELECT * FROM customers WHERE email = 'x@y.com'), scenario 2: "Find recent orders" (SELECT id, amount FROM orders WHERE created_at > '2024-01-01'), scenario 3: "Find users with name like pattern" (SELECT * FROM users WHERE name LIKE '%Smith%'), scenario 4: "Complex multi-filter query" (multiple AND conditions), scenario 5: "Export query for different databases" (generate for all 3 dialects), verify generated SQL is correct and executable | Restrictions: Test complete workflows, verify SQL correctness, include realistic support scenarios, test all dialects | Success: All scenarios pass, generated SQL is valid and useful, covers real-world support use cases_

- [ ] 29. Add keyboard shortcuts and help system
  - Files: ui/app.py, ui/screens/help_screen.py
  - Implement keyboard shortcuts (q=quit, c=copy, s=save, h=help, n=new)
  - Create help screen showing all shortcuts and usage
  - Add footer showing available shortcuts
  - Purpose: Improve usability and discoverability
  - _Leverage: Textual key bindings, Screen system_
  - _Requirements: Requirement 1 (keyboard-first), Usability requirements_
  - _Prompt: Role: UX-focused Frontend Developer with Textual expertise | Task: Add keyboard shortcuts to SQLTransApp in ui/app.py using Textual bindings (q for quit, c for copy SQL, s for save to file, h for help, n for new query, ESC to clear focus), create HelpScreen in ui/screens/help_screen.py showing table of all shortcuts with descriptions, add Footer to main screen showing common shortcuts, implement action_* methods for each shortcut, make help screen dismissible with ESC or q | Restrictions: Use Textual action system, make shortcuts intuitive, include help screen, show shortcuts in footer, don't conflict with text input | Success: All shortcuts work, help screen is informative, footer shows key shortcuts, keyboard navigation is efficient_

- [ ] 30. Add error handling and logging
  - Files: utils/logging.py, ui/app.py, sql/builder.py
  - Set up Python logging to ~/.sqltrans/logs/sqltrans.log
  - Add try/except blocks around UI operations
  - Display user-friendly errors in UI, log technical details
  - Purpose: Improve reliability and debuggability
  - _Leverage: Python logging module_
  - _Requirements: Requirement 5 (error handling), Reliability requirements_
  - _Prompt: Role: Backend Developer with error handling and logging expertise | Task: Implement logging utilities in utils/logging.py setting up Python logger writing to ~/.sqltrans/logs/sqltrans.log with rotating file handler, configure log levels (DEBUG to file, INFO+ to console), add error handling throughout app.py, builder.py, and widgets catching exceptions, logging technical details, and showing user-friendly messages in UI (use Textual notifications or error labels), handle common errors (file permission, clipboard unavailable, invalid input) gracefully | Restrictions: Use stdlib logging, rotate log files, don't expose stack traces to users, log enough detail for debugging, create log directory if missing | Success: Errors logged to file, users see friendly messages, app doesn't crash, logs are useful for debugging_

## Phase 1E: Packaging and Distribution

- [ ] 31. Configure package metadata in pyproject.toml
  - File: pyproject.toml
  - Set up package metadata (name, version, description, authors)
  - Configure build system (setuptools or hatch)
  - Define console scripts entry point
  - Add project dependencies and optional dependencies
  - Purpose: Prepare package for distribution
  - _Leverage: PEP 621 pyproject.toml standard_
  - _Requirements: Non-functional (distribution requirements)_
  - _Prompt: Role: Python Packaging Expert with pyproject.toml expertise | Task: Configure pyproject.toml for SQLTrans package, set metadata (name="sqltrans", version="0.1.0", description="Interactive SQL query builder for support engineers", authors, license="MIT", python requires ">=3.10"), configure build system (use setuptools or hatchling), add dependencies (textual, rich, pyperclip), add dev dependencies in [project.optional-dependencies] dev section (pytest, mypy, black, ruff), define console script entry point sqltrans pointing to sqltrans.__main__:main, add project URLs (repository, issues) | Restrictions: Follow PEP 621, use modern build backend, specify minimum Python 3.10, include all dependencies | Success: Package metadata complete, dependencies listed, console script defined, follows modern Python packaging standards_

- [ ] 32. Create PyInstaller spec for standalone executable
  - Files: sqltrans.spec, scripts/build_exe.py
  - Configure PyInstaller to bundle app as executable
  - Include all dependencies and resources
  - Test executable on target platforms
  - Purpose: Create standalone exe for users without Python
  - _Leverage: PyInstaller_
  - _Requirements: Non-functional (distribution as executable)_
  - _Prompt: Role: DevOps Engineer with PyInstaller and cross-platform packaging experience | Task: Create PyInstaller spec file sqltrans.spec configuring build of standalone executable, include all dependencies (textual, rich, pyperclip), bundle resources (config defaults), set appropriate options for console app, create build script scripts/build_exe.py automating PyInstaller build for Windows/Mac/Linux, configure for one-file or one-folder dist based on platform, test executable launches and works without Python installed | Restrictions: Use PyInstaller, include all runtime dependencies, test on all platforms (Windows, Mac, Linux), ensure executable is self-contained | Success: Executable builds successfully, runs without Python installed, includes all dependencies, works on all target platforms_

- [ ] 33. Write user documentation
  - Files: README.md, docs/user-guide.md, docs/development.md
  - Create comprehensive README with installation and quickstart
  - Write user guide with examples and screenshots (ASCII art for terminal)
  - Write development guide for contributors
  - Purpose: Help users and developers understand and use SQLTrans
  - _Leverage: Markdown, examples from testing_
  - _Requirements: All requirements (documentation)_
  - _Prompt: Role: Technical Writer with CLI tool documentation expertise | Task: Write comprehensive documentation: README.md with project overview, installation (pip and executable), quick start example, features list, screenshots (ASCII art of TUI), usage examples; docs/user-guide.md with detailed walkthrough of all features, keyboard shortcuts, examples for common scenarios (customer lookup, order queries), troubleshooting section; docs/development.md with setup instructions, architecture overview, how to add new dialects, testing guide, contribution guidelines | Restrictions: Clear and concise writing, include examples, use ASCII art for terminal screenshots, cover all features, explain troubleshooting | Success: Documentation is complete and helpful, users can get started quickly, developers can contribute, all features explained_

- [ ] 34. Create example queries and usage guide
  - Files: examples/sample_queries.md, examples/support_scenarios.md
  - Document common support scenarios with example queries
  - Show how to use tool for each scenario
  - Include queries for all three dialects
  - Purpose: Provide ready-to-use examples for support engineers
  - _Leverage: Real support scenarios_
  - _Requirements: Product goals (support engineer efficiency)_
  - _Prompt: Role: Technical Writer with database and support experience | Task: Create example documentation in examples/ directory, sample_queries.md showing 10-15 common queries (customer lookup by email/id, order search by date range, user search with LIKE, multi-condition filters) with screenshots of building them in the tool, support_scenarios.md describing real support scenarios and how to use SQLTrans to solve them, include versions of queries for all three dialects (PostgreSQL, Oracle, Generic), add tips for efficient query building | Restrictions: Use realistic support scenarios, show tool usage step-by-step, include all dialects, make examples copy-pasteable | Success: Examples are practical and useful, cover common scenarios, demonstrate tool features, support engineers can follow them easily_

- [ ] 35. Final testing and quality assurance
  - Files: All test files, CI configuration (future)
  - Run full test suite (unit, integration, E2E)
  - Check code coverage (aim for >90%)
  - Run mypy type checking with strict mode
  - Run black and ruff for code quality
  - Test on all platforms (Windows, Mac, Linux)
  - Purpose: Ensure quality before release
  - _Leverage: pytest, coverage, mypy, black, ruff_
  - _Requirements: All requirements_
  - _Prompt: Role: QA Lead with Python quality assurance expertise | Task: Perform comprehensive QA for SQLTrans, run pytest with coverage (pytest --cov=sqltrans --cov-report=html) aiming for >90%, run mypy in strict mode on entire codebase, run black to verify formatting, run ruff for linting, test manually on Windows, Mac, and Linux terminals, verify all features work, test edge cases, verify error handling, check performance (startup time, response time), create QA checklist documenting all tests performed and results | Restrictions: Must achieve >90% code coverage, mypy must pass in strict mode, no linting errors, test on all platforms, document all findings | Success: All tests pass, coverage >90%, type checking passes, code quality verified, works on all platforms, ready for release_
