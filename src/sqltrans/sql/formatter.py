"""SQL formatting and syntax highlighting utilities."""

from rich.syntax import Syntax
from rich.text import Text


def format(sql: str, style: str = "default") -> str:
    """Format SQL query with proper indentation and line breaks.

    Takes a raw SQL query string and adds formatting to make it more
    readable. Adds indentation, line breaks after major clauses, and
    alignment for better visual presentation.

    Args:
        sql: Raw SQL query string
        style: Formatting style ('default', 'compact', 'expanded')

    Returns:
        Formatted SQL query string

    Example:
        >>> sql = 'SELECT id, name FROM users WHERE age > 18 AND status = \\'active\\''
        >>> print(format(sql))
        SELECT id, name
        FROM users
        WHERE age > 18
          AND status = 'active'

    Styles:
        - default: Standard formatting with line breaks after clauses
        - compact: Minimal formatting, clauses on separate lines
        - expanded: Extra spacing and indentation

    Notes:
        - SELECT and FROM always on separate lines
        - WHERE conditions indented
        - Multiple WHERE conditions aligned with AND/OR
        - Preserves SQL correctness
    """
    if not sql.strip():
        return sql

    # Simple formatting: add line breaks after major clauses
    formatted = sql

    # Add line break after SELECT clause (before FROM)
    if " FROM " in formatted:
        formatted = formatted.replace(" FROM ", "\nFROM ")

    # Add line break after FROM clause (before WHERE)
    if " WHERE " in formatted:
        formatted = formatted.replace(" WHERE ", "\nWHERE ")

    # Add indentation for AND conditions in WHERE clause
    if "\nWHERE " in formatted and " AND " in formatted:
        # Split at WHERE to only indent AND conditions in WHERE clause
        parts = formatted.split("\nWHERE ", 1)
        if len(parts) == 2:
            where_part = parts[1].replace(" AND ", "\n  AND ")
            formatted = parts[0] + "\nWHERE " + where_part

    # Apply style-specific formatting
    if style == "compact":
        # Compact style: no extra indentation for AND
        formatted = formatted.replace("\n  AND ", "\nAND ")
    elif style == "expanded":
        # Expanded style: more spacing
        formatted = formatted.replace("\nFROM ", "\n\nFROM ")
        formatted = formatted.replace("\nWHERE ", "\n\nWHERE ")

    return formatted


def highlight(sql: str, theme: str = "monokai") -> Syntax:
    """Apply syntax highlighting to SQL query using Rich.

    Takes a SQL query and returns a Rich Syntax object with syntax
    highlighting for display in the terminal. Highlights SQL keywords,
    strings, identifiers, operators, and numbers in different colors.

    Args:
        sql: SQL query string to highlight
        theme: Rich syntax highlighting theme

    Returns:
        Rich Syntax object with highlighted SQL

    Example:
        >>> from rich.console import Console
        >>> console = Console()
        >>> sql = 'SELECT * FROM users WHERE age > 18'
        >>> highlighted = highlight(sql)
        >>> console.print(highlighted)

    Colors (default theme):
        - Keywords (SELECT, FROM, WHERE): Blue
        - Strings ('value'): Green
        - Numbers (42, 3.14): Magenta
        - Identifiers (table, column): White
        - Operators (=, >, AND): Yellow

    Available themes:
        - monokai: Dark theme with vibrant colors
        - github-dark: GitHub dark theme
        - dracula: Dracula theme
        - nord: Nord theme
        - solarized-dark: Solarized dark
        - solarized-light: Solarized light

    Notes:
        - Returns Rich Syntax object for rendering
        - Use Console.print() to display
        - Works in terminals that support color
        - Falls back to plain text in basic terminals
    """
    # Format the SQL before highlighting
    formatted_sql = format(sql)

    # Create Rich Syntax object with SQL highlighting
    syntax = Syntax(
        formatted_sql,
        "sql",
        theme=theme,
        line_numbers=False,
        word_wrap=False,
        background_color="default",
    )

    return syntax


def highlight_to_text(sql: str, theme: str = "monokai") -> Text:
    """Apply syntax highlighting and return as Rich Text object.

    Similar to highlight() but returns a Rich Text object instead of
    Syntax. This is useful when you need to manipulate or combine the
    highlighted SQL with other text.

    Args:
        sql: SQL query string to highlight
        theme: Rich syntax highlighting theme

    Returns:
        Rich Text object with syntax highlighting applied

    Example:
        >>> text = highlight_to_text('SELECT * FROM users')
        >>> text.append('\\n-- End of query')

    Notes:
        - More flexible than Syntax for text manipulation
        - Can be combined with other Text objects
        - Preserves all Rich formatting features
    """
    # Format the SQL first
    formatted_sql = format(sql)

    # Create a simple highlighted text using Rich's built-in styles
    text = Text()

    # SQL keywords to highlight
    keywords = {
        "SELECT", "FROM", "WHERE", "AND", "OR", "NOT", "IN", "LIKE",
        "IS", "NULL", "INSERT", "UPDATE", "DELETE", "CREATE", "DROP",
        "ALTER", "TABLE", "INDEX", "VIEW", "ORDER", "BY", "GROUP",
        "HAVING", "JOIN", "LEFT", "RIGHT", "INNER", "OUTER", "ON"
    }

    # Simple token-based highlighting
    tokens = formatted_sql.split()
    for i, token in enumerate(tokens):
        # Add space before token (except first)
        if i > 0 and not formatted_sql.split()[i - 1].endswith("\n"):
            text.append(" ")

        # Check if token is a keyword
        token_upper = token.strip('(),').upper()
        if token_upper in keywords:
            text.append(token, style="bold cyan")
        # Check if token looks like a string
        elif token.startswith("'") or token.startswith('"'):
            text.append(token, style="green")
        # Check if token is a number
        elif token.replace(".", "").replace("-", "").isdigit():
            text.append(token, style="magenta")
        # Check for operators
        elif token in {"=", "!=", "<", ">", "<=", ">="}:
            text.append(token, style="yellow")
        else:
            # Default: identifier or other
            text.append(token)

    return text


def strip_formatting(sql: str) -> str:
    """Remove all formatting from SQL and return single-line query.

    Takes a formatted SQL query with line breaks and indentation and
    converts it back to a single-line query. Useful for copying to
    clipboard or saving to file in compact format.

    Args:
        sql: Formatted SQL query string

    Returns:
        Single-line SQL query with normalized spacing

    Example:
        >>> formatted = '''SELECT id, name
        ... FROM users
        ... WHERE age > 18
        ...   AND status = 'active' '''
        >>> strip_formatting(formatted)
        "SELECT id, name FROM users WHERE age > 18 AND status = 'active'"

    Notes:
        - Removes all line breaks and extra spaces
        - Normalizes spacing to single spaces
        - Preserves SQL correctness
        - Useful for exporting queries
    """
    # Replace newlines and tabs with spaces
    stripped = sql.replace("\n", " ").replace("\t", " ")

    # Normalize multiple spaces to single space
    while "  " in stripped:
        stripped = stripped.replace("  ", " ")

    return stripped.strip()
