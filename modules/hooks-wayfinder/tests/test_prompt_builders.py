import asyncio
from pathlib import Path

import pytest
from amplifier_module_hooks_wayfinder import (
    _NEVER_MORE_IMPORTANT,
    CatalogItem,
    SessionCatalog,
    WayfinderConfig,
    WayfinderHooks,
    _build_hint_block,
    _build_index_block,
    _build_self_intro_block,
    _build_signal_summon_block,
    load_catalog,
)

ROOT = Path(__file__).resolve().parents[3]
DOCTOR_ACTION = 'read_file("@wayfinder:content/bulletins/doctor.md")'
DOCTOR = load_catalog([("default", ROOT / "content")], curate=False)["doctor"]
DOCTOR_SIGNAL_CASES = [
    (0, "/doctor"),
    (
        0,
        "/doctor Inspect my provider configuration and model routing. "
        "Do not change settings, load credentials, or run live probes.",
    ),
    (0, "Tell me about /doctor."),
    (0, "Please run /DOCTOR."),
    (1, "Inspect my Amplifier CLI configuration."),
    (1, "Please check Amplifier CLI provider setup."),
    (1, "Diagnose Amplifier CLI model routing."),
    (1, "Diagnosing Amplifier CLI startup."),
    (1, "Check my Amplifier CLI health."),
    (1, "Please inspect the Amplifier CLI's health."),
    (1, "Diagnose Amplifier CLI health."),
    (1, "Inspect Amplifier CLI health before my next task."),
    (2, "My Amplifier CLI configuration is behaving unexpectedly."),
    (2, "Amplifier CLI provider setup is broken."),
    (2, "Amplifier CLI model routing isn't working."),
    (2, "Amplifier CLI is reading the wrong settings."),
    (3, "Tell me about the doctor offer in Wayfinder."),
    (3, "What is the doctor bulletin from Wayfinder?"),
    (3, "Explain Wayfinder's doctor offer."),
    (3, "Show me the Wayfinder doctor bulletin."),
    (4, "Something is wrong with my Amplifier CLI."),
    (4, "Something feels wrong with the Amplifier CLI."),
    (4, "Give my Amplifier CLI a check-up."),
    (4, "Please give the Amplifier CLI a routine health checkup."),
    (
        5,
        "I want to check the health of my Amplifier CLI before starting a task. "
        "What can help? Explain only; do not run diagnostics or change anything.",
    ),
    (5, "Check the health of my Amplifier CLI."),
    (5, "Please inspect the health of the Amplifier CLI."),
    (5, "I would like to check the health of Amplifier CLI."),
]
DOCTOR_UNRELATED_CASES = [
    "Diagnose my project's failing tests.",
    "I need Amplifier CLI to diagnose my project's failing tests.",
    "I use Amplifier CLI, but Homebrew doctor reports warnings.",
    "Inspect Amplifier CLI while fixing my app.",
    "Explain Amplifier CLI model routing.",
    "How do I switch models in Amplifier CLI?",
    "I have a provider error in my app.",
    "My config is broken.",
    "Diagnose Amplifier Unified provider configuration.",
    "My agent's doctor failed.",
    "I need a medical doctor.",
    "Call Claude Code /doctor.",
    "/doctor in Claude Code",
    "/doctor in ClaudeCode",
    "Explain /doctor in Homebrew.",
    "/doctor Diagnose my project's failing tests.",
    "/doctor Inspect my agent.",
    "What is /doctor in Amplifier Unified?",
    "My Amplifier CLI project has failing tests.",
    "Amplifier CLI is useful. Diagnose my project's failing tests.",
    "Please check Amplifier CLI. My provider setup is broken.",
    "/doctorate is not a command.",
    "/doctor " + "Inspect my setup. " * 20,
    "The doctor offered me a medical appointment.",
    "Explain Homebrew's doctor offer.",
    "Wayfinder can help. My doctor offered medical advice.",
    "Check my health.",
    "Check my project's health using Amplifier CLI.",
    "Give Amplifier Unified a health check-up.",
    "Give Claude Code a check-up.",
    "Something is wrong with my Amplifier CLI project.",
    "Something is wrong with my Amplifier CLI app.",
    "Check the health of my Amplifier CLI project.",
    "I want to check the health of my Amplifier CLI agent.",
    "Check the health of Amplifier Unified.",
    "I want to check my health using Amplifier CLI.",
]


def _item() -> CatalogItem:
    return CatalogItem(
        id="goal",
        category="practice",
        headline="Turn a fuzzy request into a clear goal",
        action='read_file("@wayfinder:content/practices/goal.md")',
        source_path="content/practices/goal.md",
    )


def test_hint_block_distinguishes_direct_request_from_optional_offer() -> None:
    block = _build_hint_block(_item())

    assert "directly requested work this capability can fulfill" in block
    assert "without a duplicate Wayfinder ack" in block
    assert "normal host/tool/safety/destructive approvals still apply" in block
    assert "message merely makes this an optional useful next step" in block
    assert (
        'show the exact action (would show: read_file("@wayfinder:content/'
        'practices/goal.md"))' in block
    )
    assert "wait for an explicit ack" in block


def test_signal_summon_explicit_action_needs_no_duplicate_wayfinder_ack() -> None:
    block = _build_signal_summon_block(_item())

    assert "A signal match establishes relevance only" in block
    assert "explicitly requested the matching action" in block
    assert "install, run, use, execute, edit, or implement it" in block
    assert "carry out that in-scope request" in block
    assert "without a duplicate Wayfinder ack" in block
    assert "Normal host/tool/safety/destructive approvals still apply" in block


def test_signal_summon_topical_match_authorizes_packet_read_only() -> None:
    block = _build_signal_summon_block(_item())

    assert "to read the packet" in block
    assert "NOT by itself authorize any command, skill, installation" in block
    assert "merely topical, relevance-seeking, or informational" in block
    assert "read and answer from the packet only" in block
    assert "Any action or install is then an optional Wayfinder offer" in block
    assert "show the exact action and wait for explicit ack" in block
    assert "Never act on relevance alone" in block


def test_self_intro_uses_the_same_consent_and_native_approval_boundary() -> None:
    block = _build_self_intro_block(_item())

    assert "Offers named in the overview remain optional" in block
    assert "unless the user directly requests one" in block
    assert "without a duplicate Wayfinder ack" in block
    assert "host/tool/safety/destructive approvals still apply" in block
    assert "Never run an unsolicited suggestion unattended" in block


def test_every_injected_block_leads_with_the_subordination_guard() -> None:
    """Every injected wayfinder block must carry the subordination line --

    the captured-session hijack (0629f373) showed a model treating a
    conditional wayfinder offer as "mandatory" off an unrelated phrase in
    the user's own message. Every injection must make explicit, up front,
    that it is conditional and never outranks the user's actual request.
    """
    item = _item()
    catalog = SessionCatalog(items={item.id: item})
    hooks = WayfinderHooks(WayfinderConfig())

    blocks = [
        _build_index_block(catalog),
        _build_hint_block(item),
        _build_self_intro_block(item),
        _build_signal_summon_block(item),
        hooks._build_menu_block(catalog),
    ]

    for block in blocks:
        assert _NEVER_MORE_IMPORTANT in block
        assert "ONLY IF" in block
        assert "IGNORE this reminder entirely" in block

    # The light-lead block needs a start_items/promoted_lead entry to render
    # at all (a bare `items` catalog produces nothing to tease).
    light_catalog = SessionCatalog(items={item.id: item}, start_items=[item])
    light = hooks._build_light_lead_block(light_catalog)
    assert light  # sanity: this catalog does produce a lead
    assert _NEVER_MORE_IMPORTANT in light
    assert "ONLY IF" in light
    assert "IGNORE this reminder entirely" in light

    # The menu's "nothing left to show" path (all items declined) also
    # carries the guard -- it's a separate return statement in the source.
    catalog_all_declined = SessionCatalog(items={item.id: item}, declined_ids={item.id})
    empty_menu = hooks._build_menu_block(catalog_all_declined)
    assert _NEVER_MORE_IMPORTANT in empty_menu
    assert "ONLY IF" in empty_menu


def test_catalog_and_menu_prompts_apply_the_same_consent_boundary() -> None:
    item = _item()
    catalog = SessionCatalog(items={item.id: item})

    index = _build_index_block(catalog)
    menu = WayfinderHooks(WayfinderConfig())._build_menu_block(catalog)

    assert "direct user request matching an item" in index
    assert "without a duplicate Wayfinder ack" in index
    assert "unsolicited optional suggestions" in index
    assert "merely listed item" in menu
    assert "optional offer needing an explicit ack" in menu
    assert "directly asks to open or use an item" in menu
    assert "without a duplicate Wayfinder ack" in menu


@pytest.mark.parametrize(
    ("relative_path", "direct_request", "optional_offer"),
    [
        (
            "content/practices/device-ui-testing.md",
            "explicit request to install or run a tester",
            "Wayfinder introduces installation or testing as an optional next step",
        ),
        (
            "content/practices/simulated-user-research.md",
            "explicit request to install or run it",
            "Wayfinder suggests installation or a research run as an optional next step",
        ),
        (
            "content/practices/loop-until-proven.md",
            "explicit request to install the bundle or run one of these skills",
            "Wayfinder introduces installation or skill use as an optional next step",
        ),
        (
            "content/practices/work-tracker.md",
            "explicit request to install, start, or use it",
            "Wayfinder introduces setup or use as an optional next step",
        ),
        (
            "content/concepts/about-wayfinder.md",
            "explicitly ask to run or install a matching capability",
            "Optional offers are ack-gated",
        ),
        (
            "content/bulletins/doctor.md",
            "explicit request to run doctor",
            "Wayfinder introduces execution as an optional next step",
        ),
    ],
)
def test_packet_install_and_action_wording_distinguishes_requests_from_offers(
    relative_path: str,
    direct_request: str,
    optional_offer: str,
) -> None:
    body = (ROOT / relative_path).read_text()

    assert direct_request in body
    assert "without duplicate Wayfinder ack" in body or (
        "without another Wayfinder ack" in body
    )
    assert optional_offer in body
    assert "Native host, tool, safety, and destructive-action approvals" in body or (
        "native host, tool, safety, and destructive-action approvals" in body
    )


def test_decline_semantics_preserve_soft_and_hard_behavior() -> None:
    """Decline semantics survive the lean-head rewrite of the consent floor.

    ``context/propose-and-ack.md`` was condensed for the always-on head
    (model_performance-smy5, from zc6t's measured patch set): the soft/hard
    decline clauses are now mid-sentence, so their leading article and the
    em-dash parenthetical around "no second ack" changed form. The SUBSTANCE
    is asserted here verbatim and is unchanged; only the surrounding
    punctuation moved. See ``test_always_on_head.py`` for the budget pin that
    keeps the verbose form from coming back.
    """
    consent = (ROOT / "context/propose-and-ack.md").read_text()
    about = (ROOT / "content/concepts/about-wayfinder.md").read_text()

    assert 'soft "not now/later" writes nothing and may resurface' in consent
    assert (
        'hard "not interested / stop offering this / never" itself authorizes'
        in consent
    )
    assert "no second ack" in consent
    assert '"Not now/later" writes nothing and may resurface' in about
    assert (
        'A hard "not interested/stop/never" is remembered without asking again' in about
    )


def test_vision_and_packet_authoring_contract_preserve_signal_boundary() -> None:
    """The signal boundary's authoritative home is the packet contract.

    Deliberate contract update (see VISION.md changelog, 2026-09-03): VISION
    was genre-conformed ahead of ratification — it keeps the PRINCIPLE and
    points at the contract; contracts/packet.v1.md Core clause 6 carries the
    MECHANICS verbatim; the authoring skill is unchanged. This test guards all
    three homes so the boundary can never silently vanish from any of them.
    """
    vision = " ".join((ROOT / "VISION.md").read_text().split())
    contract = " ".join((ROOT / "contracts/packet.v1.md").read_text().split())
    authoring = (ROOT / "skills/wayfinder-pack/SKILL.md").read_text()

    # Vision: the principle + the pointer, not the mechanics.
    assert "never acts merely because its topic matched" in vision
    assert "Nothing wayfinder initiates runs unattended" in vision
    assert "packet contract" in vision

    # Contract: the mechanics, verbatim (Core clause 6).
    assert "Signals establish relevance, never consent" in contract
    assert "A signal match authorizes reading the packet" in contract
    assert "never authorizes executing" in contract

    # Authoring skill: unchanged.
    assert "A match establishes relevance, not execution consent" in authoring
    assert "It authorizes\n  reading the packet" in authoring
    assert "without duplicate Wayfinder ack" in authoring
    assert "any optional action remains\n  propose→show→ack→act" in authoring


@pytest.mark.parametrize(("pattern_index", "phrasing"), DOCTOR_SIGNAL_CASES)
def test_doctor_real_packet_patterns_match_focused_phrasing(
    pattern_index: int, phrasing: str
) -> None:
    assert DOCTOR.prompt_patterns[pattern_index].search(phrasing)


@pytest.mark.parametrize("phrasing", DOCTOR_UNRELATED_CASES)
def test_every_doctor_pattern_rejects_unrelated_intent(phrasing: str) -> None:
    for pattern in DOCTOR.prompt_patterns:
        assert not pattern.search(phrasing), pattern.pattern


def test_doctor_menu_headline_preserves_the_passive_checkup_limit() -> None:
    """The menu sees the headline without the packet body's limitations."""
    assert "setup check-up" in DOCTOR.headline
    assert "not a health verdict" in DOCTOR.headline
    catalog = SessionCatalog(items={DOCTOR.id: DOCTOR})
    menu = WayfinderHooks(WayfinderConfig())._build_menu_block(catalog)
    assert DOCTOR.headline in menu


@pytest.mark.parametrize("declined", [False, True], ids=["available", "declined"])
def test_doctor_is_derived_promoted_and_decline_filtered(
    tmp_path: Path, declined: bool
) -> None:
    assert DOCTOR.id == "doctor"
    assert DOCTOR.category == "bulletin"
    assert DOCTOR.promoted
    assert DOCTOR.on_events == ["session:start"]
    assert DOCTOR.action == DOCTOR_ACTION
    assert Path(DOCTOR.source_path) == ROOT / "content/bulletins/doctor.md"
    assert DOCTOR.try_now == ["/doctor", DOCTOR_SIGNAL_CASES[1][1]]
    items = load_catalog([("default", ROOT / "content")], curate=False)
    assert [item.id for item in items.values() if item.action == DOCTOR_ACTION] == [
        "doctor"
    ]

    declines_path = tmp_path / "declines.md"
    if declined:
        declines_path.write_text("- doctor\n", encoding="utf-8")
    hooks = WayfinderHooks(
        WayfinderConfig(
            content_dir=str(ROOT / "content"),
            declines_path=str(declines_path),
            surfaced_path=str(tmp_path / "surfaced.jsonl"),
        )
    )
    session_id = "doctor-catalog-test"

    async def submit():
        data = {"session_id": session_id, "parent_id": None}
        await hooks.on_session_start("session:start", data)
        return await hooks.on_prompt_submit(
            "prompt:submit", {**data, "prompt": "/doctor"}
        )

    result = asyncio.run(submit())
    catalog = hooks._catalogs[session_id]
    menu = hooks._build_menu_block(catalog)
    assert (DOCTOR_ACTION in menu) is not declined
    assert (DOCTOR.headline in menu) is not declined
    assert ("doctor" in catalog.declined_ids) is declined
    assert (DOCTOR_ACTION in (result.context_injection or "")) is not declined
    assert ("doctor" in hooks._hinted.get(session_id, set())) is not declined


@pytest.mark.parametrize("later_turn", [False, True], ids=["first", "later"])
@pytest.mark.parametrize(
    ("prompt", "expected_doctor"),
    [(phrase, True) for _, phrase in DOCTOR_SIGNAL_CASES]
    + [(phrase, False) for phrase in DOCTOR_UNRELATED_CASES],
)
def test_doctor_full_catalog_selection_and_ephemeral_guidance(
    tmp_path: Path, later_turn: bool, prompt: str, expected_doctor: bool
) -> None:
    """Check hook selection and instruction text, not model execution or consent."""
    hooks = WayfinderHooks(
        WayfinderConfig(
            content_dir=str(ROOT / "content"),
            declines_path=str(tmp_path / "declines.md"),
            surfaced_path=str(tmp_path / "surfaced.jsonl"),
        )
    )
    session_id = "doctor-signal-test"

    async def submit():
        data = {"session_id": session_id, "parent_id": None}
        await hooks.on_session_start("session:start", data)
        if later_turn:
            first = await hooks.on_prompt_submit(
                "prompt:submit",
                {**data, "prompt": "Please implement this change."},
            )
            assert first.action == "continue"
        return await hooks.on_prompt_submit("prompt:submit", {**data, "prompt": prompt})

    result = asyncio.run(submit())
    injection = result.context_injection or ""
    if not expected_doctor:
        assert DOCTOR_ACTION not in injection
        assert "doctor" not in hooks._hinted.get(session_id, set())
        return

    assert result.action == "inject_context"
    assert result.ephemeral
    assert result.context_injection_role == "user"
    assert DOCTOR_ACTION in injection
    assert DOCTOR.headline in injection
    assert hooks._hinted[session_id] == {"doctor"}
    assert _NEVER_MORE_IMPORTANT in injection
    # Body and execution instructions remain on-demand, not auto-injected.
    assert "Your Amplifier CLI is behaving oddly" not in injection
    assert "app-cli:cli-doctor" not in injection
    assert "host/tool/safety/destructive approvals still apply" in injection
    if later_turn:
        assert "directly requested work this capability can fulfill" in injection
        assert "duplicate Wayfinder ack" in injection
        assert "show the exact action" in injection
        assert "wait for an explicit ack" in injection
    else:
        assert "A signal match establishes relevance only" in injection
        assert "explicitly requested the matching action" in injection
        assert "without a duplicate Wayfinder ack" in injection
        assert "read and answer from the packet only" in injection
        assert "show the exact action and wait for explicit ack" in injection
