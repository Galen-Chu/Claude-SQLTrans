"""Dialect selector widget for choosing SQL dialect."""

from textual.app import ComposeResult
from textual.containers import Vertical
from textual.message import Message
from textual.widgets import RadioButton, RadioSet, Static


class DialectSelector(Vertical):
    """Widget for selecting SQL dialect (PostgreSQL, Oracle, Generic).

    Displays radio buttons for the three supported SQL dialects and emits
    events when the selection changes.

    Events:
        DialectChanged: Emitted when dialect selection changes

    Example:
        >>> selector = DialectSelector()
        >>> selector.current_dialect
        'generic'
    """

    DEFAULT_CSS = """
    DialectSelector {
        height: auto;
        border: solid $primary;
        padding: 1;
    }

    DialectSelector Static {
        text-style: bold;
        margin-bottom: 1;
    }

    DialectSelector RadioSet {
        height: auto;
    }
    """

    class DialectChanged(Message):
        """Message emitted when dialect changes."""

        def __init__(self, dialect: str) -> None:
            """Initialize message with new dialect.

            Args:
                dialect: New dialect name
            """
            self.dialect = dialect
            super().__init__()

    def __init__(self, default_dialect: str = "generic") -> None:
        """Initialize dialect selector.

        Args:
            default_dialect: Initial dialect to select (default: generic)
        """
        super().__init__()
        self.current_dialect = default_dialect

    def compose(self) -> ComposeResult:
        """Compose the widget layout.

        Returns:
            ComposeResult with label and radio buttons
        """
        yield Static("SQL Dialect:")
        with RadioSet(id="dialect-radio-set"):
            yield RadioButton("PostgreSQL", id="radio-postgresql")
            yield RadioButton("Oracle", id="radio-oracle")
            yield RadioButton("Generic SQL", id="radio-generic", value=True)

    def on_mount(self) -> None:
        """Set initial selection when widget is mounted."""
        # RadioButtons are already set up with default (Generic) selected
        # If we need a different default, we handle it here
        if self.current_dialect != "generic":
            self._update_selection()

    def on_radio_set_changed(self, event: RadioSet.Changed) -> None:
        """Handle radio button selection change.

        Args:
            event: RadioSet changed event
        """
        # Get the selected button's value
        if event.pressed.label.plain == "PostgreSQL":
            new_dialect = "postgresql"
        elif event.pressed.label.plain == "Oracle":
            new_dialect = "oracle"
        else:
            new_dialect = "generic"

        if new_dialect != self.current_dialect:
            self.current_dialect = new_dialect
            self.post_message(self.DialectChanged(new_dialect))

    def _update_selection(self) -> None:
        """Update radio button selection based on current_dialect."""
        # We can toggle buttons programmatically
        if self.current_dialect == "postgresql":
            btn = self.query_one("#radio-postgresql", RadioButton)
            btn.toggle()
        elif self.current_dialect == "oracle":
            btn = self.query_one("#radio-oracle", RadioButton)
            btn.toggle()
        else:
            btn = self.query_one("#radio-generic", RadioButton)
            if not btn.value:
                btn.toggle()

    def set_dialect(self, dialect: str) -> None:
        """Programmatically set the dialect.

        Args:
            dialect: Dialect to select (postgresql, oracle, generic)
        """
        if dialect not in ["postgresql", "oracle", "generic"]:
            return

        self.current_dialect = dialect
        self._update_selection()
