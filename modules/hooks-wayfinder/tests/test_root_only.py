"""Root-only gate: wayfinder fires only in top-level (human) sessions.

parent_id rides on every event's data dict (kernel-merged via
set_default_fields): None for a root session, a string for any sub-agent /
recipe-step / fork-skill session. hooks-wayfinder must be a complete no-op
(HookResult(action="continue"), zero catalog assembly, zero injection) for
any session with a non-None parent_id, and must behave normally for a
genuine root session. A missing parent_id key is treated fail-safe-silent
(as a sub-session), and the whole gate is bypassable via root_only=False.
"""

from __future__ import annotations

import asyncio
from pathlib import Path

import pytest
from amplifier_module_hooks_wayfinder import WayfinderConfig, WayfinderHooks

_OFFER_MD = """\
---
id: root-only-test-offer
category: practice
headline: Test headline for the root-only gate
try_now:
  - "do the thing now"
action: read_file("@wayfinder:content/root-only-test-offer.md")
signals:
  on_event: session:start
---
Body text for the offer, unused by these tests.
"""


def _make_hooks(tmp_path: Path, **config_overrides: object) -> WayfinderHooks:
    """A hooks instance with one session:start offer, fully hermetic (no
    real ~/.amplifier/wayfinder reads/writes)."""
    content_dir = tmp_path / "content"
    content_dir.mkdir()
    (content_dir / "root-only-test-offer.md").write_text(_OFFER_MD, encoding="utf-8")

    kwargs: dict[str, object] = {
        "content_dir": str(content_dir),
        "declines_path": str(tmp_path / "declines.md"),
        "surfaced_path": str(tmp_path / "surfaced.jsonl"),
        "promoted_rotation": False,
    }
    kwargs.update(config_overrides)
    config = WayfinderConfig(**kwargs)  # type: ignore[arg-type]
    return WayfinderHooks(config)


def _run(coro):
    return asyncio.run(coro)


# --------------------------------------------------------------------------- #
# Sub-session: parent_id set to a string -> both handlers are a full no-op.
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("prompt", ["what's new?", "what else?"])
def test_sub_session_session_start_and_prompt_submit_are_no_ops(
    tmp_path: Path, prompt: str
) -> None:
    hooks = _make_hooks(tmp_path)
    data = {"session_id": "sub-session-1", "parent_id": "delegating-parent-id"}

    start_result = _run(hooks.on_session_start("session:start", data))
    assert start_result.action == "continue"
    # No catalog assembly happened for a gated-out sub-session.
    assert "sub-session-1" not in hooks._catalogs

    submit_result = _run(
        hooks.on_prompt_submit("prompt:submit", {**data, "prompt": prompt})
    )
    assert submit_result.action == "continue"
    assert submit_result.context_injection is None


# --------------------------------------------------------------------------- #
# Root session: parent_id is None -> handler proceeds normally (fires).
# --------------------------------------------------------------------------- #
def test_root_session_proceeds_and_surfaces_the_orienting_lead(tmp_path: Path) -> None:
    hooks = _make_hooks(tmp_path)
    data = {"session_id": "root-session-1", "parent_id": None}

    start_result = _run(hooks.on_session_start("session:start", data))
    assert start_result.action == "continue"
    # Unlike the sub-session case, assembly DID happen for a root session.
    assert "root-session-1" in hooks._catalogs

    submit_result = _run(
        hooks.on_prompt_submit("prompt:submit", {**data, "prompt": "what's new?"})
    )
    assert submit_result.action == "inject_context"
    assert submit_result.context_injection is not None
    assert "root-only-test-offer" in submit_result.context_injection
    assert "Test headline for the root-only gate" in submit_result.context_injection


# --------------------------------------------------------------------------- #
# Missing parent_id key entirely -> fail-safe: treated as sub-session, silent.
# --------------------------------------------------------------------------- #
def test_missing_parent_id_key_fails_safe_to_silent(tmp_path: Path) -> None:
    hooks = _make_hooks(tmp_path)
    data = {"session_id": "unknown-parentage-session"}  # no parent_id key at all

    start_result = _run(hooks.on_session_start("session:start", data))
    assert start_result.action == "continue"
    assert "unknown-parentage-session" not in hooks._catalogs

    submit_result = _run(
        hooks.on_prompt_submit("prompt:submit", {**data, "prompt": "what's new?"})
    )
    assert submit_result.action == "continue"
    assert submit_result.context_injection is None


# --------------------------------------------------------------------------- #
# root_only=False bypasses the gate even for a sub-session.
# --------------------------------------------------------------------------- #
def test_root_only_false_bypasses_gate_for_sub_session(tmp_path: Path) -> None:
    hooks = _make_hooks(tmp_path, root_only=False)
    data = {"session_id": "sub-session-bypassed", "parent_id": "some-delegating-parent"}

    start_result = _run(hooks.on_session_start("session:start", data))
    assert start_result.action == "continue"
    # Assembly DID happen this time; the gate was bypassed.
    assert "sub-session-bypassed" in hooks._catalogs

    submit_result = _run(
        hooks.on_prompt_submit("prompt:submit", {**data, "prompt": "what's new?"})
    )
    assert submit_result.action == "inject_context"
    assert submit_result.context_injection is not None
    assert "root-only-test-offer" in submit_result.context_injection
