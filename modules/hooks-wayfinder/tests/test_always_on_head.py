"""Always-on head pin: the two `context.include` files stay lean AND complete.

`behaviors/wayfinder.yaml` wires `context/wayfinder-voice.md` and
`context/propose-and-ack.md` via `context.include`. That means their bytes are
paid for on **every request of every session**, whether or not wayfinder ever
speaks. AGENTS.md states the budget directly: "keep the pair lean; each < 1000
tok, and prefer smaller" and "Keep each such file < 500 tokens".

This file pins the lean-head v1 form applied under `model_performance-smy5`
(zc6t's measured patch set, foundation SHA 4384805) so it cannot silently drift
back to the verbose stock form. Three independent guards, because any one alone
is defeatable:

1. **Budget ceiling** -- a reversion to the stock prose blows it. Stock was
   2,048 / 1,974 chars; lean is 1,645 / 1,587.
2. **Rule presence** -- every load-bearing rule, constraint, command and
   pointer that stock carried is still here verbatim-in-substance. A "lean"
   rewrite that drops a rule fails here, not in review.
3. **Scaffolding absence** -- the stock section headings are gone and stay
   gone. This is what actually catches a well-meaning re-expansion that
   happens to squeak under the budget.

Run:
    PYTHONPATH=modules/hooks-wayfinder python3 -m pytest modules/hooks-wayfinder/tests -q
"""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]

VOICE = "context/wayfinder-voice.md"
CONSENT = "context/propose-and-ack.md"

# Measured at the lean-head v1 apply, plus ~100 chars of editing headroom.
# Stock (pre-patch) was 2,048 and 1,974 -- both are well above these ceilings,
# so a straight revert fails.
BUDGET_CHARS = {VOICE: 1_750, CONSENT: 1_700}
PAIR_BUDGET_CHARS = 3_450


def _text(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


# --------------------------------------------------------------------------- #
# 1. Budget ceiling
# --------------------------------------------------------------------------- #
@pytest.mark.parametrize("relative_path", [VOICE, CONSENT])
def test_always_on_file_stays_within_char_budget(relative_path: str) -> None:
    text = _text(relative_path)
    ceiling = BUDGET_CHARS[relative_path]
    assert len(text) <= ceiling, (
        f"{relative_path} is {len(text)} chars, over the {ceiling}-char "
        "always-on ceiling. This file is in context.include -- it is paid for "
        "on every request of every session. Trim it, or raise the ceiling "
        "deliberately with a measured reason."
    )


def test_always_on_pair_stays_within_combined_budget() -> None:
    total = len(_text(VOICE)) + len(_text(CONSENT))
    assert total <= PAIR_BUDGET_CHARS, (
        f"the always-on pair is {total} chars, over the "
        f"{PAIR_BUDGET_CHARS}-char combined ceiling."
    )


# --------------------------------------------------------------------------- #
# 2. Rule presence -- nothing stock carried was lost in the condense
# --------------------------------------------------------------------------- #
VOICE_RULES = [
    # Scope gate
    "Top-level human sessions only",
    "sub-agents, recipe steps, and fork-skill sessions ignore this file",
    # Register
    "curated, plain, opinionated",
    "not a feed, changelog, or marketing",
    "real commands, honest gotchas, no hype",
    "one thing at a time",
    "honest about newness and thin evidence",
    # Render, don't recite
    "Render, don't recite",
    "never echoed verbatim or forced into a template",
    # Requests vs offers
    "Direct requests are not offers",
    "without another Wayfinder ack",
    "Optional suggestions are offers",
    "show the exact action, wait for explicit ack, never act unattended",
    "Normal host, tool, safety, destructive approvals always apply",
    # Commands + pointers
    "`/provider`",
    "`/goal`",
    "`/monitor`",
    "`/council`",
    "invoke skills by natural-language name unless the app wires a slash form",
    "never auto-install",
    "a direct install request needs no duplicate ack",
    "Confirm a command is available this session before offering it",
    "`wayfinder-pack`",
    # Boundaries
    "point, don't absorb",
    "`app-cli:cli-expert`",
    "Prefer current, verified claims and point at the source of truth",
    # The attention-cost bar. Present in stock, absent from the raw upstream
    # lean draft, restored here at +84 chars. This is the whole reason the
    # channel must stay small -- do not drop it again.
    "at almost no attention cost",
]

CONSENT_RULES = [
    # Scope gate
    "Top-level human sessions only",
    "no Wayfinder consent gate there",
    # What consent covers -- and does not
    "Consent gates only optional steering Wayfinder itself initiates",
    "never work the user directly requests",
    "do not re-ask",
    "never recast a direct request as a Wayfinder offer",
    "Clarify ambiguous scope",
    "Normal host, tool, safety, destructive-action approvals still apply",
    # The four steps, in order
    "1. Propose",
    "catalog offer-id",
    "2. Show",
    "the exact command, skill load, or delegation, in a code block, before asking",
    "No exact command, no ack request: work it out first",
    "3. Ack",
    "silence is not consent, ambiguity is not consent",
    "4. Act",
    "run exactly what you showed, nothing more, then stop",
    # Guardrails
    "Never unattended",
    "needs a fresh human ack",
    "never batch consent or act on a schedule",
    "only a HARD \"no\" is written",
    'soft "not now/later" writes nothing and may resurface',
    'hard "not interested / stop offering this / never" itself authorizes',
    "${AMPLIFIER_WAYFINDER_DIR:-~/.amplifier/wayfinder}/declines.md",
    "no second ack",
    "Install honesty",
    "shows its exact install command under the same ack gate",
]


@pytest.mark.parametrize("rule", VOICE_RULES)
def test_voice_retains_every_load_bearing_rule(rule: str) -> None:
    assert rule in _text(VOICE), (
        f"{VOICE} no longer carries {rule!r}. The lean head trades prose for "
        "density, never rules -- restore it."
    )


@pytest.mark.parametrize("rule", CONSENT_RULES)
def test_consent_retains_every_load_bearing_rule(rule: str) -> None:
    assert rule in _text(CONSENT), (
        f"{CONSENT} no longer carries {rule!r}. The consent floor is the one "
        "thing that must never thin out -- restore it."
    )


# --------------------------------------------------------------------------- #
# 3. Scaffolding absence -- the verbose stock form stays gone
# --------------------------------------------------------------------------- #
STOCK_SCAFFOLDING = {
    VOICE: [
        "## Render, don't recite",
        "## How wayfinder talks",
        "## Requests, offers, and installs",
        "## Boundaries",
    ],
    CONSENT: [
        "## Guardrails",
        "**Propose.**",
        "**Show.**",
        "**Ack.**",
        "**Act.**",
    ],
}


@pytest.mark.parametrize(
    ("relative_path", "heading"),
    [(p, h) for p, hs in STOCK_SCAFFOLDING.items() for h in hs],
)
def test_stock_section_scaffolding_does_not_return(
    relative_path: str, heading: str
) -> None:
    assert heading not in _text(relative_path), (
        f"{relative_path} has regained the stock scaffolding {heading!r}. "
        "These files were condensed deliberately for the always-on head; "
        "re-expanding them costs every request of every session."
    )
