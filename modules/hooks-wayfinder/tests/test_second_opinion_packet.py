"""Exercise Second Opinion through the full catalog.

The full catalog matters here: a broader bulletin previously won before the
review-councils packet could handle an explicitly named council.
"""

from __future__ import annotations

import asyncio
from pathlib import Path

import pytest
from amplifier_module_hooks_wayfinder import WayfinderConfig, WayfinderHooks


CONTENT = Path(__file__).resolve().parents[3] / "content"
PACKET = CONTENT / "bulletins" / "second-opinion.md"
ACTION = 'read_file("@wayfinder:content/bulletins/second-opinion.md")'
COUNCIL_ACTION = 'read_file("@wayfinder:content/practices/review-councils.md")'


async def _submit(
    tmp_path: Path, prompt: str, *, later_turn: bool
) -> tuple[WayfinderHooks, object, str]:
    hooks = WayfinderHooks(
        WayfinderConfig(
            content_dir=str(CONTENT),
            declines_path=str(tmp_path / "declines.md"),
            surfaced_path=str(tmp_path / "surfaced.jsonl"),
            promoted_rotation=False,
        )
    )
    session_id = f"second-opinion-{'later' if later_turn else 'first'}"
    data = {"session_id": session_id, "parent_id": None}
    await hooks.on_session_start("session:start", data)
    if later_turn:
        await hooks.on_prompt_submit(
            "prompt:submit", {**data, "prompt": "Please implement this change."}
        )
    return (
        hooks,
        await hooks.on_prompt_submit("prompt:submit", {**data, "prompt": prompt}),
        session_id,
    )


@pytest.mark.parametrize("later_turn", [False, True], ids=["first", "later"])
@pytest.mark.parametrize(
    ("prompt", "expected_action"),
    [
        ("Get a design council to review this design.", COUNCIL_ACTION),
        (
            "Have multiple reviewers review this mockup with a design council.",
            COUNCIL_ACTION,
        ),
        ("Get a design council for fresh eyes on this design.", COUNCIL_ACTION),
        ("Get a council review for fresh eyes on this design.", COUNCIL_ACTION),
        # Slash council names have their own existing matcher limitation; this
        # bulletin must still leave the explicitly requested workflow alone.
        ("Use /design-council for fresh eyes on this mockup.", None),
        ("Use /product-council for independent reviewers.", None),
        ("Please get someone to review my change before I merge it.", None),
        ("Please have Alice review my work.", None),
        ("Use Second Opinion to independently review this work.", ACTION),
        ("Use second-opinion to review this work.", ACTION),
        ("Could I get fresh eyes on this work?", ACTION),
        ("Could I get independent reviewers to look at this?", ACTION),
        ("I want another perspective on this plan.", ACTION),
    ],
)
def test_full_catalog_routes_second_opinion_prompts(
    tmp_path: Path, later_turn: bool, prompt: str, expected_action: str | None
) -> None:
    hooks, result, session_id = asyncio.run(
        _submit(tmp_path, prompt, later_turn=later_turn)
    )
    injection = result.context_injection or ""

    if expected_action is None:
        assert ACTION not in injection
        assert "second-opinion" not in hooks._hinted.get(session_id, set())
    else:
        assert result.action == "inject_context"
        assert expected_action in injection
        assert (
            ACTION not in injection
            if expected_action == COUNCIL_ACTION
            else COUNCIL_ACTION not in injection
        )


def test_hard_decline_suppresses_an_explicit_second_opinion_request(
    tmp_path: Path,
) -> None:
    (tmp_path / "declines.md").write_text("- second-opinion\n", encoding="utf-8")
    hooks, result, session_id = asyncio.run(
        _submit(
            tmp_path,
            "Use Second Opinion to independently review this work.",
            later_turn=False,
        )
    )

    assert ACTION not in (result.context_injection or "")
    assert "second-opinion" in hooks._catalogs[session_id].declined_ids
    assert "second-opinion" not in hooks._hinted.get(session_id, set())


def test_signal_summon_distinguishes_explicit_requests_from_optional_offers(
    tmp_path: Path,
) -> None:
    _, result, _ = asyncio.run(
        _submit(
            tmp_path,
            "Use Second Opinion to independently review this work.",
            later_turn=False,
        )
    )
    injection = result.context_injection or ""

    assert "explicitly requested the matching action" in injection
    assert "without a duplicate Wayfinder ack" in injection
    assert "optional Wayfinder offer" in injection
    assert "wait for explicit ack" in injection
    assert "any direct user request" not in injection


def test_try_now_is_portable_and_does_not_assume_reviewer_aliases() -> None:
    frontmatter = PACKET.read_text(encoding="utf-8").split("---", 2)[1]
    try_now = frontmatter.split("try_now:", 1)[1].split("signals:", 1)[0]

    assert "Use Second Opinion for an independent review of this work." in try_now
    assert "Ask me which configured reviewers to use before launching any review." in try_now
    assert "Astra" not in try_now
    assert "Fable" not in try_now