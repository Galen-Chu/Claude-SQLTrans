"""Tests for the NL→SQL adapter.

The LLM is mocked throughout — these tests verify the *adapter* logic (prompt
assembly, SQL extraction, and the read-only safety gate the draft must pass),
not the model itself. A live end-to-end test against the real Claude API would
run only when ``ANTHROPIC_API_KEY`` is set.
"""

import pytest

from sqltrans.db.introspection import TableSchema, ColumnSchema
from sqltrans.sql.nl2sql import (
    NL2SQLError,
    NL2SQLResult,
    extract_sql,
    nl2sql,
)


class FakeLLM:
    """Fake LLM client returning a canned response, for deterministic tests."""

    def __init__(self, response: str):
        self.response = response
        self.last_system = None
        self.last_user = None

    def complete(self, system, user, *, model, max_tokens):
        self.last_system = system
        self.last_user = user
        return self.response


# --------------------------------------------------------------------------- #
# SQL extraction
# --------------------------------------------------------------------------- #


class TestExtractSql:
    def test_fenced_block(self):
        assert extract_sql("```sql\nSELECT 1\n```") == "SELECT 1"

    def test_fenced_block_after_prose(self):
        out = extract_sql("Here you go:\n```sql\nSELECT id FROM t\n```")
        assert out == "SELECT id FROM t"

    def test_last_fence_wins(self):
        text = "```sql\nSELECT 1\n```\nActually:\n```sql\nSELECT 2\n```"
        assert extract_sql(text) == "SELECT 2"

    def test_bare_select(self):
        assert extract_sql("SELECT * FROM users") == "SELECT * FROM users"

    def test_bare_cte(self):
        sql = "WITH x AS (SELECT 1) SELECT * FROM x"
        assert extract_sql(sql) == sql

    def test_prose_only_returns_none(self):
        assert extract_sql("I can't help with that.") is None

    def test_empty_returns_none(self):
        assert extract_sql("") is None
        assert extract_sql("   ") is None


# --------------------------------------------------------------------------- #
# End-to-end adapter (mocked LLM)
# --------------------------------------------------------------------------- #


class TestNL2SQLHappyPath:
    def test_returns_validated_sql(self):
        llm = FakeLLM("```sql\nSELECT id, email FROM users\n```")
        result = nl2sql("show me users", llm=llm)
        assert result.validated is True
        assert "SELECT" in result.sql
        assert "FROM users" in result.sql

    def test_schema_included_in_prompt(self):
        llm = FakeLLM("```sql\nSELECT * FROM orders\n```")
        schema = [
            TableSchema(
                name="orders",
                columns=[
                    ColumnSchema(name="id", type="INTEGER"),
                    ColumnSchema(name="total", type="REAL"),
                ],
            )
        ]
        nl2sql("list orders", schema=schema, llm=llm)
        assert "orders" in llm.last_user
        assert "total" in llm.last_user
        assert "Schema (table: columns)" in llm.last_user

    def test_dialect_appended_to_system_prompt(self):
        llm = FakeLLM("```sql\nSELECT 1\n```")
        nl2sql("get one", dialect="postgresql", llm=llm)
        assert "postgres" in llm.last_system

    def test_transpile_to_target(self):
        llm = FakeLLM("```sql\nSELECT NVL(x, 0) FROM t\n```")
        result = nl2sql(
            "get x",
            dialect="oracle",
            transpile_to="postgres",
            llm=llm,
        )
        assert result.validated is True
        assert "COALESCE(x, 0)" in result.sql
        assert result.dialect == "postgres"
        assert any("Transpiled" in w for w in result.warnings)


class TestNL2SQLSafetyGate:
    def test_drop_draft_is_rejected_not_returned(self):
        # The model ignores instructions and emits a DROP. The safety layer
        # must catch it and mark the result invalid.
        llm = FakeLLM("```sql\nDROP TABLE users\n```")
        result = nl2sql("delete users", llm=llm)
        assert result.validated is False
        assert result.sql is None
        assert any("read-only policy" in w for w in result.warnings)

    def test_update_draft_is_rejected(self):
        llm = FakeLLM("```sql\nUPDATE users SET email = 'x'\n```")
        result = nl2sql("set emails", llm=llm)
        assert result.validated is False
        assert result.sql is None

    def test_select_into_draft_is_rejected(self):
        llm = FakeLLM("```sql\nSELECT * INTO archive FROM users\n```")
        result = nl2sql("archive users", llm=llm)
        assert result.validated is False

    def test_multistatement_draft_is_rejected(self):
        llm = FakeLLM("```sql\nSELECT 1; DROP TABLE users;\n```")
        result = nl2sql("trick", llm=llm)
        assert result.validated is False


class TestNL2SQLNoSQLResponse:
    def test_model_declines_gracefully(self):
        llm = FakeLLM("I can't write that as a single read-only query.")
        result = nl2sql("delete everything", llm=llm)
        assert result.validated is False
        assert result.sql is None
        assert any("did not produce" in w for w in result.warnings)


class TestNL2SQLErrors:
    def test_empty_prompt_raises(self):
        with pytest.raises(ValueError):
            nl2sql("   ", llm=FakeLLM(""))

    def test_llm_call_failure_wrapped(self):
        class Boom:
            def complete(self, system, user, *, model, max_tokens):
                raise RuntimeError("network down")

        with pytest.raises(NL2SQLError, match="LLM call failed"):
            nl2sql("x", llm=Boom())
