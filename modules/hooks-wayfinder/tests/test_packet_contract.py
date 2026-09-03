"""Conformance kit for wayfinder's packet contract (``contracts/packet.v1.md``).

Plain pytest: no DTU, no network, no model. Two jobs:

1. Validate every REAL packet under ``content/**`` -- discovered exactly the
   way the consumer discovers it (``WayfinderHooks._resolve_own_dir()`` +
   ``sorted(content_dir.rglob("*.md"))``, the same call ``load_catalog``
   makes) -- against the Core clauses that are mechanically checkable in a
   contributor-runnable, no-model test: C2, C3, C4, C6, C7.
2. Run the same validator over one per-clause NEGATIVE fixture per targeted
   clause under ``tests/fixtures/packet_contract/`` and assert each fails
   *exactly* the clause it targets (the discriminating-pair requirement --
   no omnibus broken packet), plus one POSITIVE fixture proving C8 (unknown
   frontmatter keys are tolerated, never fatal).

The validator reuses the consumer's own ``parse_frontmatter`` (frontmatter
split + YAML load) and ``_item_from_meta`` (the same field
coercion/stripping the consumer applies) rather than reimplementing either --
see ``_load`` below. Clause checks themselves (kebab-case, mention-form
resolution, regex compilation, ISO-date parsing) are the contract's own
logic and have no equivalent in the consumer to reuse.

C8 (unknown keys ignored) has no *negative* fixture by construction: there
is no way for an unknown key to make a conformant packet fail, so its
fixture is the positive ``unknown-keys-ok.md`` alone.

Clause 8's Core neighbor, C1 ("one file, one packet") and C5 ("catalog is
derived, never registered") are structural properties of the consumer's own
architecture, not per-packet frontmatter shape -- nothing here to assert per
packet. They are exercised by the consumer's own existing test suite, not
this contract kit.
"""

from __future__ import annotations

import re
from datetime import date, datetime
from pathlib import Path

import pytest
from amplifier_module_hooks_wayfinder import (
    CatalogItem,
    WayfinderConfig,
    WayfinderHooks,
    _as_str_list,
    _item_from_meta,
    parse_frontmatter,
)

# --------------------------------------------------------------------------- #
# Discovery -- mirrors the consumer's own content-dir resolution + scan.
# --------------------------------------------------------------------------- #
# A bare WayfinderHooks(WayfinderConfig()) never touches the coordinator
# (own-dir auto-detection needs no mention_resolver -- only an explicit
# ``content_dir`` override starting with "@" would), so this is hermetic:
# no network, no model, no coordinator required.
_HOOKS = WayfinderHooks(WayfinderConfig())
_resolved_content_dir = _HOOKS._resolve_own_dir()
assert _resolved_content_dir is not None and _resolved_content_dir.is_dir(), (
    "could not resolve wayfinder's own content dir via the consumer's own "
    "WayfinderHooks._resolve_own_dir(); the contract kit and the consumer "
    "must agree on where packets live"
)
# Explicitly-typed (non-Optional) module global -- the assert above only
# narrows the type within this module-level scope, not inside the functions
# defined below that reference it.
CONTENT_DIR: Path = _resolved_content_dir

# The bundle root is the parent of the auto-detected content dir -- the same
# directory the "@wayfinder:" mention namespace resolves against (bundle.md
# registers this bundle's own content under that namespace).
BUNDLE_ROOT = CONTENT_DIR.parent

FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures" / "packet_contract"

_KEBAB_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")
# C4: "matches @[\w-]+: inside it" -- namespace, colon, then a bare path run
# (stops at whitespace/quote/paren so a read_file("@ns:path.md") wrapper
# resolves cleanly).
_MENTION_RE = re.compile(r'@(?P<ns>[\w-]+):(?P<path>[^\s"\')]+)')
_CATEGORIES = {"bulletin", "practice", "concept"}
_MENTION_NAMESPACE = "wayfinder"


def _discover_real_packets() -> list[Path]:
    """Exactly ``load_catalog``'s own discovery: ``sorted(dir.rglob("*.md"))``.

    Deliberately calls the SAME method + the SAME glob the consumer's
    ``load_catalog`` uses (see ``amplifier_module_hooks_wayfinder.load_catalog``)
    so the validator's population can never silently drift from what the
    hook itself would assemble into the session catalog.
    """
    return sorted(CONTENT_DIR.rglob("*.md"))


def _load(path: Path) -> tuple[dict, CatalogItem | None]:
    """Parse one packet file via the consumer's OWN parse functions.

    ``parse_frontmatter`` does the real YAML/frontmatter split;
    ``_item_from_meta`` does the real field coercion. ``item`` is ``None``
    exactly when the consumer itself would silently skip the file (no
    parseable frontmatter, or no usable ``id``) -- callers fall back to the
    raw ``meta`` dict for clause checks in that case.
    """
    text = path.read_text(encoding="utf-8")
    meta, _body = parse_frontmatter(text)
    item = _item_from_meta(meta, str(path))
    return meta, item


def _validate_packet(
    path: Path, meta: dict, item: CatalogItem | None
) -> dict[str, list[str]]:
    """Check one packet against Core clauses C2/C3/C4/C6/C7.

    Returns ``{clause: [violation message, ...]}``; an empty dict means the
    packet is fully conformant. Every violation message names the packet
    file and the violated clause number, per the "external contributor
    reads these" requirement.
    """
    violations: dict[str, list[str]] = {}

    def fail(clause: str, msg: str) -> None:
        violations.setdefault(clause, []).append(f"{path}: [{clause}] {msg}")

    # -- C2 + C3: id -- #
    raw_id = meta.get("id")
    if not (isinstance(raw_id, str) and raw_id.strip()):
        fail("C2", "id is missing, empty, or not a string")
        fail("C3", "required field 'id' is missing or empty")
    else:
        rid = raw_id.strip()
        if not _KEBAB_RE.match(rid):
            fail(
                "C2",
                f"id {rid!r} is not kebab-case (must match ^[a-z0-9][a-z0-9-]*$)",
            )

    # -- C3: remaining required fields -- #
    # Prefer the consumer's own coerced item fields (matches what the hook
    # actually sees); fall back to raw meta only when id was missing/invalid
    # and _item_from_meta therefore returned None (the one case the consumer
    # itself never constructs an item at all).
    if item is not None:
        category, headline, trigger, action = (
            item.category,
            item.headline,
            item.trigger,
            item.action,
        )
    else:
        category = str(meta.get("category") or "").strip()
        headline = str(meta.get("headline") or "").strip()
        trigger = str(meta.get("trigger") or "").strip()
        action = str(meta.get("action") or "").strip()

    for field_name, val in (
        ("category", category),
        ("headline", headline),
        ("trigger", trigger),
        ("action", action),
    ):
        if not val:
            fail("C3", f"required field {field_name!r} is missing or empty")
    if category and category not in _CATEGORIES:
        fail(
            "C3",
            f"category {category!r} is not in the registered vocabulary {sorted(_CATEGORIES)}",
        )

    # -- C4: action is a "@namespace:" mention resolving to this packet's own file -- #
    if action:
        m = _MENTION_RE.search(action)
        if not m:
            fail(
                "C4",
                f"action {action!r} has no @namespace: mention form -- "
                "looks like a bare filesystem path, which C4 forbids",
            )
        else:
            ns = m.group("ns")
            mention_path = m.group("path")
            if ns != _MENTION_NAMESPACE:
                fail(
                    "C4",
                    f"action mention namespace {ns!r} != {_MENTION_NAMESPACE!r}",
                )
            resolved = (BUNDLE_ROOT / mention_path).resolve()
            if resolved != path.resolve():
                fail(
                    "C4",
                    f"action mentions {mention_path!r} (-> {resolved}), which is "
                    f"not this packet's own file ({path.resolve()})",
                )

    # -- C6: every signals.prompt_matches entry compiles as a regex -- #
    signals = meta.get("signals")
    signals = signals if isinstance(signals, dict) else {}
    for pat in _as_str_list(signals.get("prompt_matches")):
        try:
            re.compile(pat)
        except re.error as exc:
            fail("C6", f"prompt_matches entry {pat!r} does not compile: {exc}")

    # -- C7: verified_at (ISO date) required; provenance required + non-empty -- #
    verified_at = meta.get("verified_at")
    if verified_at is None or (
        isinstance(verified_at, str) and not verified_at.strip()
    ):
        fail("C7", "verified_at is missing")
    elif isinstance(verified_at, (date, datetime)):
        pass  # YAML already parsed an unquoted ISO date literal -- valid.
    else:
        try:
            date.fromisoformat(str(verified_at).strip())
        except ValueError:
            fail("C7", f"verified_at {verified_at!r} does not parse as an ISO date")

    provenance = meta.get("provenance")
    if not (provenance and str(provenance).strip()):
        fail("C7", "provenance is missing or empty")

    return violations


# --------------------------------------------------------------------------- #
# Real content/** tree
# --------------------------------------------------------------------------- #
def test_content_discovery_matches_consumer_and_excludes_fixtures() -> None:
    packets = _discover_real_packets()
    assert packets, "expected at least one real packet under content/**"
    for p in packets:
        assert FIXTURES_DIR not in p.parents, (
            f"{p} is under the fixtures dir -- real-packet discovery must "
            "never pick up test fixtures"
        )
        assert p.is_relative_to(CONTENT_DIR)


@pytest.mark.parametrize(
    "path",
    _discover_real_packets(),
    ids=lambda p: str(p.relative_to(CONTENT_DIR)),
)
def test_real_packet_conforms_to_core_clauses(path: Path) -> None:
    meta, item = _load(path)
    violations = _validate_packet(path, meta, item)
    assert not violations, (
        f"{path} violates the packet contract (contracts/packet.v1.md):\n"
        + "\n".join(msg for msgs in violations.values() for msg in msgs)
    )


def test_ids_are_unique_across_real_packets_only() -> None:
    """C2 uniqueness -- spans real content/** packets only; fixtures excluded."""
    seen: dict[str, Path] = {}
    dupes: list[str] = []
    for path in _discover_real_packets():
        meta, _item = _load(path)
        raw_id = meta.get("id")
        if not (isinstance(raw_id, str) and raw_id.strip()):
            continue  # missing/invalid id is a C2/C3 finding, reported elsewhere
        rid = raw_id.strip()
        if rid in seen:
            dupes.append(f"id {rid!r} used by both {seen[rid]} and {path}")
        else:
            seen[rid] = path
    assert not dupes, "duplicate packet ids (C2):\n" + "\n".join(dupes)


# --------------------------------------------------------------------------- #
# Per-clause negative fixtures (+ one positive fixture)
# --------------------------------------------------------------------------- #
# filename -> the set of clauses that MUST fail for that fixture. Every
# clause NOT listed must PASS (the discriminating-pair requirement). Only
# missing-id.md legitimately targets two clauses at once: C2 and C3 both
# independently require `id`, so a missing id fails both by the contract's
# own text, not by test-construction sloppiness.
_FIXTURE_EXPECTATIONS: dict[str, set[str]] = {
    "missing-id.md": {"C2", "C3"},
    "bad-id-format.md": {"C2"},
    "missing-headline.md": {"C3"},
    "bad-category.md": {"C3"},
    "missing-action.md": {"C3"},
    "action-filesystem-path.md": {"C4"},
    "action-wrong-target.md": {"C4"},
    "bad-regex.md": {"C6"},
    "missing-verified-at.md": {"C7"},
    "bad-verified-at.md": {"C7"},
    "unknown-keys-ok.md": set(),  # positive fixture (C8): fully conformant
}


def test_fixtures_directory_covers_expected_set() -> None:
    on_disk = {p.name for p in FIXTURES_DIR.glob("*.md")}
    expected = set(_FIXTURE_EXPECTATIONS)
    assert on_disk == expected, (
        "fixtures dir does not match the expected set -- "
        f"on disk only: {on_disk - expected}; expected only: {expected - on_disk}"
    )


@pytest.mark.parametrize(
    "filename,expected_failures", sorted(_FIXTURE_EXPECTATIONS.items())
)
def test_fixture_fails_exactly_its_targeted_clause(
    filename: str, expected_failures: set[str]
) -> None:
    path = FIXTURES_DIR / filename
    assert path.is_file(), f"missing fixture {path}"
    meta, item = _load(path)
    violations = _validate_packet(path, meta, item)
    actual_failures = set(violations)
    assert actual_failures == expected_failures, (
        f"{filename}: expected exactly {expected_failures or '{}'} to fail, "
        f"got {actual_failures or '{}'}\n"
        + "\n".join(msg for msgs in violations.values() for msg in msgs)
    )


def test_unknown_keys_fixture_is_fully_conformant_and_parses() -> None:
    """C8: unknown frontmatter keys are ignored, never fatal -- positive fixture."""
    path = FIXTURES_DIR / "unknown-keys-ok.md"
    meta, item = _load(path)
    assert meta, "frontmatter must parse"
    assert "totally_unknown_key" in meta  # sanity: the unknown key really is there
    assert item is not None, (
        "a fully conformant packet must still construct a CatalogItem despite "
        "carrying unknown frontmatter keys"
    )
    violations = _validate_packet(path, meta, item)
    assert not violations, f"unknown-keys-ok.md must be fully green: {violations}"
