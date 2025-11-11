"""Clipboard utilities for copying SQL to system clipboard."""

import logging
from typing import Optional

try:
    import pyperclip
    PYPERCLIP_AVAILABLE = True
except ImportError:
    PYPERCLIP_AVAILABLE = False


logger = logging.getLogger(__name__)


def is_clipboard_available() -> bool:
    """Check if clipboard functionality is available.

    Tests whether pyperclip is installed and can access the system clipboard.
    This is useful for headless environments, SSH sessions, or systems without
    clipboard support.

    Returns:
        True if clipboard is available, False otherwise

    Example:
        >>> if is_clipboard_available():
        ...     copy_to_clipboard("SELECT * FROM users")
        ... else:
        ...     print("Clipboard not available")

    Notes:
        - Returns False if pyperclip is not installed
        - Returns False if clipboard access fails (headless, SSH, etc.)
        - Safe to call in any environment
    """
    if not PYPERCLIP_AVAILABLE:
        logger.debug("pyperclip module not available")
        return False

    try:
        # Try to access clipboard
        pyperclip.paste()
        return True
    except Exception as e:
        logger.debug(f"Clipboard not available: {e}")
        return False


def copy_to_clipboard(text: str) -> tuple[bool, Optional[str]]:
    """Copy text to system clipboard.

    Attempts to copy the provided text to the system clipboard using pyperclip.
    Handles errors gracefully and returns success status.

    Args:
        text: Text to copy to clipboard

    Returns:
        Tuple of (success: bool, error_message: Optional[str])
        - (True, None) if copy succeeded
        - (False, error_message) if copy failed

    Example:
        >>> success, error = copy_to_clipboard("SELECT * FROM users")
        >>> if success:
        ...     print("Copied to clipboard!")
        ... else:
        ...     print(f"Failed: {error}")

    Notes:
        - Never raises exceptions
        - Logs errors for debugging
        - Works cross-platform (Windows, macOS, Linux)
        - Returns False in headless/SSH environments
        - Returns descriptive error messages
    """
    if not PYPERCLIP_AVAILABLE:
        error = "pyperclip module not installed"
        logger.error(error)
        return False, error

    try:
        pyperclip.copy(text)
        logger.info(f"Copied {len(text)} characters to clipboard")
        return True, None
    except Exception as e:
        error = f"Failed to copy to clipboard: {str(e)}"
        logger.error(error)
        return False, error


def get_clipboard_content() -> tuple[bool, Optional[str]]:
    """Get current clipboard content.

    Retrieves the current text content from the system clipboard.
    This is primarily for testing and advanced use cases.

    Returns:
        Tuple of (success: bool, content: Optional[str])
        - (True, content) if retrieval succeeded
        - (False, None) if retrieval failed

    Example:
        >>> success, content = get_clipboard_content()
        >>> if success:
        ...     print(f"Clipboard contains: {content}")

    Notes:
        - Never raises exceptions
        - Returns None if clipboard is empty
        - Returns False in headless/SSH environments
    """
    if not PYPERCLIP_AVAILABLE:
        logger.error("pyperclip module not installed")
        return False, None

    try:
        content = pyperclip.paste()
        return True, content
    except Exception as e:
        logger.error(f"Failed to read from clipboard: {e}")
        return False, None
