"""Cached SQLAlchemy engines, keyed by connection URL.

Creating an engine per request wastes the connection pool and can leak pooled
connections until garbage collection. This module keeps a small process-level
cache so the pool is reused across the repeated calls an interactive session
makes. The cache is thread-safe.
"""

from __future__ import annotations

import threading
from typing import Any, Dict, Tuple

from sqlalchemy.engine import Engine

from sqltrans.db.introspection import create_db_engine
from sqltrans.utils.logging import get_logger

logger = get_logger("sqltrans.db.engine")

_engine_cache: Dict[Tuple[str, Tuple[Tuple[str, Any], ...]], Engine] = {}
_lock = threading.Lock()


def get_engine(url: str, **engine_kwargs: Any) -> Engine:
    """Return a cached engine for ``url``, creating one on first use.

    The same URL (and equivalent engine kwargs) always returns the same Engine
    and its connection pool, so interactive sessions reuse connections instead
    of rebuilding them. ``create_db_engine`` does not open a connection until
    first use, so caching an engine is cheap.

    Args:
        url: SQLAlchemy connection URL (may contain credentials — never logged).
        **engine_kwargs: Forwarded to ``create_engine`` (e.g. ``pool_pre_ping``).

    Returns:
        A SQLAlchemy ``Engine``.
    """
    key = (url, tuple(sorted(engine_kwargs.items())))
    with _lock:
        engine = _engine_cache.get(key)
        if engine is None:
            engine = create_db_engine(url, **engine_kwargs)
            _engine_cache[key] = engine
            logger.info("Created and cached engine for %s", _redact(url))
        return engine


def dispose_all() -> None:
    """Dispose every cached engine (e.g. on application shutdown)."""
    with _lock:
        for engine in _engine_cache.values():
            engine.dispose()
        _engine_cache.clear()
        logger.info("Disposed all cached engines")


def _redact(url: str) -> str:
    """Return the URL with any embedded credentials masked, for safe logging."""
    if "://" in url and "@" in url:
        scheme, rest = url.split("://", 1)
        _, _, tail = rest.partition("@")
        return f"{scheme}://***@{tail}" if tail else f"{scheme}://***"
    if "@" in url:
        _, _, tail = url.partition("@")
        return f"***@{tail}" if tail else "***"
    return url
