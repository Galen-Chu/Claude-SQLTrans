"""Logging utilities for SQLTrans.

Provides centralized logging configuration with file and console handlers.
Logs are written to ~/.sqltrans/logs/ with automatic rotation.
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from typing import Optional


def get_log_directory() -> Path:
    """Get the log directory path, creating it if necessary.

    Returns:
        Path to log directory (~/.sqltrans/logs/)

    Raises:
        OSError: If directory cannot be created
    """
    # Use home directory
    home = Path.home()
    log_dir = home / ".sqltrans" / "logs"

    # Create directory if it doesn't exist
    try:
        log_dir.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        # If we can't create in home directory, use temp directory
        import tempfile
        log_dir = Path(tempfile.gettempdir()) / "sqltrans" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)

    return log_dir


def setup_logging(
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    console_level: str = "WARNING",
) -> logging.Logger:
    """Set up logging configuration for SQLTrans.

    Creates both file and console handlers. File logs include DEBUG and above,
    console logs include WARNING and above by default.

    Args:
        log_level: Logging level for file handler (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional custom log file name (default: sqltrans.log)
        console_level: Logging level for console handler

    Returns:
        Configured logger instance

    Example:
        >>> logger = setup_logging(log_level="DEBUG")
        >>> logger.info("Application started")
    """
    # Get the root logger for sqltrans
    logger = logging.getLogger("sqltrans")

    # Don't propagate to root logger
    logger.propagate = False

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Set logger level to DEBUG to capture all messages
    logger.setLevel(logging.DEBUG)

    # Create log directory and file
    log_dir = get_log_directory()
    if log_file is None:
        log_file = "sqltrans.log"
    log_path = log_dir / log_file

    # File handler with rotation (10 MB max, keep 5 backups)
    try:
        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setLevel(getattr(logging, log_level.upper()))

        # Detailed format for file logs
        file_formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    except (OSError, IOError) as e:
        # If file logging fails, log to stderr
        print(f"Warning: Could not set up file logging: {e}", file=sys.stderr)

    # Console handler for warnings and errors
    console_handler = logging.StreamHandler(sys.stderr)
    console_handler.setLevel(getattr(logging, console_level.upper()))

    # Simpler format for console
    console_formatter = logging.Formatter(
        "%(levelname)s: %(message)s"
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    logger.debug(f"Logging initialized. Log file: {log_path}")

    return logger


def get_logger(name: str = "sqltrans") -> logging.Logger:
    """Get a logger instance.

    Args:
        name: Logger name (default: sqltrans)

    Returns:
        Logger instance

    Example:
        >>> logger = get_logger("sqltrans.ui")
        >>> logger.debug("Rendering widget")
    """
    return logging.getLogger(name)


class LoggingMixin:
    """Mixin class to add logging to any class.

    Provides a logger property that automatically uses the class name.

    Example:
        >>> class MyWidget(LoggingMixin):
        ...     def do_something(self):
        ...         self.logger.info("Doing something")
    """

    @property
    def logger(self) -> logging.Logger:
        """Get logger for this class.

        Returns:
            Logger instance with class-qualified name
        """
        class_name = self.__class__.__name__
        module_name = self.__class__.__module__
        return get_logger(f"{module_name}.{class_name}")


def log_exception(logger: logging.Logger, message: str, exc: Exception) -> None:
    """Log an exception with full traceback.

    Args:
        logger: Logger instance
        message: Error message
        exc: Exception instance

    Example:
        >>> try:
        ...     risky_operation()
        ... except Exception as e:
        ...     log_exception(logger, "Operation failed", e)
    """
    logger.error(f"{message}: {exc!r}", exc_info=True)


def log_function_call(logger: logging.Logger, func_name: str, **kwargs: object) -> None:
    """Log a function call with arguments.

    Args:
        logger: Logger instance
        func_name: Function name
        **kwargs: Function arguments to log

    Example:
        >>> log_function_call(logger, "build_query", table="users", columns=["id", "name"])
    """
    args_str = ", ".join(f"{k}={v!r}" for k, v in kwargs.items())
    logger.debug(f"Calling {func_name}({args_str})")


# Initialize default logger when module is imported
_default_logger = setup_logging()
