"""PostgreSQL SQL dialect implementation."""

from typing import Union


class PostgreSQLDialect:
    """PostgreSQL-specific SQL dialect implementation.

    PostgreSQL uses:
    - Double quotes for identifiers ("table_name", "column_name")
    - Single quotes for string literals ('value')
    - Single quote escaping by doubling ('O''Brien')
    - Standard number formatting
    - Case-sensitive identifiers when quoted

    Reference: https://www.postgresql.org/docs/current/sql-syntax-lexical.html
    """

    def quote_identifier(self, name: str) -> str:
        """Quote identifier using PostgreSQL double-quote syntax.

        PostgreSQL uses double quotes to:
        - Preserve case sensitivity
        - Allow spaces and special characters
        - Use reserved keywords as identifiers

        Args:
            name: Identifier to quote

        Returns:
            Double-quoted identifier with escaped quotes

        Example:
            >>> d = PostgreSQLDialect()
            >>> d.quote_identifier("user_id")
            '"user_id"'
            >>> d.quote_identifier('table"name')
            '"table""name"'
        """
        # Escape any existing double quotes by doubling them
        escaped = name.replace('"', '""')
        return f'"{escaped}"'

    def format_string_literal(self, value: str) -> str:
        """Format string literal using PostgreSQL single-quote syntax.

        PostgreSQL string escaping:
        - Surround with single quotes
        - Escape single quotes by doubling them ('O''Brien')
        - Backslashes may need escaping in some configurations

        Args:
            value: String value to format

        Returns:
            Single-quoted string with escaped quotes

        Example:
            >>> d = PostgreSQLDialect()
            >>> d.format_string_literal("Hello")
            "'Hello'"
            >>> d.format_string_literal("It's nice")
            "'It''s nice'"
        """
        # Escape single quotes by doubling them
        escaped = value.replace("'", "''")
        return f"'{escaped}'"

    def format_number_literal(self, value: Union[int, float]) -> str:
        """Format number literal for PostgreSQL.

        PostgreSQL accepts standard numeric formats:
        - Integers: 42, -17
        - Floats: 3.14, -2.5, 1.23e10

        Args:
            value: Numeric value (int or float)

        Returns:
            String representation of number

        Example:
            >>> d = PostgreSQLDialect()
            >>> d.format_number_literal(42)
            '42'
            >>> d.format_number_literal(3.14)
            '3.14'
        """
        return str(value)

    def get_null_keyword(self) -> str:
        """Return the NULL keyword for PostgreSQL.

        Returns:
            The string "NULL"

        Example:
            >>> d = PostgreSQLDialect()
            >>> d.get_null_keyword()
            'NULL'
        """
        return "NULL"

    def supports_feature(self, feature: str) -> bool:
        """Check if PostgreSQL supports a specific SQL feature.

        PostgreSQL is a feature-rich database with extensive SQL support.

        Supported features:
        - RETURNING: Return values from INSERT/UPDATE/DELETE
        - CTE: Common Table Expressions (WITH clause)
        - WINDOW: Window functions
        - ARRAY: Array data types and operations
        - JSON: JSON and JSONB support

        Args:
            feature: Feature name to check (uppercase)

        Returns:
            True if supported, False otherwise

        Example:
            >>> d = PostgreSQLDialect()
            >>> d.supports_feature("RETURNING")
            True
            >>> d.supports_feature("TOP")
            False
        """
        supported_features = {
            "RETURNING",
            "CTE",
            "WINDOW",
            "ARRAY",
            "JSON",
            "LIMIT",
            "OFFSET",
        }
        return feature.upper() in supported_features
