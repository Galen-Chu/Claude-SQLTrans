"""Configuration management for SQLTrans."""

import logging
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Optional

try:
    import tomllib  # Python 3.11+
except ImportError:
    try:
        import tomli as tomllib  # Fallback for Python 3.10
    except ImportError:
        tomllib = None  # type: ignore

logger = logging.getLogger(__name__)


@dataclass
class Config:
    """SQLTrans configuration settings.

    Attributes:
        default_dialect: Default SQL dialect to use (postgresql, oracle, generic)
        theme: Syntax highlighting theme for SQL preview
        auto_format: Whether to auto-format SQL queries
        show_line_numbers: Whether to show line numbers in SQL preview
        recent_tables: List of recently used table names
        recent_columns: List of recently used column names
    """

    default_dialect: str = "generic"
    theme: str = "monokai"
    auto_format: bool = True
    show_line_numbers: bool = False
    recent_tables: list[str] = None  # type: ignore
    recent_columns: list[str] = None  # type: ignore

    def __post_init__(self) -> None:
        """Initialize default values after dataclass initialization."""
        if self.recent_tables is None:
            self.recent_tables = []
        if self.recent_columns is None:
            self.recent_columns = []


def get_config_path() -> Path:
    """Get the path to the configuration file.

    Returns:
        Path to ~/.sqltrans/config.toml

    Example:
        >>> path = get_config_path()
        >>> print(path)
        /home/user/.sqltrans/config.toml

    Notes:
        - Creates ~/.sqltrans directory if it doesn't exist
        - Returns platform-appropriate path (Windows, macOS, Linux)
    """
    config_dir = Path.home() / ".sqltrans"
    config_dir.mkdir(exist_ok=True)
    return config_dir / "config.toml"


def get_default_config() -> Config:
    """Get default configuration.

    Returns:
        Config instance with default settings

    Example:
        >>> config = get_default_config()
        >>> config.default_dialect
        'generic'
    """
    return Config()


def load_config() -> Config:
    """Load configuration from file.

    Loads configuration from ~/.sqltrans/config.toml. If the file doesn't
    exist or is corrupted, returns default configuration and creates a new
    config file.

    Returns:
        Config instance with loaded or default settings

    Example:
        >>> config = load_config()
        >>> config.default_dialect
        'postgresql'

    Notes:
        - Creates default config file if missing
        - Handles corrupted config gracefully
        - Never raises exceptions
        - Logs errors for debugging
    """
    config_path = get_config_path()

    # Check if config file exists
    if not config_path.exists():
        logger.info(f"Config file not found at {config_path}, creating default")
        config = get_default_config()
        save_config(config)
        return config

    # Check if tomllib is available
    if tomllib is None:
        logger.warning("tomllib/tomli not available, using default config")
        return get_default_config()

    # Try to load config
    try:
        with open(config_path, "rb") as f:
            data = tomllib.load(f)

        # Create Config from loaded data
        config = Config(
            default_dialect=data.get("default_dialect", "generic"),
            theme=data.get("theme", "monokai"),
            auto_format=data.get("auto_format", True),
            show_line_numbers=data.get("show_line_numbers", False),
            recent_tables=data.get("recent_tables", []),
            recent_columns=data.get("recent_columns", []),
        )

        logger.info(f"Loaded config from {config_path}")
        return config

    except Exception as e:
        logger.error(f"Failed to load config from {config_path}: {e}")
        logger.info("Using default configuration")
        return get_default_config()


def save_config(config: Config) -> bool:
    """Save configuration to file.

    Saves the provided configuration to ~/.sqltrans/config.toml in TOML format.

    Args:
        config: Config instance to save

    Returns:
        True if save succeeded, False otherwise

    Example:
        >>> config = Config(default_dialect="postgresql")
        >>> save_config(config)
        True

    Notes:
        - Creates config directory if needed
        - Writes in TOML format
        - Never raises exceptions
        - Logs errors for debugging
    """
    config_path = get_config_path()

    try:
        # Convert config to dict
        config_dict = asdict(config)

        # Generate TOML content manually (since tomli_w might not be available)
        toml_lines = ["# SQLTrans Configuration", ""]

        # Write string values
        toml_lines.append(f'default_dialect = "{config.default_dialect}"')
        toml_lines.append(f'theme = "{config.theme}"')

        # Write boolean values
        toml_lines.append(f"auto_format = {str(config.auto_format).lower()}")
        toml_lines.append(
            f"show_line_numbers = {str(config.show_line_numbers).lower()}"
        )

        # Write array values
        toml_lines.append("")
        toml_lines.append(f"recent_tables = {config.recent_tables}")
        toml_lines.append(f"recent_columns = {config.recent_columns}")

        # Write to file
        toml_content = "\n".join(toml_lines)
        with open(config_path, "w") as f:
            f.write(toml_content)

        logger.info(f"Saved config to {config_path}")
        return True

    except Exception as e:
        logger.error(f"Failed to save config to {config_path}: {e}")
        return False


def update_recent_table(table_name: str, max_recent: int = 10) -> None:
    """Update recent tables list with a new table name.

    Adds the table name to the recent tables list, moving it to the front
    if it already exists. Limits the list to max_recent items.

    Args:
        table_name: Table name to add to recent list
        max_recent: Maximum number of recent items to keep (default: 10)

    Example:
        >>> update_recent_table("users")
        >>> update_recent_table("orders")
        >>> config = load_config()
        >>> config.recent_tables
        ['orders', 'users']

    Notes:
        - Most recent item is first in list
        - Removes duplicates (keeps most recent)
        - Automatically saves config
    """
    config = load_config()

    # Remove if already exists
    if table_name in config.recent_tables:
        config.recent_tables.remove(table_name)

    # Add to front
    config.recent_tables.insert(0, table_name)

    # Limit size
    config.recent_tables = config.recent_tables[:max_recent]

    # Save
    save_config(config)


def update_recent_column(column_name: str, max_recent: int = 20) -> None:
    """Update recent columns list with a new column name.

    Adds the column name to the recent columns list, moving it to the front
    if it already exists. Limits the list to max_recent items.

    Args:
        column_name: Column name to add to recent list
        max_recent: Maximum number of recent items to keep (default: 20)

    Example:
        >>> update_recent_column("id")
        >>> update_recent_column("email")
        >>> config = load_config()
        >>> config.recent_columns
        ['email', 'id']

    Notes:
        - Most recent item is first in list
        - Removes duplicates (keeps most recent)
        - Automatically saves config
    """
    config = load_config()

    # Remove if already exists
    if column_name in config.recent_columns:
        config.recent_columns.remove(column_name)

    # Add to front
    config.recent_columns.insert(0, column_name)

    # Limit size
    config.recent_columns = config.recent_columns[:max_recent]

    # Save
    save_config(config)
