"""Database schema models for tables and columns."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Column:
    """Represents a database column.

    Attributes:
        name: Column name
        data_type: Optional column data type (for future schema discovery)
    """

    name: str
    data_type: Optional[str] = None

    def __str__(self) -> str:
        """Return string representation of column."""
        if self.data_type:
            return f"{self.name} ({self.data_type})"
        return self.name

    def __repr__(self) -> str:
        """Return detailed representation for debugging."""
        return f"Column(name={self.name!r}, data_type={self.data_type!r})"


@dataclass
class Table:
    """Represents a database table.

    Attributes:
        name: Table name
        columns: List of columns in the table (for future schema discovery)
    """

    name: str
    columns: list[Column] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        """Initialize default values after dataclass initialization."""
        if self.columns is None:
            self.columns = []

    def __str__(self) -> str:
        """Return string representation of table."""
        col_count = len(self.columns)
        if col_count == 0:
            return self.name
        return f"{self.name} ({col_count} columns)"

    def __repr__(self) -> str:
        """Return detailed representation for debugging."""
        return f"Table(name={self.name!r}, columns={self.columns!r})"
