"""Filter models for WHERE clause conditions."""

from dataclasses import dataclass
from typing import Any, Optional, Protocol


# Valid SQL operators
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

# Operators that don't require a value
NULL_OPERATORS = {"IS NULL", "IS NOT NULL"}


class BaseDialect(Protocol):
    """Protocol for SQL dialect implementations.

    This is a forward declaration for type hints. The actual implementation
    is in sqltrans.sql.dialects.base module.
    """

    def quote_identifier(self, name: str) -> str:
        """Quote an identifier (table/column name)."""
        ...

    def format_string_literal(self, value: str) -> str:
        """Format a string literal value."""
        ...

    def format_number_literal(self, value: int | float) -> str:
        """Format a number literal value."""
        ...


@dataclass
class Filter:
    """Represents a WHERE clause condition.

    Attributes:
        column: Column name to filter on
        operator: SQL comparison operator
        value: Value to compare against (None for IS NULL/IS NOT NULL)
    """

    column: str
    operator: str
    value: Optional[Any] = None

    def validate(self) -> tuple[bool, str]:
        """Validate filter is well-formed.

        Returns:
            Tuple of (is_valid, error_message).
            If valid, error_message is empty string.
        """
        # Validate operator
        if self.operator not in VALID_OPERATORS:
            return False, f"Invalid operator: {self.operator}"

        # Check value requirements based on operator
        if self.operator in NULL_OPERATORS:
            if self.value is not None:
                return (
                    False,
                    f"Operator '{self.operator}' should not have a value",
                )
        else:
            # All other operators require a value
            if self.value is None:
                return (
                    False,
                    f"Operator '{self.operator}' requires a value",
                )

            # Validate IN operator has list value
            if self.operator == "IN":
                if not isinstance(self.value, (list, tuple)):
                    return (
                        False,
                        "Operator 'IN' requires a list or tuple of values",
                    )
                if len(self.value) == 0:
                    return False, "Operator 'IN' requires at least one value"

        return True, ""

    def to_sql(self, dialect: BaseDialect) -> str:
        """Generate SQL condition string for this filter.

        Args:
            dialect: SQL dialect for proper escaping and formatting

        Returns:
            SQL condition string (e.g., '"name" = \'John\'')

        Raises:
            ValueError: If filter is invalid

        Example:
            >>> from sqltrans.sql.dialects.postgresql import PostgreSQLDialect
            >>> f = Filter("age", ">", 18)
            >>> f.to_sql(PostgreSQLDialect())
            '"age" > 18'
        """
        # Validate filter first
        is_valid, error_msg = self.validate()
        if not is_valid:
            raise ValueError(f"Cannot generate SQL for invalid filter: {error_msg}")

        # Quote the column name
        quoted_column = dialect.quote_identifier(self.column)

        # Handle NULL operators (no value)
        if self.operator in NULL_OPERATORS:
            return f"{quoted_column} {self.operator}"

        # Handle IN operator (list of values)
        if self.operator == "IN":
            # Format each value in the list
            formatted_values = []
            for val in self.value:  # type: ignore
                if isinstance(val, str):
                    formatted_values.append(dialect.format_string_literal(val))
                elif isinstance(val, (int, float)):
                    formatted_values.append(dialect.format_number_literal(val))
                else:
                    # Treat as string
                    formatted_values.append(dialect.format_string_literal(str(val)))

            values_str = ", ".join(formatted_values)
            return f"{quoted_column} {self.operator} ({values_str})"

        # Handle other operators with single value
        # Determine value type and format appropriately
        if isinstance(self.value, str):
            formatted_value = dialect.format_string_literal(self.value)
        elif isinstance(self.value, (int, float)):
            formatted_value = dialect.format_number_literal(self.value)
        else:
            # Fallback: convert to string
            formatted_value = dialect.format_string_literal(str(self.value))

        return f"{quoted_column} {self.operator} {formatted_value}"

    def __str__(self) -> str:
        """Return human-readable representation of filter."""
        if self.operator in NULL_OPERATORS:
            return f"{self.column} {self.operator}"
        return f"{self.column} {self.operator} {self.value}"

    def __repr__(self) -> str:
        """Return detailed representation for debugging."""
        return (
            f"Filter(column={self.column!r}, "
            f"operator={self.operator!r}, value={self.value!r})"
        )
