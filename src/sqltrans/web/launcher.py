"""Web server launcher for SQLTrans GUI mode."""

import socket
import sys
import webbrowser
from pathlib import Path
from threading import Timer
from typing import Optional

import uvicorn

from sqltrans.utils.logging import get_logger

logger = get_logger("sqltrans.web.launcher")


def find_free_port(start_port: int = 8000, max_attempts: int = 10) -> int:
    """Find an available port starting from start_port.

    Args:
        start_port: Port number to start checking from
        max_attempts: Maximum number of ports to try

    Returns:
        An available port number

    Raises:
        RuntimeError: If no free port found within max_attempts
    """
    for port in range(start_port, start_port + max_attempts):
        try:
            # Try to bind to the port
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("127.0.0.1", port))
                logger.info(f"Found free port: {port}")
                return port
        except OSError:
            # Port is in use, try next one
            logger.debug(f"Port {port} is in use, trying next...")
            continue

    raise RuntimeError(
        f"Could not find a free port between {start_port} and {start_port + max_attempts - 1}"
    )


def open_browser(url: str) -> None:
    """Open the default web browser to the specified URL.

    Args:
        url: URL to open
    """
    try:
        logger.info(f"Opening browser to {url}")
        webbrowser.open(url)
    except Exception as e:
        logger.warning(f"Could not open browser automatically: {e}")
        print(f"\nCould not open browser automatically.")
        print(f"Please open your browser manually and navigate to: {url}")


def launch_web_gui(initial_dialect: str = "generic", port: Optional[int] = None) -> None:
    """Launch the web GUI server and open browser.

    Args:
        initial_dialect: Initial SQL dialect to use
        port: Port number to use (None = auto-find)
    """
    logger.info("Starting SQLTrans Web GUI")

    # Set initial dialect in the app
    from sqltrans.web.app import query_state

    query_state.set_dialect(initial_dialect)
    logger.info(f"Initial dialect set to: {initial_dialect}")

    # Find available port
    if port is None:
        try:
            port = find_free_port()
        except RuntimeError as e:
            logger.error(f"Error finding free port: {e}")
            print(f"Error: {e}", file=sys.stderr)
            print("\nTry specifying a port manually or use TUI mode (sqltrans --tui)")
            sys.exit(1)

    # Construct URL
    url = f"http://127.0.0.1:{port}"

    # Print startup message
    print("\n" + "=" * 60)
    print("SQLTrans Web GUI")
    print("=" * 60)
    print(f"\nServer starting on: {url}")
    print(f"SQL Dialect: {initial_dialect}")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60 + "\n")

    # Schedule browser opening after 1.5 seconds (give server time to start)
    Timer(1.5, open_browser, args=[url]).start()

    try:
        # Start the server (this blocks until Ctrl+C)
        uvicorn.run(
            "sqltrans.web.app:app",
            host="127.0.0.1",
            port=port,
            log_level="warning",  # Reduce console noise
            access_log=False,  # Disable access logs in console
        )
    except KeyboardInterrupt:
        print("\n\nShutting down SQLTrans Web GUI...")
        logger.info("Server stopped by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        print(f"\nServer error: {e}", file=sys.stderr)
        print("Check logs at ~/.sqltrans/logs/sqltrans.log for details")
        sys.exit(1)
