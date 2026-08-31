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
)

ROOT = Path(__file__).resolve().parents[3]


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
    consent = (ROOT / "context/propose-and-ack.md").read_text()
    about = (ROOT / "content/concepts/about-wayfinder.md").read_text()

    assert 'A soft "not now/later" writes nothing and may resurface' in consent
    assert (
        'A hard "not interested / stop offering this / never" itself authorizes'
        in consent
    )
    assert "—no second ack—" in consent
    assert '"Not now/later" writes nothing and may resurface' in about
    assert (
        'A hard "not interested/stop/never" is remembered without asking again' in about
    )


def test_vision_and_packet_authoring_contract_preserve_signal_boundary() -> None:
    vision = (ROOT / "VISION.md").read_text()
    authoring = (ROOT / "skills/wayfinder-pack/SKILL.md").read_text()

    assert "A signal match authorizes reading the relevant packet" in vision
    assert "not executing its actions" in vision
    assert "without duplicate Wayfinder ack" in vision
    assert "native approvals still apply" in vision
    assert "A match establishes relevance, not execution consent" in authoring
    assert "It authorizes\n  reading the packet" in authoring
    assert "without duplicate Wayfinder ack" in authoring
    assert "any optional action remains\n  propose→show→ack→act" in authoring
