"""Table name input widget with validation."""

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.message import Message
from textual.widgets import Input, Static

from sqltrans.utils.validation import validate_identifier


class TableInput(Vertical):
    """Widget for inputting and validating table names.

    Provides an input field with real-time validation feedback. Shows
    validation errors inline and emits events when valid table names are entered.

    Events:
        TableChanged: Emitted when a valid table name is entered

    Example:
        >>> table_input = TableInput()
        >>> table_input.get_table()
        'users'
    """

    DEFAULT_CSS = """
    TableInput {
        height: auto;
        border: solid $primary;
        padding: 1;
    }

    TableInput Static {
        text-style: bold;
        margin-bottom: 1;
    }

    TableInput .error {
        color: $error;
        margin-top: 1;
    }

    TableInput .warning {
        color: $warning;
        margin-top: 1;
    }

    TableInput Input.-valid {
        border: solid $success;
    }

    TableInput Input.-invalid {
        border: solid $error;
    }
    """

    class TableChanged(Message):
        """Message emitted when table name changes."""

        def __init__(self, table_name: str) -> None:
            """Initialize message with table name.

            Args:
                table_name: New table name
            """
            self.table_name = table_name
            super().__init__()

    def __init__(self, initial_table: str = "") -> None:
        """Initialize table input widget.

        Args:
            initial_table: Initial table name to display
        """
        super().__init__()
        self.current_table = initial_table
        self.is_valid = False

    def compose(self) -> ComposeResult:
        """Compose the widget layout.

        Returns:
            ComposeResult with label, input, and error message
        """
        yield Static("Table Name:")
        yield Input(
            placeholder="Enter table name (e.g., users, orders)",
            value=self.current_table,
            id="table-input",
        )
        yield Static("", id="table-error", classes="error")

    def on_input_changed(self, event: Input.Changed) -> None:
        """Handle input value changes with validation.

        Args:
            event: Input changed event
        """
        if event.input.id != "table-input":
            return

        table_name = event.value.strip()

        # Clear error initially
        error_label = self.query_one("#table-error", Static)
        input_widget = self.query_one("#table-input", Input)

        # Empty input is allowed but not valid for query
        if not table_name:
            error_label.update("")
            input_widget.remove_class("-valid", "-invalid")
            self.is_valid = False
            return

        # Validate the identifier
        is_valid, error_msg = validate_identifier(table_name)

        if is_valid:
            # Check if it's a warning (SQL keyword)
            if error_msg and "Warning" in error_msg:
                error_label.update(error_msg)
                error_label.remove_class("error")
                error_label.add_class("warning")
            else:
                error_label.update("")

            input_widget.remove_class("-invalid")
            input_widget.add_class("-valid")
            self.is_valid = True
            self.current_table = table_name

            # Emit event for valid table
            self.post_message(self.TableChanged(table_name))
        else:
            # Show error
            error_label.update(error_msg)
            error_label.remove_class("warning")
            error_label.add_class("error")
            input_widget.remove_class("-valid")
            input_widget.add_class("-invalid")
            self.is_valid = False

    def get_table(self) -> str:
        """Get the current valid table name.

        Returns:
            Current table name if valid, empty string otherwise
        """
        return self.current_table if self.is_valid else ""

    def set_table(self, table_name: str) -> None:
        """Programmatically set the table name.

        Args:
            table_name: Table name to set
        """
        input_widget = self.query_one("#table-input", Input)
        input_widget.value = table_name
        # The on_input_changed handler will handle validation

    def clear(self) -> None:
        """Clear the input field."""
        self.set_table("")
        self.current_table = ""
        self.is_valid = False
