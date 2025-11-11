"""SQL preview widget with syntax highlighting and export options."""

from pathlib import Path

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Static

from sqltrans.sql.formatter import format, highlight
from sqltrans.utils.clipboard import copy_to_clipboard


class SQLPreview(Vertical):
    """Widget for displaying SQL with syntax highlighting and export options.

    Shows formatted SQL with Rich syntax highlighting. Provides buttons for
    copying to clipboard and saving to file.

    Example:
        >>> preview = SQLPreview()
        >>> preview.update_sql("SELECT * FROM users")
    """

    DEFAULT_CSS = """
    SQLPreview {
        height: auto;
        border: solid $primary;
        padding: 1;
    }

    SQLPreview .header {
        text-style: bold;
        margin-bottom: 1;
    }

    SQLPreview .sql-display {
        height: 15;
        border: solid $accent;
        padding: 1;
        margin-bottom: 1;
        overflow-y: scroll;
    }

    SQLPreview .empty-sql {
        color: $text-muted;
        text-style: italic;
    }

    SQLPreview .button-row {
        height: auto;
    }

    SQLPreview .button-row Button {
        width: 1fr;
        margin: 0 1;
    }

    SQLPreview .status {
        height: auto;
        margin-top: 1;
    }

    SQLPreview .status-success {
        color: $success;
    }

    SQLPreview .status-error {
        color: $error;
    }
    """

    def __init__(self) -> None:
        """Initialize SQL preview widget."""
        super().__init__()
        self.current_sql = ""

    def compose(self) -> ComposeResult:
        """Compose the widget layout.

        Returns:
            ComposeResult with header, SQL display, and buttons
        """
        yield Static("SQL Preview:", classes="header")

        # SQL display area
        yield Static(
            "No query to display\n(Add table and columns to generate SQL)",
            id="sql-display",
            classes="sql-display empty-sql",
        )

        # Action buttons
        with Horizontal(classes="button-row"):
            yield Button("📋 Copy", id="copy-btn", variant="primary")
            yield Button("💾 Save", id="save-btn", variant="success")

        # Status message
        yield Static("", id="status-message", classes="status")

    def update_sql(self, sql: str) -> None:
        """Update the displayed SQL.

        Args:
            sql: SQL query string to display

        Example:
            >>> preview.update_sql("SELECT id FROM users WHERE age > 18")
        """
        self.current_sql = sql

        display = self.query_one("#sql-display", Static)

        if not sql or not sql.strip():
            display.update("No query to display")
            display.add_class("empty-sql")
        else:
            # Format and highlight the SQL
            try:
                formatted_sql = format(sql)
                highlighted = highlight(formatted_sql, theme="monokai")
                display.update(highlighted)
                display.remove_class("empty-sql")
            except Exception as e:
                # Fallback to plain text if highlighting fails
                display.update(sql)
                display.remove_class("empty-sql")

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses.

        Args:
            event: Button pressed event
        """
        if event.button.id == "copy-btn":
            await self._copy_to_clipboard()
        elif event.button.id == "save-btn":
            await self._save_to_file()

    async def _copy_to_clipboard(self) -> None:
        """Copy current SQL to clipboard."""
        status_label = self.query_one("#status-message", Static)

        if not self.current_sql or not self.current_sql.strip():
            status_label.update("❌ No SQL to copy")
            status_label.remove_class("status-success")
            status_label.add_class("status-error")
            return

        success, error = copy_to_clipboard(self.current_sql)

        if success:
            status_label.update("✓ Copied to clipboard!")
            status_label.remove_class("status-error")
            status_label.add_class("status-success")
        else:
            status_label.update(f"❌ Failed to copy: {error}")
            status_label.remove_class("status-success")
            status_label.add_class("status-error")

        # Clear status after 3 seconds
        self.set_timer(3.0, lambda: status_label.update(""))

    async def _save_to_file(self) -> None:
        """Save current SQL to file.

        Note: In a full implementation, this would show a file dialog.
        For now, it saves to a default location.
        """
        status_label = self.query_one("#status-message", Static)

        if not self.current_sql or not self.current_sql.strip():
            status_label.update("❌ No SQL to save")
            status_label.remove_class("status-success")
            status_label.add_class("status-error")
            return

        try:
            # Save to default location (could be enhanced with file dialog)
            save_path = Path.home() / "sqltrans_query.sql"

            with open(save_path, "w") as f:
                f.write(self.current_sql)

            status_label.update(f"✓ Saved to {save_path}")
            status_label.remove_class("status-error")
            status_label.add_class("status-success")

        except Exception as e:
            status_label.update(f"❌ Failed to save: {str(e)}")
            status_label.remove_class("status-success")
            status_label.add_class("status-error")

        # Clear status after 5 seconds
        self.set_timer(5.0, lambda: status_label.update(""))

    def get_sql(self) -> str:
        """Get the current SQL.

        Returns:
            Current SQL query string
        """
        return self.current_sql

    def clear(self) -> None:
        """Clear the SQL display."""
        self.update_sql("")
