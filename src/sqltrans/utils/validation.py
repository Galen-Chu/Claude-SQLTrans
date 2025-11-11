"""Input validation utilities for SQL identifiers and values."""

import re
from typing import Any


# SQL reserved keywords (common across PostgreSQL, Oracle, and SQL standard)
SQL_KEYWORDS = {
    "SELECT",
    "FROM",
    "WHERE",
    "INSERT",
    "UPDATE",
    "DELETE",
    "CREATE",
    "DROP",
    "ALTER",
    "TABLE",
    "INDEX",
    "VIEW",
    "GRANT",
    "REVOKE",
    "AND",
    "OR",
    "NOT",
    "NULL",
    "IS",
    "IN",
    "LIKE",
    "BETWEEN",
    "EXISTS",
    "ALL",
    "ANY",
    "SOME",
    "UNION",
    "INTERSECT",
    "EXCEPT",
    "ORDER",
    "GROUP",
    "BY",
    "HAVING",
    "AS",
    "ON",
    "JOIN",
    "INNER",
    "OUTER",
    "LEFT",
    "RIGHT",
    "FULL",
    "CROSS",
    "NATURAL",
    "DISTINCT",
    "UNIQUE",
    "PRIMARY",
    "FOREIGN",
    "KEY",
    "REFERENCES",
    "CONSTRAINT",
    "CHECK",
    "DEFAULT",
    "CASCADE",
    "SET",
    "BEGIN",
    "COMMIT",
    "ROLLBACK",
    "TRANSACTION",
    "CASE",
    "WHEN",
    "THEN",
    "ELSE",
    "END",
}

# Valid operators for WHERE clauses
VALID_OPERATORS = {
    "=",
    "!=",
    "<",
    ">",
    "<=",
    ">=",
    "LIKE",
    "IN",
    "IS NULL",
    "IS NOT NULL",
}

# Pattern for valid SQL identifiers
# Starts with letter or underscore, followed by letters, digits, or underscores
IDENTIFIER_PATTERN = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]*$")


def validate_identifier(name: str) -> tuple[bool, str]:
    """Validate SQL identifier (table or column name).

    Args:
        name: Identifier to validate

    Returns:
        Tuple of (is_valid, error_message).
        If valid, error_message is empty string.

    Examples:
        >>> validate_identifier("users")
        (True, '')
        >>> validate_identifier("user_name")
        (True, '')
        >>> validate_identifier("123invalid")
        (False, 'Identifier must start with a letter or underscore')
        >>> validate_identifier("user-name")
        (False, 'Identifier contains invalid characters')
    """
    # Check for empty
    if not name or not name.strip():
        return False, "Identifier cannot be empty"

    name = name.strip()

    # Check length (most databases have limit around 30-128 chars)
    if len(name) > 128:
        return False, "Identifier is too long (max 128 characters)"

    # Check for SQL injection patterns
    dangerous_patterns = [";", "--", "/*", "*/", "XP_", "SP_", "DROP", "';"]
    for pattern in dangerous_patterns:
        if pattern in name.upper():
            return (
                False,
                f"Identifier contains potentially dangerous pattern: {pattern}",
            )

    # Check pattern
    if not IDENTIFIER_PATTERN.match(name):
        if name[0].isdigit():
            return False, "Identifier must start with a letter or underscore"
        return False, "Identifier contains invalid characters (only letters, digits, underscore allowed)"

    # Warn about SQL keywords but allow if quoted
    if name.upper() in SQL_KEYWORDS:
        return (
            True,
            f"Warning: '{name}' is a SQL keyword and must be quoted in queries",
        )

    return True, ""


def is_sql_keyword(name: str) -> bool:
    """Check if name is a SQL reserved keyword.

    Args:
        name: Identifier to check

    Returns:
        True if name is a SQL keyword

    Examples:
        >>> is_sql_keyword("SELECT")
        True
        >>> is_sql_keyword("users")
        False
    """
    return name.upper() in SQL_KEYWORDS


def validate_operator(op: str) -> bool:
    """Validate SQL operator.

    Args:
        op: Operator to validate

    Returns:
        True if operator is valid

    Examples:
        >>> validate_operator("=")
        True
        >>> validate_operator("LIKE")
        True
        >>> validate_operator("INVALID")
        False
    """
    return op in VALID_OPERATORS


def validate_value(value: str, value_type: str) -> tuple[bool, Any, str]:
    """Parse and validate filter value.

    Args:
        value: String value to parse
        value_type: Type of value ('string', 'number', 'list')

    Returns:
        Tuple of (is_valid, parsed_value, error_message).
        If valid, parsed_value contains the typed value and error_message is empty.

    Examples:
        >>> validate_value("John", "string")
        (True, 'John', '')
        >>> validate_value("123", "number")
        (True, 123, '')
        >>> validate_value("1,2,3", "list")
        (True, ['1', '2', '3'], '')
    """
    if not value and value_type != "string":
        return False, None, "Value cannot be empty"

    try:
        if value_type == "string":
            # Check for SQL injection patterns in string values
            dangerous = ["';", "';--", "' OR '", "' AND '", "1=1", "1' OR '1'='1"]
            value_upper = value.upper()
            for pattern in dangerous:
                if pattern in value_upper:
                    return (
                        False,
                        None,
                        f"Value contains potentially dangerous SQL pattern: {pattern}",
                    )
            return True, value, ""

        elif value_type == "number":
            # Try to parse as number
            # First check if it looks like a number
            if not re.match(r"^-?\d+\.?\d*$", value.strip()):
                return False, None, "Value is not a valid number"

            # Try int first, then float
            try:
                parsed = int(value)
            except ValueError:
                try:
                    parsed = float(value)
                except ValueError:
                    return False, None, "Value is not a valid number"

            return True, parsed, ""

        elif value_type == "list":
            # Parse comma-separated list
            if not value.strip():
                return False, None, "List cannot be empty"

            # Split by comma and strip whitespace
            items = [item.strip() for item in value.split(",")]

            # Remove empty items
            items = [item for item in items if item]

            if len(items) == 0:
                return False, None, "List must contain at least one value"

            # Check each item for SQL injection
            for item in items:
                item_upper = item.upper()
                dangerous = ["';", "--", "/*", "DROP", "DELETE", "UPDATE"]
                for pattern in dangerous:
                    if pattern in item_upper:
                        return (
                            False,
                            None,
                            f"List item contains dangerous pattern: {pattern}",
                        )

            return True, items, ""

        else:
            return False, None, f"Unknown value type: {value_type}"

    except Exception as e:
        return False, None, f"Error parsing value: {str(e)}"
