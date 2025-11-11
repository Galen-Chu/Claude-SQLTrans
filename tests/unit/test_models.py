"""Unit tests for data models (schema, filters, query)."""

import pytest
from sqltrans.models.schema import Column, Table
from sqltrans.models.filters import Filter, VALID_OPERATORS, NULL_OPERATORS
from sqltrans.models.query import QueryState, VALID_DIALECTS


class TestColumn:
    """Tests for Column model."""

    def test_column_creation_basic(self):
        """Test creating a column with name only."""
        col = Column(name="user_id")
        assert col.name == "user_id"
        assert col.data_type is None

    def test_column_creation_with_type(self):
        """Test creating a column with data type."""
        col = Column(name="email", data_type="VARCHAR(255)")
        assert col.name == "email"
        assert col.data_type == "VARCHAR(255)"

    def test_column_str_without_type(self):
        """Test string representation without data type."""
        col = Column(name="username")
        assert str(col) == "username"

    def test_column_str_with_type(self):
        """Test string representation with data type."""
        col = Column(name="age", data_type="INTEGER")
        assert str(col) == "age (INTEGER)"

    def test_column_repr(self):
        """Test detailed representation."""
        col = Column(name="status", data_type="BOOLEAN")
        assert repr(col) == "Column(name='status', data_type='BOOLEAN')"

    def test_column_equality(self):
        """Test column equality comparison."""
        col1 = Column(name="id", data_type="INT")
        col2 = Column(name="id", data_type="INT")
        assert col1 == col2


class TestTable:
    """Tests for Table model."""

    def test_table_creation_basic(self):
        """Test creating a table with name only."""
        table = Table(name="users")
        assert table.name == "users"
        assert table.columns == []

    def test_table_creation_with_columns(self):
        """Test creating a table with columns."""
        col1 = Column(name="id", data_type="INT")
        col2 = Column(name="name", data_type="VARCHAR")
        table = Table(name="customers", columns=[col1, col2])
        assert table.name == "customers"
        assert len(table.columns) == 2
        assert table.columns[0].name == "id"
        assert table.columns[1].name == "name"

    def test_table_str_without_columns(self):
        """Test string representation without columns."""
        table = Table(name="orders")
        assert str(table) == "orders"

    def test_table_str_with_columns(self):
        """Test string representation with columns."""
        col1 = Column(name="id")
        col2 = Column(name="total")
        table = Table(name="invoices", columns=[col1, col2])
        assert str(table) == "invoices (2 columns)"

    def test_table_repr(self):
        """Test detailed representation."""
        col = Column(name="id")
        table = Table(name="products", columns=[col])
        expected = "Table(name='products', columns=[Column(name='id', data_type=None)])"
        assert repr(table) == expected

    def test_table_columns_mutable(self):
        """Test that table columns list is mutable."""
        table = Table(name="items")
        assert len(table.columns) == 0

        col = Column(name="item_id")
        table.columns.append(col)
        assert len(table.columns) == 1
        assert table.columns[0].name == "item_id"


class TestFilter:
    """Tests for Filter model."""

    def test_filter_creation_basic(self):
        """Test creating a filter with all attributes."""
        f = Filter(column="age", operator="=", value=25)
        assert f.column == "age"
        assert f.operator == "="
        assert f.value == 25

    def test_filter_creation_null_operator(self):
        """Test creating a filter with IS NULL operator."""
        f = Filter(column="deleted_at", operator="IS NULL")
        assert f.column == "deleted_at"
        assert f.operator == "IS NULL"
        assert f.value is None

    def test_filter_validate_equality_operator_valid(self):
        """Test validation of equality operator with value."""
        f = Filter(column="status", operator="=", value="active")
        is_valid, error = f.validate()
        assert is_valid is True
        assert error == ""

    def test_filter_validate_comparison_operators_valid(self):
        """Test validation of comparison operators."""
        operators = ["!=", "<", ">", "<=", ">="]
        for op in operators:
            f = Filter(column="price", operator=op, value=100)
            is_valid, error = f.validate()
            assert is_valid is True, f"Operator {op} should be valid"
            assert error == ""

    def test_filter_validate_like_operator_valid(self):
        """Test validation of LIKE operator."""
        f = Filter(column="name", operator="LIKE", value="%Smith%")
        is_valid, error = f.validate()
        assert is_valid is True
        assert error == ""

    def test_filter_validate_in_operator_valid_list(self):
        """Test validation of IN operator with list."""
        f = Filter(column="status", operator="IN", value=["active", "pending"])
        is_valid, error = f.validate()
        assert is_valid is True
        assert error == ""

    def test_filter_validate_in_operator_valid_tuple(self):
        """Test validation of IN operator with tuple."""
        f = Filter(column="id", operator="IN", value=(1, 2, 3))
        is_valid, error = f.validate()
        assert is_valid is True
        assert error == ""

    def test_filter_validate_is_null_valid(self):
        """Test validation of IS NULL operator without value."""
        f = Filter(column="deleted_at", operator="IS NULL")
        is_valid, error = f.validate()
        assert is_valid is True
        assert error == ""

    def test_filter_validate_is_not_null_valid(self):
        """Test validation of IS NOT NULL operator without value."""
        f = Filter(column="email", operator="IS NOT NULL")
        is_valid, error = f.validate()
        assert is_valid is True
        assert error == ""

    def test_filter_validate_invalid_operator(self):
        """Test validation with invalid operator."""
        f = Filter(column="age", operator="BETWEEN", value=25)
        is_valid, error = f.validate()
        assert is_valid is False
        assert "Invalid operator" in error

    def test_filter_validate_missing_value_for_comparison(self):
        """Test validation when value is missing for comparison operator."""
        f = Filter(column="price", operator="=", value=None)
        is_valid, error = f.validate()
        assert is_valid is False
        assert "requires a value" in error

    def test_filter_validate_null_operator_with_value(self):
        """Test validation when IS NULL has a value (invalid)."""
        f = Filter(column="deleted_at", operator="IS NULL", value="something")
        is_valid, error = f.validate()
        assert is_valid is False
        assert "should not have a value" in error

    def test_filter_validate_in_operator_with_non_list(self):
        """Test validation when IN operator has non-list value."""
        f = Filter(column="status", operator="IN", value="active")
        is_valid, error = f.validate()
        assert is_valid is False
        assert "requires a list or tuple" in error

    def test_filter_validate_in_operator_with_empty_list(self):
        """Test validation when IN operator has empty list."""
        f = Filter(column="status", operator="IN", value=[])
        is_valid, error = f.validate()
        assert is_valid is False
        assert "at least one value" in error

    def test_filter_str_with_value(self):
        """Test string representation with value."""
        f = Filter(column="age", operator=">", value=18)
        assert str(f) == "age > 18"

    def test_filter_str_null_operator(self):
        """Test string representation for NULL operator."""
        f = Filter(column="deleted_at", operator="IS NULL")
        assert str(f) == "deleted_at IS NULL"

    def test_filter_repr(self):
        """Test detailed representation."""
        f = Filter(column="status", operator="=", value="active")
        expected = "Filter(column='status', operator='=', value='active')"
        assert repr(f) == expected

    def test_filter_to_sql_implemented(self):
        """Test that to_sql generates SQL correctly (implemented in Phase 1B)."""
        from sqltrans.sql.dialects.postgresql import PostgreSQLDialect

        f = Filter(column="name", operator="=", value="test")
        dialect = PostgreSQLDialect()
        result = f.to_sql(dialect)

        # Should generate proper SQL
        assert '"name"' in result
        assert "=" in result
        assert "'test'" in result


class TestQueryState:
    """Tests for QueryState model."""

    def test_query_state_creation_default(self):
        """Test creating query state with defaults."""
        state = QueryState()
        assert state.table is None
        assert state.columns == []
        assert state.filters == []
        assert state.dialect == "generic"

    def test_query_state_creation_with_dialect(self):
        """Test creating query state with specific dialect."""
        state = QueryState(dialect="postgresql")
        assert state.dialect == "postgresql"

    def test_query_state_creation_invalid_dialect(self):
        """Test creating query state with invalid dialect raises error."""
        with pytest.raises(ValueError) as exc_info:
            QueryState(dialect="invalid")

        assert "Invalid dialect" in str(exc_info.value)

    def test_add_table_valid(self):
        """Test adding a valid table name."""
        state = QueryState()
        state.add_table("users")
        assert state.table == "users"

    def test_add_table_with_whitespace(self):
        """Test adding table name with whitespace trims it."""
        state = QueryState()
        state.add_table("  customers  ")
        assert state.table == "customers"

    def test_add_table_empty_raises_error(self):
        """Test adding empty table name raises ValueError."""
        state = QueryState()
        with pytest.raises(ValueError) as exc_info:
            state.add_table("")

        assert "cannot be empty" in str(exc_info.value)

    def test_add_table_whitespace_only_raises_error(self):
        """Test adding whitespace-only table name raises ValueError."""
        state = QueryState()
        with pytest.raises(ValueError) as exc_info:
            state.add_table("   ")

        assert "cannot be empty" in str(exc_info.value)

    def test_add_column_valid(self):
        """Test adding a valid column."""
        state = QueryState()
        state.add_column("user_id")
        assert "user_id" in state.columns
        assert len(state.columns) == 1

    def test_add_column_multiple(self):
        """Test adding multiple columns."""
        state = QueryState()
        state.add_column("id")
        state.add_column("name")
        state.add_column("email")
        assert state.columns == ["id", "name", "email"]

    def test_add_column_with_whitespace(self):
        """Test adding column with whitespace trims it."""
        state = QueryState()
        state.add_column("  email  ")
        assert state.columns == ["email"]

    def test_add_column_empty_raises_error(self):
        """Test adding empty column raises ValueError."""
        state = QueryState()
        with pytest.raises(ValueError) as exc_info:
            state.add_column("")

        assert "cannot be empty" in str(exc_info.value)

    def test_add_column_duplicate_raises_error(self):
        """Test adding duplicate column raises ValueError."""
        state = QueryState()
        state.add_column("id")
        with pytest.raises(ValueError) as exc_info:
            state.add_column("id")

        assert "already exists" in str(exc_info.value)

    def test_remove_column_valid(self):
        """Test removing an existing column."""
        state = QueryState()
        state.add_column("id")
        state.add_column("name")
        state.remove_column("id")
        assert state.columns == ["name"]

    def test_remove_column_not_found_raises_error(self):
        """Test removing non-existent column raises ValueError."""
        state = QueryState()
        state.add_column("id")
        with pytest.raises(ValueError) as exc_info:
            state.remove_column("name")

        assert "not found" in str(exc_info.value)

    def test_add_filter_valid(self):
        """Test adding a valid filter."""
        state = QueryState()
        f = Filter(column="age", operator=">", value=18)
        state.add_filter(f)
        assert len(state.filters) == 1
        assert state.filters[0].column == "age"

    def test_add_filter_multiple(self):
        """Test adding multiple filters."""
        state = QueryState()
        f1 = Filter(column="age", operator=">", value=18)
        f2 = Filter(column="status", operator="=", value="active")
        state.add_filter(f1)
        state.add_filter(f2)
        assert len(state.filters) == 2

    def test_add_filter_invalid_raises_error(self):
        """Test adding invalid filter raises ValueError."""
        state = QueryState()
        f = Filter(column="age", operator="INVALID", value=18)
        with pytest.raises(ValueError) as exc_info:
            state.add_filter(f)

        assert "Invalid filter" in str(exc_info.value)

    def test_remove_filter_valid(self):
        """Test removing a filter by index."""
        state = QueryState()
        f1 = Filter(column="age", operator=">", value=18)
        f2 = Filter(column="status", operator="=", value="active")
        state.add_filter(f1)
        state.add_filter(f2)

        state.remove_filter(0)
        assert len(state.filters) == 1
        assert state.filters[0].column == "status"

    def test_remove_filter_invalid_index_raises_error(self):
        """Test removing filter with invalid index raises IndexError."""
        state = QueryState()
        f = Filter(column="age", operator=">", value=18)
        state.add_filter(f)

        with pytest.raises(IndexError):
            state.remove_filter(5)

    def test_remove_filter_negative_index_raises_error(self):
        """Test removing filter with negative index raises IndexError."""
        state = QueryState()
        with pytest.raises(IndexError):
            state.remove_filter(-1)

    def test_set_dialect_valid(self):
        """Test setting a valid dialect."""
        state = QueryState()
        state.set_dialect("postgresql")
        assert state.dialect == "postgresql"

    def test_set_dialect_case_insensitive(self):
        """Test setting dialect is case-insensitive."""
        state = QueryState()
        state.set_dialect("POSTGRESQL")
        assert state.dialect == "postgresql"

    def test_set_dialect_invalid_raises_error(self):
        """Test setting invalid dialect raises ValueError."""
        state = QueryState()
        with pytest.raises(ValueError) as exc_info:
            state.set_dialect("mysql")

        assert "Invalid dialect" in str(exc_info.value)

    def test_clear_resets_state(self):
        """Test clear resets query state but preserves dialect."""
        state = QueryState(dialect="oracle")
        state.add_table("users")
        state.add_column("id")
        state.add_column("name")
        f = Filter(column="age", operator=">", value=18)
        state.add_filter(f)

        state.clear()

        assert state.table is None
        assert state.columns == []
        assert state.filters == []
        assert state.dialect == "oracle"  # Preserved

    def test_to_dict_complete_state(self):
        """Test serialization of complete query state."""
        state = QueryState(dialect="postgresql")
        state.add_table("users")
        state.add_column("id")
        state.add_column("email")
        f = Filter(column="age", operator=">", value=18)
        state.add_filter(f)

        data = state.to_dict()

        assert data["table"] == "users"
        assert data["columns"] == ["id", "email"]
        assert data["dialect"] == "postgresql"
        assert len(data["filters"]) == 1
        assert data["filters"][0]["column"] == "age"
        assert data["filters"][0]["operator"] == ">"
        assert data["filters"][0]["value"] == 18

    def test_to_dict_empty_state(self):
        """Test serialization of empty query state."""
        state = QueryState()
        data = state.to_dict()

        assert data["table"] is None
        assert data["columns"] == []
        assert data["filters"] == []
        assert data["dialect"] == "generic"

    def test_from_dict_complete_state(self):
        """Test deserialization of complete query state."""
        data = {
            "table": "customers",
            "columns": ["id", "name", "email"],
            "filters": [
                {"column": "status", "operator": "=", "value": "active"},
                {"column": "age", "operator": ">=", "value": 21}
            ],
            "dialect": "oracle"
        }

        state = QueryState.from_dict(data)

        assert state.table == "customers"
        assert state.columns == ["id", "name", "email"]
        assert len(state.filters) == 2
        assert state.filters[0].column == "status"
        assert state.filters[1].column == "age"
        assert state.dialect == "oracle"

    def test_from_dict_empty_state(self):
        """Test deserialization of empty query state."""
        data = {"dialect": "generic"}
        state = QueryState.from_dict(data)

        assert state.table is None
        assert state.columns == []
        assert state.filters == []
        assert state.dialect == "generic"

    def test_serialization_round_trip(self):
        """Test that serialization and deserialization preserve state."""
        original = QueryState(dialect="postgresql")
        original.add_table("orders")
        original.add_column("id")
        original.add_column("total")
        f1 = Filter(column="status", operator="=", value="paid")
        f2 = Filter(column="total", operator=">", value=100)
        original.add_filter(f1)
        original.add_filter(f2)

        # Serialize and deserialize
        data = original.to_dict()
        restored = QueryState.from_dict(data)

        # Compare
        assert restored.table == original.table
        assert restored.columns == original.columns
        assert restored.dialect == original.dialect
        assert len(restored.filters) == len(original.filters)
        for i, f in enumerate(original.filters):
            assert restored.filters[i].column == f.column
            assert restored.filters[i].operator == f.operator
            assert restored.filters[i].value == f.value

    def test_str_complete_state(self):
        """Test string representation with complete state."""
        state = QueryState(dialect="postgresql")
        state.add_table("users")
        state.add_column("id")
        state.add_column("name")
        f = Filter(column="age", operator=">", value=18)
        state.add_filter(f)

        result = str(state)
        assert "FROM users" in result
        assert "SELECT 2 columns" in result
        assert "WHERE 1 filters" in result
        assert "(postgresql)" in result

    def test_str_empty_columns(self):
        """Test string representation with no columns (SELECT *)."""
        state = QueryState()
        state.add_table("products")

        result = str(state)
        assert "SELECT *" in result

    def test_str_no_filters(self):
        """Test string representation with no filters."""
        state = QueryState()
        state.add_table("items")

        result = str(state)
        assert "WHERE" not in result

    def test_repr(self):
        """Test detailed representation."""
        state = QueryState(dialect="oracle")
        state.add_table("test")

        result = repr(state)
        assert "QueryState(" in result
        assert "table='test'" in result
        assert "dialect='oracle'" in result


# Fixtures for reusable test data
@pytest.fixture
def sample_columns():
    """Provide sample columns for tests."""
    return [
        Column(name="id", data_type="INTEGER"),
        Column(name="name", data_type="VARCHAR(100)"),
        Column(name="email", data_type="VARCHAR(255)")
    ]


@pytest.fixture
def sample_table(sample_columns):
    """Provide a sample table with columns."""
    return Table(name="users", columns=sample_columns)


@pytest.fixture
def sample_filters():
    """Provide sample filters for tests."""
    return [
        Filter(column="age", operator=">", value=18),
        Filter(column="status", operator="=", value="active"),
        Filter(column="deleted_at", operator="IS NULL")
    ]


@pytest.fixture
def sample_query_state(sample_filters):
    """Provide a sample query state."""
    state = QueryState(dialect="postgresql")
    state.add_table("users")
    state.add_column("id")
    state.add_column("name")
    for f in sample_filters:
        state.add_filter(f)
    return state
