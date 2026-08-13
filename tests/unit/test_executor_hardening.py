"""Tests for read-only execution hardening: row cap, offset, cache, rejection."""

import pytest
from sqlalchemy import text

from sqltrans.db import clear_result_cache, execute_read_only, get_engine
from sqltrans.sql.transpiler import UnsafeQueryError


@pytest.fixture
def engine(tmp_path):
    url = f"sqlite:///{tmp_path / 't.db'}"
    eng = get_engine(url)
    with eng.connect() as conn:
        conn.execute(text("CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT)"))
        for i in range(10):
            conn.execute(
                text("INSERT INTO users (id, name) VALUES (:i, :n)"),
                {"i": i, "n": f"u{i}"},
            )
        conn.commit()
    yield eng


def test_row_limit_truncation(engine):
    clear_result_cache()
    r = execute_read_only(
        engine, "SELECT * FROM users ORDER BY id", row_limit=5, use_cache=False
    )
    assert r.row_count == 5
    assert r.truncated is True
    assert r.columns == ["id", "name"]


def test_offset_pagination(engine):
    clear_result_cache()
    r = execute_read_only(
        engine, "SELECT * FROM users ORDER BY id", row_limit=5, offset=3, use_cache=False
    )
    assert r.row_count == 5
    # skipped ids 0,1,2 -> first returned id is 3
    assert r.rows[0][0] == 3


def test_result_cache_hit(engine):
    clear_result_cache()
    sql = "SELECT * FROM users ORDER BY id"
    r1 = execute_read_only(engine, sql, row_limit=100, use_cache=True)
    r2 = execute_read_only(engine, sql, row_limit=100, use_cache=True)
    assert r1.rows == r2.rows
    assert r2.row_count == 10


def test_rejects_write(engine):
    clear_result_cache()
    with pytest.raises(UnsafeQueryError):
        execute_read_only(engine, "DELETE FROM users", use_cache=False)


def test_statement_timeout_noop_on_sqlite(engine):
    # sqlite has no statement_timeout mapping; the call must still succeed.
    clear_result_cache()
    r = execute_read_only(
        engine, "SELECT COUNT(*) FROM users", statement_timeout_ms=1000
    )
    assert r.rows[0][0] == 10
