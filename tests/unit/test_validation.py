"""Unit tests for validation utilities."""

import pytest
from sqltrans.utils.validation import (
    validate_identifier,
    is_sql_keyword,
    validate_operator,
    validate_value,
    SQL_KEYWORDS,
    VALID_OPERATORS,
)


class TestValidateIdentifier:
    """Tests for validate_identifier function."""

    def test_valid_simple_name(self):
        """Test validation of simple valid identifier."""
        is_valid, error = validate_identifier("users")
        assert is_valid is True
        assert error == ""

    def test_valid_with_underscore(self):
        """Test validation of identifier with underscore."""
        is_valid, error = validate_identifier("user_name")
        assert is_valid is True
        assert error == ""

    def test_valid_starting_with_underscore(self):
        """Test validation of identifier starting with underscore."""
        is_valid, error = validate_identifier("_private")
        assert is_valid is True
        assert error == ""

    def test_valid_with_numbers(self):
        """Test validation of identifier with numbers."""
        is_valid, error = validate_identifier("user123")
        assert is_valid is True
        assert error == ""

    def test_valid_mixed_case(self):
        """Test validation of mixed case identifier."""
        is_valid, error = validate_identifier("UserName")
        assert is_valid is True
        assert error == ""

    def test_empty_string_invalid(self):
        """Test that empty string is invalid."""
        is_valid, error = validate_identifier("")
        assert is_valid is False
        assert "cannot be empty" in error

    def test_whitespace_only_invalid(self):
        """Test that whitespace-only string is invalid."""
        is_valid, error = validate_identifier("   ")
        assert is_valid is False
        assert "cannot be empty" in error

    def test_starting_with_digit_invalid(self):
        """Test that identifier starting with digit is invalid."""
        is_valid, error = validate_identifier("123invalid")
        assert is_valid is False
        assert "must start with a letter or underscore" in error

    def test_hyphen_invalid(self):
        """Test that identifier with hyphen is invalid."""
        is_valid, error = validate_identifier("user-name")
        assert is_valid is False
        assert "invalid characters" in error

    def test_space_invalid(self):
        """Test that identifier with space is invalid."""
        is_valid, error = validate_identifier("user name")
        assert is_valid is False
        assert "invalid characters" in error

    def test_special_characters_invalid(self):
        """Test that special characters are invalid."""
        invalid_chars = ["@", "#", "$", "%", "^", "&", "*", "(", ")", "-", "+", "="]
        for char in invalid_chars:
            is_valid, error = validate_identifier(f"user{char}name")
            assert is_valid is False, f"Character {char} should be invalid"

    def test_too_long_invalid(self):
        """Test that identifiers longer than 128 chars are invalid."""
        long_name = "a" * 129
        is_valid, error = validate_identifier(long_name)
        assert is_valid is False
        assert "too long" in error

    def test_max_length_valid(self):
        """Test that identifier of exactly 128 chars is valid."""
        max_name = "a" * 128
        is_valid, error = validate_identifier(max_name)
        assert is_valid is True

    def test_sql_injection_semicolon(self):
        """Test that semicolon is detected as dangerous."""
        is_valid, error = validate_identifier("user;DROP")
        assert is_valid is False
        assert "dangerous pattern" in error

    def test_sql_injection_comment(self):
        """Test that SQL comment syntax is detected."""
        is_valid, error = validate_identifier("user--comment")
        assert is_valid is False
        assert "dangerous pattern" in error

    def test_sql_injection_multiline_comment(self):
        """Test that multiline comment syntax is detected."""
        is_valid, error = validate_identifier("user/*comment*/")
        assert is_valid is False
        assert "dangerous pattern" in error

    def test_sql_injection_drop(self):
        """Test that DROP keyword is detected."""
        is_valid, error = validate_identifier("userDROP")
        assert is_valid is False
        assert "dangerous pattern" in error

    def test_sql_injection_quote_semicolon(self):
        """Test that quote-semicolon pattern is detected."""
        is_valid, error = validate_identifier("user';")
        assert is_valid is False
        assert "dangerous pattern" in error

    def test_sql_injection_xp_procedure(self):
        """Test that xp_ prefix (SQL Server procedures) is detected."""
        is_valid, error = validate_identifier("xp_cmdshell")
        assert is_valid is False
        assert "dangerous pattern" in error

    def test_sql_injection_sp_procedure(self):
        """Test that sp_ prefix (stored procedures) is detected."""
        is_valid, error = validate_identifier("sp_executesql")
        assert is_valid is False
        assert "dangerous pattern" in error

    def test_sql_keyword_warning(self):
        """Test that SQL keywords return warning but are valid."""
        is_valid, error = validate_identifier("SELECT")
        assert is_valid is True
        assert "Warning" in error
        assert "keyword" in error

    def test_sql_keyword_lowercase_warning(self):
        """Test that lowercase SQL keywords also return warning."""
        is_valid, error = validate_identifier("select")
        assert is_valid is True
        assert "Warning" in error

    def test_whitespace_trimmed(self):
        """Test that whitespace is trimmed before validation."""
        is_valid, error = validate_identifier("  users  ")
        assert is_valid is True
        assert error == ""


class TestIsSQLKeyword:
    """Tests for is_sql_keyword function."""

    def test_select_is_keyword(self):
        """Test that SELECT is recognized as keyword."""
        assert is_sql_keyword("SELECT") is True

    def test_select_lowercase_is_keyword(self):
        """Test that select (lowercase) is recognized as keyword."""
        assert is_sql_keyword("select") is True

    def test_from_is_keyword(self):
        """Test that FROM is recognized as keyword."""
        assert is_sql_keyword("FROM") is True

    def test_where_is_keyword(self):
        """Test that WHERE is recognized as keyword."""
        assert is_sql_keyword("WHERE") is True

    def test_all_keywords_recognized(self):
        """Test that all SQL keywords are recognized."""
        for keyword in SQL_KEYWORDS:
            assert is_sql_keyword(keyword) is True
            assert is_sql_keyword(keyword.lower()) is True

    def test_non_keyword_is_not_keyword(self):
        """Test that non-keywords return False."""
        assert is_sql_keyword("users") is False
        assert is_sql_keyword("customer_id") is False
        assert is_sql_keyword("my_table") is False


class TestValidateOperator:
    """Tests for validate_operator function."""

    def test_equality_operator_valid(self):
        """Test that = operator is valid."""
        assert validate_operator("=") is True

    def test_inequality_operator_valid(self):
        """Test that != operator is valid."""
        assert validate_operator("!=") is True

    def test_comparison_operators_valid(self):
        """Test that comparison operators are valid."""
        assert validate_operator("<") is True
        assert validate_operator(">") is True
        assert validate_operator("<=") is True
        assert validate_operator(">=") is True

    def test_like_operator_valid(self):
        """Test that LIKE operator is valid."""
        assert validate_operator("LIKE") is True

    def test_in_operator_valid(self):
        """Test that IN operator is valid."""
        assert validate_operator("IN") is True

    def test_is_null_operator_valid(self):
        """Test that IS NULL operator is valid."""
        assert validate_operator("IS NULL") is True

    def test_is_not_null_operator_valid(self):
        """Test that IS NOT NULL operator is valid."""
        assert validate_operator("IS NOT NULL") is True

    def test_all_valid_operators(self):
        """Test that all valid operators are recognized."""
        for op in VALID_OPERATORS:
            assert validate_operator(op) is True

    def test_invalid_operator(self):
        """Test that invalid operators return False."""
        assert validate_operator("INVALID") is False
        assert validate_operator("BETWEEN") is False
        assert validate_operator("EXISTS") is False
        assert validate_operator("==") is False


class TestValidateValue:
    """Tests for validate_value function."""

    # String value tests
    def test_string_simple_valid(self):
        """Test validation of simple string."""
        is_valid, value, error = validate_value("John", "string")
        assert is_valid is True
        assert value == "John"
        assert error == ""

    def test_string_with_spaces_valid(self):
        """Test validation of string with spaces."""
        is_valid, value, error = validate_value("John Doe", "string")
        assert is_valid is True
        assert value == "John Doe"

    def test_string_empty_valid(self):
        """Test that empty string is valid for string type."""
        is_valid, value, error = validate_value("", "string")
        assert is_valid is True
        assert value == ""

    def test_string_with_numbers_valid(self):
        """Test string with numbers."""
        is_valid, value, error = validate_value("User123", "string")
        assert is_valid is True
        assert value == "User123"

    def test_string_sql_injection_quote_semicolon(self):
        """Test that '; pattern is detected in strings."""
        is_valid, value, error = validate_value("test'; DROP TABLE users;--", "string")
        assert is_valid is False
        assert "dangerous" in error

    def test_string_sql_injection_quote_comment(self):
        """Test that ';-- pattern is detected."""
        is_valid, value, error = validate_value("admin';--", "string")
        assert is_valid is False
        assert "dangerous" in error

    def test_string_sql_injection_or_clause(self):
        """Test that ' OR ' pattern is detected."""
        is_valid, value, error = validate_value("test' OR '1'='1", "string")
        assert is_valid is False
        assert "dangerous" in error

    def test_string_sql_injection_and_clause(self):
        """Test that ' AND ' pattern is detected."""
        is_valid, value, error = validate_value("test' AND '1'='1", "string")
        assert is_valid is False
        assert "dangerous" in error

    def test_string_sql_injection_always_true(self):
        """Test that 1=1 pattern is detected."""
        is_valid, value, error = validate_value("' OR 1=1--", "string")
        assert is_valid is False
        assert "dangerous" in error

    def test_string_sql_injection_tautology(self):
        """Test that tautology pattern is detected."""
        is_valid, value, error = validate_value("admin' OR '1'='1", "string")
        assert is_valid is False
        assert "dangerous" in error

    # Number value tests
    def test_number_integer_valid(self):
        """Test validation of integer."""
        is_valid, value, error = validate_value("123", "number")
        assert is_valid is True
        assert value == 123
        assert isinstance(value, int)
        assert error == ""

    def test_number_negative_integer_valid(self):
        """Test validation of negative integer."""
        is_valid, value, error = validate_value("-456", "number")
        assert is_valid is True
        assert value == -456

    def test_number_float_valid(self):
        """Test validation of float."""
        is_valid, value, error = validate_value("123.45", "number")
        assert is_valid is True
        assert value == 123.45
        assert isinstance(value, float)

    def test_number_negative_float_valid(self):
        """Test validation of negative float."""
        is_valid, value, error = validate_value("-67.89", "number")
        assert is_valid is True
        assert value == -67.89

    def test_number_zero_valid(self):
        """Test validation of zero."""
        is_valid, value, error = validate_value("0", "number")
        assert is_valid is True
        assert value == 0

    def test_number_with_whitespace_valid(self):
        """Test number with surrounding whitespace."""
        is_valid, value, error = validate_value("  42  ", "number")
        assert is_valid is True
        assert value == 42

    def test_number_non_numeric_invalid(self):
        """Test that non-numeric string is invalid."""
        is_valid, value, error = validate_value("abc", "number")
        assert is_valid is False
        assert "not a valid number" in error

    def test_number_empty_invalid(self):
        """Test that empty string is invalid for number."""
        is_valid, value, error = validate_value("", "number")
        assert is_valid is False
        assert "cannot be empty" in error

    def test_number_mixed_invalid(self):
        """Test that mixed alphanumeric is invalid."""
        is_valid, value, error = validate_value("123abc", "number")
        assert is_valid is False
        assert "not a valid number" in error

    # List value tests
    def test_list_single_item_valid(self):
        """Test validation of single-item list."""
        is_valid, value, error = validate_value("item1", "list")
        assert is_valid is True
        assert value == ["item1"]
        assert error == ""

    def test_list_multiple_items_valid(self):
        """Test validation of multi-item list."""
        is_valid, value, error = validate_value("item1,item2,item3", "list")
        assert is_valid is True
        assert value == ["item1", "item2", "item3"]

    def test_list_with_spaces_valid(self):
        """Test list with spaces around items."""
        is_valid, value, error = validate_value("item1 , item2 , item3", "list")
        assert is_valid is True
        assert value == ["item1", "item2", "item3"]

    def test_list_numbers_valid(self):
        """Test list of numbers."""
        is_valid, value, error = validate_value("1,2,3,4,5", "list")
        assert is_valid is True
        assert value == ["1", "2", "3", "4", "5"]

    def test_list_mixed_valid(self):
        """Test list with mixed content."""
        is_valid, value, error = validate_value("active,pending,123", "list")
        assert is_valid is True
        assert value == ["active", "pending", "123"]

    def test_list_empty_invalid(self):
        """Test that empty list is invalid."""
        is_valid, value, error = validate_value("", "list")
        assert is_valid is False
        assert "cannot be empty" in error

    def test_list_only_commas_invalid(self):
        """Test that list of only commas is invalid."""
        is_valid, value, error = validate_value(",,,", "list")
        assert is_valid is False
        assert "at least one value" in error

    def test_list_sql_injection_quote_semicolon(self):
        """Test that dangerous patterns in list items are detected."""
        is_valid, value, error = validate_value("item1,';DROP TABLE", "list")
        assert is_valid is False
        assert "dangerous pattern" in error

    def test_list_sql_injection_comment(self):
        """Test that SQL comments in list are detected."""
        is_valid, value, error = validate_value("item1,item2--comment", "list")
        assert is_valid is False
        assert "dangerous pattern" in error

    def test_list_sql_injection_multiline_comment(self):
        """Test that multiline comments in list are detected."""
        is_valid, value, error = validate_value("item1,/*comment*/item2", "list")
        assert is_valid is False
        assert "dangerous pattern" in error

    def test_list_sql_injection_drop(self):
        """Test that DROP keyword in list is detected."""
        is_valid, value, error = validate_value("item1,DROP TABLE,item2", "list")
        assert is_valid is False
        assert "dangerous pattern" in error

    def test_list_sql_injection_delete(self):
        """Test that DELETE keyword in list is detected."""
        is_valid, value, error = validate_value("item1,DELETE FROM users", "list")
        assert is_valid is False
        assert "dangerous pattern" in error

    def test_list_sql_injection_update(self):
        """Test that UPDATE keyword in list is detected."""
        is_valid, value, error = validate_value("UPDATE users,item2", "list")
        assert is_valid is False
        assert "dangerous pattern" in error

    # Unknown type tests
    def test_unknown_type_invalid(self):
        """Test that unknown value type returns error."""
        is_valid, value, error = validate_value("test", "unknown")
        assert is_valid is False
        assert "Unknown value type" in error

    # Edge cases
    def test_string_single_quote_allowed(self):
        """Test that single quote alone in string is allowed (not a pattern)."""
        is_valid, value, error = validate_value("O'Connor", "string")
        assert is_valid is True
        assert value == "O'Connor"

    def test_number_decimal_point_only_invalid(self):
        """Test that decimal point only is invalid."""
        is_valid, value, error = validate_value(".", "number")
        assert is_valid is False
        assert "not a valid number" in error

    def test_list_trailing_comma_handled(self):
        """Test that trailing comma doesn't create empty item."""
        is_valid, value, error = validate_value("item1,item2,", "list")
        assert is_valid is True
        assert value == ["item1", "item2"]

    def test_list_leading_comma_handled(self):
        """Test that leading comma doesn't create empty item."""
        is_valid, value, error = validate_value(",item1,item2", "list")
        assert is_valid is True
        assert value == ["item1", "item2"]


# Parametrized tests for comprehensive coverage
class TestValidateIdentifierParametrized:
    """Parametrized tests for identifier validation."""

    @pytest.mark.parametrize("name", [
        "users",
        "user_name",
        "_private",
        "MyTable",
        "table123",
        "a",
        "_",
        "TABLE_NAME_123",
    ])
    def test_valid_identifiers(self, name):
        """Test various valid identifier formats."""
        is_valid, _ = validate_identifier(name)
        assert is_valid is True

    @pytest.mark.parametrize("name,expected_error", [
        ("123table", "must start"),
        ("user-name", "invalid characters"),
        ("user name", "invalid characters"),
        ("user@domain", "invalid characters"),
        ("user;drop", "dangerous pattern"),
        ("user--", "dangerous pattern"),
        ("user/**/", "dangerous pattern"),
    ])
    def test_invalid_identifiers(self, name, expected_error):
        """Test various invalid identifier formats."""
        is_valid, error = validate_identifier(name)
        assert is_valid is False
        assert expected_error in error.lower()


class TestValidateValueParametrized:
    """Parametrized tests for value validation."""

    @pytest.mark.parametrize("value,expected", [
        ("0", 0),
        ("42", 42),
        ("-17", -17),
        ("3.14", 3.14),
        ("-2.5", -2.5),
    ])
    def test_valid_numbers(self, value, expected):
        """Test various valid number formats."""
        is_valid, parsed, error = validate_value(value, "number")
        assert is_valid is True
        assert parsed == expected

    @pytest.mark.parametrize("injection_pattern", [
        "'; DROP TABLE users;--",
        "admin' OR '1'='1",
        "' OR 1=1--",
        "test';--",
        "' AND '1'='1",
        "1' OR '1'='1",
    ])
    def test_sql_injection_patterns_in_strings(self, injection_pattern):
        """Test that various SQL injection patterns are detected in strings."""
        is_valid, _, error = validate_value(injection_pattern, "string")
        assert is_valid is False
        assert "dangerous" in error.lower()

    @pytest.mark.parametrize("dangerous_item", [
        "';",
        "--",
        "/*",
        "DROP",
        "DELETE",
        "UPDATE",
    ])
    def test_dangerous_patterns_in_lists(self, dangerous_item):
        """Test that dangerous patterns in list items are detected."""
        list_value = f"item1,{dangerous_item},item2"
        is_valid, _, error = validate_value(list_value, "list")
        assert is_valid is False
        assert "dangerous" in error.lower()
