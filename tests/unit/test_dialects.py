"""Unit tests for SQL dialect implementations."""

import pytest
from sqltrans.sql.dialects.postgresql import PostgreSQLDialect
from sqltrans.sql.dialects.oracle import OracleDialect
from sqltrans.sql.dialects.generic import GenericDialect


class TestPostgreSQLDialect:
    """Tests for PostgreSQL dialect."""

    @pytest.fixture
    def dialect(self):
        """Provide PostgreSQL dialect instance."""
        return PostgreSQLDialect()

    def test_quote_identifier_simple(self, dialect):
        """Test quoting simple identifier."""
        assert dialect.quote_identifier("user_id") == '"user_id"'

    def test_quote_identifier_with_uppercase(self, dialect):
        """Test that uppercase is preserved."""
        assert dialect.quote_identifier("UserName") == '"UserName"'

    def test_quote_identifier_with_spaces(self, dialect):
        """Test quoting identifier with spaces."""
        assert dialect.quote_identifier("user name") == '"user name"'

    def test_quote_identifier_with_embedded_quote(self, dialect):
        """Test escaping embedded double quotes."""
        assert dialect.quote_identifier('table"name') == '"table""name"'

    def test_quote_identifier_with_multiple_quotes(self, dialect):
        """Test escaping multiple double quotes."""
        assert dialect.quote_identifier('col"umn"name') == '"col""umn""name"'

    def test_format_string_literal_simple(self, dialect):
        """Test formatting simple string."""
        assert dialect.format_string_literal("hello") == "'hello'"

    def test_format_string_literal_with_quote(self, dialect):
        """Test escaping single quote in string."""
        assert dialect.format_string_literal("It's") == "'It''s'"

    def test_format_string_literal_with_multiple_quotes(self, dialect):
        """Test escaping multiple single quotes."""
        assert dialect.format_string_literal("'test'") == "'''test'''"

    def test_format_string_literal_sql_injection_attempt(self, dialect):
        """Test that SQL injection attempts are safely escaped."""
        injection = "'; DROP TABLE users;--"
        result = dialect.format_string_literal(injection)
        assert result == "'''; DROP TABLE users;--'"
        assert "''" in result  # Quote is escaped

    def test_format_string_literal_empty(self, dialect):
        """Test formatting empty string."""
        assert dialect.format_string_literal("") == "''"

    def test_format_number_literal_integer(self, dialect):
        """Test formatting integer."""
        assert dialect.format_number_literal(42) == "42"

    def test_format_number_literal_negative(self, dialect):
        """Test formatting negative integer."""
        assert dialect.format_number_literal(-17) == "-17"

    def test_format_number_literal_float(self, dialect):
        """Test formatting float."""
        assert dialect.format_number_literal(3.14) == "3.14"

    def test_format_number_literal_zero(self, dialect):
        """Test formatting zero."""
        assert dialect.format_number_literal(0) == "0"

    def test_get_null_keyword(self, dialect):
        """Test NULL keyword."""
        assert dialect.get_null_keyword() == "NULL"

    def test_supports_feature_returning(self, dialect):
        """Test that RETURNING is supported."""
        assert dialect.supports_feature("RETURNING") is True

    def test_supports_feature_cte(self, dialect):
        """Test that CTE is supported."""
        assert dialect.supports_feature("CTE") is True

    def test_supports_feature_top(self, dialect):
        """Test that TOP is not supported."""
        assert dialect.supports_feature("TOP") is False


class TestOracleDialect:
    """Tests for Oracle dialect."""

    @pytest.fixture
    def dialect(self):
        """Provide Oracle dialect instance."""
        return OracleDialect()

    def test_quote_identifier_simple(self, dialect):
        """Test quoting simple identifier."""
        assert dialect.quote_identifier("user_id") == '"user_id"'

    def test_quote_identifier_preserves_case(self, dialect):
        """Test that case is preserved when quoted."""
        assert dialect.quote_identifier("TableName") == '"TableName"'

    def test_quote_identifier_with_spaces(self, dialect):
        """Test quoting identifier with spaces."""
        assert dialect.quote_identifier("user name") == '"user name"'

    def test_quote_identifier_with_embedded_quote(self, dialect):
        """Test escaping embedded double quotes."""
        assert dialect.quote_identifier('col"name') == '"col""name"'

    def test_format_string_literal_simple(self, dialect):
        """Test formatting simple string."""
        assert dialect.format_string_literal("hello") == "'hello'"

    def test_format_string_literal_with_quote(self, dialect):
        """Test escaping single quote in string."""
        assert dialect.format_string_literal("It's") == "'It''s'"

    def test_format_string_literal_sql_injection_attempt(self, dialect):
        """Test that SQL injection attempts are safely escaped."""
        injection = "admin' OR '1'='1"
        result = dialect.format_string_literal(injection)
        assert result == "'admin'' OR ''1''=''1'"
        # All single quotes should be doubled
        assert "admin''" in result

    def test_format_number_literal_integer(self, dialect):
        """Test formatting integer."""
        assert dialect.format_number_literal(100) == "100"

    def test_format_number_literal_float(self, dialect):
        """Test formatting float."""
        assert dialect.format_number_literal(99.99) == "99.99"

    def test_get_null_keyword(self, dialect):
        """Test NULL keyword."""
        assert dialect.get_null_keyword() == "NULL"

    def test_supports_feature_cte(self, dialect):
        """Test that CTE is supported."""
        assert dialect.supports_feature("CTE") is True

    def test_supports_feature_limit(self, dialect):
        """Test that LIMIT is not supported (Oracle uses ROWNUM)."""
        assert dialect.supports_feature("LIMIT") is False


class TestGenericDialect:
    """Tests for Generic ANSI SQL dialect."""

    @pytest.fixture
    def dialect(self):
        """Provide Generic dialect instance."""
        return GenericDialect()

    def test_quote_identifier_simple(self, dialect):
        """Test quoting simple identifier."""
        assert dialect.quote_identifier("customers") == '"customers"'

    def test_quote_identifier_with_underscore(self, dialect):
        """Test quoting identifier with underscore."""
        assert dialect.quote_identifier("order_total") == '"order_total"'

    def test_quote_identifier_with_embedded_quote(self, dialect):
        """Test escaping embedded double quotes."""
        assert dialect.quote_identifier('test"name') == '"test""name"'

    def test_format_string_literal_simple(self, dialect):
        """Test formatting simple string."""
        assert dialect.format_string_literal("test") == "'test'"

    def test_format_string_literal_with_quote(self, dialect):
        """Test escaping single quote in string."""
        assert dialect.format_string_literal("O'Connor") == "'O''Connor'"

    def test_format_string_literal_sql_injection_attempt(self, dialect):
        """Test that SQL injection attempts are safely escaped."""
        injection = "' OR 1=1--"
        result = dialect.format_string_literal(injection)
        assert result == "''' OR 1=1--'"
        assert "''" in result

    def test_format_number_literal_integer(self, dialect):
        """Test formatting integer."""
        assert dialect.format_number_literal(12345) == "12345"

    def test_format_number_literal_float(self, dialect):
        """Test formatting float."""
        assert dialect.format_number_literal(123.456) == "123.456"

    def test_get_null_keyword(self, dialect):
        """Test NULL keyword."""
        assert dialect.get_null_keyword() == "NULL"

    def test_supports_feature_returns_false(self, dialect):
        """Test that generic dialect claims no advanced features."""
        assert dialect.supports_feature("CTE") is False
        assert dialect.supports_feature("RETURNING") is False
        assert dialect.supports_feature("WINDOW") is False


# Parametrized tests across all dialects
@pytest.mark.parametrize("dialect_class", [
    PostgreSQLDialect,
    OracleDialect,
    GenericDialect,
])
class TestAllDialects:
    """Parametrized tests that run on all dialects."""

    def test_quote_identifier_sql_keywords(self, dialect_class):
        """Test that SQL keywords can be quoted."""
        dialect = dialect_class()
        assert dialect.quote_identifier("select") == '"select"'
        assert dialect.quote_identifier("from") == '"from"'
        assert dialect.quote_identifier("where") == '"where"'

    def test_format_string_literal_special_characters(self, dialect_class):
        """Test formatting strings with special characters."""
        dialect = dialect_class()
        # Semicolon should be preserved (not a quoting issue)
        result = dialect.format_string_literal("test;value")
        assert result == "'test;value'"

    def test_format_string_literal_backslash(self, dialect_class):
        """Test formatting string with backslash."""
        dialect = dialect_class()
        result = dialect.format_string_literal("path\\to\\file")
        assert result == "'path\\to\\file'"

    def test_quote_identifier_empty_string_preserved(self, dialect_class):
        """Test that empty identifier is quoted (though invalid)."""
        dialect = dialect_class()
        # Empty string should be quoted even though it's invalid SQL
        result = dialect.quote_identifier("")
        assert result == '""'

    def test_format_number_literal_large_integer(self, dialect_class):
        """Test formatting large integer."""
        dialect = dialect_class()
        result = dialect.format_number_literal(999999999)
        assert result == "999999999"

    def test_format_number_literal_small_float(self, dialect_class):
        """Test formatting small float."""
        dialect = dialect_class()
        result = dialect.format_number_literal(0.001)
        assert "0.001" in result

    def test_get_null_keyword_uppercase(self, dialect_class):
        """Test that NULL keyword is uppercase."""
        dialect = dialect_class()
        assert dialect.get_null_keyword() == "NULL"

    def test_quote_identifier_special_chars(self, dialect_class):
        """Test quoting identifiers with various special characters."""
        dialect = dialect_class()
        # Spaces
        assert dialect.quote_identifier("user name") == '"user name"'
        # Numbers
        assert dialect.quote_identifier("user123") == '"user123"'
        # Hyphen (though invalid unquoted)
        assert dialect.quote_identifier("user-id") == '"user-id"'


# SQL Injection Prevention Tests
class TestSQLInjectionPrevention:
    """Security-focused tests for SQL injection prevention."""

    @pytest.fixture
    def dialects(self):
        """Provide all dialect instances."""
        return [
            PostgreSQLDialect(),
            OracleDialect(),
            GenericDialect(),
        ]

    @pytest.mark.parametrize("injection_pattern", [
        "'; DROP TABLE users;--",
        "admin' OR '1'='1",
        "' OR 1=1--",
        "'; DELETE FROM users WHERE '1'='1",
        "admin'--",
        "' UNION SELECT password FROM users--",
        "1' AND '1'='1",
    ])
    def test_string_injection_patterns_escaped(self, dialects, injection_pattern):
        """Test that various SQL injection patterns are safely escaped."""
        for dialect in dialects:
            result = dialect.format_string_literal(injection_pattern)
            # Result should be quoted
            assert result.startswith("'")
            assert result.endswith("'")
            # All embedded single quotes should be doubled
            # Count quotes (excluding outer quotes)
            inner_content = result[1:-1]
            assert "''" in inner_content or "'" not in inner_content

    @pytest.mark.parametrize("dangerous_identifier", [
        "users; DROP TABLE customers;--",
        'table";DROP TABLE users;"',
        "users--comment",
        "users/*comment*/",
    ])
    def test_identifier_injection_patterns_escaped(self, dialects, dangerous_identifier):
        """Test that dangerous identifier patterns are escaped."""
        for dialect in dialects:
            result = dialect.quote_identifier(dangerous_identifier)
            # Result should be quoted with double quotes
            assert result.startswith('"')
            assert result.endswith('"')
            # If there are embedded quotes, they should be doubled
            if '"' in dangerous_identifier:
                assert '""' in result

    def test_comment_injection_in_string(self, dialects):
        """Test that SQL comments in strings are safely escaped."""
        comment_patterns = ["--", "/*", "*/", "#"]
        for dialect in dialects:
            for pattern in comment_patterns:
                test_str = f"test{pattern}comment"
                result = dialect.format_string_literal(test_str)
                # Should be safely quoted
                assert result.startswith("'")
                assert result.endswith("'")

    def test_multiline_injection(self, dialects):
        """Test that multiline injection attempts are escaped."""
        multiline = "test'\nDROP TABLE users;\n--"
        for dialect in dialects:
            result = dialect.format_string_literal(multiline)
            # Single quotes should be escaped
            assert "''" in result or result == "'test'\nDROP TABLE users;\n--'"

    def test_unicode_and_special_chars(self, dialects):
        """Test handling of unicode and special characters."""
        special_strings = [
            "test\x00null",  # Null byte
            "test\ttab",  # Tab
            "test\nline",  # Newline
            "test'quote",  # Quote
            "test\\backslash",  # Backslash
        ]
        for dialect in dialects:
            for test_str in special_strings:
                result = dialect.format_string_literal(test_str)
                # Should be quoted and quotes escaped
                assert result.startswith("'")
                assert result.endswith("'")
