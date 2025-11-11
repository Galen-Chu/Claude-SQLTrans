"""CLI entry point for SQLTrans application."""

import argparse
import sys
from pathlib import Path

from sqltrans.ui.app import SQLTransApp
from sqltrans.utils.config import load_config
from sqltrans.utils.logging import setup_logging, get_logger


def get_version() -> str:
    """Get the application version.

    Returns:
        Version string
    """
    # In a real implementation, this would read from pyproject.toml
    return "0.1.0"


def main() -> None:
    """Main entry point for SQLTrans CLI.

    Parses command-line arguments and launches the TUI application.

    Example:
        $ python -m sqltrans
        $ python -m sqltrans --dialect postgresql
        $ python -m sqltrans --version
    """
    parser = argparse.ArgumentParser(
        prog="sqltrans",
        description="SQLTrans - Interactive SQL Query Builder for the terminal",
        epilog="Build SQL queries with validation and syntax highlighting",
    )

    parser.add_argument(
        "--dialect",
        "-d",
        choices=["postgresql", "oracle", "generic"],
        help="Initial SQL dialect to use (default: from config or generic)",
    )

    parser.add_argument(
        "--version",
        "-v",
        action="version",
        version=f"SQLTrans {get_version()}",
    )

    args = parser.parse_args()

    # Set up logging
    setup_logging(log_level="INFO", console_level="WARNING")
    logger = get_logger("sqltrans.main")
    logger.info(f"SQLTrans {get_version()} starting")

    # Determine initial dialect
    initial_dialect = "generic"

    if args.dialect:
        # Use CLI argument
        initial_dialect = args.dialect
        logger.info(f"Using CLI dialect: {initial_dialect}")
    else:
        # Try to load from config
        try:
            config = load_config()
            initial_dialect = config.default_dialect
            logger.info(f"Loaded dialect from config: {initial_dialect}")
        except Exception as e:
            # Fall back to generic
            logger.debug(f"Could not load config: {e}, using default dialect")
            pass

    # Launch the application
    try:
        logger.info("Launching TUI application")
        app = SQLTransApp(initial_dialect=initial_dialect)
        app.run()
        logger.info("Application exited normally")
    except KeyboardInterrupt:
        # Clean exit on Ctrl+C
        logger.info("Application interrupted by user")
        print("\nExiting SQLTrans...")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        print(f"Error: {e}", file=sys.stderr)
        print("Check logs at ~/.sqltrans/logs/sqltrans.log for details", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
