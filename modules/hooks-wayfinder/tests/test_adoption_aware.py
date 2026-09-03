"""Adoption-aware offer ranking (config knob: adoption_aware).

A measured miss motivates this: the catalog's rotation lead surfaced
``/goal`` with beginner framing to a user whose own data showed 131
goal-runs that day. The fix is NOT a ranking algorithm in this hook -- the
hook stays deterministic. On explicit engagement (the orienting catalog
index and the F3 re-summonable menu) it now instructs the agent to load the
``wayfinder-scout`` skill, which does the actual ranking against the
reader's own usage evidence. This module tests three things:

1. The ``adoption_aware`` config knob itself (default true, ``from_dict``
   wiring).
2. ``builds_on`` ladder metadata: parsed onto ``CatalogItem`` and annotated
   in both injection blocks' offer lines.
3. The scout wording: present (and the index block's lead header made
   conditional) when the knob is on; both blocks byte-identical to today's
   pre-existing output when the knob is off.
"""

from __future__ import annotations

from amplifier_module_hooks_wayfinder import (
    CatalogItem,
    SessionCatalog,
    WayfinderConfig,
    WayfinderHooks,
    _build_index_block,
    _item_from_meta,
    _subordination_guard,
)

_ID_GOAL_ACTION = 'read_file("@wayfinder:content/practices/goal.md")'


def _goal_item(**overrides: object) -> CatalogItem:
    base: dict[str, object] = dict(
        id="goal",
        category="practice",
        headline="Turn a fuzzy request into a clear goal",
        try_now=["run /goal"],
        action=_ID_GOAL_ACTION,
        source_path="content/practices/goal.md",
    )
    base.update(overrides)
    return CatalogItem(**base)  # type: ignore[arg-type]


# --------------------------------------------------------------------------- #
# 1. The config knob itself
# --------------------------------------------------------------------------- #
def test_adoption_aware_defaults_true() -> None:
    assert WayfinderConfig().adoption_aware is True


def test_adoption_aware_from_dict_false_wiring() -> None:
    assert WayfinderConfig.from_dict({"adoption_aware": False}).adoption_aware is False
    # Omitted entirely -> default true, matching every other bool knob's pattern.
    assert WayfinderConfig.from_dict({}).adoption_aware is True
    assert WayfinderConfig.from_dict(None).adoption_aware is True


class _FakeHookRegistry:
    def register(self, *_args: object, **_kwargs: object) -> None:
        pass


class _FakeCoordinator:
    def __init__(self) -> None:
        self.hooks = _FakeHookRegistry()


def test_mount_config_report_includes_adoption_aware() -> None:
    import asyncio

    from amplifier_module_hooks_wayfinder import mount

    report = asyncio.run(
        mount(coordinator=_FakeCoordinator(), config={"adoption_aware": False})
    )
    assert report["config"]["adoption_aware"] is False


# --------------------------------------------------------------------------- #
# 2. builds_on ladder metadata
# --------------------------------------------------------------------------- #
def test_builds_on_parsed_onto_catalog_item_from_a_list() -> None:
    meta = {
        "id": "goal-batch",
        "category": "practice",
        "headline": "Run 2+ tasks as parallel lanes",
        "trigger": "2+ independent tasks",
        "action": 'read_file("@wayfinder:content/practices/goal-batch.md")',
        "builds_on": ["goal"],
    }
    item = _item_from_meta(meta, "content/practices/goal-batch.md")
    assert item is not None
    assert item.builds_on == ["goal"]


def test_builds_on_parsed_onto_catalog_item_from_a_scalar() -> None:
    meta = {
        "id": "goal-batch",
        "category": "practice",
        "headline": "Run 2+ tasks as parallel lanes",
        "builds_on": "goal",
    }
    item = _item_from_meta(meta, "content/practices/goal-batch.md")
    assert item is not None
    assert item.builds_on == ["goal"]


def test_builds_on_absent_field_yields_empty_list() -> None:
    meta = {
        "id": "goal",
        "category": "practice",
        "headline": "Turn a fuzzy request into a clear goal",
    }
    item = _item_from_meta(meta, "content/practices/goal.md")
    assert item is not None
    assert item.builds_on == []
    # Also true for a bare CatalogItem() construction (dataclass default).
    assert _goal_item().builds_on == []


def test_builds_on_annotated_in_index_block_line() -> None:
    plain = _goal_item(id="goal")
    ladder = _goal_item(
        id="goal-batch",
        headline="Run 2+ tasks as parallel lanes",
        builds_on=["goal"],
        action='read_file("@wayfinder:content/practices/goal-batch.md")',
    )
    catalog = SessionCatalog(items={plain.id: plain, ladder.id: ladder})

    block = _build_index_block(catalog)

    assert "- goal [practice]: Turn a fuzzy request into a clear goal\n" in block
    assert "(builds on:" not in block.split("- goal [practice]:")[1].split("\n")[0]
    assert (
        "- goal-batch [practice]: Run 2+ tasks as parallel lanes "
        "(builds on: goal)" in block
    )


def test_builds_on_annotated_in_menu_block_line() -> None:
    plain = _goal_item(id="goal")
    ladder = _goal_item(
        id="ten-lane-highway",
        headline="Keep ~10 lanes full",
        builds_on=["goal", "goal-batch"],
        action='read_file("@wayfinder:content/concepts/ten-lane-highway.md")',
    )
    catalog = SessionCatalog(items={plain.id: plain, ladder.id: ladder})
    hooks = WayfinderHooks(WayfinderConfig())

    block = hooks._build_menu_block(catalog)

    assert (
        "- ten-lane-highway [practice]: Keep ~10 lanes full "
        "(builds on: goal, goal-batch)" in block
    )
    # The item with no builds_on carries no annotation on its own line.
    for line in block.splitlines():
        if line.startswith("- goal [practice]"):
            assert "(builds on:" not in line


# --------------------------------------------------------------------------- #
# 3. Scout wording, gated on the knob
# --------------------------------------------------------------------------- #
def _catalog_with_lead() -> SessionCatalog:
    item = _goal_item()
    return SessionCatalog(items={item.id: item}, start_items=[item])


def test_index_block_adoption_aware_true_carries_scout_instruction_and_conditional_lead() -> (
    None
):
    block = _build_index_block(_catalog_with_lead(), adoption_aware=True)

    assert (
        "if a skill named 'wayfinder-scout' is available (load_skill), load "
        "and follow it" in block
    )
    assert "reader's OWN usage evidence (local artifacts and runtime markers)" in block
    assert "Never lead with an offer the reader already uses daily" in block
    assert "never lead with a rung below one they've mastered" in block
    assert "the rotation order is the designed fallback" in block
    assert (
        "DEFAULT LEAD \u2014 surface this (once, commands-first, 2\u20133 line "
        "summary; read the file on demand) UNLESS the wayfinder-scout "
        "ranking demotes it:" in block
    )
    assert "SURFACE NOW" not in block


def test_menu_block_adoption_aware_true_carries_scout_instruction() -> None:
    item = _goal_item()
    catalog = SessionCatalog(items={item.id: item})
    hooks = WayfinderHooks(WayfinderConfig(adoption_aware=True))

    block = hooks._build_menu_block(catalog)

    assert (
        "if a skill named 'wayfinder-scout' is available (load_skill), load "
        "and follow it" in block
    )
    assert "the rotation order is the designed fallback" in block


def test_scout_instruction_comes_after_guard_and_consent_before_offer_list() -> None:
    """Guard stays FIRST; the scout paragraph lands after guard/consent, and
    strictly before the 'Offers on the menu:' list itself."""
    block = _build_index_block(_catalog_with_lead(), adoption_aware=True)
    lines = block.splitlines()

    guard_idx = next(i for i, line in enumerate(lines) if line.startswith("ONLY IF"))
    scout_idx = next(i for i, line in enumerate(lines) if "wayfinder-scout" in line)
    offers_idx = next(
        i for i, line in enumerate(lines) if line == "Offers on the menu:"
    )

    assert guard_idx == 1  # immediately after the opening <system-reminder> tag
    assert guard_idx < scout_idx < offers_idx


def test_index_block_adoption_aware_false_is_byte_identical_to_original() -> None:
    """No scout mention; the original unconditional 'SURFACE NOW' lead."""
    item = _goal_item()
    catalog = SessionCatalog(items={item.id: item}, start_items=[item])

    expected = (
        '<system-reminder source="hooks-wayfinder">\n'
        + _subordination_guard(
            "the user's CURRENT message explicitly asks about wayfinder, "
            "what's available, or other options"
        )
        + "\n"
        + (
            "wayfinder \u2014 offer catalog for this session (DERIVED from content "
            "frontmatter; declined offers already filtered out). A direct user "
            "request matching an item authorizes ordinary in-scope work without a "
            "duplicate Wayfinder ack. Surface unsolicited optional suggestions "
            "below ONLY via propose\u2192show\u2192ack\u2192act, one at a time, in wayfinder's voice."
        )
        + "\n"
        + (
            "To show any packet's body, run its `body:` action EXACTLY as written "
            "(including its @namespace prefix \u2014 it may point to another bundle). "
            "Never glob/grep/search for the file. This menu is authoritative about "
            "what EXISTS: if an item is listed, it exists \u2014 follow its action."
        )
        + "\n\n"
        + "Offers on the menu:\n"
        + "- goal [practice]: Turn a fuzzy request into a clear goal\n"
        + f"    body: {_ID_GOAL_ACTION}\n"
        + "\n"
        + (
            "SURFACE NOW \u2014 this session's lead (once, commands-first, lead with a "
            "2\u20133 line summary; read the file on demand for the rest, never paste "
            "the whole thing):"
        )
        + "\n"
        + "  goal \u2014 Turn a fuzzy request into a clear goal\n"
        + "  Try it now:\n"
        + "    1. run /goal\n"
        + f"  For the Why / Gotchas / More: {_ID_GOAL_ACTION} on demand.\n"
        + "</system-reminder>"
    )

    block = _build_index_block(catalog, adoption_aware=False)
    assert block == expected
    assert "wayfinder-scout" not in block
    assert "DEFAULT LEAD" not in block


def test_menu_block_adoption_aware_false_is_byte_identical_to_original() -> None:
    item = _goal_item()
    catalog = SessionCatalog(items={item.id: item})
    hooks = WayfinderHooks(WayfinderConfig(adoption_aware=False))

    expected = (
        '<system-reminder source="hooks-wayfinder">\n'
        + _subordination_guard(
            "the current user message explicitly asks to see wayfinder "
            "options or the menu (for example, what else, or show me "
            "the menu)"
        )
        + "\n"
        + (
            "The user asked what else is available \u2014 surface the FULL "
            "current wayfinder menu (declined offers already filtered out), "
            "in wayfinder's voice, as a compact list. Showing the list IS "
            "the answer, so no propose\u2192ack gate applies. Do not open or act "
            "on a merely listed item; that would be an optional offer needing "
            "an explicit ack. If the user directly asks to open or use an item, "
            "fulfill that in-scope request without a duplicate Wayfinder ack."
        )
        + "\n"
        + (
            "To open any packet, run its `body:` action EXACTLY as written "
            "(including its @namespace prefix); never glob/grep/search for "
            "the file. This menu is authoritative about what EXISTS."
        )
        + "\n\n"
        + "Offers on the menu:\n"
        + "- goal [practice]: Turn a fuzzy request into a clear goal\n"
        + f"    body: {_ID_GOAL_ACTION}\n"
        + "</system-reminder>"
    )

    block = hooks._build_menu_block(catalog)
    assert block == expected
    assert "wayfinder-scout" not in block
