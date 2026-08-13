"""Tests for the SQLTrans CLI subcommands."""

import argparse

import pytest
from sqlalchemy import text

from sqltrans import __main__ as cli
from sqltrans.db import get_engine


def test_build_parser_has_subcommands():
    parser = cli.build_parser()
    # Empty argv yields a namespace with no func (main() prints help).
    ns = parser.parse_args([])
    assert not getattr(ns, "func", None)
    assert parser.format_help()


def _ns(**kw):
    base = {"query": None, "file": None}
    base.update(kw)
    return argparse.Namespace(**base)


def test_cmd_translate_oracle_to_postgres(capsys):
    args = _ns(read="oracle", write="postgres", query="SELECT NVL(x, 0) FROM t")
    cli.cmd_translate(args)
    assert "COALESCE" in capsys.readouterr().out


def test_cmd_translate_rejects_write(capsys):
    args = _ns(read=None, write=None, query="DELETE FROM t")
    with pytest.raises(SystemExit):
        cli.cmd_translate(args)
    assert "read-only" in capsys.readouterr().err


def _sqlite_url(tmp_path):
    url = f"sqlite:///{tmp_path / 'cli.db'}"
    engine = get_engine(url)
    with engine.connect() as conn:
        conn.execute(text("CREATE TABLE users (id INTEGER, name TEXT)"))
        conn.execute(text("INSERT INTO users VALUES (1, 'a'), (2, 'b')"))
        conn.commit()
    return url


def test_cmd_run_select(tmp_path, capsys):
    url = _sqlite_url(tmp_path)
    args = _ns(
        connection=None,
        url=url,
        query="SELECT * FROM users ORDER BY id",
        dialect=None,
        row_limit=100,
        timeout=1000,
    )
    cli.cmd_run(args)
    out = capsys.readouterr().out
    assert "id" in out and "name" in out


def test_cmd_run_rejects_delete(tmp_path, capsys):
    url = _sqlite_url(tmp_path)
    args = _ns(
        connection=None,
        url=url,
        query="DELETE FROM users",
        dialect=None,
        row_limit=100,
        timeout=1000,
    )
    with pytest.raises(SystemExit):
        cli.cmd_run(args)
    assert "read-only" in capsys.readouterr().err
