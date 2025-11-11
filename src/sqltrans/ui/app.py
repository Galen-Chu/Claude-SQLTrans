"""Main SQLTrans Textual application."""

from textual.app import App

from sqltrans.ui.screens.query_builder import QueryBuilderScreen


class SQLTransApp(App):
    """SQLTrans - Interactive SQL Query Builder.

    A terminal-based application for building SQL queries with support for
    multiple database dialects. Features real-time validation, syntax
    highlighting, and clipboard integration.

    Example:
        >>> app = SQLTransApp()
        >>> app.run()
    """

    CSS = """
    Screen {
        background: $surface;
    }
    """

    TITLE = "SQLTrans - SQL Query Builder"
    SUB_TITLE = "Build SQL queries interactively"

    def __init__(self, initial_dialect: str = "generic") -> None:
        """Initialize SQLTrans application.

        Args:
            initial_dialect: Initial SQL dialect to use
        """
        super().__init__()
        self.initial_dialect = initial_dialect

    def on_mount(self) -> None:
        """Mount the application and show main screen."""
        # Push the query builder screen
        self.push_screen(QueryBuilderScreen())
