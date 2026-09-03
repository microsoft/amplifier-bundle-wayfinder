"""Conformance-ledger checks for wayfinder (``ledger/rows.yaml``).

Two jobs, both plain pytest -- no DTU, no network, no model, no subprocess:

1. **Row probes** -- the assertions ``ledger/rows.yaml`` cites by name for the
   Core clauses the repo's own contract kit deliberately declines to assert
   (C1 and C5 -- see ``modules/hooks-wayfinder/tests/test_packet_contract.py``
   docstring, "structural properties of the consumer's own architecture"), plus
   the OPEN-PINNED row that pins an undecided call against current behavior.
   Every other row is ``kind: indexed`` and cites that kit directly; this file
   never reimplements it.

2. **Coverage tripwires** (LEDGER-FORMAT §6) -- run with the ledger, every
   time: every REQUIRED clause of the FROZEN contract is cited by >=1 row;
   every row's quote verifies against contract bytes; every assertion ref
   resolves; every GAP/VIOLATION row carries a live ``work`` ref.

Run:
    PYTHONPATH=modules/hooks-wayfinder python3 -m pytest ledger/checks -q
"""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[2]
ROWS_PATH = ROOT / "ledger" / "rows.yaml"
CONTRACT_PATH = ROOT / "contracts" / "packet.v1.md"

# Import the consumer the same way the repo's own kit does. Adding the module
# dir to sys.path keeps these checks runnable whether or not PYTHONPATH is set.
_MODULE_DIR = ROOT / "modules" / "hooks-wayfinder"
if str(_MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(_MODULE_DIR))

from amplifier_module_hooks_wayfinder import (  # noqa: E402
    WayfinderConfig,
    WayfinderHooks,
    load_catalog,
    parse_frontmatter,
)

DISPOSITIONS = {
    "CONFORMS",
    "GAP",
    "VIOLATION",
    "OPEN-PINNED",
    "NOT-ASSERTABLE",
    "EXCLUDED",
    "DIVERGED",
}

# Every REQUIRED clause of the FROZEN contract (tripwire 1). "Conformance" is
# included because the contract's Conformance section names a check the ledger
# is explicitly required to carry (as NOT-ASSERTABLE) and "SYNC" because §4
# mandates the pin row.
REQUIRED_CLAUSES = {f"Core {n}" for n in range(1, 9)} | {"Conformance", "SYNC"}


def _rows() -> list[dict]:
    data = yaml.safe_load(ROWS_PATH.read_text(encoding="utf-8"))
    assert isinstance(data, list), (
        "ledger/rows.yaml must parse as a top-level YAML LIST of rows "
        "(LEDGER-FORMAT §2) -- no wrapper mapping, no `meta:` key"
    )
    return data


def _collapse(text: str) -> str:
    """Whitespace-collapsed form used for quote matching (LEDGER-FORMAT §2)."""
    return " ".join(text.split())


ROWS = _rows()
CONTRACT_COLLAPSED = _collapse(CONTRACT_PATH.read_text(encoding="utf-8"))


# --------------------------------------------------------------------------- #
# Discovery helpers -- mirror the consumer's own resolution exactly.
# --------------------------------------------------------------------------- #
_HOOKS = WayfinderHooks(WayfinderConfig())
_own = _HOOKS._resolve_own_dir()
assert _own is not None and _own.is_dir(), (
    "could not resolve wayfinder's own content dir via the consumer's own "
    "WayfinderHooks._resolve_own_dir()"
)
CONTENT_DIR: Path = _own

# C1's registered content sources, verbatim from the clause.
REGISTERED_SOURCES = ("bulletins", "practices", "concepts")


def _real_packets() -> list[Path]:
    return sorted(CONTENT_DIR.rglob("*.md"))


# --------------------------------------------------------------------------- #
# LGR-000 -- SYNC row: contract file pin
# --------------------------------------------------------------------------- #
def test_row_lgr_000() -> None:
    """A hash mismatch is a mandatory full-ledger re-review, never a bump."""
    row = _row("LGR-000")
    pins = row.get("sync")
    assert pins, "SYNC row must pin at least one contract file"
    for pin in pins:
        path = ROOT / pin["path"]
        assert path.is_file(), f"pinned contract file is missing: {pin['path']}"
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        assert actual == pin["sha256"], (
            f"LEDGER-INTEGRITY: {pin['path']} changed since the ledger was "
            f"seeded (pinned {pin['sha256'][:12]}, now {actual[:12]}).\n"
            "This triggers a MANDATORY FULL-LEDGER RE-REVIEW -- never a silent "
            "hash bump. Quote verification proves the quoted text still exists; "
            "only the re-review confirms each row's READING of it is still "
            "correct. Two legal exits: revert the contract change, or in the "
            "SAME change re-review every row and update this pin. Doing neither "
            "means main carries a ledger that lies. That is drift."
        )


# --------------------------------------------------------------------------- #
# LGR-001 -- Core 1: one file, one packet
# --------------------------------------------------------------------------- #
def test_row_lgr_001() -> None:
    packets = _real_packets()
    assert packets, "expected at least one real packet under content/**"

    # Half 1: every packet sits under one of the three registered sources.
    misplaced = []
    for path in packets:
        rel = path.relative_to(CONTENT_DIR)
        if rel.parts[0] not in REGISTERED_SOURCES:
            misplaced.append(str(rel))
    assert not misplaced, (
        "REGRESSION [Core 1] packets outside a registered content source "
        f"{REGISTERED_SOURCES}: {misplaced}"
    )

    # Half 2: file <-> packet is a bijection. load_catalog makes exactly one
    # _item_from_meta call per file, so a file can contribute at most one
    # packet; assert no file is silently dropped and no id spans two files.
    items = load_catalog([("default", CONTENT_DIR)], curate=False)
    source_paths = [Path(it.source_path).resolve() for it in items.values()]
    assert len(items) == len(packets), (
        "[Core 1] file<->packet is not 1:1: "
        f"{len(packets)} markdown files under content/** produced "
        f"{len(items)} catalog items. Either a file carries no parseable "
        "packet, or two files collided on one id."
    )
    assert len(set(source_paths)) == len(source_paths), (
        "[Core 1] two catalog items claim the same source file"
    )
    assert set(source_paths) == {p.resolve() for p in packets}, (
        "[Core 1] catalog source files do not match the discovered packet set"
    )


# --------------------------------------------------------------------------- #
# LGR-006 -- Core 5: catalog derived from frontmatter alone
# --------------------------------------------------------------------------- #
_PROBE_PACKET = """---
id: ledger-probe-packet
category: practice
headline: "A throwaway packet used to prove the catalog is derived."
trigger: "never -- this file only exists inside a tmp_path during the probe"
action: 'read_file("@wayfinder:content/practices/ledger-probe-packet.md")'
verified_at: 2026-09-03
provenance: "ledger/checks/test_ledger.py, LGR-006 probe"
---

Body.
"""


def test_row_lgr_006(tmp_path: Path) -> None:
    """Adding a conforming file adds the offer; removing it removes it."""
    src = tmp_path / "practices"
    src.mkdir()

    # Before: nothing to derive from -- and no registration step exists to skip.
    assert load_catalog([("probe", tmp_path)], curate=False) == {}

    packet = src / "ledger-probe-packet.md"
    packet.write_text(_PROBE_PACKET, encoding="utf-8")

    # After: the offer exists purely because the FILE exists. Nothing was
    # registered, indexed, or declared anywhere.
    items = load_catalog([("probe", tmp_path)], curate=False)
    assert set(items) == {"ledger-probe-packet"}, (
        "[Core 5] adding a conforming file did not add the offer"
    )
    assert items["ledger-probe-packet"].headline, (
        "[Core 5] the derived item's fields must come from frontmatter alone"
    )

    packet.unlink()
    assert load_catalog([("probe", tmp_path)], curate=False) == {}, (
        "[Core 5] removing the file did not remove the offer"
    )


# --------------------------------------------------------------------------- #
# LGR-007 -- Core 5: no index/registry file exists or is read (absence)
# --------------------------------------------------------------------------- #
_REGISTRY_STEMS = {
    "index",
    "catalog",
    "registry",
    "manifest",
    "offer-catalog",
    "offers",
}
_REGISTRY_SUFFIXES = {".md", ".yaml", ".yml", ".json", ".toml"}


def test_row_lgr_007() -> None:
    """Absence assertion: a silently-introduced registry flips this row red."""
    # The historical registry the derived catalog replaced.
    legacy = ROOT / "context" / "offer-catalog.md"
    assert not legacy.exists(), (
        "[Core 5] context/offer-catalog.md is back. The catalog is derived; "
        "'No index file exists to update, and none may be introduced.'"
    )

    # Any registry-shaped file anywhere under the content tree.
    found = [
        str(p.relative_to(ROOT))
        for p in CONTENT_DIR.rglob("*")
        if p.is_file()
        and p.suffix.lower() in _REGISTRY_SUFFIXES
        and p.stem.lower() in _REGISTRY_STEMS
    ]
    assert not found, (
        f"[Core 5] registry-shaped file(s) introduced under content/: {found}"
    )

    # And the consumer reads none: catalog assembly is rglob over *.md only.
    src = (_MODULE_DIR / "amplifier_module_hooks_wayfinder" / "__init__.py").read_text(
        encoding="utf-8"
    )
    body = src[src.index("def load_catalog(") :]
    body = body[: body.index("\ndef ", 1)]
    assert 'rglob("*.md")' in body, (
        "[Core 5] load_catalog no longer derives the catalog by scanning markdown files"
    )
    # A registry being read would appear as a filename LITERAL. Matching the
    # bare word would false-positive on `load_catalog`/`CatalogItem` itself.
    registry_literal = re.compile(
        r"""['"][\w./-]*(?:"""
        + "|".join(re.escape(s) for s in sorted(_REGISTRY_STEMS))
        + r""")\.(?:md|ya?ml|json|toml)['"]""",
        re.IGNORECASE,
    )
    hit = registry_literal.search(body)
    assert hit is None, (
        f"[Core 5] load_catalog now reads a registry file literal: {hit.group(0)}"  # type: ignore[union-attr]
    )


# --------------------------------------------------------------------------- #
# LGR-015 -- OPEN-PINNED: filename stem vs id (undecided; pinned both ways)
# --------------------------------------------------------------------------- #
# The pinned SET, not a single file: renaming current.md flips this row (the
# decision got made -- record it), and adding a SECOND filename!=id packet also
# flips it (the latitude spread -- decide before it becomes the norm).
_PINNED_STEM_ID_DIVERGENCES = {("bulletins/current.md", "switch-models")}


def test_row_lgr_015() -> None:
    actual = set()
    for path in _real_packets():
        meta, _body = parse_frontmatter(path.read_text(encoding="utf-8"))
        raw_id = meta.get("id")
        if not (isinstance(raw_id, str) and raw_id.strip()):
            continue
        rel = path.relative_to(CONTENT_DIR).as_posix()
        if path.stem != raw_id.strip():
            actual.add((rel, raw_id.strip()))

    assert actual == _PINNED_STEM_ID_DIVERGENCES, (
        "UNDECIDED-MOVEMENT [LGR-015] the filename-stem vs id divergence set "
        f"changed.\n  pinned:   {sorted(_PINNED_STEM_ID_DIVERGENCES)}\n"
        f"  observed: {sorted(actual)}\n"
        "The contract does not require filename==id; this row pins the "
        "current, UNDECIDED state so neither 'fixing' nor spreading it happens "
        "silently. Two legal exits: revert, or in the SAME change update "
        "LGR-015 (and the contract, if the call is to require agreement). "
        "Doing neither means main carries a ledger that lies. That is drift."
    )


# --------------------------------------------------------------------------- #
# Coverage tripwires (LEDGER-FORMAT §6) -- run with the ledger, every time.
# --------------------------------------------------------------------------- #
def _row(row_id: str) -> dict:
    for row in ROWS:
        if row.get("id") == row_id:
            return row
    raise AssertionError(f"no ledger row {row_id}")


def test_rows_are_well_formed_and_uniquely_identified() -> None:
    ids = [r.get("id") for r in ROWS]
    assert len(ids) == len(set(ids)), f"duplicate row ids: {ids}"
    assert ROWS[0].get("id") == "LGR-000", (
        "the SYNC row must be the first row in the list (LEDGER-FORMAT §4)"
    )
    for row in ROWS:
        rid = row.get("id")
        assert re.fullmatch(r"LGR-\d{3}", str(rid)), f"malformed row id {rid!r}"
        assert row.get("title"), f"{rid}: missing title"
        assert row.get("disposition") in DISPOSITIONS, (
            f"{rid}: disposition {row.get('disposition')!r} is outside the "
            f"vocabulary {sorted(DISPOSITIONS)}"
        )
        contract = row.get("contract")
        assert isinstance(contract, dict), f"{rid}: missing `contract:` block"
        assert contract.get("quote"), (
            f"{rid}: quote must live NESTED under `contract:` -- a top-level "
            "quote is malformed and dodges verification"
        )
        assert contract.get("clause"), f"{rid}: missing contract.clause"


def test_tripwire_1_every_required_clause_is_cited_by_a_row() -> None:
    cited = {r["contract"]["clause"] for r in ROWS}
    missing = REQUIRED_CLAUSES - cited
    assert not missing, (
        "LEDGER-INTEGRITY: REQUIRED clause(s) of a FROZEN contract cited by no "
        f"ledger row: {sorted(missing)}"
    )


def test_tripwire_3a_every_quote_verifies_against_contract_bytes() -> None:
    failures = []
    for row in ROWS:
        quote = _collapse(row["contract"]["quote"])
        if quote not in CONTRACT_COLLAPSED:
            failures.append(f"{row['id']}: {quote[:90]!r}")
    assert not failures, (
        "LEDGER-INTEGRITY: quote(s) no longer verify against "
        f"{CONTRACT_PATH.name} bytes (whitespace-collapsed contiguous match):\n"
        + "\n".join(failures)
    )


def test_tripwire_3b_every_assertion_ref_resolves() -> None:
    module = sys.modules[__name__]
    for row in ROWS:
        rid = row["id"]
        assertion = row.get("assertion") or {}
        kind = assertion.get("kind")
        assert kind in {"probe", "indexed", "absence", "none"}, (
            f"{rid}: unknown assertion.kind {kind!r}"
        )

        if kind == "none":
            assert row["disposition"] in {"NOT-ASSERTABLE", "OPEN-PINNED"}, (
                f"{rid}: assertion.kind 'none' is legal only for NOT-ASSERTABLE"
            )
            continue

        if kind in {"probe", "absence"}:
            ref = assertion.get("ref")
            assert isinstance(ref, str) and hasattr(module, ref), (
                f"{rid}: probe ref {ref!r} does not resolve to a function in "
                f"{Path(__file__).name}"
            )
            continue

        # indexed: verify STATICALLY (parse, don't import) so cites may cross
        # environment boundaries.
        refs = assertion.get("ref")
        assert isinstance(refs, list) and refs, f"{rid}: indexed ref must be a list"
        for cite in refs:
            file_part, _, test_name = str(cite).partition("::")
            path = ROOT / file_part
            assert path.is_file(), f"{rid}: cited test file missing: {file_part}"
            assert test_name, f"{rid}: cite {cite!r} names no test"
            src = path.read_text(encoding="utf-8")
            assert re.search(
                rf"^\s*(?:async )?def {re.escape(test_name)}\(", src, re.M
            ), f"{rid}: cited test {test_name!r} not found in {file_part}"


def test_tripwire_3c_red_rows_carry_a_live_work_ref() -> None:
    for row in ROWS:
        if row["disposition"] in {"GAP", "VIOLATION"}:
            assert row.get("work"), (
                f"{row['id']}: a {row['disposition']} row without a filed "
                "`work` ref is a ledger that lies"
            )


def test_undecided_and_unassertable_rows_carry_a_justification() -> None:
    for row in ROWS:
        if row["disposition"] in {"OPEN-PINNED", "NOT-ASSERTABLE", "DIVERGED"}:
            assert row.get("justification"), (
                f"{row['id']}: {row['disposition']} requires a justification -- "
                "judgment is named here, never smuggled"
            )


def test_probe_and_row_cross_check_is_bidirectional() -> None:
    """Every probe in this file is cited by a row, and vice versa."""
    cited = {
        (row.get("assertion") or {}).get("ref")
        for row in ROWS
        if (row.get("assertion") or {}).get("kind") in {"probe", "absence"}
    }
    defined = {
        name for name in dir(sys.modules[__name__]) if name.startswith("test_row_lgr_")
    }
    assert cited == defined, (
        f"probe<->row drift -- cited but undefined: {sorted(cited - defined)}; "
        f"defined but uncited: {sorted(defined - cited)}"
    )


@pytest.mark.parametrize("row", ROWS, ids=[r["id"] for r in ROWS])
def test_self_governed_contract_has_no_diverged_rows(row: dict) -> None:
    """DIVERGED is illegal for a contract this team owns (LEDGER-FORMAT §3)."""
    assert row["disposition"] != "DIVERGED", (
        f"{row['id']}: contracts/packet.v1.md is self-governed -- disagreement "
        "is a CANDIDATE amendment, not a ledgered divergence"
    )
