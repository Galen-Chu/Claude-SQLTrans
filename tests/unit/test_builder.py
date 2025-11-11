"""Unit tests for SQL QueryBuilder."""

import pytest
from sqltrans.models.query import QueryState
from sqltrans.models.filters import Filter
from sqltrans.sql.builder import QueryBuilder
from sqltrans.sql.dialects.postgresql import PostgreSQLDialect
from sqltrans.sql.dialects.oracle import OracleDialect
from sqltrans.sql.dialects.generic import GenericDialect


class TestQueryBuilderBasic:
    """Basic tests for QueryBuilder."""

    @pytest.fixture
    def postgresql_dialect(self):
        """Provide PostgreSQL dialect."""
        return PostgreSQLDialect()

    @pytest.fixture
    def state_with_table(self):
        """Provide query state with table."""
        state = QueryState()
        state.add_table("users")
        return state

    def test_builder_creation(self, state_with_table, postgresql_dialect):
        """Test creating QueryBuilder instance."""
        builder = QueryBuilder(state_with_table, postgresql_dialect)
        assert builder.state == state_with_table
        assert builder.dialect == postgresql_dialect

    def test_build_select_with_columns(self, state_with_table, postgresql_dialect):
        """Test building SELECT clause with specific columns."""
        state_with_table.add_column("id")
        state_with_table.add_column("name")
        builder = QueryBuilder(state_with_table, postgresql_dialect)

        result = builder.build_select()
        assert result == 'SELECT "id", "name"'

    def test_build_select_no_columns(self, state_with_table, postgresql_dialect):
        """Test building SELECT clause with no columns (SELECT *)."""
        builder = QueryBuilder(state_with_table, postgresql_dialect)

        result = builder.build_select()
        assert result == "SELECT *"

    def test_build_select_single_column(self, state_with_table, postgresql_dialect):
        """Test building SELECT clause with single column."""
        state_with_table.add_column("email")
        builder = QueryBuilder(state_with_table, postgresql_dialect)

        result = builder.build_select()
        assert result == 'SELECT "email"'

    def test_build_from_with_table(self, state_with_table, postgresql_dialect):
        """Test building FROM clause."""
        builder = QueryBuilder(state_with_table, postgresql_dialect)

        result = builder.build_from()
        assert result == 'FROM "users"'

    def test_build_from_without_table_raises_error(self, postgresql_dialect):
        """Test that building FROM without table raises error."""
        state = QueryState()
        builder = QueryBuilder(state, postgresql_dialect)

        with pytest.raises(ValueError) as exc_info:
            builder.build_from()

        assert "without a table" in str(exc_info.value).lower()

    def test_build_where_with_filters(self, state_with_table, postgresql_dialect):
        """Test building WHERE clause with filters."""
        f1 = Filter("age", ">", 18)
        f2 = Filter("status", "=", "active")
        state_with_table.add_filter(f1)
        state_with_table.add_filter(f2)

        builder = QueryBuilder(state_with_table, postgresql_dialect)
        result = builder.build_where()

        assert result.startswith("WHERE")
        assert '"age" > 18' in result
        assert '"status" = \'active\'' in result
        assert " AND " in result

    def test_build_where_no_filters(self, state_with_table, postgresql_dialect):
        """Test building WHERE clause with no filters returns empty string."""
        builder = QueryBuilder(state_with_table, postgresql_dialect)

        result = builder.build_where()
        assert result == ""

    def test_build_where_single_filter(self, state_with_table, postgresql_dialect):
        """Test building WHERE clause with single filter."""
        f = Filter("email", "IS NOT NULL")
        state_with_table.add_filter(f)

        builder = QueryBuilder(state_with_table, postgresql_dialect)
        result = builder.build_where()

        assert result == 'WHERE "email" IS NOT NULL'

    def test_build_query_complete(self, state_with_table, postgresql_dialect):
        """Test building complete query with SELECT, FROM, WHERE."""
        state_with_table.add_column("id")
        state_with_table.add_column("name")
        f = Filter("age", ">=", 21)
        state_with_table.add_filter(f)

        builder = QueryBuilder(state_with_table, postgresql_dialect)
        result = builder.build_query()

        assert 'SELECT "id", "name"' in result
        assert 'FROM "users"' in result
        assert 'WHERE "age" >= 21' in result

    def test_build_query_without_filters(self, state_with_table, postgresql_dialect):
        """Test building query without WHERE clause."""
        state_with_table.add_column("id")

        builder = QueryBuilder(state_with_table, postgresql_dialect)
        result = builder.build_query()

        assert result == 'SELECT "id" FROM "users"'
        assert "WHERE" not in result

    def test_build_query_select_star(self, state_with_table, postgresql_dialect):
        """Test building query with SELECT *."""
        builder = QueryBuilder(state_with_table, postgresql_dialect)
        result = builder.build_query()

        assert result == 'SELECT * FROM "users"'

    def test_build_query_without_table_raises_error(self, postgresql_dialect):
        """Test that building query without table raises error."""
        state = QueryState()
        state.add_column("id")

        builder = QueryBuilder(state, postgresql_dialect)

        with pytest.raises(ValueError) as exc_info:
            builder.build_query()

        assert "without a table" in str(exc_info.value).lower()


class TestQueryBuilderDialects:
    """Test QueryBuilder with different SQL dialects."""

    @pytest.fixture
    def base_state(self):
        """Provide basic query state."""
        state = QueryState()
        state.add_table("customers")
        state.add_column("customer_id")
        state.add_column("email")
        f = Filter("status", "=", "active")
        state.add_filter(f)
        return state

    def test_postgresql_query(self, base_state):
        """Test query generation for PostgreSQL."""
        dialect = PostgreSQLDialect()
        builder = QueryBuilder(base_state, dialect)
        result = builder.build_query()

        assert 'SELECT "customer_id", "email"' in result
        assert 'FROM "customers"' in result
        assert '"status" = \'active\'' in result

    def test_oracle_query(self, base_state):
        """Test query generation for Oracle."""
        dialect = OracleDialect()
        builder = QueryBuilder(base_state, dialect)
        result = builder.build_query()

        assert 'SELECT "customer_id", "email"' in result
        assert 'FROM "customers"' in result
        assert '"status" = \'active\'' in result

    def test_generic_query(self, base_state):
        """Test query generation for Generic SQL."""
        dialect = GenericDialect()
        builder = QueryBuilder(base_state, dialect)
        result = builder.build_query()

        assert 'SELECT "customer_id", "email"' in result
        assert 'FROM "customers"' in result
        assert '"status" = \'active\'' in result


class TestQueryBuilderFilters:
    """Test QueryBuilder with various filter types."""

    @pytest.fixture
    def state(self):
        """Provide query state with table."""
        state = QueryState()
        state.add_table("orders")
        return state

    @pytest.fixture
    def dialect(self):
        """Provide PostgreSQL dialect."""
        return PostgreSQLDialect()

    def test_filter_with_string_value(self, state, dialect):
        """Test filter with string value."""
        f = Filter("customer_name", "=", "John Doe")
        state.add_filter(f)

        builder = QueryBuilder(state, dialect)
        result = builder.build_query()

        assert '"customer_name" = \'John Doe\'' in result

    def test_filter_with_number_value(self, state, dialect):
        """Test filter with numeric value."""
        f = Filter("total", ">", 100)
        state.add_filter(f)

        builder = QueryBuilder(state, dialect)
        result = builder.build_query()

        assert '"total" > 100' in result

    def test_filter_with_float_value(self, state, dialect):
        """Test filter with float value."""
        f = Filter("price", "<=", 99.99)
        state.add_filter(f)

        builder = QueryBuilder(state, dialect)
        result = builder.build_query()

        assert '"price" <= 99.99' in result

    def test_filter_is_null(self, state, dialect):
        """Test IS NULL filter."""
        f = Filter("deleted_at", "IS NULL")
        state.add_filter(f)

        builder = QueryBuilder(state, dialect)
        result = builder.build_query()

        assert '"deleted_at" IS NULL' in result

    def test_filter_is_not_null(self, state, dialect):
        """Test IS NOT NULL filter."""
        f = Filter("confirmed_at", "IS NOT NULL")
        state.add_filter(f)

        builder = QueryBuilder(state, dialect)
        result = builder.build_query()

        assert '"confirmed_at" IS NOT NULL' in result

    def test_filter_like(self, state, dialect):
        """Test LIKE filter."""
        f = Filter("email", "LIKE", "%@example.com")
        state.add_filter(f)

        builder = QueryBuilder(state, dialect)
        result = builder.build_query()

        assert '"email" LIKE \'%@example.com\'' in result

    def test_filter_in_with_strings(self, state, dialect):
        """Test IN filter with string values."""
        f = Filter("status", "IN", ["pending", "processing", "completed"])
        state.add_filter(f)

        builder = QueryBuilder(state, dialect)
        result = builder.build_query()

        assert '"status" IN' in result
        assert "'pending'" in result
        assert "'processing'" in result
        assert "'completed'" in result

    def test_filter_in_with_numbers(self, state, dialect):
        """Test IN filter with numeric values."""
        f = Filter("id", "IN", [1, 2, 3, 5, 8])
        state.add_filter(f)

        builder = QueryBuilder(state, dialect)
        result = builder.build_query()

        assert '"id" IN (1, 2, 3, 5, 8)' in result

    def test_multiple_filters_and_combination(self, state, dialect):
        """Test multiple filters combined with AND."""
        f1 = Filter("status", "=", "active")
        f2 = Filter("total", ">", 50)
        f3 = Filter("deleted_at", "IS NULL")
        state.add_filter(f1)
        state.add_filter(f2)
        state.add_filter(f3)

        builder = QueryBuilder(state, dialect)
        result = builder.build_query()

        # Check all conditions are present
        assert '"status" = \'active\'' in result
        assert '"total" > 50' in result
        assert '"deleted_at" IS NULL' in result
        # Check AND connectors (should be 2 for 3 conditions)
        assert result.count(" AND ") == 2


class TestQueryBuilderEdgeCases:
    """Test QueryBuilder with edge cases and special scenarios."""

    def test_table_name_with_special_characters(self):
        """Test table name with spaces (requires quoting)."""
        state = QueryState()
        state.add_table("user orders")  # Space in name
        dialect = PostgreSQLDialect()

        builder = QueryBuilder(state, dialect)
        result = builder.build_query()

        assert '"user orders"' in result

    def test_column_name_with_special_characters(self):
        """Test column name with special characters."""
        state = QueryState()
        state.add_table("items")
        state.add_column("item-id")  # Hyphen in name

        dialect = PostgreSQLDialect()
        builder = QueryBuilder(state, dialect)
        result = builder.build_query()

        assert '"item-id"' in result

    def test_string_value_with_quotes(self):
        """Test string value containing single quotes."""
        state = QueryState()
        state.add_table("users")
        f = Filter("name", "=", "O'Brien")  # Quote in value
        state.add_filter(f)

        dialect = PostgreSQLDialect()
        builder = QueryBuilder(state, dialect)
        result = builder.build_query()

        # Single quote should be escaped
        assert "O''Brien" in result

    def test_sql_injection_in_filter_value_prevented(self):
        """Test that SQL injection in filter values is prevented."""
        state = QueryState()
        state.add_table("users")
        # Attempted SQL injection
        f = Filter("username", "=", "admin' OR '1'='1")
        state.add_filter(f)

        dialect = PostgreSQLDialect()
        builder = QueryBuilder(state, dialect)
        result = builder.build_query()

        # The injection should be escaped
        assert "admin'' OR ''1''=''1" in result

    def test_many_columns(self):
        """Test query with many columns."""
        state = QueryState()
        state.add_table("data")
        for i in range(20):
            state.add_column(f"col{i}")

        dialect = GenericDialect()
        builder = QueryBuilder(state, dialect)
        result = builder.build_query()

        # Check all columns are present
        for i in range(20):
            assert f'"col{i}"' in result

    def test_many_filters(self):
        """Test query with many filters."""
        state = QueryState()
        state.add_table("logs")
        for i in range(10):
            f = Filter(f"field{i}", "=", f"value{i}")
            state.add_filter(f)

        dialect = GenericDialect()
        builder = QueryBuilder(state, dialect)
        result = builder.build_query()

        # Check all filters are present
        for i in range(10):
            assert f'"field{i}"' in result
            assert f"'value{i}'" in result
        # Check AND count (should be 9 for 10 filters)
        assert result.count(" AND ") == 9

    def test_repr(self):
        """Test __repr__ method."""
        state = QueryState()
        state.add_table("test")
        dialect = GenericDialect()

        builder = QueryBuilder(state, dialect)
        result = repr(builder)

        assert "QueryBuilder" in result


# Integration-like tests with realistic scenarios
class TestQueryBuilderRealisticScenarios:
    """Test QueryBuilder with realistic query scenarios."""

    def test_user_lookup_by_email(self):
        """Test realistic user lookup query."""
        state = QueryState()
        state.add_table("users")
        state.add_column("id")
        state.add_column("username")
        state.add_column("email")
        state.add_column("created_at")
        f = Filter("email", "=", "user@example.com")
        state.add_filter(f)

        builder = QueryBuilder(state, PostgreSQLDialect())
        result = builder.build_query()

        expected_parts = [
            'SELECT "id", "username", "email", "created_at"',
            'FROM "users"',
            'WHERE "email" = \'user@example.com\''
        ]
        for part in expected_parts:
            assert part in result

    def test_order_search_with_multiple_conditions(self):
        """Test order search with multiple conditions."""
        state = QueryState()
        state.add_table("orders")
        state.add_column("order_id")
        state.add_column("customer_name")
        state.add_column("total")
        state.add_column("status")

        f1 = Filter("status", "IN", ["pending", "processing"])
        f2 = Filter("total", ">", 100)
        f3 = Filter("deleted_at", "IS NULL")
        state.add_filter(f1)
        state.add_filter(f2)
        state.add_filter(f3)

        builder = QueryBuilder(state, PostgreSQLDialect())
        result = builder.build_query()

        assert 'SELECT "order_id", "customer_name", "total", "status"' in result
        assert 'FROM "orders"' in result
        assert '"status" IN' in result
        assert '"total" > 100' in result
        assert '"deleted_at" IS NULL' in result

    def test_all_active_records(self):
        """Test selecting all columns from active records."""
        state = QueryState()
        state.add_table("products")
        # No columns = SELECT *
        f = Filter("active", "=", "true")
        state.add_filter(f)

        builder = QueryBuilder(state, OracleDialect())
        result = builder.build_query()

        assert result == 'SELECT * FROM "products" WHERE "active" = \'true\''
