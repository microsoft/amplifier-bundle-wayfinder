"""Exercise the real autocompletion packet through the catalog consumer."""

from __future__ import annotations

import asyncio
from pathlib import Path

import pytest
from amplifier_module_hooks_wayfinder import (
    WayfinderConfig,
    WayfinderHooks,
    load_catalog,
)

CONTENT = Path(__file__).resolve().parents[3] / "content"
ACTION = 'read_file("@wayfinder:content/bulletins/autocompletion.md")'
SWITCH_MODELS_ACTION = 'read_file("@wayfinder:content/bulletins/current.md")'
ITEM = load_catalog([("default", CONTENT)], curate=False)["autocompletion"]


@pytest.mark.parametrize(
    ("pattern_index", "phrasing"),
    [
        (0, "Tell me about Amplifier autocompletion."),
        (0, "Does Amplifier's tab completion handle arguments?"),
        (0, "Is Amplifier auto-completing command names now?"),
        (1, "How do slash command menus in Amplifier work?"),
        (1, "Show me slash completion in Amplifier."),
        (1, "Can I turn off slash popups for Amplifier?"),
        (2, "How do I get shell autocomplete for Amplifier working in fish?"),
        (2, "Explain Bash tab completion for Amplifier."),
        (2, "Does Zsh autocompletion for Amplifier need setup?"),
        (3, "Can I disable argument popups in Amplifier?"),
        (3, "Are command suggestions available in Amplifier?"),
        (3, "Can I type custom values with argument suggestions in Amplifier?"),
    ],
)
def test_signal_covers_real_phrasing(pattern_index: int, phrasing: str) -> None:
    assert ITEM.prompt_patterns[pattern_index].search(phrasing)


@pytest.mark.parametrize(
    "phrasing",
    [
        "Install Amplifier completion.",
        "How do I see a list of Amplifier slash commands?",
        "What argument choices does Amplifier offer for /provider?",
        "Turn off Amplifier's slash popup.",
        "Turn off Amplifier’s slash popup.",
        "How do I install shell completion for Amplifier?",
        "Where is Amplifier’s slash menu?",
        "Which options does Amplifier offer for /provider?",
    ],
)
def test_signal_covers_direct_completion_requests(phrasing: str) -> None:
    assert any(pattern.search(phrasing) for pattern in ITEM.prompt_patterns)


@pytest.mark.parametrize(
    "phrasing",
    [
        "Autocomplete the shipping address in this web form.",
        "Complete the task before lunch.",
        "My Tab key changes focus between text fields.",
        "Add autocomplete to the search box.",
        "Use bash to complete the report.",
        "Configure Discord slash command menus.",
        "Add shell autocomplete to my CLI.",
        "Add command suggestions to my editor.",
        "Can Amplifier autocomplete my code?",
        "Can Amplifier autocomplete code in my editor?",
        "Does Amplifier autocomplete the address field?",
        "Can Amplifier autocomplete my search form?",
        "Can Amplifier autocompletion help my code editor?",
        "Does Amplifier autocompletion suggest Python code?",
        "Enable Amplifier autocompletion for my search form.",
        "Install autocomplete for my editor.",
        "Use Amplifier to add shell completion to my own CLI.",
    ],
)
def test_signals_ignore_unrelated_completion(phrasing: str) -> None:
    assert not any(pattern.search(phrasing) for pattern in ITEM.prompt_patterns)


def test_signal_keeps_terminal_completion_relevant() -> None:
    assert any(
        pattern.search("Does Amplifier tab completion work in my VS Code terminal?")
        for pattern in ITEM.prompt_patterns
    )


def test_catalog_discovers_promoted_packet_and_its_action() -> None:
    assert ITEM.category == "bulletin"
    assert ITEM.promoted
    assert ITEM.action == ACTION
    assert Path(ITEM.source_path) == CONTENT / "bulletins" / "autocompletion.md"


@pytest.mark.parametrize(
    "prompt",
    [
        "Tell me about Amplifier autocompletion.",
        "How do I get shell autocomplete for Amplifier working in fish?",
        "Install Amplifier completion.",
    ],
)
def test_first_prompt_summons_packet_with_consent_boundary(
    tmp_path: Path, prompt: str
) -> None:
    hooks = WayfinderHooks(
        WayfinderConfig(
            content_dir=str(CONTENT),
            declines_path=str(tmp_path / "declines.md"),
            surfaced_path=str(tmp_path / "surfaced.jsonl"),
            promoted_rotation=False,
        )
    )

    async def submit():
        data = {"session_id": "completion-packet-test", "parent_id": None}
        await hooks.on_session_start("session:start", data)
        return await hooks.on_prompt_submit(
            "prompt:submit", {**data, "prompt": prompt}
        )

    result = asyncio.run(submit())
    assert result.action == "inject_context"
    assert result.context_injection is not None
    assert ACTION in result.context_injection
    assert "A signal match establishes relevance only" in result.context_injection
    assert "Never act on relevance alone" in result.context_injection
    assert "merely topical, relevance-seeking, or informational" in result.context_injection
    assert "explicitly requested the matching action" in result.context_injection


@pytest.mark.parametrize(
    "prompt",
    [
        "Install Amplifier completion.",
        "How do I see a list of Amplifier slash commands?",
        "What argument choices does Amplifier offer for /provider?",
        "Turn off Amplifier's slash popup.",
        "Turn off Amplifier’s slash popup.",
        "How do I install shell completion for Amplifier?",
        "Where is Amplifier’s slash menu?",
        "Which options does Amplifier offer for /provider?",
    ],
)
def test_full_catalog_first_prompt_summons_autocompletion(
    tmp_path: Path, prompt: str
) -> None:
    hooks = WayfinderHooks(
        WayfinderConfig(
            content_dir=str(CONTENT),
            declines_path=str(tmp_path / "declines.md"),
            surfaced_path=str(tmp_path / "surfaced.jsonl"),
            promoted_rotation=False,
        )
    )

    async def submit():
        data = {"session_id": "full-catalog-completion-test", "parent_id": None}
        await hooks.on_session_start("session:start", data)
        return await hooks.on_prompt_submit(
            "prompt:submit", {**data, "prompt": prompt}
        )

    result = asyncio.run(submit())
    assert result.action == "inject_context"
    assert result.context_injection is not None
    assert ACTION in result.context_injection
    assert SWITCH_MODELS_ACTION not in result.context_injection


@pytest.mark.parametrize(
    "prompt",
    [
        "Can Amplifier autocomplete my code?",
        "Can Amplifier autocomplete code in my editor?",
        "Does Amplifier autocomplete the address field?",
        "Can Amplifier autocomplete my search form?",
        "Can Amplifier autocompletion help my code editor?",
        "Does Amplifier autocompletion suggest Python code?",
        "Enable Amplifier autocompletion for my search form.",
        "Configure Discord slash menus",
        "Install autocomplete for my editor",
        "Use Amplifier to add shell completion to my own CLI",
    ],
)
def test_full_catalog_ignores_unrelated_completion_requests(
    tmp_path: Path, prompt: str
) -> None:
    hooks = WayfinderHooks(
        WayfinderConfig(
            content_dir=str(CONTENT),
            declines_path=str(tmp_path / "declines.md"),
            surfaced_path=str(tmp_path / "surfaced.jsonl"),
            promoted_rotation=False,
        )
    )
    session_id = "full-catalog-unrelated-completion-test"

    async def submit():
        data = {"session_id": session_id, "parent_id": None}
        await hooks.on_session_start("session:start", data)
        return await hooks.on_prompt_submit(
            "prompt:submit", {**data, "prompt": prompt}
        )

    result = asyncio.run(submit())
    assert "autocompletion" not in hooks._hinted.get(session_id, set())
    assert ACTION not in (result.context_injection or "")


def test_recorded_hard_decline_suppresses_autocompletion_signal(tmp_path: Path) -> None:
    declines_path = tmp_path / "declines.md"
    declines_path.write_text("- autocompletion\n", encoding="utf-8")
    hooks = WayfinderHooks(
        WayfinderConfig(
            content_dir=str(CONTENT),
            declines_path=str(declines_path),
            surfaced_path=str(tmp_path / "surfaced.jsonl"),
            promoted_rotation=False,
        )
    )
    session_id = "declined-autocompletion-test"

    async def submit():
        data = {"session_id": session_id, "parent_id": None}
        await hooks.on_session_start("session:start", data)
        return await hooks.on_prompt_submit(
            "prompt:submit", {**data, "prompt": "Install Amplifier completion."}
        )

    result = asyncio.run(submit())
    assert "autocompletion" in hooks._catalogs[session_id].declined_ids
    assert "autocompletion" not in hooks._hinted.get(session_id, set())
    assert ACTION not in (result.context_injection or "")