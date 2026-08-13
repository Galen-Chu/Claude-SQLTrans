"""Natural-language → SQL via Claude, routed through the read-only safety layer.

This is the v2 *assistance* layer. It asks Claude to draft a SQL statement from
a user's plain-language request, optionally made schema-aware with live table/
column metadata. The model's output is then **untrusted by default**: it is
parsed and run through the same AST read-only policy (Phase 1) before it is
returned as runnable SQL.

Flow::

    prompt ─▶ assemble (system + schema context) ─▶ Claude ─▶ raw text
                                                            │
                                          extract_sql ──────┘
                                                            │
                                  validate_read_only ◀──────┘
                                     │            │
                                  passes       rejects ─▶ validated=False
                                     │
                          (optional) transpile ─▶ validated SQL

The contract: ``NL2SQLResult.validated`` is True **only** when the draft passed
the read-only policy. Callers that execute the result must still re-validate (or
use :func:`sqltrans.db.executor.execute_read_only`, which validates again).
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol

from sqltrans.db.introspection import TableSchema, render_schema_for_prompt
from sqltrans.sql.transpiler import (
    TranspileError,
    UnsafeQueryError,
    normalize_dialect,
    transpile,
    validate_read_only,
)
from sqltrans.utils.logging import get_logger

logger = get_logger("sqltrans.sql.nl2sql")

# Per the claude-api skill: default to claude-opus-5, exact ID, no date suffix.
DEFAULT_MODEL = "claude-opus-5"
DEFAULT_MAX_TOKENS = 16_000

# SQL keywords that indicate a line/block is the start of a query.
_SQL_STARTERS = {"SELECT", "WITH"}

# Matches a fenced code block, optional ```sql language tag, capturing the body.
_FENCE_RE = re.compile(r"```(?:sql)?\s*\n?(.*?)```", re.IGNORECASE | re.DOTALL)

# Per-dialect few-shot examples (request -> SQL) injected into the user prompt
# to steer output toward idiomatic SQL for the target database. Kept small and
# high-signal; the draft is always re-validated by the read-only gate before it
# is returned as runnable SQL.
_FEW_SHOT: Dict[str, List[tuple[str, str]]] = {
    "postgres": [
        (
            "count active users grouped by plan",
            "SELECT plan, COUNT(*) FROM users WHERE active IS TRUE GROUP BY plan",
        ),
        (
            "orders for user 42 in the last 7 days",
            "SELECT * FROM orders WHERE user_id = 42 "
            "AND created_at >= CURRENT_DATE - INTERVAL '7 days'",
        ),
    ],
    "oracle": [
        (
            "count active users grouped by plan",
            "SELECT plan, COUNT(*) FROM users WHERE active = 1 GROUP BY plan",
        ),
        (
            "orders for user 42 in the last 7 days",
            "SELECT * FROM orders WHERE user_id = 42 AND created_at >= SYSDATE - 7",
        ),
    ],
    "mysql": [
        (
            "count active users grouped by plan",
            "SELECT plan, COUNT(*) FROM users WHERE active = 1 GROUP BY plan",
        ),
        (
            "orders for user 42 in the last 7 days",
            "SELECT * FROM orders WHERE user_id = 42 "
            "AND created_at >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)",
        ),
    ],
    "tsql": [
        (
            "count active users grouped by plan",
            "SELECT plan, COUNT(*) FROM users WHERE active = 1 GROUP BY plan",
        ),
        (
            "orders for user 42 in the last 7 days",
            "SELECT * FROM orders WHERE user_id = 42 "
            "AND created_at >= DATEADD(day, -7, GETDATE())",
        ),
    ],
}


def _few_shot_for(dialect: Optional[str]) -> List[tuple[str, str]]:
    """Return few-shot examples for a dialect (alias-normalized), or ``[]``."""
    if not dialect:
        return []
    try:
        return _FEW_SHOT.get(normalize_dialect(dialect), [])
    except ValueError:
        return []


# --------------------------------------------------------------------------- #
# Errors
# --------------------------------------------------------------------------- #


class NL2SQLError(Exception):
    """Raised when the LLM call itself fails (network, auth, refusal, ...)."""


# --------------------------------------------------------------------------- #
# Result
# --------------------------------------------------------------------------- #


@dataclass
class NL2SQLResult:
    """Outcome of a natural-language → SQL conversion.

    Attributes:
        sql: The validated SQL string, or ``None`` if no safe SQL was produced.
        validated: True iff ``sql`` passed the read-only policy. Always False
            when ``sql`` is None.
        warnings: Non-fatal notes (e.g. transpile applied, draft rejected,
            no SQL extractable). Surface to the user.
        raw: The model's full text response, for debugging/audit.
        dialect: The resolved output dialect, if any.
    """

    sql: Optional[str] = None
    validated: bool = False
    warnings: List[str] = field(default_factory=list)
    raw: str = ""
    dialect: Optional[str] = None


# --------------------------------------------------------------------------- #
# LLM client abstraction (so tests inject a fake; no API calls needed)
# --------------------------------------------------------------------------- #


class LLMClient(Protocol):
    """Minimal LLM interface: system + user prompt in, text out."""

    def complete(
        self,
        system: str,
        user: str,
        *,
        model: str,
        max_tokens: int,
    ) -> str:
        ...


class AnthropicLLMClient:
    """LLM client backed by the Anthropic SDK (Claude).

    The SDK client is constructed lazily with no arguments, so it resolves
    credentials the standard way (``ANTHROPIC_API_KEY``, an ``ant auth login``
    profile, etc.). Importing this module does not require a key; only calling
    :meth:`complete` does.
    """

    def __init__(self, api_key: Optional[str] = None) -> None:
        import anthropic

        self._client = (
            anthropic.Anthropic(api_key=api_key) if api_key else anthropic.Anthropic()
        )

    def complete(
        self,
        system: str,
        user: str,
        *,
        model: str,
        max_tokens: int,
    ) -> str:
        response = self._client.messages.create(
            model=model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": user}],
            thinking={"type": "adaptive"},
        )

        # Opus 5 / Fable 5 safety classifiers can decline a request. Check before
        # reading content (a refusal yields an empty content array).
        if response.stop_reason == "refusal":
            raise NL2SQLError(
                "The model declined to generate SQL for this request."
            )

        return "".join(block.text for block in response.content if block.type == "text")


# --------------------------------------------------------------------------- #
# Prompt assembly
# --------------------------------------------------------------------------- #


_SYSTEM_PROMPT = """\
You are a SQL assistant for customer-support engineers. Convert the user's \
plain-language request into a single read-only SQL SELECT statement that \
answers their question.

Hard requirements:
- Output ONLY a single read-only SELECT statement. Never INSERT, UPDATE, DELETE, \
TRUNCATE, CREATE, DROP, ALTER, GRANT, COMMIT, or any DDL/DML/DCL/TCL.
- Never use SELECT ... INTO (it creates a table).
- Output exactly one statement. Do not chain statements with semicolons.
- Respond with the SQL in a single fenced ```sql code block and nothing else. \
If the request cannot be answered as a single read-only SELECT, respond with a \
plain sentence explaining why and output no code block.
- Use only the tables and columns provided in the schema, if one is given.
- If a target dialect is specified, write valid SQL for that dialect.
"""


def _build_system_prompt(dialect: Optional[str]) -> str:
    if not dialect:
        return _SYSTEM_PROMPT
    target = normalize_dialect(dialect)
    return _SYSTEM_PROMPT + f"\nTarget dialect: {target}.\n"


def _build_user_prompt(
    prompt: str,
    schema: Optional[List[TableSchema]],
    dialect: Optional[str] = None,
) -> str:
    parts: List[str] = []
    if schema:
        rendered = render_schema_for_prompt(schema)
        if rendered:
            parts.append(rendered)
            parts.append("")  # blank line between schema and request

    few_shot = _few_shot_for(dialect)
    if few_shot:
        parts.append("Examples of the SQL style expected:")
        for req, sql in few_shot:
            parts.append(f"  Request: {req}")
            parts.append(f"  SQL: {sql}")
        parts.append("")

    parts.append("Request:")
    parts.append(prompt)
    return "\n".join(parts)


# --------------------------------------------------------------------------- #
# SQL extraction from the model's text response
# --------------------------------------------------------------------------- #


def extract_sql(text: str) -> Optional[str]:
    """Pull a SQL statement out of an LLM response.

    Handles fenced code blocks (```sql ... ```), bare SQL with no surrounding
    prose, and prose-prefixed SQL. Returns ``None`` if no SQL is found — which
    the caller treats as "the model declined / had nothing to offer."

    The extraction is best-effort; whatever it returns is **always** re-parsed
    and policy-checked by the caller, so a wrong extraction cannot leak unsafe
    SQL through.
    """
    if not text or not text.strip():
        return None

    # 1. Prefer fenced blocks; if there are several, the last is the final answer.
    fences = _FENCE_RE.findall(text)
    if fences:
        return fences[-1].strip()

    # 2. No fence: maybe the whole response is the SQL.
    stripped = text.strip()
    first_token = stripped.split(None, 1)[0].upper() if stripped else ""
    if first_token in _SQL_STARTERS or stripped.startswith("("):
        return stripped

    # 3. Otherwise scan for the first line that starts a statement.
    for line in stripped.splitlines():
        line = line.strip()
        if not line:
            continue
        token = line.split(None, 1)[0].upper()
        if token in _SQL_STARTERS:
            return line

    return None


# --------------------------------------------------------------------------- #
# Feedback ("did this answer the question?" loop)
# --------------------------------------------------------------------------- #


def _feedback_path() -> Path:
    """Return the path to the append-only feedback log."""
    return Path.home() / ".sqltrans" / "feedback.jsonl"


def record_feedback(
    *,
    prompt: str,
    sql: Optional[str],
    accepted: bool,
    dialect: Optional[str] = None,
    validated: bool = False,
    comment: str = "",
) -> Path:
    """Append a labelled feedback record to ``~/.sqltrans/feedback.jsonl``.

    Drives the "did this answer the question?" control so future NL→SQL quality
    work has real signal. The file is append-only JSON Lines.

    Args:
        prompt: The original natural-language request.
        sql: The SQL that was produced (``None`` if none was generated).
        accepted: True if the user accepted the result as correct.
        dialect: The dialect the draft targeted, if any.
        validated: Whether the draft passed the read-only policy.
        comment: Optional free-text note from the user.

    Returns:
        The path the record was written to.
    """
    path = _feedback_path()
    path.parent.mkdir(exist_ok=True)
    entry: Dict[str, Any] = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "prompt": prompt,
        "sql": sql,
        "accepted": bool(accepted),
        "dialect": dialect,
        "validated": bool(validated),
        "comment": comment,
    }
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    logger.info("Recorded NL→SQL feedback (accepted=%s)", entry["accepted"])
    return path


# --------------------------------------------------------------------------- #
# Main entry point
# --------------------------------------------------------------------------- #


def nl2sql(
    prompt: str,
    *,
    dialect: Optional[str] = None,
    schema: Optional[List[TableSchema]] = None,
    llm: Optional[LLMClient] = None,
    model: str = DEFAULT_MODEL,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    transpile_to: Optional[str] = None,
) -> NL2SQLResult:
    """Convert a natural-language request into validated, read-only SQL.

    Args:
        prompt: The user's natural-language request.
        dialect: Source/target dialect hint (name or alias).
        schema: Optional live schema (from
            :func:`sqltrans.db.introspection.introspect`) for schema-aware SQL.
        llm: Optional LLM client (inject a fake in tests). Defaults to
            :class:`AnthropicLLMClient`, which calls Claude.
        model: Claude model ID. Defaults to ``claude-opus-5``.
        max_tokens: Output token budget for the LLM call.
        transpile_to: If given, transpile the validated draft to this dialect
            before returning.

    Returns:
        An :class:`NL2SQLResult`. ``validated`` is True only when the draft
        passed the read-only policy.

    Raises:
        NL2SQLError: If the LLM call itself fails (network, auth, refusal).
        ValueError: If a dialect name is unrecognized.
    """
    if not prompt or not prompt.strip():
        raise ValueError("prompt cannot be empty")

    client = llm if llm is not None else AnthropicLLMClient()

    system = _build_system_prompt(dialect)
    user = _build_user_prompt(prompt, schema, dialect)

    logger.info("Calling LLM for NL→SQL (model=%s)", model)
    try:
        raw = client.complete(
            system=system, user=user, model=model, max_tokens=max_tokens
        )
    except NL2SQLError:
        raise
    except Exception as e:  # SDK network/auth errors, etc.
        raise NL2SQLError(f"LLM call failed: {e}") from e

    draft = extract_sql(raw)

    # No SQL extractable — model likely explained why it couldn't help.
    if draft is None:
        return NL2SQLResult(
            sql=None,
            validated=False,
            warnings=["The model did not produce a SQL statement.", f"Model said: {raw.strip()[:200]}"],
            raw=raw,
        )

    # The load-bearing safety gate: validate the draft against the AST policy.
    try:
        validate_read_only(draft, dialect=dialect)
    except UnsafeQueryError as e:
        logger.warning("Rejected NL→SQL draft (unsafe): %s", e)
        return NL2SQLResult(
            sql=None,
            validated=False,
            warnings=[f"Draft rejected by read-only policy: {e}"],
            raw=raw,
        )
    except TranspileError as e:
        logger.warning("NL→SQL draft did not parse: %s", e)
        return NL2SQLResult(
            sql=None,
            validated=False,
            warnings=[f"Draft did not parse as SQL: {e}"],
            raw=raw,
        )

    # Validated. Optionally transpile to a target dialect.
    final_sql = draft
    warnings: List[str] = []
    out_dialect = normalize_dialect(dialect)

    if transpile_to:
        target = normalize_dialect(transpile_to)
        try:
            final_sql = transpile(draft, read=dialect, write=target, pretty=True)
            out_dialect = target
            warnings.append(
                f"Transpiled from {normalize_dialect(dialect) or 'default'} to {target}."
            )
        except Exception as e:
            # Transpile is best-effort; fall back to the source-dialect draft,
            # which already passed validation.
            warnings.append(
                f"Could not transpile to {target}: {e}. Returning source SQL."
            )

    logger.info("NL→SQL succeeded (validated=True)")
    return NL2SQLResult(
        sql=final_sql,
        validated=True,
        warnings=warnings,
        raw=raw,
        dialect=out_dialect,
    )
