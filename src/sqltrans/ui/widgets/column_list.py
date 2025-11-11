"""Column list widget for managing SELECT clause columns."""

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.message import Message
from textual.widgets import Button, Input, Label, Static

from sqltrans.utils.validation import validate_identifier


class ColumnList(Vertical):
    """Widget for managing list of columns in SELECT clause.

    Allows adding and removing columns with validation. Shows current columns
    in a scrollable list with remove buttons for each.

    Events:
        ColumnsChanged: Emitted when column list changes

    Example:
        >>> column_list = ColumnList()
        >>> column_list.add_column("id")
        >>> column_list.get_columns()
        ['id']
    """

    DEFAULT_CSS = """
    ColumnList {
        height: auto;
        border: solid $primary;
        padding: 1;
    }

    ColumnList .header {
        text-style: bold;
        margin-bottom: 1;
    }

    ColumnList .add-section {
        height: auto;
        margin-bottom: 1;
    }

    ColumnList .add-controls {
        height: auto;
    }

    ColumnList .add-controls Input {
        width: 3fr;
    }

    ColumnList .add-controls Button {
        width: 1fr;
    }

    ColumnList .error {
        color: $error;
        margin-top: 1;
    }

    ColumnList .columns-scroll {
        height: 10;
        border: solid $accent;
        margin-top: 1;
    }

    ColumnList .column-item {
        height: auto;
        padding: 0 1;
    }

    ColumnList .column-item Label {
        width: 3fr;
    }

    ColumnList .column-item Button {
        width: 1fr;
    }

    ColumnList .empty-message {
        color: $text-muted;
        text-style: italic;
        padding: 1;
    }
    """

    class ColumnsChanged(Message):
        """Message emitted when columns change."""

        def __init__(self, columns: list[str]) -> None:
            """Initialize message with column list.

            Args:
                columns: Current list of columns
            """
            self.columns = columns
            super().__init__()

    def __init__(self, initial_columns: list[str] | None = None) -> None:
        """Initialize column list widget.

        Args:
            initial_columns: Initial list of columns
        """
        super().__init__()
        self.columns: list[str] = initial_columns or []

    def compose(self) -> ComposeResult:
        """Compose the widget layout.

        Returns:
            ComposeResult with header, add section, and column list
        """
        yield Static("Columns (SELECT):", classes="header")

        with Vertical(classes="add-section"):
            with Horizontal(classes="add-controls"):
                yield Input(
                    placeholder="Enter column name",
                    id="column-input",
                )
                yield Button("Add", id="add-column-btn", variant="success")
            yield Static("", id="column-error", classes="error")

        with VerticalScroll(classes="columns-scroll", id="columns-container"):
            self._render_columns()

    def _render_columns(self) -> ComposeResult:
        """Render the current column list.

        Returns:
            ComposeResult with column items or empty message
        """
        if not self.columns:
            yield Static("No columns (SELECT *)", classes="empty-message")
        else:
            for i, column in enumerate(self.columns):
                with Horizontal(classes="column-item"):
                    yield Label(column)
                    yield Button("Remove", id=f"remove-{i}", variant="error")

    async def _refresh_columns(self) -> None:
        """Refresh the column list display."""
        container = self.query_one("#columns-container", VerticalScroll)
        await container.remove_children()

        if not self.columns:
            await container.mount(Static("No columns (SELECT *)", classes="empty-message"))
        else:
            for i, column in enumerate(self.columns):
                row = Horizontal(classes="column-item")
                await row.mount(Label(column))
                await row.mount(Button("Remove", id=f"remove-{i}", variant="error"))
                await container.mount(row)

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses.

        Args:
            event: Button pressed event
        """
        if event.button.id == "add-column-btn":
            await self._add_column()
        elif event.button.id and event.button.id.startswith("remove-"):
            # Extract index from button id
            index = int(event.button.id.split("-")[1])
            await self._remove_column(index)

    async def _add_column(self) -> None:
        """Add a new column from the input field."""
        input_widget = self.query_one("#column-input", Input)
        error_label = self.query_one("#column-error", Static)

        column_name = input_widget.value.strip()

        # Validate
        if not column_name:
            error_label.update("Column name cannot be empty")
            return

        # Check for duplicates
        if column_name in self.columns:
            error_label.update(f"Column '{column_name}' already exists")
            return

        # Validate identifier
        is_valid, error_msg = validate_identifier(column_name)
        if not is_valid:
            error_label.update(error_msg)
            return

        # Add column
        self.columns.append(column_name)
        error_label.update("")
        input_widget.value = ""

        # Refresh display
        await self._refresh_columns()

        # Emit event
        self.post_message(self.ColumnsChanged(self.columns.copy()))

    async def _remove_column(self, index: int) -> None:
        """Remove a column by index.

        Args:
            index: Index of column to remove
        """
        if 0 <= index < len(self.columns):
            self.columns.pop(index)

            # Refresh display
            await self._refresh_columns()

            # Emit event
            self.post_message(self.ColumnsChanged(self.columns.copy()))

    def get_columns(self) -> list[str]:
        """Get the current list of columns.

        Returns:
            List of column names
        """
        return self.columns.copy()

    async def set_columns(self, columns: list[str]) -> None:
        """Programmatically set the column list.

        Args:
            columns: List of column names
        """
        self.columns = columns.copy()
        await self._refresh_columns()

    async def clear(self) -> None:
        """Clear all columns."""
        self.columns = []
        await self._refresh_columns()
        self.post_message(self.ColumnsChanged([]))
