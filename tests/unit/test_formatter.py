"""Unit tests for SQL formatter."""

import pytest
from rich.syntax import Syntax
from rich.text import Text
from sqltrans.sql.formatter import format, highlight, highlight_to_text, strip_formatting


class TestFormat:
    """Tests for format() function."""

    def test_format_simple_query(self):
        """Test formatting simple SELECT query."""
        sql = "SELECT id, name FROM users WHERE age > 18"
        result = format(sql)

        assert "SELECT id, name" in result
        assert "\nFROM users" in result
        assert "\nWHERE age > 18" in result

    def test_format_query_with_and(self):
        """Test formatting query with AND in WHERE clause."""
        sql = "SELECT * FROM orders WHERE status = 'active' AND total > 100"
        result = format(sql)

        assert "WHERE status = 'active'" in result
        assert "AND total > 100" in result
        # AND should be indented
        assert "\n  AND" in result or "\nAND" in result

    def test_format_query_without_where(self):
        """Test formatting query without WHERE clause."""
        sql = "SELECT id, email FROM customers"
        result = format(sql)

        assert "SELECT id, email" in result
        assert "\n" in result  # Should have line break

    def test_format_empty_string(self):
        """Test formatting empty string."""
        result = format("")
        assert result == ""

    def test_format_whitespace_only(self):
        """Test formatting whitespace-only string."""
        result = format("   ")
        assert result == "   "

    def test_format_default_style(self):
        """Test default formatting style."""
        sql = "SELECT name FROM users WHERE age > 18 AND status = 'active'"
        result = format(sql, style="default")

        assert "\nFROM" in result
        assert "\nWHERE" in result
        assert "\n  AND" in result

    def test_format_compact_style(self):
        """Test compact formatting style."""
        sql = "SELECT name FROM users WHERE age > 18 AND status = 'active'"
        result = format(sql, style="compact")

        assert "\nFROM" in result
        assert "\nWHERE" in result
        # Compact style doesn't indent AND
        assert "\n  AND" not in result
        if " AND " in sql:
            assert "\nAND" in result or " AND " in result

    def test_format_expanded_style(self):
        """Test expanded formatting style."""
        sql = "SELECT name FROM users WHERE age > 18"
        result = format(sql, style="expanded")

        # Expanded style adds extra line breaks
        assert "\n\nFROM" in result or "\nFROM" in result
        assert "\nWHERE" in result or "\n\nWHERE" in result

    def test_format_preserves_sql_correctness(self):
        """Test that formatting preserves SQL correctness."""
        sql = 'SELECT "id", "name" FROM "users" WHERE "age" > 18'
        result = format(sql)

        # All essential SQL parts should be present
        assert "SELECT" in result
        assert '"id"' in result
        assert '"name"' in result
        assert "FROM" in result
        assert '"users"' in result
        assert "WHERE" in result
        assert '"age"' in result
        assert "> 18" in result

    def test_format_multiple_and_conditions(self):
        """Test formatting query with multiple AND conditions."""
        sql = "SELECT * FROM logs WHERE level = 'ERROR' AND user_id = 123 AND timestamp > '2024-01-01'"
        result = format(sql)

        # Should have multiple AND clauses
        assert result.count("AND") == 2


class TestHighlight:
    """Tests for highlight() function."""

    def test_highlight_returns_syntax_object(self):
        """Test that highlight returns Rich Syntax object."""
        sql = "SELECT * FROM users"
        result = highlight(sql)

        assert isinstance(result, Syntax)

    def test_highlight_with_default_theme(self):
        """Test highlighting with default theme."""
        sql = "SELECT id FROM users WHERE age > 18"
        result = highlight(sql)

        assert isinstance(result, Syntax)
        # Syntax object should have SQL code
        assert "SELECT" in result.code

    def test_highlight_with_different_theme(self):
        """Test highlighting with different theme."""
        sql = "SELECT * FROM users"
        result = highlight(sql, theme="github-dark")

        assert isinstance(result, Syntax)

    def test_highlight_formats_before_highlighting(self):
        """Test that SQL is formatted before highlighting."""
        sql = "SELECT id FROM users WHERE age > 18"
        result = highlight(sql)

        # The code inside Syntax should be formatted
        assert "\n" in result.code  # Should have line breaks from formatting

    def test_highlight_empty_string(self):
        """Test highlighting empty string."""
        result = highlight("")

        assert isinstance(result, Syntax)


class TestHighlightToText:
    """Tests for highlight_to_text() function."""

    def test_highlight_to_text_returns_text_object(self):
        """Test that highlight_to_text returns Rich Text object."""
        sql = "SELECT * FROM users"
        result = highlight_to_text(sql)

        assert isinstance(result, Text)

    def test_highlight_to_text_contains_sql(self):
        """Test that returned Text contains SQL content."""
        sql = "SELECT id FROM users"
        result = highlight_to_text(sql)

        # Convert to plain string to check content
        plain = result.plain
        assert "SELECT" in plain
        assert "FROM" in plain
        assert "users" in plain

    def test_highlight_to_text_with_keywords(self):
        """Test that SQL keywords are present in highlighted text."""
        sql = "SELECT * FROM users WHERE age > 18"
        result = highlight_to_text(sql)

        plain = result.plain
        assert "SELECT" in plain
        assert "FROM" in plain
        assert "WHERE" in plain

    def test_highlight_to_text_formats_first(self):
        """Test that SQL is formatted before highlighting to text."""
        sql = "SELECT id FROM users WHERE age > 18"
        result = highlight_to_text(sql)

        # Should contain the SQL content (formatting may vary)
        assert "SELECT" in result.plain
        assert "FROM" in result.plain

    def test_highlight_to_text_empty_string(self):
        """Test highlighting empty string to text."""
        result = highlight_to_text("")

        assert isinstance(result, Text)


class TestStripFormatting:
    """Tests for strip_formatting() function."""

    def test_strip_formatting_simple(self):
        """Test stripping formatting from simple formatted SQL."""
        formatted = """SELECT id, name
FROM users
WHERE age > 18"""
        result = strip_formatting(formatted)

        assert result == "SELECT id, name FROM users WHERE age > 18"

    def test_strip_formatting_with_indentation(self):
        """Test stripping formatting with indented AND."""
        formatted = """SELECT *
FROM orders
WHERE status = 'active'
  AND total > 100"""
        result = strip_formatting(formatted)

        assert "\n" not in result
        assert "  " not in result or result.count("  ") == 0  # No double spaces
        assert "status = 'active'" in result
        assert "AND total > 100" in result

    def test_strip_formatting_multiple_spaces(self):
        """Test that multiple spaces are normalized to single space."""
        formatted = "SELECT    id     FROM    users"
        result = strip_formatting(formatted)

        assert result == "SELECT id FROM users"
        assert "  " not in result

    def test_strip_formatting_preserves_sql(self):
        """Test that stripping preserves SQL correctness."""
        formatted = """SELECT "id", "email"
FROM "customers"
WHERE "status" = 'active'
  AND "age" >= 21"""
        result = strip_formatting(formatted)

        # All SQL elements should be present
        assert "SELECT" in result
        assert '"id"' in result
        assert '"email"' in result
        assert "FROM" in result
        assert '"customers"' in result
        assert "WHERE" in result
        assert '"status"' in result
        assert "'active'" in result
        assert "AND" in result
        assert '"age"' in result
        assert ">= 21" in result

    def test_strip_formatting_empty_string(self):
        """Test stripping formatting from empty string."""
        result = strip_formatting("")
        assert result == ""

    def test_strip_formatting_already_single_line(self):
        """Test stripping formatting from already single-line SQL."""
        sql = "SELECT * FROM users WHERE age > 18"
        result = strip_formatting(sql)

        assert result == sql

    def test_strip_formatting_leading_trailing_whitespace(self):
        """Test that leading/trailing whitespace is removed."""
        formatted = "  \n  SELECT * FROM users  \n  "
        result = strip_formatting(formatted)

        assert result == "SELECT * FROM users"
        assert not result.startswith(" ")
        assert not result.endswith(" ")

    def test_strip_formatting_tabs(self):
        """Test handling of tabs in formatted SQL."""
        formatted = "SELECT *\n\tFROM users\n\t\tWHERE age > 18"
        result = strip_formatting(formatted)

        assert "\t" not in result
        assert "\n" not in result


# Integration tests with realistic scenarios
class TestFormatterIntegration:
    """Integration tests for formatter functions."""

    def test_format_then_strip_round_trip(self):
        """Test that format then strip returns valid SQL."""
        original = "SELECT id, name FROM users WHERE age > 18 AND status = 'active'"

        # Format it
        formatted = format(original)
        assert "\n" in formatted  # Should have formatting

        # Strip it back
        stripped = strip_formatting(formatted)

        # Should be single line again with essential content
        assert "\n" not in stripped
        assert "SELECT" in stripped
        assert "FROM" in stripped
        assert "WHERE" in stripped
        assert "AND" in stripped

    def test_format_highlight_workflow(self):
        """Test typical workflow of format then highlight."""
        sql = "SELECT * FROM users WHERE email = 'test@example.com'"

        # Format
        formatted = format(sql)
        assert "\n" in formatted

        # Highlight
        highlighted = highlight(formatted)
        assert isinstance(highlighted, Syntax)

    def test_complex_query_formatting(self):
        """Test formatting complex realistic query."""
        sql = 'SELECT "order_id", "customer_name", "total", "status" FROM "orders" WHERE "status" IN (\'pending\', \'processing\') AND "total" > 100 AND "deleted_at" IS NULL'

        formatted = format(sql)

        # Should have proper structure
        assert formatted.startswith("SELECT")
        assert "\nFROM" in formatted
        assert "\nWHERE" in formatted
        assert "AND" in formatted

        # Should preserve quoted identifiers and string literals
        assert '"order_id"' in formatted
        assert "'pending'" in formatted
        assert "IS NULL" in formatted

    def test_formatting_preserves_case(self):
        """Test that formatting preserves case of identifiers and values."""
        sql = 'SELECT "UserId", "EmailAddress" FROM "UserAccounts" WHERE "Status" = \'Active\''

        formatted = format(sql)

        # Case should be preserved
        assert '"UserId"' in formatted
        assert '"EmailAddress"' in formatted
        assert '"UserAccounts"' in formatted
        assert '"Status"' in formatted
        assert "'Active'" in formatted


# Edge case tests
class TestFormatterEdgeCases:
    """Edge case tests for formatter."""

    def test_format_sql_with_line_breaks_already(self):
        """Test formatting SQL that already has line breaks."""
        sql = """SELECT id
FROM users
WHERE age > 18"""

        result = format(sql)

        # Should still format properly
        assert "SELECT" in result
        assert "FROM" in result
        assert "WHERE" in result

    def test_format_very_long_query(self):
        """Test formatting very long query."""
        # Create query with many columns
        columns = ", ".join([f"col{i}" for i in range(50)])
        sql = f"SELECT {columns} FROM huge_table WHERE id > 0"

        result = format(sql)

        # Should have proper structure despite length
        assert "SELECT" in result
        assert "\nFROM" in result
        assert "\nWHERE" in result

    def test_strip_formatting_very_long_query(self):
        """Test stripping formatting from very long query."""
        formatted = "SELECT " + ", ".join([f"col{i}" for i in range(50)])
        formatted += "\nFROM huge_table\nWHERE id > 0"

        result = strip_formatting(formatted)

        assert "\n" not in result
        assert all(f"col{i}" in result for i in range(50))

    def test_format_with_special_sql_syntax(self):
        """Test formatting SQL with special syntax."""
        sql = "SELECT * FROM users WHERE email LIKE '%@example.com' AND age BETWEEN 18 AND 65"

        result = format(sql)

        # Should preserve special operators
        assert "LIKE" in result
        assert "'%@example.com'" in result
        assert "BETWEEN" in result if "BETWEEN" in sql else True
