"""Base SQL dialect protocol defining the interface for all SQL dialects."""

from typing import Protocol, Union


class BaseDialect(Protocol):
    """Protocol defining the interface that all SQL dialects must implement.

    This protocol ensures that all dialect implementations provide consistent
    methods for quoting identifiers, formatting literals, and checking features.
    Different databases have different quoting and escaping rules, so each
    dialect implementation must handle its database's specific requirements.

    Example implementations:
        - PostgreSQL: Uses double quotes for identifiers, single quotes for strings
        - Oracle: Uses double quotes for case-sensitive identifiers
        - Generic: ANSI SQL-92 standard compliant

    Methods:
        quote_identifier: Escape and quote SQL identifiers (table/column names)
        format_string_literal: Escape and quote string values
        format_number_literal: Format numeric values
        get_null_keyword: Return the NULL keyword for the dialect
        supports_feature: Check if dialect supports a specific feature
    """

    def quote_identifier(self, name: str) -> str:
        """Quote and escape a SQL identifier (table or column name).

        Identifiers are database object names like tables and columns. Different
        databases use different quoting characters and have different rules for
        when quoting is required.

        Args:
            name: The identifier to quote (e.g., "user_id", "MyTable")

        Returns:
            Properly quoted identifier safe for use in SQL queries
            (e.g., "user_id", "MyTable", etc. depending on dialect)

        Example:
            >>> dialect = PostgreSQLDialect()
            >>> dialect.quote_identifier("user_name")
            '"user_name"'
            >>> dialect.quote_identifier("table with spaces")
            '"table with spaces"'

        Notes:
            - Must handle special characters and reserved words
            - Must escape any quote characters within the identifier
            - Should prevent SQL injection
        """
        ...

    def format_string_literal(self, value: str) -> str:
        """Format and escape a string literal value.

        String literals are the actual data values in WHERE clauses and other
        contexts. They must be properly escaped to prevent SQL injection.

        Args:
            value: The string value to format (e.g., "John", "O'Brien")

        Returns:
            Properly escaped and quoted string literal
            (e.g., "'John'", "'O''Brien'")

        Example:
            >>> dialect = PostgreSQLDialect()
            >>> dialect.format_string_literal("Hello")
            "'Hello'"
            >>> dialect.format_string_literal("It's")
            "'It''s'"

        Notes:
            - Must escape single quotes and other special characters
            - Must prevent SQL injection attacks
            - Different databases may have different escaping rules
        """
        ...

    def format_number_literal(self, value: Union[int, float]) -> str:
        """Format a numeric literal value.

        Numbers generally don't require quoting but may need specific formatting
        for different databases (e.g., scientific notation, precision).

        Args:
            value: The numeric value to format (int or float)

        Returns:
            String representation of the number suitable for SQL
            (e.g., "42", "3.14", "-17.5")

        Example:
            >>> dialect = PostgreSQLDialect()
            >>> dialect.format_number_literal(42)
            '42'
            >>> dialect.format_number_literal(3.14159)
            '3.14159'

        Notes:
            - Integers should be formatted without decimal point
            - Floats should preserve reasonable precision
            - Should handle negative numbers
        """
        ...

    def get_null_keyword(self) -> str:
        """Return the NULL keyword for this dialect.

        Most SQL databases use 'NULL', but this method allows for dialect-specific
        variations if needed.

        Returns:
            The NULL keyword as a string (typically "NULL")

        Example:
            >>> dialect = GenericDialect()
            >>> dialect.get_null_keyword()
            'NULL'

        Notes:
            - Typically returns "NULL" for most databases
            - Provided as a method for consistency and future extensibility
        """
        ...

    def supports_feature(self, feature: str) -> bool:
        """Check if this dialect supports a specific SQL feature.

        This method allows the application to query whether the dialect
        implements certain SQL features. This can be used to conditionally
        enable/disable functionality or provide warnings to users.

        Args:
            feature: Feature name to check (e.g., "RETURNING", "UPSERT", "CTE")

        Returns:
            True if feature is supported, False otherwise

        Example:
            >>> dialect = PostgreSQLDialect()
            >>> dialect.supports_feature("RETURNING")
            True
            >>> dialect.supports_feature("TOP")
            False

        Notes:
            - Feature names should be uppercase for consistency
            - Common features: "RETURNING", "LIMIT", "TOP", "CTE", "WINDOW"
            - Used primarily for advanced features, not basic SQL
        """
        ...
