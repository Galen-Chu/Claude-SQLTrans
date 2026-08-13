"""Tests for the named-connection manager (env-var-held URLs)."""

import pathlib

import pytest

from sqltrans.db import connections


def _write_conns(tmp_path, body: str) -> None:
    d = tmp_path / ".sqltrans"
    d.mkdir()
    (d / "connections.toml").write_text(body, encoding="utf-8")


def test_env_var_for_naming():
    assert connections.env_var_for("prod") == "SQLTRANS_CONN_PROD"
    assert connections.env_var_for("prod-db") == "SQLTRANS_CONN_PROD_DB"
    assert connections.env_var_for("warehouse_1") == "SQLTRANS_CONN_WAREHOUSE_1"


def test_list_connections(monkeypatch, tmp_path):
    _write_conns(
        tmp_path,
        '[connections.prod]\ndialect = "postgres"\nschema = "public"\n'
        'description = "prod replica"\n\n[connections.warehouse]\ndialect = "oracle"\n',
    )
    monkeypatch.setattr(pathlib.Path, "home", lambda: tmp_path)
    conns = connections.list_connections()
    assert set(conns) == {"prod", "warehouse"}
    assert conns["prod"].dialect == "postgres"
    assert conns["prod"].schema == "public"
    assert conns["warehouse"].schema is None


def test_resolve_url_from_env(monkeypatch, tmp_path):
    _write_conns(tmp_path, '[connections.prod]\ndialect = "postgres"\n')
    monkeypatch.setattr(pathlib.Path, "home", lambda: tmp_path)
    monkeypatch.setenv("SQLTRANS_CONN_PROD", "postgresql+psycopg://u:p@h/db")
    assert connections.resolve_url("prod") == "postgresql+psycopg://u:p@h/db"


def test_resolve_url_unknown_raises(monkeypatch, tmp_path):
    _write_conns(tmp_path, '[connections.prod]\ndialect = "postgres"\n')
    monkeypatch.setattr(pathlib.Path, "home", lambda: tmp_path)
    with pytest.raises(KeyError):
        connections.resolve_url("nope")


def test_resolve_url_env_missing_raises(monkeypatch, tmp_path):
    _write_conns(tmp_path, '[connections.prod]\ndialect = "postgres"\n')
    monkeypatch.setattr(pathlib.Path, "home", lambda: tmp_path)
    monkeypatch.delenv("SQLTRANS_CONN_PROD", raising=False)
    with pytest.raises(LookupError):
        connections.resolve_url("prod")
