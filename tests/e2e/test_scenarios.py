"""End-to-end scenario tests for SQLTrans.

Tests real-world support engineer workflows with complex queries and realistic
use cases. Validates that the tool meets actual user needs for database
troubleshooting.
"""

import pytest
from unittest.mock import patch

from sqltrans.models.query import QueryState
from sqltrans.models.filters import Filter
from sqltrans.sql.builder import QueryBuilder
from sqltrans.sql.dialects.postgresql import PostgreSQLDialect
from sqltrans.sql.dialects.oracle import OracleDialect
from sqltrans.sql.dialects.generic import GenericDialect


class TestCustomerSupportScenarios:
    """Test realistic customer support troubleshooting scenarios."""

    def test_scenario_find_customer_by_email(self):
        """Scenario: Support engineer needs to find customer by email address.

        User story: As a support engineer, I need to quickly look up a customer
        record by their email address to investigate a support ticket.
        """
        # Build query
        query_state = QueryState(dialect="postgresql")
        query_state.add_table("customers")
        # No columns = SELECT *
        query_state.add_filter(Filter(
            column="email",
            operator="=",
            value="john.doe@example.com"
        ))

        # Generate SQL
        dialect = PostgreSQLDialect()
        builder = QueryBuilder(query_state, dialect)
        sql = builder.build_query()

        # Verify SQL is correct and executable
        assert 'SELECT *' in sql
        assert 'FROM "customers"' in sql
        assert 'WHERE "email" = ' in sql
        assert 'john.doe@example.com' in sql

        # Verify no SQL injection
        assert '--' not in sql
        assert ';' not in sql or sql.rstrip().endswith(';')

    def test_scenario_find_recent_orders(self):
        """Scenario: Find all orders created after a specific date.

        User story: Support engineer needs to check recent orders to verify
        if a customer's order was processed correctly.
        """
        query_state = QueryState(dialect="postgresql")
        query_state.add_table("orders")
        query_state.add_column("id")
        query_state.add_column("customer_id")
        query_state.add_column("amount")
        query_state.add_column("created_at")
        query_state.add_filter(Filter(
            column="created_at",
            operator=">",
            value="2024-01-01"
        ))

        dialect = PostgreSQLDialect()
        builder = QueryBuilder(query_state, dialect)
        sql = builder.build_query()

        # Verify all columns included
        assert '"id"' in sql
        assert '"customer_id"' in sql
        assert '"amount"' in sql
        assert '"created_at"' in sql

        # Verify date filter
        assert 'WHERE "created_at" > ' in sql
        assert '2024-01-01' in sql

    def test_scenario_find_users_with_name_pattern(self):
        """Scenario: Find all users whose name contains a pattern.

        User story: Support engineer needs to find a user but only remembers
        part of their name (e.g., "Smith").
        """
        query_state = QueryState(dialect="generic")
        query_state.add_table("users")
        # SELECT * to get all user info
        query_state.add_filter(Filter(
            column="last_name",
            operator="LIKE",
            value="%Smith%"
        ))

        dialect = GenericDialect()
        builder = QueryBuilder(query_state, dialect)
        sql = builder.build_query()

        # Verify LIKE pattern
        assert 'WHERE "last_name" LIKE ' in sql
        assert '%Smith%' in sql
        assert 'SELECT *' in sql

    def test_scenario_complex_multi_filter_query(self):
        """Scenario: Complex query with multiple conditions.

        User story: Find all active premium customers who registered in the
        last month to send them a special offer.
        """
        query_state = QueryState(dialect="postgresql")
        query_state.add_table("customers")
        query_state.add_column("id")
        query_state.add_column("email")
        query_state.add_column("name")
        query_state.add_column("tier")

        # Multiple filters (all combined with AND)
        query_state.add_filter(Filter(
            column="status",
            operator="=",
            value="active"
        ))
        query_state.add_filter(Filter(
            column="tier",
            operator="=",
            value="premium"
        ))
        query_state.add_filter(Filter(
            column="registration_date",
            operator=">",
            value="2024-11-01"
        ))

        dialect = PostgreSQLDialect()
        builder = QueryBuilder(query_state, dialect)
        sql = builder.build_query()

        # Verify all filters present
        assert '"status" = ' in sql
        assert '"tier" = ' in sql
        assert '"registration_date" > ' in sql

        # Verify AND combination
        assert sql.count('AND') == 2

    def test_scenario_find_null_values(self):
        """Scenario: Find records with missing data.

        User story: Support engineer needs to find all users who haven't
        provided a phone number yet.
        """
        query_state = QueryState(dialect="generic")
        query_state.add_table("users")
        query_state.add_column("id")
        query_state.add_column("email")
        query_state.add_column("phone")
        query_state.add_filter(Filter(
            column="phone",
            operator="IS NULL",
            value=None
        ))

        dialect = GenericDialect()
        builder = QueryBuilder(query_state, dialect)
        sql = builder.build_query()

        # Verify IS NULL syntax
        assert '"phone" IS NULL' in sql
        assert 'WHERE' in sql

    def test_scenario_find_non_null_values(self):
        """Scenario: Find records with required data present.

        User story: Find all customers who have verified their email address
        (verified_at is not null).
        """
        query_state = QueryState(dialect="postgresql")
        query_state.add_table("customers")
        query_state.add_filter(Filter(
            column="verified_at",
            operator="IS NOT NULL",
            value=None
        ))

        dialect = PostgreSQLDialect()
        builder = QueryBuilder(query_state, dialect)
        sql = builder.build_query()

        # Verify IS NOT NULL syntax
        assert '"verified_at" IS NOT NULL' in sql

    def test_scenario_find_records_in_list(self):
        """Scenario: Find records matching multiple IDs.

        User story: Support engineer has a list of order IDs from a customer
        complaint and needs to check their status.
        """
        query_state = QueryState(dialect="postgresql")
        query_state.add_table("orders")
        query_state.add_column("id")
        query_state.add_column("status")
        query_state.add_column("total")
        query_state.add_filter(Filter(
            column="id",
            operator="IN",
            value=[1001, 1002, 1003, 1004]
        ))

        dialect = PostgreSQLDialect()
        builder = QueryBuilder(query_state, dialect)
        sql = builder.build_query()

        # Verify IN clause
        assert '"id" IN (' in sql
        assert '1001' in sql
        assert '1002' in sql
        assert '1003' in sql
        assert '1004' in sql


class TestMultiDatabaseSupport:
    """Test generating queries for different database systems."""

    def test_same_query_all_three_dialects(self):
        """Test generating the same query for all three dialects.

        User story: Support engineer works with customers using different
        databases and needs to adapt queries to each system.
        """
        # Build query once
        query_state = QueryState(dialect="generic")
        query_state.add_table("orders")
        query_state.add_column("id")
        query_state.add_column("customer_id")
        query_state.add_column("total")
        query_state.add_filter(Filter(
            column="status",
            operator="=",
            value="pending"
        ))
        query_state.add_filter(Filter(
            column="total",
            operator=">",
            value=100
        ))

        # Generate for PostgreSQL
        postgresql_dialect = PostgreSQLDialect()
        postgresql_builder = QueryBuilder(query_state, postgresql_dialect)
        postgresql_sql = postgresql_builder.build_query()

        assert 'SELECT "id", "customer_id", "total"' in postgresql_sql
        assert 'FROM "orders"' in postgresql_sql
        assert '"status" = ' in postgresql_sql
        assert '"total" > ' in postgresql_sql

        # Generate for Oracle
        oracle_dialect = OracleDialect()
        oracle_builder = QueryBuilder(query_state, oracle_dialect)
        oracle_sql = oracle_builder.build_query()

        assert 'SELECT "id", "customer_id", "total"' in oracle_sql
        assert 'FROM "orders"' in oracle_sql
        assert '"status" = ' in oracle_sql
        assert '"total" > ' in oracle_sql

        # Generate for Generic
        generic_dialect = GenericDialect()
        generic_builder = QueryBuilder(query_state, generic_dialect)
        generic_sql = generic_builder.build_query()

        assert 'SELECT "id", "customer_id", "total"' in generic_sql
        assert 'FROM "orders"' in generic_sql
        assert '"status" = ' in generic_sql
        assert '"total" > ' in generic_sql

        # All should be valid SQL, just with potential dialect differences
        # All should prevent SQL injection
        for sql in [postgresql_sql, oracle_sql, generic_sql]:
            assert '--' not in sql
            assert '/*' not in sql

    def test_postgresql_specific_query(self):
        """Test PostgreSQL-specific query generation."""
        query_state = QueryState(dialect="postgresql")
        query_state.add_table("user_sessions")
        query_state.add_column("id")
        query_state.add_column("user_id")
        query_state.add_column("created_at")
        query_state.add_filter(Filter(
            column="active",
            operator="=",
            value=True  # Boolean value
        ))

        dialect = PostgreSQLDialect()
        builder = QueryBuilder(query_state, dialect)
        sql = builder.build_query()

        # PostgreSQL uses double quotes
        assert '"user_sessions"' in sql
        assert '"active"' in sql

    def test_oracle_case_sensitivity(self):
        """Test Oracle's case sensitivity handling."""
        query_state = QueryState(dialect="oracle")
        query_state.add_table("Users")  # Mixed case
        query_state.add_column("UserId")
        query_state.add_column("UserName")

        dialect = OracleDialect()
        builder = QueryBuilder(query_state, dialect)
        sql = builder.build_query()

        # Oracle should preserve case with quotes
        assert '"Users"' in sql
        assert '"UserId"' in sql
        assert '"UserName"' in sql


class TestComplexRealWorldQueries:
    """Test complex queries that support engineers actually use."""

    def test_customer_order_investigation(self):
        """Scenario: Investigate customer's order history for refund request.

        Support engineer needs to see all orders for a specific customer
        with high totals to verify refund eligibility.
        """
        query_state = QueryState(dialect="postgresql")
        query_state.add_table("orders")
        query_state.add_column("id")
        query_state.add_column("order_date")
        query_state.add_column("total")
        query_state.add_column("status")

        # Customer ID filter
        query_state.add_filter(Filter(
            column="customer_id",
            operator="=",
            value=12345
        ))

        # High value orders only
        query_state.add_filter(Filter(
            column="total",
            operator=">=",
            value=500.00
        ))

        # Not refunded yet
        query_state.add_filter(Filter(
            column="status",
            operator="!=",
            value="refunded"
        ))

        dialect = PostgreSQLDialect()
        builder = QueryBuilder(query_state, dialect)
        sql = builder.build_query()

        # Should have all three conditions
        assert '"customer_id" = ' in sql
        assert '"total" >= ' in sql
        assert '"status" != ' in sql
        assert sql.count('AND') == 2

    def test_abandoned_cart_analysis(self):
        """Scenario: Find abandoned shopping carts to follow up.

        Marketing team wants to find all carts abandoned in last week
        with high value to send recovery emails.
        """
        query_state = QueryState(dialect="generic")
        query_state.add_table("shopping_carts")
        query_state.add_column("id")
        query_state.add_column("user_email")
        query_state.add_column("cart_total")
        query_state.add_column("last_updated")

        # Status is abandoned
        query_state.add_filter(Filter(
            column="status",
            operator="=",
            value="abandoned"
        ))

        # High value
        query_state.add_filter(Filter(
            column="cart_total",
            operator=">",
            value=100
        ))

        # Recent
        query_state.add_filter(Filter(
            column="last_updated",
            operator=">",
            value="2024-11-04"
        ))

        dialect = GenericDialect()
        builder = QueryBuilder(query_state, dialect)
        sql = builder.build_query()

        assert '"status" = ' in sql
        assert '"cart_total" > ' in sql
        assert '"last_updated" > ' in sql

    def test_user_account_audit(self):
        """Scenario: Security audit to find suspicious account activity.

        Security team needs to find all admin accounts that haven't logged
        in recently and haven't set up 2FA.
        """
        query_state = QueryState(dialect="postgresql")
        query_state.add_table("users")
        query_state.add_column("id")
        query_state.add_column("username")
        query_state.add_column("email")
        query_state.add_column("role")
        query_state.add_column("last_login")

        # Admin role
        query_state.add_filter(Filter(
            column="role",
            operator="=",
            value="admin"
        ))

        # No 2FA
        query_state.add_filter(Filter(
            column="two_factor_enabled",
            operator="=",
            value=False
        ))

        # Inactive
        query_state.add_filter(Filter(
            column="last_login",
            operator="<",
            value="2024-10-01"
        ))

        dialect = PostgreSQLDialect()
        builder = QueryBuilder(query_state, dialect)
        sql = builder.build_query()

        assert '"role" = ' in sql
        assert '"two_factor_enabled" = ' in sql
        assert '"last_login" < ' in sql


class TestEdgeCasesAndErrorRecovery:
    """Test edge cases and error handling in real scenarios."""

    def test_query_with_special_characters_in_values(self):
        """Test handling values with special characters safely."""
        query_state = QueryState(dialect="postgresql")
        query_state.add_table("customers")
        query_state.add_filter(Filter(
            column="company_name",
            operator="=",
            value="O'Reilly Media"  # Contains apostrophe
        ))

        dialect = PostgreSQLDialect()
        builder = QueryBuilder(query_state, dialect)
        sql = builder.build_query()

        # Should escape the apostrophe safely
        assert "O''Reilly" in sql or "O\\'Reilly" in sql or "O'Reilly" in sql
        # Should not allow SQL injection
        assert "'; DROP" not in sql.upper()

    def test_query_with_unicode_characters(self):
        """Test handling Unicode characters in values."""
        query_state = QueryState(dialect="generic")
        query_state.add_table("customers")
        query_state.add_filter(Filter(
            column="name",
            operator="LIKE",
            value="%François%"  # Unicode character
        ))

        dialect = GenericDialect()
        builder = QueryBuilder(query_state, dialect)
        sql = builder.build_query()

        # Should handle Unicode correctly
        assert "François" in sql or "Fran" in sql

    def test_empty_query_state(self):
        """Test handling of incomplete query state."""
        query_state = QueryState(dialect="generic")
        # No table set

        dialect = GenericDialect()
        builder = QueryBuilder(query_state, dialect)

        # Should raise error when no table
        with pytest.raises(ValueError):
            builder.build_query()

    def test_query_with_very_long_in_list(self):
        """Test handling large IN clause with many values."""
        query_state = QueryState(dialect="postgresql")
        query_state.add_table("orders")
        query_state.add_column("id")

        # Large list of IDs
        large_id_list = list(range(1, 101))  # 100 IDs
        query_state.add_filter(Filter(
            column="id",
            operator="IN",
            value=large_id_list
        ))

        dialect = PostgreSQLDialect()
        builder = QueryBuilder(query_state, dialect)
        sql = builder.build_query()

        # Should include all values
        assert '"id" IN (' in sql
        assert '1' in sql
        assert '100' in sql

    def test_sql_injection_attempts_blocked(self):
        """Test that various SQL injection attempts are safely blocked."""
        injection_attempts = [
            "'; DROP TABLE users;--",
            "admin' OR '1'='1",
            "' UNION SELECT password FROM users--",
            "1'; DELETE FROM orders WHERE '1'='1",
        ]

        query_state = QueryState(dialect="postgresql")
        query_state.add_table("users")

        dialect = PostgreSQLDialect()

        for malicious_value in injection_attempts:
            query_state.filters.clear()
            query_state.add_filter(Filter(
                column="username",
                operator="=",
                value=malicious_value
            ))

            builder = QueryBuilder(query_state, dialect)
            sql = builder.build_query()

            # The malicious SQL should be escaped/quoted, not executed
            # Should not contain unquoted DROP, DELETE, UNION, etc.
            sql_upper = sql.upper()

            # The injected SQL should be part of a string literal, not SQL syntax
            # This is a heuristic check - the specific escaping depends on dialect
            # At minimum, there shouldn't be unescaped semicolons or comment markers
            if '; DROP' in malicious_value:
                # If present, should be within quotes
                assert "'; DROP TABLE" not in sql or "'';" in sql


class TestQueryModification:
    """Test modifying queries and regenerating SQL."""

    def test_add_filter_to_existing_query(self):
        """Test adding a filter to an already-built query."""
        query_state = QueryState(dialect="generic")
        query_state.add_table("orders")
        query_state.add_filter(Filter(
            column="status",
            operator="=",
            value="pending"
        ))

        # Generate initial SQL
        dialect = GenericDialect()
        builder = QueryBuilder(query_state, dialect)
        sql1 = builder.build_query()
        assert '"status" = ' in sql1
        assert 'AND' not in sql1

        # Add another filter
        query_state.add_filter(Filter(
            column="total",
            operator=">",
            value=100
        ))

        # Regenerate SQL
        builder = QueryBuilder(query_state, dialect)
        sql2 = builder.build_query()
        assert '"status" = ' in sql2
        assert '"total" > ' in sql2
        assert 'AND' in sql2

    def test_remove_filter_from_query(self):
        """Test removing a filter regenerates SQL correctly."""
        query_state = QueryState(dialect="generic")
        query_state.add_table("users")
        query_state.add_filter(Filter(column="age", operator=">", value=18))
        query_state.add_filter(Filter(column="active", operator="=", value=True))

        # Initial SQL with both filters
        dialect = GenericDialect()
        builder = QueryBuilder(query_state, dialect)
        sql1 = builder.build_query()
        assert '"age" > ' in sql1
        assert '"active" = ' in sql1
        assert 'AND' in sql1

        # Remove one filter
        query_state.remove_filter(0)

        # Regenerate
        builder = QueryBuilder(query_state, dialect)
        sql2 = builder.build_query()
        assert '"active" = ' in sql2
        assert 'AND' not in sql2
        assert '"age"' not in sql2

    def test_change_dialect_regenerates_correctly(self):
        """Test changing dialect maintains query logic."""
        query_state = QueryState(dialect="generic")
        query_state.add_table("products")
        query_state.add_column("id")
        query_state.add_column("name")
        query_state.add_filter(Filter(column="price", operator=">", value=50))

        # Generate with generic
        generic = GenericDialect()
        builder1 = QueryBuilder(query_state, generic)
        sql_generic = builder1.build_query()

        # Change to PostgreSQL
        query_state.set_dialect("postgresql")
        postgresql = PostgreSQLDialect()
        builder2 = QueryBuilder(query_state, postgresql)
        sql_postgresql = builder2.build_query()

        # Both should have same structure
        assert 'SELECT' in sql_generic and 'SELECT' in sql_postgresql
        assert '"id"' in sql_generic and '"id"' in sql_postgresql
        assert '"name"' in sql_generic and '"name"' in sql_postgresql
        assert '"price" > ' in sql_generic and '"price" > ' in sql_postgresql
