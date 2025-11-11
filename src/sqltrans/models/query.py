"""Query state model for managing the query being built."""

from dataclasses import dataclass, field
from typing import Optional

from sqltrans.models.filters import Filter


# Valid SQL dialects
VALID_DIALECTS = {"postgresql", "oracle", "generic"}


@dataclass
class QueryState:
    """Represents the current query being constructed.

    Attributes:
        table: Table name for FROM clause
        columns: List of column names for SELECT clause
        filters: List of WHERE clause conditions
        dialect: Target SQL dialect (postgresql, oracle, generic)
    """

    table: Optional[str] = None
    columns: list[str] = field(default_factory=list)
    filters: list[Filter] = field(default_factory=list)
    dialect: str = "generic"

    def __post_init__(self) -> None:
        """Validate initial state after dataclass initialization."""
        if self.dialect not in VALID_DIALECTS:
            raise ValueError(
                f"Invalid dialect: {self.dialect}. "
                f"Must be one of {', '.join(VALID_DIALECTS)}"
            )

    def add_table(self, name: str) -> None:
        """Set the table name for the FROM clause.

        Args:
            name: Table name

        Raises:
            ValueError: If name is empty or invalid
        """
        if not name or not name.strip():
            raise ValueError("Table name cannot be empty")

        self.table = name.strip()

    def add_column(self, name: str) -> None:
        """Add a column to the SELECT clause.

        Args:
            name: Column name

        Raises:
            ValueError: If name is empty or already exists
        """
        if not name or not name.strip():
            raise ValueError("Column name cannot be empty")

        name = name.strip()

        # Prevent duplicates
        if name in self.columns:
            raise ValueError(f"Column '{name}' already exists")

        self.columns.append(name)

    def remove_column(self, name: str) -> None:
        """Remove a column from the SELECT clause.

        Args:
            name: Column name to remove

        Raises:
            ValueError: If column doesn't exist
        """
        if name not in self.columns:
            raise ValueError(f"Column '{name}' not found")

        self.columns.remove(name)

    def add_filter(self, filter_obj: Filter) -> None:
        """Add a WHERE clause condition.

        Args:
            filter_obj: Filter object to add

        Raises:
            ValueError: If filter is invalid
        """
        # Validate filter first
        is_valid, error_msg = filter_obj.validate()
        if not is_valid:
            raise ValueError(f"Invalid filter: {error_msg}")

        self.filters.append(filter_obj)

    def remove_filter(self, index: int) -> None:
        """Remove a filter by index.

        Args:
            index: Index of filter to remove

        Raises:
            IndexError: If index is out of range
        """
        if index < 0 or index >= len(self.filters):
            raise IndexError(f"Filter index {index} out of range")

        self.filters.pop(index)

    def set_dialect(self, dialect: str) -> None:
        """Set the target SQL dialect.

        Args:
            dialect: Dialect name (postgresql, oracle, generic)

        Raises:
            ValueError: If dialect is invalid
        """
        dialect = dialect.lower()

        if dialect not in VALID_DIALECTS:
            raise ValueError(
                f"Invalid dialect: {dialect}. "
                f"Must be one of {', '.join(VALID_DIALECTS)}"
            )

        self.dialect = dialect

    def clear(self) -> None:
        """Reset query state to empty, keeping current dialect."""
        self.table = None
        self.columns.clear()
        self.filters.clear()
        # Note: dialect is preserved

    def to_dict(self) -> dict[str, Any]:  # type: ignore[name-defined]
        """Serialize query state to dictionary.

        Returns:
            Dictionary representation of query state
        """
        return {
            "table": self.table,
            "columns": self.columns.copy(),
            "filters": [
                {
                    "column": f.column,
                    "operator": f.operator,
                    "value": f.value,
                }
                for f in self.filters
            ],
            "dialect": self.dialect,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "QueryState":  # type: ignore[name-defined]
        """Deserialize query state from dictionary.

        Args:
            data: Dictionary representation

        Returns:
            QueryState instance
        """
        state = cls(dialect=data.get("dialect", "generic"))

        if data.get("table"):
            state.add_table(data["table"])

        for column in data.get("columns", []):
            state.add_column(column)

        for filter_data in data.get("filters", []):
            filter_obj = Filter(
                column=filter_data["column"],
                operator=filter_data["operator"],
                value=filter_data.get("value"),
            )
            state.add_filter(filter_obj)

        return state

    def __str__(self) -> str:
        """Return human-readable representation of query state."""
        parts = []

        if self.table:
            parts.append(f"FROM {self.table}")

        col_count = len(self.columns)
        if col_count > 0:
            parts.append(f"SELECT {col_count} columns")
        else:
            parts.append("SELECT *")

        filter_count = len(self.filters)
        if filter_count > 0:
            parts.append(f"WHERE {filter_count} filters")

        parts.append(f"({self.dialect})")

        return " | ".join(parts)

    def __repr__(self) -> str:
        """Return detailed representation for debugging."""
        return (
            f"QueryState(table={self.table!r}, "
            f"columns={self.columns!r}, "
            f"filters={self.filters!r}, "
            f"dialect={self.dialect!r})"
        )
