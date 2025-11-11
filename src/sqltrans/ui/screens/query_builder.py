"""Query builder screen assembling all widgets."""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header, Static

from sqltrans.models.query import QueryState
from sqltrans.sql.builder import QueryBuilder
from sqltrans.sql.dialects.postgresql import PostgreSQLDialect
from sqltrans.sql.dialects.oracle import OracleDialect
from sqltrans.sql.dialects.generic import GenericDialect
from sqltrans.ui.widgets.dialect_selector import DialectSelector
from sqltrans.ui.widgets.table_input import TableInput
from sqltrans.ui.widgets.column_list import ColumnList
from sqltrans.ui.widgets.filter_editor import FilterEditor
from sqltrans.ui.widgets.sql_preview import SQLPreview
from sqltrans.utils.logging import get_logger

logger = get_logger("sqltrans.ui.query_builder")


class QueryBuilderScreen(Screen):
    """Main screen for building SQL queries.

    Assembles all widgets (dialect selector, table input, column list,
    filter editor, SQL preview) into a cohesive interface. Maintains
    query state and regenerates SQL whenever inputs change.

    Example:
        >>> screen = QueryBuilderScreen()
        >>> app.push_screen(screen)
    """

    CSS = """
    QueryBuilderScreen {
        layout: grid;
        grid-size: 3 2;
        grid-gutter: 1;
        padding: 1;
    }

    QueryBuilderScreen #top-bar {
        column-span: 3;
        height: auto;
    }

    QueryBuilderScreen #left-panel {
        row-span: 1;
    }

    QueryBuilderScreen #center-panel {
        row-span: 1;
    }

    QueryBuilderScreen #right-panel {
        row-span: 1;
    }

    QueryBuilderScreen .panel {
        height: 100%;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("c", "copy", "Copy SQL"),
        ("n", "new", "New Query"),
        ("?", "help", "Help"),
    ]

    def __init__(self) -> None:
        """Initialize query builder screen."""
        super().__init__()
        self.query_state = QueryState(dialect="generic")
        self.dialect_map = {
            "postgresql": PostgreSQLDialect(),
            "oracle": OracleDialect(),
            "generic": GenericDialect(),
        }

    def compose(self) -> ComposeResult:
        """Compose the screen layout.

        Returns:
            ComposeResult with header, widgets, and footer
        """
        yield Header(show_clock=True)

        # Top bar with dialect selector
        with Container(id="top-bar"):
            yield DialectSelector(default_dialect="generic")

        # Left panel: Table and Columns
        with Vertical(id="left-panel", classes="panel"):
            yield TableInput()
            yield ColumnList()

        # Center panel: Filters
        with Vertical(id="center-panel", classes="panel"):
            yield FilterEditor()

        # Right panel: SQL Preview
        with Vertical(id="right-panel", classes="panel"):
            yield SQLPreview()

        yield Footer()

    def on_mount(self) -> None:
        """Initialize when screen is mounted."""
        logger.info("Query builder screen mounted")
        self.update_preview()

    def on_dialect_selector_dialect_changed(
        self, message: DialectSelector.DialectChanged
    ) -> None:
        """Handle dialect selection changes.

        Args:
            message: Dialect changed message
        """
        logger.info(f"Dialect changed to: {message.dialect}")
        self.query_state.set_dialect(message.dialect)
        self.update_preview()

    def on_table_input_table_changed(self, message: TableInput.TableChanged) -> None:
        """Handle table name changes.

        Args:
            message: Table changed message
        """
        try:
            logger.debug(f"Table changed to: {message.table_name}")
            self.query_state.add_table(message.table_name)
            self.update_preview()
        except ValueError as e:
            # Table validation failed (should be caught by widget)
            logger.warning(f"Table validation failed: {e}")
            self.notify(
                f"Invalid table name: {message.table_name}",
                severity="warning",
                timeout=3
            )

    def on_column_list_columns_changed(
        self, message: ColumnList.ColumnsChanged
    ) -> None:
        """Handle column list changes.

        Args:
            message: Columns changed message
        """
        # Clear existing columns
        self.query_state.columns.clear()

        # Add new columns
        for column in message.columns:
            try:
                self.query_state.add_column(column)
            except ValueError:
                # Column validation failed
                pass

        self.update_preview()

    def on_filter_editor_filters_changed(
        self, message: FilterEditor.FiltersChanged
    ) -> None:
        """Handle filter list changes.

        Args:
            message: Filters changed message
        """
        # Update query state filters
        self.query_state.filters = message.filters.copy()
        self.update_preview()

    def update_preview(self) -> None:
        """Regenerate SQL and update preview."""
        sql_preview = self.query_one(SQLPreview)

        # Check if we have minimum requirements for a query
        if not self.query_state.table:
            sql_preview.update_sql("")
            return

        try:
            logger.debug(f"Updating preview for {self.query_state.dialect} dialect")

            # Get the appropriate dialect
            dialect = self.dialect_map[self.query_state.dialect]

            # Build the query
            builder = QueryBuilder(self.query_state, dialect)
            sql = builder.build_query()

            # Update preview
            sql_preview.update_sql(sql)

        except ValueError as e:
            # User-caused validation errors (e.g., missing table)
            logger.warning(f"Validation error: {e}")
            sql_preview.update_sql(f"-- Validation Error:\n-- {str(e)}")
        except Exception as e:
            # Unexpected errors
            logger.error(f"Error generating SQL: {e}", exc_info=True)
            sql_preview.update_sql(
                f"-- Error generating SQL:\n-- {str(e)}\n-- Check logs for details"
            )
            self.notify(
                f"Error: {str(e)}",
                severity="error",
                title="SQL Generation Error",
                timeout=5
            )

    def action_copy(self) -> None:
        """Copy SQL to clipboard (keyboard shortcut)."""
        sql_preview = self.query_one(SQLPreview)
        # Trigger the copy button
        self.run_worker(sql_preview._copy_to_clipboard())

    async def action_new(self) -> None:
        """Start a new query (clear all inputs)."""
        # Clear all widgets
        table_input = self.query_one(TableInput)
        column_list = self.query_one(ColumnList)
        filter_editor = self.query_one(FilterEditor)

        table_input.clear()
        await column_list.clear()
        await filter_editor.clear()

        # Reset query state
        self.query_state.clear()

        # Update preview
        self.update_preview()

    def action_help(self) -> None:
        """Show help information."""
        from sqltrans.ui.screens.help_screen import HelpScreen
        self.app.push_screen(HelpScreen())

    def action_quit(self) -> None:
        """Quit the application."""
        self.app.exit()
