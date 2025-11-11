"""Help screen showing keyboard shortcuts and usage information."""

from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header, Markdown, Static


HELP_MARKDOWN = """
# SQLTrans Help

## 🎯 Overview

SQLTrans is an interactive SQL query builder for support engineers. Build SELECT queries with WHERE clauses for multiple database systems without memorizing syntax.

## ⌨️ Keyboard Shortcuts

| Key | Action | Description |
|-----|--------|-------------|
| **q** | Quit | Exit the application |
| **c** | Copy | Copy SQL to clipboard |
| **n** | New Query | Clear all inputs and start fresh |
| **?** | Help | Show this help screen |
| **ESC** | Close | Close help/dialogs |
| **Tab** | Navigate | Move between input fields |
| **Enter** | Submit | Confirm input/click button |

## 📋 Workflow

### 1. Select SQL Dialect
Choose your target database at the top:
- **PostgreSQL** - PostgreSQL database
- **Oracle** - Oracle SQL database
- **Generic SQL** - ANSI SQL-92 compatible

### 2. Enter Table Name
Type the table name in the **Table Name** field. Real-time validation ensures it's a valid identifier.

### 3. Add Columns (Optional)
Add columns for the SELECT clause:
- Enter column name
- Click **Add** button
- Leave empty for `SELECT *`
- Remove columns with Remove button

### 4. Add Filters (Optional)
Build WHERE clause conditions:
- Enter **column name**
- Select **operator** (=, !=, <, >, <=, >=, LIKE, IN, IS NULL, IS NOT NULL)
- Enter **value** (disabled for IS NULL/IS NOT NULL)
- Click **Add Filter**
- Multiple filters combine with AND

### 5. View & Export SQL
The SQL preview updates automatically:
- **Copy button** - Copy to clipboard
- **Save button** - Save to file
- Syntax highlighting for readability

## 🔍 Operators

### Comparison Operators
- **=** - Equals (`WHERE age = 18`)
- **!=** - Not equals (`WHERE status != 'deleted'`)
- **<** - Less than (`WHERE price < 100`)
- **>** - Greater than (`WHERE qty > 0`)
- **<=** - Less or equal (`WHERE score <= 100`)
- **>=** - Greater or equal (`WHERE age >= 21`)

### Pattern Matching
- **LIKE** - Pattern match with wildcards
  - Example: `WHERE name LIKE '%Smith%'`
  - Use `%` for any characters, `_` for single character

### List Matching
- **IN** - Match any value in list
  - Example: `WHERE id IN (1,2,3)`
  - Enter comma-separated values

### Null Checks
- **IS NULL** - Check for null values
  - Example: `WHERE email IS NULL`
- **IS NOT NULL** - Check for non-null values
  - Example: `WHERE verified_at IS NOT NULL`

## 📝 Examples

### Find Customer by Email
```
Table: customers
Columns: (leave empty for SELECT *)
Filter: email = 'john@example.com'
```

### Recent Orders
```
Table: orders
Columns: id, amount, created_at
Filter: created_at > '2024-01-01'
```

### Active Premium Users
```
Table: users
Columns: id, email, tier
Filters:
  - status = 'active'
  - tier = 'premium'
```

### Pattern Search
```
Table: customers
Columns: id, name, email
Filter: name LIKE '%Smith%'
```

## 🔒 Security

- **SQL Injection Prevention** - All inputs validated and escaped
- **Identifier Validation** - Prevents dangerous patterns
- **Value Validation** - Detects injection attempts
- **Dialect-Specific Escaping** - Proper quoting for each database

## 💡 Tips

- Use **Tab** to navigate between fields quickly
- Press **c** to copy SQL without clicking
- Press **n** to clear and start a new query
- The preview updates automatically as you type
- Empty column list generates `SELECT *`
- All validation errors show inline
- Hover over buttons to see what they do

## 🐛 Troubleshooting

### Clipboard doesn't work
- On Linux, install `xclip` or `xsel`
- Check clipboard permissions

### Validation errors
- Identifiers must start with letter/underscore
- Identifiers can only contain letters, numbers, underscore
- No spaces or special characters in names
- Values are validated based on operator

### SQL looks wrong
- Check you selected the correct dialect
- PostgreSQL and Oracle have different identifier quoting
- Generic SQL uses ANSI SQL-92 standard

## 📚 Documentation

For more information:
- Check README.md in the project directory
- See `.spec-workflow/specs/` for detailed specifications
- Visit: https://github.com/sqltrans/sqltrans

---

**Press ESC or q to close this help screen**
"""


class HelpScreen(Screen):
    """Help screen with keyboard shortcuts and usage guide.

    Shows comprehensive help information including keyboard shortcuts,
    workflow, operators, examples, and troubleshooting tips.

    Example:
        >>> self.app.push_screen(HelpScreen())
    """

    CSS = """
    HelpScreen {
        align: center middle;
    }

    HelpScreen Container {
        width: 90%;
        height: 90%;
        background: $surface;
        border: thick $primary;
    }

    HelpScreen Vertical {
        width: 100%;
        height: 100%;
        padding: 1;
    }

    HelpScreen Markdown {
        width: 100%;
        height: 1fr;
    }

    HelpScreen Button {
        width: 20;
        margin: 1 2;
    }
    """

    BINDINGS = [
        ("escape", "close", "Close"),
        ("q", "close", "Close"),
    ]

    def compose(self) -> ComposeResult:
        """Compose the help screen layout.

        Returns:
            ComposeResult with header, help content, and buttons
        """
        with Container():
            with Vertical():
                yield Header(show_clock=False)
                yield Markdown(HELP_MARKDOWN)
                yield Button("Close (ESC)", variant="primary", id="close-btn")
                yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button presses.

        Args:
            event: Button pressed event
        """
        if event.button.id == "close-btn":
            self.action_close()

    def action_close(self) -> None:
        """Close the help screen."""
        self.app.pop_screen()
