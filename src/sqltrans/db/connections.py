"""Named database connections with environment-variable-held credentials.

Connection *metadata* (name, dialect, schema, description) lives in
``~/.sqltrans/connections.toml``. The actual connection URL — which may contain
credentials — is read from the environment variable ``SQLTRANS_CONN_<NAME>``,
so secrets are never written to disk by this tool.

Example ``connections.toml``::

    [connections.prod]
    dialect = "postgres"
    schema  = "public"
    description = "Production replica (read-only role)"

    [connections.warehouse]
    dialect = "oracle"

With the URL provided out-of-band, e.g. in the shell::

    export SQLTRANS_CONN_PROD="postgresql+psycopg://ro_user:****@host/db"

This module never reads, logs, or persists the URL beyond handing it to the
engine cache for the duration of a process.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

from sqlalchemy.engine import Engine

from sqltrans.db.engine import get_engine
from sqltrans.utils.logging import get_logger

logger = get_logger("sqltrans.db.connections")

try:  # Python 3.11+
    import tomllib
except ImportError:  # pragma: no cover - fallback for 3.10
    try:
        import tomli as tomllib  # type: ignore
    except ImportError:
        tomllib = None  # type: ignore

_ENV_PREFIX = "SQLTRANS_CONN_"


@dataclass
class ConnectionInfo:
    """Non-secret metadata for a named connection."""

    name: str
    dialect: Optional[str] = None
    schema: Optional[str] = None
    description: Optional[str] = None


def connections_path() -> Path:
    """Return the path to ``~/.sqltrans/connections.toml`` (creates the dir)."""
    config_dir = Path.home() / ".sqltrans"
    config_dir.mkdir(exist_ok=True)
    return config_dir / "connections.toml"


def env_var_for(name: str) -> str:
    """Return the env-var name that holds ``name``'s connection URL.

    Non-alphanumeric characters become ``_`` and the result is upper-cased, so
    ``"prod-db"`` → ``SQLTRANS_CONN_PROD_DB``.
    """
    suffix = "".join(ch if ch.isalnum() else "_" for ch in name).upper()
    return f"{_ENV_PREFIX}{suffix}"


def _read_metadata() -> Dict[str, dict]:
    """Read the ``[connections.*]`` tables as ``{name: metadata_dict}``."""
    path = connections_path()
    if not path.exists() or tomllib is None:
        return {}
    try:
        with open(path, "rb") as f:
            data = tomllib.load(f)
    except Exception as e:
        logger.warning("Could not read %s: %s", path, e)
        return {}
    conns = data.get("connections", {})
    if not isinstance(conns, dict):
        return {}
    return {name: meta for name, meta in conns.items() if isinstance(meta, dict)}


def list_connections() -> Dict[str, ConnectionInfo]:
    """List registered connections — metadata only, never URLs."""
    return {
        name: ConnectionInfo(
            name=name,
            dialect=meta.get("dialect"),
            schema=meta.get("schema"),
            description=meta.get("description"),
        )
        for name, meta in _read_metadata().items()
    }


def resolve_url(name: str) -> str:
    """Resolve a named connection's URL from its environment variable.

    Args:
        name: Registered connection name.

    Returns:
        The connection URL read from ``$SQLTRANS_CONN_<NAME>``.

    Raises:
        KeyError: If ``name`` is not registered in ``connections.toml``.
        LookupError: If registered but its env var is unset.
    """
    if name not in _read_metadata():
        raise KeyError(f"Unknown connection: {name!r}")
    var = env_var_for(name)
    url = os.environ.get(var)
    if not url:
        raise LookupError(
            f"Connection {name!r} requires its URL in ${var}, which is unset."
        )
    return url


def resolve_engine(name: str) -> Engine:
    """Resolve a named connection to a cached SQLAlchemy engine."""
    return get_engine(resolve_url(name))
