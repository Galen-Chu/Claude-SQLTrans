"""Tests for the v2 sqlglot-backed transpiler and read-only policy."""

import pytest

from sqltrans.sql.transpiler import (
    SUPPORTED_DIALECTS,
    TranspileError,
    UnsafeQueryError,
    enforce_read_only,
    normalize_dialect,
    parse_one_statement,
    transpile,
    validate_read_only,
)


# --------------------------------------------------------------------------- #
# Dialect normalization
# --------------------------------------------------------------------------- #


class TestNormalizeDialect:
    def test_none_passes_through(self):
        assert normalize_dialect(None) is None

    def test_canonical_names(self):
        assert normalize_dialect("postgres") == "postgres"
        assert normalize_dialect("oracle") == "oracle"

    def test_aliases(self):
        assert normalize_dialect("postgresql") == "postgres"
        assert normalize_dialect("PG") == "postgres"
        assert normalize_dialect("mssql") == "tsql"
        assert normalize_dialect("SQLServer") == "tsql"
        assert normalize_dialect("mariadb") == "mysql"

    def test_unknown_raises(self):
        with pytest.raises(ValueError, match="Unknown dialect"):
            normalize_dialect("cobol")


# --------------------------------------------------------------------------- #
# Happy-path transpilation (the actual Oracle -> Postgres value proposition)
# --------------------------------------------------------------------------- #


class TestTranspileHappyPath:
    def test_nvl_becomes_coalesce(self):
        out = transpile(
            "SELECT NVL(manager_id, 0) FROM employees",
            read="oracle",
            write="postgres",
            pretty=False,
        )
        assert "COALESCE(manager_id, 0)" in out
        assert "NVL" not in out

    def test_sysdate_becomes_current_timestamp(self):
        out = transpile(
            "SELECT SYSDATE FROM dual",
            read="oracle",
            write="postgres",
            pretty=False,
        )
        assert "CURRENT_TIMESTAMP" in out

    def test_join_aliases_get_as(self):
        out = transpile(
            "SELECT e.name FROM employees e LEFT JOIN departments d ON e.dept_id = d.id",
            read="oracle",
            write="postgres",
            pretty=False,
        )
        assert "employees AS e" in out
        assert "departments AS d" in out

    def test_dialect_aliases_accepted(self):
        # 'postgresql' must be accepted as an alias for 'postgres'
        out = transpile(
            "SELECT * FROM users WHERE id = 1",
            read="postgresql",
            write="tsql",
            pretty=False,
        )
        assert "SELECT" in out and "FROM users" in out

    def test_pretty_output_is_multiline(self):
        out = transpile(
            "SELECT a, b FROM t WHERE a > 1",
            read="postgres",
            write="postgres",
            pretty=True,
        )
        assert "\n" in out

    def test_no_dialect_uses_default(self):
        # read/write None should still produce valid SQL
        out = transpile("SELECT 1 AS x", pretty=False)
        assert "SELECT" in out


# --------------------------------------------------------------------------- #
# Read-only policy: every write/DDL/DCL/TCL/command shape must be rejected
# --------------------------------------------------------------------------- #


WRITE_STATEMENTS = [
    "INSERT INTO t (a) VALUES (1)",
    "UPDATE t SET a = 1 WHERE id = 2",
    "DELETE FROM t WHERE id = 2",
    "MERGE INTO t USING s ON t.id = s.id WHEN MATCHED THEN UPDATE SET t.a = s.a",
]

DDL_STATEMENTS = [
    "CREATE TABLE t (a int)",
    "DROP TABLE t",
    "ALTER TABLE t ADD COLUMN b int",
    "TRUNCATE TABLE t",
]

DCL_TCL_COMMANDS = [
    "GRANT SELECT ON t TO bob",
    "REVOKE SELECT ON t FROM bob",
    "COMMIT",
    "BEGIN",
    "VACUUM t",
]


@pytest.mark.parametrize("sql", WRITE_STATEMENTS + DDL_STATEMENTS + DCL_TCL_COMMANDS)
def test_write_and_ddl_statements_rejected(sql):
    with pytest.raises(UnsafeQueryError):
        transpile(sql, read="postgres", write="postgres")


class TestReadOnlyPolicy:
    def test_multi_statement_injection_rejected(self):
        # The classic injection vector: a benign SELECT chained to DROP.
        with pytest.raises(UnsafeQueryError, match="one statement"):
            transpile(
                "SELECT * FROM users; DROP TABLE users;",
                read="postgres",
                write="postgres",
            )

    def test_select_into_rejected(self):
        with pytest.raises(UnsafeQueryError, match="INTO"):
            transpile(
                "SELECT * INTO archive FROM users",
                read="postgres",
                write="postgres",
            )

    def test_select_with_subquery_allowed(self):
        # Subqueries, IN, EXISTS are all read-only and must pass.
        sql = "SELECT * FROM orders WHERE user_id IN (SELECT id FROM users WHERE active = 1)"
        out = transpile(sql, read="postgres", write="postgres", pretty=False)
        assert "IN" in out

    def test_cte_allowed(self):
        sql = "WITH active AS (SELECT id FROM users WHERE active = 1) SELECT * FROM active"
        out = transpile(sql, read="postgres", write="postgres", pretty=False)
        assert "WITH" in out

    def test_union_allowed(self):
        out = transpile(
            "SELECT 1 UNION SELECT 2",
            read="postgres",
            write="postgres",
            pretty=False,
        )
        assert "UNION" in out

    def test_validate_returns_ast(self):
        # validate_read_only returns the AST so callers can inspect it
        from sqlglot import exp

        ast = validate_read_only("SELECT 1", dialect="postgres")
        assert isinstance(ast, exp.Select)

    def test_enforce_read_only_idempotent_on_valid(self):
        ast = parse_one_statement("SELECT 1 FROM t", dialect="postgres")
        assert enforce_read_only(ast) is ast


# --------------------------------------------------------------------------- #
# Error handling
# --------------------------------------------------------------------------- #


class TestErrors:
    def test_empty_input(self):
        with pytest.raises(TranspileError, match="empty"):
            transpile("   ", read="postgres", write="postgres")

    def test_unparseable_input(self):
        with pytest.raises(TranspileError):
            transpile("SELECT FROM WHERE", read="postgres", write="postgres")

    def test_validate_can_be_disabled_for_trusted_internal_use(self):
        # validate=False bypasses the policy; documented escape hatch.
        out = transpile(
            "DROP TABLE t",
            read="postgres",
            write="postgres",
            validate=False,
            pretty=False,
        )
        assert "DROP TABLE" in out


# --------------------------------------------------------------------------- #
# Web endpoint (FastAPI TestClient)
# --------------------------------------------------------------------------- #


class TestTranspileEndpoint:
    @pytest.fixture(scope="class")
    def client(self):
        from fastapi.testclient import TestClient

        from sqltrans.web.app import app

        return TestClient(app)

    def test_list_dialects(self, client):
        resp = client.get("/api/transpile/dialects")
        assert resp.status_code == 200
        data = resp.json()
        assert "postgres" in data["dialects"]
        assert "oracle" in data["dialects"]

    def test_transpile_oracle_to_postgres(self, client):
        resp = client.post(
            "/api/transpile",
            json={
                "sql": "SELECT NVL(x, 0) FROM employees",
                "read": "oracle",
                "write": "postgres",
            },
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "COALESCE(x, 0)" in data["sql"]
        assert data["read"] == "oracle"
        assert data["write"] == "postgres"

    def test_rejects_drop_with_400(self, client):
        resp = client.post(
            "/api/transpile",
            json={"sql": "DROP TABLE users", "read": "postgres", "write": "postgres"},
        )
        assert resp.status_code == 400
        assert "not permitted" in resp.json()["detail"]

    def test_rejects_multi_statement_with_400(self, client):
        resp = client.post(
            "/api/transpile",
            json={
                "sql": "SELECT 1; DROP TABLE t;",
                "read": "postgres",
                "write": "postgres",
            },
        )
        assert resp.status_code == 400
        assert "one statement" in resp.json()["detail"]

    def test_unparseable_returns_422(self, client):
        resp = client.post(
            "/api/transpile",
            json={"sql": "SELECT FROM WHERE", "read": "postgres", "write": "postgres"},
        )
        assert resp.status_code == 422
