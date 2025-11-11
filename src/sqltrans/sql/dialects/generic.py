"""Generic ANSI SQL dialect implementation."""

from typing import Union


class GenericDialect:
    """Generic ANSI SQL-92 compliant dialect implementation.

    This dialect follows the ANSI SQL-92 standard and provides maximum
    compatibility across different database systems. It uses conservative
    syntax that works in most SQL databases.

    ANSI SQL-92 standard:
    - Double quotes for identifiers (optional for simple names)
    - Single quotes for string literals
    - Single quote escaping by doubling
    - Standard numeric formats
    - No vendor-specific extensions

    Use this dialect when:
    - Target database is unknown
    - Maximum portability is required
    - Learning SQL basics
    - Generating queries for multiple database types

    Reference: ISO/IEC 9075:1992 (SQL-92 standard)
    """

    def quote_identifier(self, name: str) -> str:
        """Quote identifier using ANSI SQL-92 double-quote syntax.

        ANSI SQL-92 identifier quoting:
        - Double quotes for all identifiers (safest approach)
        - Escape existing double quotes by doubling
        - Works consistently across most databases

        Args:
            name: Identifier to quote

        Returns:
            Double-quoted identifier with escaped quotes

        Example:
            >>> d = GenericDialect()
            >>> d.quote_identifier("user_id")
            '"user_id"'
            >>> d.quote_identifier("order_total")
            '"order_total"'
            >>> d.quote_identifier('name"test')
            '"name""test"'
        """
        # Escape any existing double quotes by doubling them
        escaped = name.replace('"', '""')
        return f'"{escaped}"'

    def format_string_literal(self, value: str) -> str:
        """Format string literal using ANSI SQL-92 single-quote syntax.

        ANSI SQL-92 string literal rules:
        - Surround with single quotes
        - Escape single quotes by doubling them
        - No backslash escaping (differs from some databases)

        Args:
            value: String value to format

        Returns:
            Single-quoted string with escaped quotes

        Example:
            >>> d = GenericDialect()
            >>> d.format_string_literal("Hello World")
            "'Hello World'"
            >>> d.format_string_literal("It's a test")
            "'It''s a test'"
        """
        # Escape single quotes by doubling them (ANSI SQL-92 standard)
        escaped = value.replace("'", "''")
        return f"'{escaped}'"

    def format_number_literal(self, value: Union[int, float]) -> str:
        """Format number literal using ANSI SQL-92 syntax.

        ANSI SQL-92 numeric formats:
        - Integers: 42, -17, 0
        - Decimals: 3.14, -2.5, 0.001
        - Scientific notation: 1.23E10 (optional)

        Args:
            value: Numeric value (int or float)

        Returns:
            String representation of number

        Example:
            >>> d = GenericDialect()
            >>> d.format_number_literal(42)
            '42'
            >>> d.format_number_literal(3.14159)
            '3.14159'
            >>> d.format_number_literal(-100)
            '-100'
        """
        return str(value)

    def get_null_keyword(self) -> str:
        """Return the NULL keyword per ANSI SQL-92.

        Returns:
            The string "NULL"

        Example:
            >>> d = GenericDialect()
            >>> d.get_null_keyword()
            'NULL'
        """
        return "NULL"

    def supports_feature(self, feature: str) -> bool:
        """Check if generic ANSI SQL-92 supports a specific feature.

        This dialect only claims support for core SQL-92 features.
        Advanced or vendor-specific features are not supported to
        ensure maximum compatibility.

        Supported features (SQL-92 core):
        - None declared (conservative approach)

        Not supported:
        - RETURNING: Vendor-specific
        - CTE: Added in SQL:1999
        - WINDOW: Added in SQL:2003
        - LIMIT: Vendor-specific (use FETCH FIRST in SQL:2008)

        Args:
            feature: Feature name to check (uppercase)

        Returns:
            False for all features (conservative approach)

        Example:
            >>> d = GenericDialect()
            >>> d.supports_feature("CTE")
            False
            >>> d.supports_feature("LIMIT")
            False

        Notes:
            Returns False for all features to maintain compatibility.
            Applications should use only basic SELECT/FROM/WHERE/ORDER BY
            when using the generic dialect.
        """
        # Generic dialect claims no advanced features for maximum compatibility
        # Only basic SELECT, FROM, WHERE, ORDER BY are assumed
        return False
