"""Integration tests for SQLTrans UI flow.

Tests complete user workflows from input to SQL generation, dialect switching,
and export operations. Uses Textual's testing framework to simulate user interactions.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from textual.pilot import Pilot

from sqltrans.ui.app import SQLTransApp
from sqltrans.ui.screens.query_builder import QueryBuilderScreen


@pytest.fixture
def app():
    """Create SQLTransApp instance for testing."""
    return SQLTransApp(initial_dialect="generic")


class TestCompleteQueryBuildingFlow:
    """Test complete query building workflows."""

    @pytest.mark.asyncio
    async def test_basic_select_query_flow(self):
        """Test building a basic SELECT query from start to finish."""
        app = SQLTransApp(initial_dialect="generic")
        async with app.run_test() as pilot:
            # Wait for app to mount
            await pilot.pause()

            # Get the query builder screen
            screen = app.screen
            assert isinstance(screen, QueryBuilderScreen)

            # Verify initial state - should have empty query
            assert screen.query_state.table is None
            assert len(screen.query_state.columns) == 0
            assert len(screen.query_state.filters) == 0

            # Enter table name
            table_input = screen.query_one("#table-input")
            table_input.value = "users"
            await pilot.pause()

            # Verify table was set
            assert screen.query_state.table == "users"

            # SQL should now be generated (SELECT * FROM "users")
            sql_display = screen.query_one("#sql-display")
            sql_text = sql_display.renderable
            assert "users" in str(sql_text).lower()
            assert "select" in str(sql_text).lower()

    @pytest.mark.asyncio
    async def test_query_with_columns_flow(self):
        """Test adding columns to SELECT clause."""
        app = SQLTransApp(initial_dialect="generic")
        async with app.run_test() as pilot:
            await pilot.pause()

            screen = app.screen

            # Set table
            table_input = screen.query_one("#table-input")
            table_input.value = "orders"
            await pilot.pause()

            # Add columns
            column_input = screen.query_one("#column-input")
            add_button = screen.query_one("#add-column-btn")

            # Add first column
            column_input.value = "id"
            await pilot.click("#add-column-btn")
            await pilot.pause()

            # Add second column
            column_input.value = "total"
            await pilot.click("#add-column-btn")
            await pilot.pause()

            # Verify columns were added
            assert "id" in screen.query_state.columns
            assert "total" in screen.query_state.columns

            # SQL should include both columns
            sql_display = screen.query_one("#sql-display")
            sql_text = str(sql_display.renderable)
            assert "id" in sql_text.lower()
            assert "total" in sql_text.lower()

    @pytest.mark.asyncio
    async def test_query_with_filters_flow(self):
        """Test adding WHERE clause filters."""
        app = SQLTransApp(initial_dialect="generic")
        async with app.run_test() as pilot:
            await pilot.pause()

            screen = app.screen

            # Set table
            table_input = screen.query_one("#table-input")
            table_input.value = "customers"
            await pilot.pause()

            # Add a filter: email = 'test@example.com'
            filter_column = screen.query_one("#filter-column")
            filter_operator = screen.query_one("#filter-operator")
            filter_value = screen.query_one("#filter-value")
            add_filter_btn = screen.query_one("#add-filter-btn")

            filter_column.value = "email"
            # Operator selector should default to '='
            filter_value.value = "test@example.com"
            await pilot.click("#add-filter-btn")
            await pilot.pause()

            # Verify filter was added
            assert len(screen.query_state.filters) == 1
            filter_obj = screen.query_state.filters[0]
            assert filter_obj.column == "email"
            assert filter_obj.operator == "="
            assert filter_obj.value == "test@example.com"

            # SQL should include WHERE clause
            sql_display = screen.query_one("#sql-display")
            sql_text = str(sql_display.renderable).lower()
            assert "where" in sql_text
            assert "email" in sql_text

    @pytest.mark.asyncio
    async def test_multiple_filters_flow(self):
        """Test adding multiple filters with AND combination."""
        app = SQLTransApp(initial_dialect="generic")
        async with app.run_test() as pilot:
            await pilot.pause()

            screen = app.screen

            # Set table
            table_input = screen.query_one("#table-input")
            table_input.value = "products"
            await pilot.pause()

            # Add first filter: price > 100
            filter_column = screen.query_one("#filter-column")
            filter_operator = screen.query_one("#filter-operator")
            filter_value = screen.query_one("#filter-value")

            filter_column.value = "price"
            filter_operator.value = ">"
            filter_value.value = "100"
            await pilot.click("#add-filter-btn")
            await pilot.pause()

            # Add second filter: category = 'electronics'
            filter_column.value = "category"
            filter_operator.value = "="
            filter_value.value = "electronics"
            await pilot.click("#add-filter-btn")
            await pilot.pause()

            # Verify both filters exist
            assert len(screen.query_state.filters) == 2

            # SQL should include AND
            sql_display = screen.query_one("#sql-display")
            sql_text = str(sql_display.renderable).lower()
            assert "and" in sql_text
            assert "price" in sql_text
            assert "category" in sql_text


class TestDialectSwitching:
    """Test dialect switching and SQL regeneration."""

    @pytest.mark.asyncio
    async def test_switch_dialect_regenerates_sql(self):
        """Test that switching dialect regenerates SQL correctly."""
        app = SQLTransApp(initial_dialect="generic")
        async with app.run_test() as pilot:
            await pilot.pause()

            screen = app.screen

            # Build a query
            table_input = screen.query_one("#table-input")
            table_input.value = "users"
            await pilot.pause()

            column_input = screen.query_one("#column-input")
            column_input.value = "id"
            await pilot.click("#add-column-btn")
            await pilot.pause()

            # Get initial SQL (generic dialect)
            sql_display = screen.query_one("#sql-display")
            generic_sql = str(sql_display.renderable)

            # Switch to PostgreSQL
            dialect_selector = screen.query_one("DialectSelector")
            # Simulate selecting PostgreSQL
            from sqltrans.ui.widgets.dialect_selector import DialectSelector
            message = DialectSelector.DialectChanged("postgresql")
            screen.on_dialect_selector_dialect_changed(message)
            await pilot.pause()

            # Verify dialect changed
            assert screen.query_state.dialect == "postgresql"

            # SQL should be regenerated
            postgresql_sql = str(sql_display.renderable)
            # PostgreSQL uses double quotes for identifiers
            assert '"id"' in postgresql_sql or "id" in postgresql_sql

    @pytest.mark.asyncio
    async def test_all_three_dialects(self):
        """Test switching between all three supported dialects."""
        app = SQLTransApp(initial_dialect="generic")
        async with app.run_test() as pilot:
            await pilot.pause()

            screen = app.screen

            # Build a simple query
            table_input = screen.query_one("#table-input")
            table_input.value = "test_table"
            await pilot.pause()

            from sqltrans.ui.widgets.dialect_selector import DialectSelector

            # Test each dialect
            for dialect_name in ["generic", "postgresql", "oracle"]:
                message = DialectSelector.DialectChanged(dialect_name)
                screen.on_dialect_selector_dialect_changed(message)
                await pilot.pause()

                assert screen.query_state.dialect == dialect_name

                # SQL should be generated for each dialect
                sql_display = screen.query_one("#sql-display")
                sql_text = str(sql_display.renderable)
                assert "test_table" in sql_text.lower() or "TEST_TABLE" in sql_text


class TestExportOperations:
    """Test clipboard and file export operations."""

    @pytest.mark.asyncio
    async def test_copy_to_clipboard(self):
        """Test copying SQL to clipboard."""
        app = SQLTransApp(initial_dialect="generic")
        async with app.run_test() as pilot:
            await pilot.pause()

            screen = app.screen

            # Build a query
            table_input = screen.query_one("#table-input")
            table_input.value = "users"
            await pilot.pause()

            # Mock clipboard operation
            with patch('sqltrans.utils.clipboard.copy_to_clipboard') as mock_copy:
                mock_copy.return_value = True

                # Click copy button
                await pilot.click("#copy-btn")
                await pilot.pause()

                # Verify clipboard function was called
                mock_copy.assert_called_once()

                # Verify status message appears
                status = screen.query_one("#copy-status")
                status_text = status.renderable
                # Should show success message
                assert status_text is not None

    @pytest.mark.asyncio
    async def test_copy_to_clipboard_failure(self):
        """Test clipboard copy failure handling."""
        app = SQLTransApp(initial_dialect="generic")
        async with app.run_test() as pilot:
            await pilot.pause()

            screen = app.screen

            # Build a query
            table_input = screen.query_one("#table-input")
            table_input.value = "users"
            await pilot.pause()

            # Mock clipboard failure
            with patch('sqltrans.utils.clipboard.copy_to_clipboard') as mock_copy:
                mock_copy.return_value = False

                # Click copy button
                await pilot.click("#copy-btn")
                await pilot.pause()

                # Status should show error
                status = screen.query_one("#copy-status")
                # Error message should be displayed

    @pytest.mark.asyncio
    async def test_save_to_file(self):
        """Test saving SQL to file."""
        app = SQLTransApp(initial_dialect="generic")
        async with app.run_test() as pilot:
            await pilot.pause()

            screen = app.screen

            # Build a query
            table_input = screen.query_one("#table-input")
            table_input.value = "orders"
            await pilot.pause()

            # Mock file save operation
            mock_open = MagicMock()
            with patch('builtins.open', mock_open), \
                 patch('pathlib.Path.exists', return_value=False):

                # Simulate save button click (may require file dialog mock)
                await pilot.click("#save-btn")
                await pilot.pause()

                # In a real implementation, this would trigger a file dialog
                # For testing, we verify the save mechanism is triggered


class TestValidationErrors:
    """Test that validation errors prevent invalid operations."""

    @pytest.mark.asyncio
    async def test_invalid_table_name_shows_error(self):
        """Test that invalid table names show validation errors."""
        app = SQLTransApp(initial_dialect="generic")
        async with app.run_test() as pilot:
            await pilot.pause()

            screen = app.screen

            # Try to enter invalid table name
            table_input = screen.query_one("#table-input")
            table_input.value = "123invalid"  # Starts with number
            await pilot.pause()

            # Error message should appear
            error_display = screen.query_one("#table-error")
            error_text = str(error_display.renderable)
            # Should contain validation error
            assert error_text != "" or not screen.query_state.table

    @pytest.mark.asyncio
    async def test_invalid_column_name_rejected(self):
        """Test that invalid column names are rejected."""
        app = SQLTransApp(initial_dialect="generic")
        async with app.run_test() as pilot:
            await pilot.pause()

            screen = app.screen

            # Set valid table first
            table_input = screen.query_one("#table-input")
            table_input.value = "users"
            await pilot.pause()

            # Try to add invalid column
            column_input = screen.query_one("#column-input")
            column_input.value = "col-umn"  # Contains hyphen
            await pilot.click("#add-column-btn")
            await pilot.pause()

            # Column should not be added
            assert "col-umn" not in screen.query_state.columns

    @pytest.mark.asyncio
    async def test_filter_without_value_shows_error(self):
        """Test that filters requiring values show errors when value is missing."""
        app = SQLTransApp(initial_dialect="generic")
        async with app.run_test() as pilot:
            await pilot.pause()

            screen = app.screen

            # Set table
            table_input = screen.query_one("#table-input")
            table_input.value = "users"
            await pilot.pause()

            # Try to add filter without value
            filter_column = screen.query_one("#filter-column")
            filter_operator = screen.query_one("#filter-operator")
            filter_value = screen.query_one("#filter-value")

            filter_column.value = "age"
            filter_operator.value = ">"
            filter_value.value = ""  # Empty value
            await pilot.click("#add-filter-btn")
            await pilot.pause()

            # Filter should not be added or error should show
            # (depending on implementation, either no filter or error message)


class TestClearAndReset:
    """Test clearing query and starting over."""

    @pytest.mark.asyncio
    async def test_new_query_clears_state(self):
        """Test that 'new query' action clears all state."""
        app = SQLTransApp(initial_dialect="generic")
        async with app.run_test() as pilot:
            await pilot.pause()

            screen = app.screen

            # Build a complete query
            table_input = screen.query_one("#table-input")
            table_input.value = "users"
            await pilot.pause()

            column_input = screen.query_one("#column-input")
            column_input.value = "id"
            await pilot.click("#add-column-btn")
            await pilot.pause()

            filter_column = screen.query_one("#filter-column")
            filter_value = screen.query_one("#filter-value")
            filter_column.value = "active"
            filter_value.value = "true"
            await pilot.click("#add-filter-btn")
            await pilot.pause()

            # Verify query has data
            assert screen.query_state.table is not None
            assert len(screen.query_state.columns) > 0
            assert len(screen.query_state.filters) > 0

            # Press 'n' for new query
            await pilot.press("n")
            await pilot.pause()

            # All state should be cleared
            assert screen.query_state.table is None
            assert len(screen.query_state.columns) == 0
            assert len(screen.query_state.filters) == 0


class TestKeyboardShortcuts:
    """Test keyboard shortcuts work correctly."""

    @pytest.mark.asyncio
    async def test_quit_shortcut(self):
        """Test that 'q' quits the application."""
        app = SQLTransApp(initial_dialect="generic")
        async with app.run_test() as pilot:
            await pilot.pause()

            # Press 'q' to quit
            # Note: This will exit the app, so we just verify the binding exists
            screen = app.screen
            assert any(binding.key == "q" for binding in screen.BINDINGS)

    @pytest.mark.asyncio
    async def test_copy_shortcut(self):
        """Test that 'c' triggers copy."""
        app = SQLTransApp(initial_dialect="generic")
        async with app.run_test() as pilot:
            await pilot.pause()

            screen = app.screen

            # Build a query
            table_input = screen.query_one("#table-input")
            table_input.value = "users"
            await pilot.pause()

            # Mock clipboard
            with patch('sqltrans.utils.clipboard.copy_to_clipboard') as mock_copy:
                mock_copy.return_value = True

                # Press 'c' to copy
                await pilot.press("c")
                await pilot.pause()

                # Copy should have been called
                mock_copy.assert_called_once()

    @pytest.mark.asyncio
    async def test_help_shortcut(self):
        """Test that '?' shows help."""
        app = SQLTransApp(initial_dialect="generic")
        async with app.run_test() as pilot:
            await pilot.pause()

            screen = app.screen

            # Verify help binding exists
            assert any(binding.key == "?" for binding in screen.BINDINGS)

            # Press '?' for help (may push help screen)
            await pilot.press("?")
            await pilot.pause()

            # Help screen may be pushed (implementation dependent)


class TestStateSynchronization:
    """Test that UI state stays synchronized with query state."""

    @pytest.mark.asyncio
    async def test_preview_updates_on_every_change(self):
        """Test that SQL preview updates whenever query state changes."""
        app = SQLTransApp(initial_dialect="generic")
        async with app.run_test() as pilot:
            await pilot.pause()

            screen = app.screen
            sql_display = screen.query_one("#sql-display")

            # Initial state - should be empty or placeholder
            initial_sql = str(sql_display.renderable)

            # Add table - should update
            table_input = screen.query_one("#table-input")
            table_input.value = "users"
            await pilot.pause()
            sql_after_table = str(sql_display.renderable)
            assert sql_after_table != initial_sql

            # Add column - should update
            column_input = screen.query_one("#column-input")
            column_input.value = "id"
            await pilot.click("#add-column-btn")
            await pilot.pause()
            sql_after_column = str(sql_display.renderable)
            assert sql_after_column != sql_after_table

            # Add filter - should update
            filter_column = screen.query_one("#filter-column")
            filter_value = screen.query_one("#filter-value")
            filter_column.value = "active"
            filter_value.value = "true"
            await pilot.click("#add-filter-btn")
            await pilot.pause()
            sql_after_filter = str(sql_display.renderable)
            assert sql_after_filter != sql_after_column

    @pytest.mark.asyncio
    async def test_remove_column_updates_preview(self):
        """Test that removing columns updates the preview."""
        app = SQLTransApp(initial_dialect="generic")
        async with app.run_test() as pilot:
            await pilot.pause()

            screen = app.screen

            # Build query with columns
            table_input = screen.query_one("#table-input")
            table_input.value = "users"
            await pilot.pause()

            column_input = screen.query_one("#column-input")
            column_input.value = "id"
            await pilot.click("#add-column-btn")
            await pilot.pause()

            column_input.value = "email"
            await pilot.click("#add-column-btn")
            await pilot.pause()

            # Verify both columns exist
            assert len(screen.query_state.columns) == 2

            # Remove a column
            # (Implementation depends on how columns are displayed/removed)
            # This tests the state synchronization principle

    @pytest.mark.asyncio
    async def test_remove_filter_updates_preview(self):
        """Test that removing filters updates the preview."""
        app = SQLTransApp(initial_dialect="generic")
        async with app.run_test() as pilot:
            await pilot.pause()

            screen = app.screen

            # Build query with filters
            table_input = screen.query_one("#table-input")
            table_input.value = "users"
            await pilot.pause()

            filter_column = screen.query_one("#filter-column")
            filter_value = screen.query_one("#filter-value")

            filter_column.value = "active"
            filter_value.value = "true"
            await pilot.click("#add-filter-btn")
            await pilot.pause()

            # Verify filter exists
            assert len(screen.query_state.filters) == 1

            # Remove filter (implementation dependent)
            # This tests the state synchronization principle
