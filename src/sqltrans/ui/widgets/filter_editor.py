"""Filter editor widget for building WHERE clause conditions."""

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.message import Message
from textual.widgets import Button, Input, Label, Select, Static

from sqltrans.models.filters import Filter, VALID_OPERATORS
from sqltrans.utils.validation import validate_identifier, validate_value


class FilterEditor(Vertical):
    """Widget for building and managing WHERE clause filters.

    Provides inputs for column name, operator selection, and value with
    validation. Displays current filters with remove buttons.

    Events:
        FiltersChanged: Emitted when filter list changes

    Example:
        >>> editor = FilterEditor()
        >>> editor.get_filters()
        [Filter("age", ">", 18)]
    """

    DEFAULT_CSS = """
    FilterEditor {
        height: auto;
        border: solid $primary;
        padding: 1;
    }

    FilterEditor .header {
        text-style: bold;
        margin-bottom: 1;
    }

    FilterEditor .add-section {
        height: auto;
        margin-bottom: 1;
    }

    FilterEditor .form-row {
        height: auto;
        margin-bottom: 1;
    }

    FilterEditor .form-row Label {
        width: 1fr;
    }

    FilterEditor .form-row Input {
        width: 2fr;
    }

    FilterEditor .form-row Select {
        width: 2fr;
    }

    FilterEditor .error {
        color: $error;
        margin-top: 1;
    }

    FilterEditor .filters-scroll {
        height: 10;
        border: solid $accent;
        margin-top: 1;
    }

    FilterEditor .filter-item {
        height: auto;
        padding: 0 1;
    }

    FilterEditor .filter-item Label {
        width: 3fr;
    }

    FilterEditor .filter-item Button {
        width: 1fr;
    }

    FilterEditor .empty-message {
        color: $text-muted;
        text-style: italic;
        padding: 1;
    }
    """

    class FiltersChanged(Message):
        """Message emitted when filters change."""

        def __init__(self, filters: list[Filter]) -> None:
            """Initialize message with filter list.

            Args:
                filters: Current list of filters
            """
            self.filters = filters
            super().__init__()

    def __init__(self, initial_filters: list[Filter] | None = None) -> None:
        """Initialize filter editor widget.

        Args:
            initial_filters: Initial list of filters
        """
        super().__init__()
        self.filters: list[Filter] = initial_filters or []

    def compose(self) -> ComposeResult:
        """Compose the widget layout.

        Returns:
            ComposeResult with header, form, and filter list
        """
        yield Static("Filters (WHERE):", classes="header")

        with Vertical(classes="add-section"):
            # Column name input
            with Horizontal(classes="form-row"):
                yield Label("Column:")
                yield Input(
                    placeholder="column_name",
                    id="filter-column-input",
                )

            # Operator selection
            with Horizontal(classes="form-row"):
                yield Label("Operator:")
                yield Select(
                    options=[
                        ("Equals (=)", "="),
                        ("Not Equals (!=)", "!="),
                        ("Less Than (<)", "<"),
                        ("Greater Than (>)", ">"),
                        ("Less or Equal (<=)", "<="),
                        ("Greater or Equal (>=)", ">="),
                        ("LIKE", "LIKE"),
                        ("IN (list)", "IN"),
                        ("IS NULL", "IS NULL"),
                        ("IS NOT NULL", "IS NOT NULL"),
                    ],
                    id="filter-operator-select",
                    allow_blank=False,
                )

            # Value input (disabled for NULL operators)
            with Horizontal(classes="form-row"):
                yield Label("Value:")
                yield Input(
                    placeholder="value or list (1,2,3)",
                    id="filter-value-input",
                )

            yield Button("Add Filter", id="add-filter-btn", variant="success")
            yield Static("", id="filter-error", classes="error")

        with VerticalScroll(classes="filters-scroll", id="filters-container"):
            self._render_filters()

    def _render_filters(self) -> ComposeResult:
        """Render the current filter list.

        Returns:
            ComposeResult with filter items or empty message
        """
        if not self.filters:
            yield Static("No filters", classes="empty-message")
        else:
            for i, filter_obj in enumerate(self.filters):
                with Horizontal(classes="filter-item"):
                    yield Label(str(filter_obj))
                    yield Button("Remove", id=f"remove-filter-{i}", variant="error")

    async def _refresh_filters(self) -> None:
        """Refresh the filter list display."""
        container = self.query_one("#filters-container", VerticalScroll)
        await container.remove_children()

        if not self.filters:
            await container.mount(Static("No filters", classes="empty-message"))
        else:
            for i, filter_obj in enumerate(self.filters):
                row = Horizontal(classes="filter-item")
                await row.mount(Label(str(filter_obj)))
                await row.mount(Button("Remove", id=f"remove-filter-{i}", variant="error"))
                await container.mount(row)

    def on_select_changed(self, event: Select.Changed) -> None:
        """Handle operator selection changes.

        Disables value input for IS NULL and IS NOT NULL operators.

        Args:
            event: Select changed event
        """
        if event.select.id != "filter-operator-select":
            return

        operator = event.value
        value_input = self.query_one("#filter-value-input", Input)

        # Disable value input for NULL operators
        if operator in ["IS NULL", "IS NOT NULL"]:
            value_input.disabled = True
            value_input.placeholder = "(no value needed)"
        else:
            value_input.disabled = False
            if operator == "IN":
                value_input.placeholder = "value1,value2,value3"
            else:
                value_input.placeholder = "value"

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses.

        Args:
            event: Button pressed event
        """
        if event.button.id == "add-filter-btn":
            await self._add_filter()
        elif event.button.id and event.button.id.startswith("remove-filter-"):
            # Extract index from button id
            index = int(event.button.id.split("-")[2])
            await self._remove_filter(index)

    async def _add_filter(self) -> None:
        """Add a new filter from the form inputs."""
        column_input = self.query_one("#filter-column-input", Input)
        operator_select = self.query_one("#filter-operator-select", Select)
        value_input = self.query_one("#filter-value-input", Input)
        error_label = self.query_one("#filter-error", Static)

        column_name = column_input.value.strip()
        operator = operator_select.value
        value_str = value_input.value.strip()

        # Validate column name
        if not column_name:
            error_label.update("Column name cannot be empty")
            return

        is_valid, error_msg = validate_identifier(column_name)
        if not is_valid:
            error_label.update(f"Invalid column: {error_msg}")
            return

        # Handle value based on operator
        value = None
        if operator not in ["IS NULL", "IS NOT NULL"]:
            if not value_str:
                error_label.update("Value is required for this operator")
                return

            # Determine value type
            if operator == "IN":
                # Parse as list
                is_valid, parsed_value, error_msg = validate_value(value_str, "list")
                if not is_valid:
                    error_label.update(f"Invalid list: {error_msg}")
                    return
                value = parsed_value
            else:
                # Try to parse as number first, then string
                is_valid_num, parsed_num, _ = validate_value(value_str, "number")
                if is_valid_num:
                    value = parsed_num
                else:
                    # Parse as string
                    is_valid_str, parsed_str, error_msg = validate_value(value_str, "string")
                    if not is_valid_str:
                        error_label.update(f"Invalid value: {error_msg}")
                        return
                    value = parsed_str

        # Create filter
        try:
            filter_obj = Filter(column=column_name, operator=operator, value=value)

            # Validate the filter
            is_valid, error_msg = filter_obj.validate()
            if not is_valid:
                error_label.update(f"Invalid filter: {error_msg}")
                return

            # Add filter
            self.filters.append(filter_obj)
            error_label.update("")

            # Clear inputs
            column_input.value = ""
            value_input.value = ""

            # Refresh display
            await self._refresh_filters()

            # Emit event
            self.post_message(self.FiltersChanged(self.filters.copy()))

        except Exception as e:
            error_label.update(f"Error creating filter: {str(e)}")

    async def _remove_filter(self, index: int) -> None:
        """Remove a filter by index.

        Args:
            index: Index of filter to remove
        """
        if 0 <= index < len(self.filters):
            self.filters.pop(index)

            # Refresh display
            await self._refresh_filters()

            # Emit event
            self.post_message(self.FiltersChanged(self.filters.copy()))

    def get_filters(self) -> list[Filter]:
        """Get the current list of filters.

        Returns:
            List of Filter objects
        """
        return self.filters.copy()

    async def set_filters(self, filters: list[Filter]) -> None:
        """Programmatically set the filter list.

        Args:
            filters: List of Filter objects
        """
        self.filters = filters.copy()
        await self._refresh_filters()

    async def clear(self) -> None:
        """Clear all filters."""
        self.filters = []
        await self._refresh_filters()
        self.post_message(self.FiltersChanged([]))
