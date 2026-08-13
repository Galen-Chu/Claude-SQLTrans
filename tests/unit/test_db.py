"""Tests for the DB layer (introspection + read-only execution).

Uses an in-memory SQLite database so no external server is needed. SQLite is a
real RDBMS: SQLAlchemy introspection, query execution, and the AST read-only
policy all behave here as they would against Postgres/MySQL.
"""

import pytest
from sqlalchemy import create_engine, text

from sqltrans.db import (
    DEFAULT_ROW_LIMIT,
    execute_read_only,
    introspect,
    render_schema_for_prompt,
)
from sqltrans.sql.transpiler import UnsafeQueryError


@pytest.fixture()
def sample_db():
    """A fresh in-memory DB with users + orders and a few rows."""
    engine = create_engine("sqlite:///:memory:")
    with engine.begin() as conn:
        conn.execute(
            text(
                "CREATE TABLE users ("
                "id INTEGER PRIMARY KEY, email TEXT NOT NULL, created_at TEXT)"
            )
        )
        conn.execute(
            text(
                "CREATE TABLE orders ("
                "id INTEGER PRIMARY KEY, user_id INTEGER, total REAL)"
            )
        )
        conn.execute(
            text(
                "INSERT INTO users (id, email) VALUES "
                "(1, 'a@b.com'), (2, 'c@d.com')"
            )
        )
        conn.execute(
            text(
                "INSERT INTO orders (user_id, total) VALUES "
                "(1, 10.0), (1, 20.0), (2, 5.0)"
            )
        )
    return engine


# --------------------------------------------------------------------------- #
# Introspection
# --------------------------------------------------------------------------- #


class TestIntrospection:
    def test_lists_tables(self, sample_db):
        names = {t.name for t in introspect(sample_db)}
        assert names == {"users", "orders"}

    def test_columns_include_type_and_nullability(self, sample_db):
        tables = {t.name: t for t in introspect(sample_db)}
        email = next(c for c in tables["users"].columns if c.name == "email")
        assert email.nullable is False
        assert "TEXT" in email.type

    def test_render_for_prompt(self, sample_db):
        rendered = render_schema_for_prompt(introspect(sample_db))
        assert "users" in rendered
        assert "email" in rendered
        assert rendered.startswith("Schema (table: columns)")

    def test_render_empty(self):
        assert render_schema_for_prompt([]) == ""


# --------------------------------------------------------------------------- #
# Read-only execution
# --------------------------------------------------------------------------- #


class TestExecuteReadOnly:
    def test_select_returns_rows(self, sample_db):
        result = execute_read_only(
            sample_db, "SELECT id, email FROM users ORDER BY id", dialect="sqlite"
        )
        assert result.columns == ["id", "email"]
        assert result.rows == [[1, "a@b.com"], [2, "c@d.com"]]
        assert result.truncated is False
        assert result.row_count == 2

    def test_aggregation(self, sample_db):
        result = execute_read_only(
            sample_db,
            "SELECT user_id, SUM(total) AS s FROM orders GROUP BY user_id ORDER BY user_id",
            dialect="sqlite",
        )
        assert result.rows == [[1, 30.0], [2, 5.0]]

    def test_join(self, sample_db):
        result = execute_read_only(
            sample_db,
            "SELECT u.email, o.total FROM users u JOIN orders o ON u.id = o.user_id "
            "ORDER BY o.id",
            dialect="sqlite",
        )
        assert result.row_count == 3
        assert result.rows[0] == ["a@b.com", 10.0]

    def test_row_limit_truncates(self, sample_db):
        result = execute_read_only(
            sample_db, "SELECT * FROM orders", dialect="sqlite", row_limit=2
        )
        assert result.row_count == 2
        assert result.truncated is True

    def test_default_row_limit_constant(self):
        assert DEFAULT_ROW_LIMIT == 1000

    def test_non_positive_row_limit_rejected(self, sample_db):
        with pytest.raises(ValueError):
            execute_read_only(sample_db, "SELECT 1", dialect="sqlite", row_limit=0)


# --------------------------------------------------------------------------- #
# Read-only enforcement at the DB layer
# --------------------------------------------------------------------------- #


WRITE_STATEMENTS = [
    "DELETE FROM users",
    "UPDATE users SET email = 'x'",
    "INSERT INTO users (id, email) VALUES (3, 'z@z.com')",
    "DROP TABLE users",
    "CREATE TABLE evil (x INTEGER)",
    "SELECT * INTO archive FROM users",
]


@pytest.mark.parametrize("sql", WRITE_STATEMENTS)
def test_write_statements_rejected_before_execution(sample_db, sql):
    # Policy gate runs before any connection is opened, so even a statement that
    # SQLite would happily execute (INSERT/DELETE) is refused.
    with pytest.raises(UnsafeQueryError):
        execute_read_only(sample_db, sql, dialect="sqlite")


def test_multistatement_rejected(sample_db):
    with pytest.raises(UnsafeQueryError):
        execute_read_only(
            sample_db,
            "SELECT 1; DROP TABLE users;",
            dialect="sqlite",
        )


def test_validated_then_executed_in_one_call(sample_db):
    # A legit SELECT is both validated and executed by the single entry point.
    result = execute_read_only(
        sample_db, "SELECT COUNT(*) FROM users", dialect="sqlite"
    )
    assert result.rows == [[2]]
