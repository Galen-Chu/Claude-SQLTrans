"""SQL dialect implementations."""

from sqltrans.sql.dialects.postgresql import PostgreSQLDialect
from sqltrans.sql.dialects.oracle import OracleDialect
from sqltrans.sql.dialects.generic import GenericDialect

__all__ = ["PostgreSQLDialect", "OracleDialect", "GenericDialect"]
