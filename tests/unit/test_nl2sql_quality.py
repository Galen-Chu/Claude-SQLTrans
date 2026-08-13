"""Tests for NL→SQL few-shot injection and feedback recording."""

import json
import pathlib

from sqltrans.sql import nl2sql


def test_build_user_prompt_includes_few_shot_for_dialect():
    prompt = nl2sql._build_user_prompt("my request", schema=None, dialect="postgres")
    assert "Examples of the SQL style expected:" in prompt
    assert "Request:" in prompt
    assert "my request" in prompt


def test_build_user_prompt_no_few_shot_without_dialect():
    prompt = nl2sql._build_user_prompt("my request", schema=None, dialect=None)
    assert "Examples" not in prompt
    assert "my request" in prompt


def test_build_user_prompt_unknown_dialect_no_examples():
    prompt = nl2sql._build_user_prompt("req", schema=None, dialect="klingon")
    assert "Examples" not in prompt
    assert "req" in prompt


def test_record_feedback_writes_jsonl(monkeypatch, tmp_path):
    monkeypatch.setattr(pathlib.Path, "home", lambda: tmp_path)
    path = nl2sql.record_feedback(
        prompt="how many users",
        sql="SELECT COUNT(*) FROM users",
        accepted=True,
        dialect="postgres",
        validated=True,
        comment="good",
    )
    assert path.exists()
    entry = json.loads(path.read_text(encoding="utf-8").strip())
    assert entry["prompt"] == "how many users"
    assert entry["accepted"] is True
    assert entry["validated"] is True
    assert entry["dialect"] == "postgres"
    assert "timestamp" in entry
