"""Oracle SQL dialect implementation."""

from typing import Union


class OracleDialect:
    """Oracle-specific SQL dialect implementation.

    Oracle SQL uses:
    - Double quotes for case-sensitive identifiers ("TableName")
    - Unquoted identifiers are converted to UPPERCASE
    - Single quotes for string literals ('value')
    - Single quote escaping by doubling ('O''Brien')
    - Standard number formatting

    Key differences from other databases:
    - Unquoted identifiers are automatically uppercased
    - Reserved words and special characters require quoting
    - 30-character limit for identifiers (pre-12.2) or 128 chars (12.2+)

    Reference: https://docs.oracle.com/en/database/oracle/oracle-database/19/sqlrf/Database-Object-Names-and-Qualifiers.html
    """

    def quote_identifier(self, name: str) -> str:
        """Quote identifier using Oracle double-quote syntax.

        Oracle identifier rules:
        - Unquoted: Converted to UPPERCASE, limited character set
        - Quoted: Case-sensitive, allows spaces and special characters
        - Double quotes preserve exact case

        Args:
            name: Identifier to quote

        Returns:
            Double-quoted identifier with escaped quotes

        Example:
            >>> d = OracleDialect()
            >>> d.quote_identifier("user_id")
            '"user_id"'
            >>> d.quote_identifier("TableName")
            '"TableName"'
            >>> d.quote_identifier('col"name')
            '"col""name"'
        """
        # Escape any existing double quotes by doubling them
        escaped = name.replace('"', '""')
        return f'"{escaped}"'

    def format_string_literal(self, value: str) -> str:
        """Format string literal using Oracle single-quote syntax.

        Oracle string escaping:
        - Surround with single quotes
        - Escape single quotes by doubling them ('O''Brien')
        - Alternative q-quote syntax exists but not used here

        Args:
            value: String value to format

        Returns:
            Single-quoted string with escaped quotes

        Example:
            >>> d = OracleDialect()
            >>> d.format_string_literal("Hello")
            "'Hello'"
            >>> d.format_string_literal("It's")
            "'It''s'"
        """
        # Escape single quotes by doubling them
        escaped = value.replace("'", "''")
        return f"'{escaped}'"

    def format_number_literal(self, value: Union[int, float]) -> str:
        """Format number literal for Oracle.

        Oracle accepts standard numeric formats:
        - Integers: 42, -17
        - Floats: 3.14, -2.5
        - Scientific notation: 1.23E10

        Args:
            value: Numeric value (int or float)

        Returns:
            String representation of number

        Example:
            >>> d = OracleDialect()
            >>> d.format_number_literal(42)
            '42'
            >>> d.format_number_literal(3.14)
            '3.14'
        """
        return str(value)

    def get_null_keyword(self) -> str:
        """Return the NULL keyword for Oracle.

        Returns:
            The string "NULL"

        Example:
            >>> d = OracleDialect()
            >>> d.get_null_keyword()
            'NULL'
        """
        return "NULL"

    def supports_feature(self, feature: str) -> bool:
        """Check if Oracle supports a specific SQL feature.

        Oracle is a comprehensive enterprise database with extensive features.

        Supported features:
        - CTE: Common Table Expressions (WITH clause)
        - WINDOW: Window functions (analytic functions)
        - ROWNUM: Oracle's row numbering
        - CONNECT_BY: Hierarchical queries
        - MERGE: MERGE statement (upsert)

        Not supported in this context:
        - RETURNING: Available but with different syntax
        - LIMIT: Oracle uses ROWNUM or FETCH FIRST instead

        Args:
            feature: Feature name to check (uppercase)

        Returns:
            True if supported, False otherwise

        Example:
            >>> d = OracleDialect()
            >>> d.supports_feature("CTE")
            True
            >>> d.supports_feature("LIMIT")
            False
        """
        supported_features = {
            "CTE",
            "WINDOW",
            "ROWNUM",
            "CONNECT_BY",
            "MERGE",
            "FETCH_FIRST",
        }
        return feature.upper() in supported_features
