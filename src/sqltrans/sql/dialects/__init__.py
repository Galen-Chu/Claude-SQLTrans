"""SQL dialect implementations."""

from sqltrans.sql.dialects.postgresql import PostgreSQLDialect
from sqltrans.sql.dialects.oracle import OracleDialect
from sqltrans.sql.dialects.generic import GenericDialect


def get_dialect(name: str):
    """Get dialect instance by name.

    Args:
        name: Dialect name (postgresql, oracle, or generic)

    Returns:
        Dialect instance
    """
    dialects = {
        'postgresql': PostgreSQLDialect(),
        'oracle': OracleDialect(),
        'generic': GenericDialect()
    }
    return dialects.get(name.lower(), GenericDialect())


__all__ = ["PostgreSQLDialect", "OracleDialect", "GenericDialect", "get_dialect"]
