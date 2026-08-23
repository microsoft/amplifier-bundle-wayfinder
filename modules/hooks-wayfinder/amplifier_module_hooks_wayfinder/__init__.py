"""hooks-wayfinder — Wayfinder's Ring 1 hook (its first Python).

Three deterministic, config-tunable, ephemeral jobs:

1. ``session:start`` — resolve the content sources, scan per-item frontmatter,
   and assemble the DERIVED offer catalog (replacing the hand-maintained
   ``offer-catalog.md``). Read the decline file and filter it here — decline
   *enforcement* is deterministic. Also pick the session's LEAD via promoted-item
   rotation: the freshest-unseen ``promoted: true`` item (lowest surfaced count,
   oldest last_shown, then id) from the persistent seen-memory, so multiple
   promoted items rotate across sessions instead of the same bulletin forever.
   This handler does the deterministic WORK and caches the result; it injects
   nothing (so nothing persistent is ever added).

2. ``prompt:submit`` (first prompt of the session) — apply the FIRST-TOUCH policy
   (F1): classify the opening prompt (orienting | greeting | task | ambiguous)
   and surface accordingly — orienting gets today's full lead (catalog index +
   rotation packet), greeting/ambiguous get a headline-only LIGHT tease, and a
   task-shaped opener gets NOTHING this turn (don't interrupt someone who came to
   work). Identity-orienting queries still route to the self-intro (deferring the
   lead), unchanged. Zero promoted items (or ``promoted_rotation: false``) falls
   back to the single ``on_event: session:start`` bulletin, as before. Any lead
   that actually lands records its surfacing in the seen-memory.

3. ``prompt:submit`` (any later prompt) — TWO signals, checked in order: the
   re-summonable MENU (F3) fires on "what else / the menu / more options" at any
   turn and injects the full current offer menu (declines filtered, notes when
   the rotation is all-seen) so the menu never dead-ends; otherwise one
   conservative ``prompt_matches`` nudge per offer, rate-limited and
   declines-filtered. A single nudge only — the hook can never act.

Why delivery rides ``prompt:submit`` and not ``session:start``: the only
CONFIRMED ephemeral-injection path in the reference orchestrator
(``loop-streaming``) is ``prompt:submit`` — it stores the ephemeral injection in
``_pending_ephemeral_injections`` for the first iteration. The shipping
``session:start`` injection pattern (``hooks-deprecation``) is *persistent*,
which the "ephemeral only, never persistent" constraint forbids. So the
``session:start`` handler assembles + decline-filters (that is where the hook
genuinely "fires at session start"), and the first ``prompt:submit`` delivers
the assembled packet ephemerally. Net: fires at session start, surfaces once,
never persists.

The WRITE of a new decline stays agent-mediated. A hard explicit decline itself
authorizes recording; a soft decline writes nothing. This hook never writes the
decline file.
"""

from __future__ import annotations

import json
import logging
import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml
from amplifier_core import HookResult

logger = logging.getLogger(__name__)

_SOURCE = "hooks-wayfinder"


# --------------------------------------------------------------------------- #
# First-touch classification defaults (F1) + menu re-summon defaults (F3)
#
# All are conservative, keyword/regex, case-insensitive (compiled with
# re.IGNORECASE). Every set is a tunable config knob; these are only the
# defaults. Precedence on the first prompt is orienting -> greeting -> task ->
# ambiguous, so each set's job differs:
#   - orienting   : SPECIFIC system-orientation phrasings only ("what's new",
#                   "what can you do") -> keep today's full-lead behavior.
#   - greeting    : WHOLE-message anchored (^...$) bare hellos, so a greeting
#                   that carries a task ("hi, help me build X") does NOT match
#                   here and falls through to the task set -> light headline.
#   - task        : work signals (imperatives, "I need", errors, a trailing ?)
#                   -> stay QUIET, don't interrupt someone who came to work.
#   - menu (F3)   : "what else / more / the menu" -> re-summon the full menu at
#                   any turn. Kept disjoint from orienting so it never steals
#                   an orienting first prompt.
# --------------------------------------------------------------------------- #
_DEFAULT_ORIENTING_PATTERNS: tuple[str, ...] = (
    r"\bwhat(?:'?s| is| are)?\s+new\b",
    r"\banything\s+new\b",
    r"\bwhat\s+can\s+you\s+(?:do|help)\b",
    r"\bwhat\s+(?:do|can)\s+you\s+do\b",
    r"\bwhat\s+are\s+you\s+(?:able|capable)\b",
    r"\bwho\s+are\s+you\b",
    r"\bwhat\s+is\s+this\b",
    r"\bwhat(?:'?s| is)\s+wayfinder\b",
    r"\bhow\s+do\s+i\s+(?:use|get\s+started|start|begin)\b",
    r"\bhow\s+does\s+this\s+work\b",
    r"\bwhat\s+should\s+i\s+know\b",
    r"\bgetting\s+started\b",
)
_DEFAULT_GREETING_PATTERNS: tuple[str, ...] = (
    (
        r"^\s*(?:hi+|hey+|hello+|yo+|sup|howdy|hiya|heya|greetings|hi\s+there|"
        r"hey\s+there|hello\s+there|good\s+(?:morning|afternoon|evening|day)|"
        r"g'?day|gm|mornin[g']?|what'?s\s+(?:up|good)|how'?s\s+it\s+going)"
        r"\b[\s!.,?~-]*$"
    ),
    r"^\s*(?:hi+|hey+|hello+|yo+|greetings)\s+wayfinder\b[\s!.,?~-]*$",
)
_DEFAULT_TASK_PATTERNS: tuple[str, ...] = (
    r"\bi\s+need\b",
    r"\bi\s+want\s+to\b",
    r"\bi'?m\s+trying\s+to\b",
    r"\bi'?d\s+like\s+to\b",
    r"\bhelp\s+me\b",
    (
        r"\bcan\s+you\s+(?:help|write|build|fix|add|make|create|implement|"
        r"refactor|debug|review|update|change|set\s+up|generate)\b"
    ),
    r"\bcould\s+you\b",
    r"\bplease\b",
    r"\blet'?s\b",
    (
        r"\b(?:build|fix|add|implement|write|debug|create|refactor|update|change|"
        r"remove|delete|install|configure|generate|migrate|optimi[sz]e)\b"
    ),
    (
        r"\berror\b|\bexception\b|\btraceback\b|\bstack\s*trace\b|"
        r"\bfail(?:ed|ing|ure)?\b|\bbug\b|\bbroken\b|\bcrash"
    ),
    r"\?\s*$",
)
_DEFAULT_MENU_PATTERNS: tuple[str, ...] = (
    r"\bwhat\s+else\b",
    r"\banything\s+else\b",
    r"\bwhat\s+other\b",
    r"\bother\s+(?:offers?|options?)\b",
    r"\bmore\s+options?\b",
    r"\bshow\s+(?:me\s+)?(?:the\s+)?(?:full\s+)?menu\b",
    r"\bthe\s+(?:full\s+)?menu\b",
    r"\bfull\s+menu\b",
    r"\blist\s+(?:the\s+|all\s+)?offers?\b",
    r"\ball\s+(?:the\s+)?offers?\b",
)


def _coerce_patterns(raw: Any, default: tuple[str, ...]) -> tuple[str, ...]:
    """Coerce a config override into a tuple of pattern strings, else default.

    Accepts a single string (one pattern), a list/tuple (many), or None/empty
    (keep the default). An override that resolves to zero usable patterns also
    falls back to the default rather than silently disabling the classifier.
    """
    if raw is None:
        return default
    if isinstance(raw, str):
        return (raw,) if raw.strip() else default
    if isinstance(raw, (list, tuple)):
        vals = tuple(str(v).strip() for v in raw if v and str(v).strip())
        return vals or default
    return default


# --------------------------------------------------------------------------- #
# Config
# --------------------------------------------------------------------------- #
@dataclass
class WayfinderConfig:
    """All knobs are tunable via the hook's ``config:`` in the behavior YAML."""

    enabled: bool = True
    # Own-dir override. Scalar, back-compat, now @-aware (accepts an @ns:path or
    # a literal filesystem path). When set it OVERRIDES the implicit
    # auto-detected own-dir (<bundle>/content). When unset the own-dir is
    # auto-detected and always loaded first.
    content_dir: str | None = None
    # Additive, keyed map of EXTRA content packs; each value is an @ns:path or a
    # literal filesystem path. A MAP (not a list) so hook-config deep-merge by
    # module id merges packs additively by key across composition instead of
    # replacing — two bundles can each add a pack. Own-dir loads first (source
    # key "default"), then these in declared order; first-id-wins on collision.
    content_sources: dict[str, str] = field(default_factory=dict)
    declines_path: str | None = None  # default: env/HOME wayfinder dir
    # Seen-memory for promoted-lead rotation. A JSONL of {id, count, last_shown}
    # records; default <wayfinder dir>/surfaced.jsonl (same env/HOME pattern as
    # declines_path). Reads tolerate missing/corrupt; the hook writes it as its
    # own deterministic bookkeeping when it surfaces a promoted lead.
    surfaced_path: str | None = None
    # Promoted-lead rotation. When true (default), session:start surfaces the
    # freshest-unseen promoted item (lowest surfaced count, tie-break oldest
    # last_shown, then id) as the lead, rotating across fresh sessions. When
    # false, behave as before: surface the single on_event:session:start
    # bulletin every session.
    promoted_rotation: bool = True
    signals_enabled: bool = True
    curate: bool = False  # False = derive-first (all items); True = only curated: true
    max_hints_per_session: int = 3
    # Offer ids that answer an ORIENTING query ("what is wayfinder?", "what can
    # you help with?", "who are you", "how do I get started"). When one of these
    # signals fires the hook injects a STRONGER, directive nudge (deliver the
    # self-introduction, in voice, this is a wayfinder question not a generic
    # Amplifier-capabilities one) and, on the first prompt, defers the
    # session:start bulletin one turn so the two don't compete for salience.
    self_intro_ids: tuple[str, ...] = ("about-wayfinder",)
    # F1 first-touch policy. When true (default), classify the FIRST prompt of a
    # session (orienting | greeting | task | ambiguous) and surface accordingly:
    # orienting -> today's full lead; greeting/ambiguous -> headline-only light
    # lead; task -> stay QUIET this turn. When false, fall back to today's
    # always-full-lead behavior. The three pattern sets below are the tunable
    # heuristics; precedence is orienting -> greeting -> task -> ambiguous.
    first_touch: bool = True
    # On the FIRST prompt, run the per-item ``prompt_matches`` check BEFORE F1
    # classification: a signal match on the opener is user-INITIATED relevance
    # (they asked about the offer's topic), so it must not be suppressed by the
    # task-QUIET bucket. When true (default), a first-prompt signal summons that
    # packet directly and skips the F1 lead entirely; the self-intro path and
    # its defer-the-lead behavior are unaffected (self-intro items are handled
    # by their own step). When false, turn-1 behaves exactly as before (F1 only;
    # per-item signals still fire on later turns). Gated additionally by
    # ``signals_enabled``.
    first_prompt_signals: bool = True
    orienting_patterns: tuple[str, ...] = _DEFAULT_ORIENTING_PATTERNS
    greeting_patterns: tuple[str, ...] = _DEFAULT_GREETING_PATTERNS
    task_patterns: tuple[str, ...] = _DEFAULT_TASK_PATTERNS
    # F3 re-summonable menu. When true (default), a menu-signal at ANY turn
    # injects the full current offer menu (declines already filtered). The
    # pattern set is tunable; kept disjoint from orienting so it never steals an
    # orienting first prompt.
    menu_enabled: bool = True
    menu_patterns: tuple[str, ...] = _DEFAULT_MENU_PATTERNS

    @classmethod
    def from_dict(cls, raw: dict[str, Any] | None) -> WayfinderConfig:
        raw = raw or {}
        raw_self_intro = raw.get("self_intro_ids")
        if raw_self_intro is None:
            self_intro_ids: tuple[str, ...] = ("about-wayfinder",)
        elif isinstance(raw_self_intro, str):
            self_intro_ids = (raw_self_intro,)
        else:
            self_intro_ids = tuple(str(v).strip() for v in raw_self_intro if v)
        raw_sources = raw.get("content_sources")
        if isinstance(raw_sources, dict):
            content_sources = {
                str(k): str(v).strip()
                for k, v in raw_sources.items()
                if v and str(v).strip()
            }
        else:
            content_sources = {}
        return cls(
            enabled=bool(raw.get("enabled", True)),
            content_dir=raw.get("content_dir") or None,
            content_sources=content_sources,
            declines_path=raw.get("declines_path") or None,
            surfaced_path=raw.get("surfaced_path") or None,
            promoted_rotation=bool(raw.get("promoted_rotation", True)),
            signals_enabled=bool(raw.get("signals_enabled", True)),
            curate=bool(raw.get("curate", False)),
            max_hints_per_session=int(raw.get("max_hints_per_session", 3)),
            self_intro_ids=self_intro_ids,
            first_touch=bool(raw.get("first_touch", True)),
            first_prompt_signals=bool(raw.get("first_prompt_signals", True)),
            orienting_patterns=_coerce_patterns(
                raw.get("orienting_patterns"), _DEFAULT_ORIENTING_PATTERNS
            ),
            greeting_patterns=_coerce_patterns(
                raw.get("greeting_patterns"), _DEFAULT_GREETING_PATTERNS
            ),
            task_patterns=_coerce_patterns(
                raw.get("task_patterns"), _DEFAULT_TASK_PATTERNS
            ),
            menu_enabled=bool(raw.get("menu_enabled", True)),
            menu_patterns=_coerce_patterns(
                raw.get("menu_patterns"), _DEFAULT_MENU_PATTERNS
            ),
        )


# --------------------------------------------------------------------------- #
# Catalog model
# --------------------------------------------------------------------------- #
@dataclass
class CatalogItem:
    id: str
    category: str
    headline: str
    try_now: list[str] = field(default_factory=list)
    trigger: str = ""
    action: str = ""
    on_events: list[str] = field(default_factory=list)
    prompt_patterns: list[re.Pattern[str]] = field(default_factory=list)
    curated: bool = False
    promoted: bool = False
    source_path: str = ""
    # Provenance: the source key this item came from ("default" = own content,
    # else the content_sources map key). Captured now; no consumer yet.
    source: str = "default"


@dataclass
class SessionCatalog:
    items: dict[str, CatalogItem] = field(default_factory=dict)
    declined_ids: set[str] = field(default_factory=set)
    index_text: str = ""
    start_items: list[CatalogItem] = field(default_factory=list)
    # The rotation-chosen promoted lead for this session (None → fall back to
    # start_items). When set, delivery records a surfacing against its id.
    promoted_lead: CatalogItem | None = None


# --------------------------------------------------------------------------- #
# Frontmatter parsing
# --------------------------------------------------------------------------- #
def parse_frontmatter(text: str) -> tuple[dict[str, Any], str]:
    """Split a ``---`` YAML frontmatter block from a markdown body.

    Returns ``({}, text)`` when there is no well-formed frontmatter. Never
    raises on malformed YAML — returns an empty meta instead.
    """
    stripped = text.lstrip("\ufeff")  # tolerate a BOM
    if not stripped.startswith("---"):
        return {}, text
    lines = stripped.splitlines(keepends=True)
    if not lines or lines[0].strip() != "---":
        return {}, text
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            fm_text = "".join(lines[1:i])
            body = "".join(lines[i + 1 :])
            try:
                meta = yaml.safe_load(fm_text)
            except yaml.YAMLError:
                logger.warning("%s: malformed frontmatter YAML; skipping item", _SOURCE)
                return {}, body
            if not isinstance(meta, dict):
                return {}, body
            return meta, body
    return {}, text


def _as_str_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, (list, tuple)):
        return [str(v) for v in value if v is not None]
    return [str(value)]


def _compile_patterns(patterns: list[str]) -> list[re.Pattern[str]]:
    compiled: list[re.Pattern[str]] = []
    for pat in patterns:
        try:
            compiled.append(re.compile(pat, re.IGNORECASE))
        except re.error:
            logger.warning(
                "%s: invalid prompt_matches regex %r; skipping", _SOURCE, pat
            )
    return compiled


def _item_from_meta(
    meta: dict[str, Any], source_path: str, source: str = "default"
) -> CatalogItem | None:
    item_id = meta.get("id")
    if not item_id or not isinstance(item_id, str):
        return None  # not a catalog item
    signals = meta.get("signals")
    if not isinstance(signals, dict):
        signals = {}
    return CatalogItem(
        id=item_id.strip(),
        category=str(meta.get("category", "")).strip(),
        headline=str(meta.get("headline", "")).strip(),
        try_now=_as_str_list(meta.get("try_now")),
        trigger=str(meta.get("trigger", "")).strip(),
        action=str(meta.get("action", "")).strip(),
        on_events=_as_str_list(signals.get("on_event")),
        prompt_patterns=_compile_patterns(_as_str_list(signals.get("prompt_matches"))),
        curated=bool(meta.get("curated", False)),
        promoted=bool(meta.get("promoted", False)),
        source_path=source_path,
        source=source,
    )


def load_catalog(
    sources: list[tuple[str, Path]], curate: bool
) -> dict[str, CatalogItem]:
    """Derive the catalog from frontmatter across ordered content sources.

    ``sources`` is an ordered ``(source_key, dir)`` list — own content first
    (key ``"default"``), then each configured pack in declared order. Each dir
    is scanned recursively. First-id-wins on collision (own/public content wins;
    a shadowed id is logged with both source keys). When ``curate`` is true,
    only items carrying ``curated: true`` are included.
    """
    items: dict[str, CatalogItem] = {}
    for source_key, content_dir in sources:
        for md_path in sorted(content_dir.rglob("*.md")):
            try:
                text = md_path.read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                logger.warning("%s: could not read %s; skipping", _SOURCE, md_path)
                continue
            meta, _ = parse_frontmatter(text)
            item = _item_from_meta(meta, str(md_path), source_key)
            if item is None:
                continue
            if curate and not item.curated:
                continue
            if item.id in items:
                logger.warning(
                    "%s: offer id %r from source %r shadowed by source %r; keeping first",
                    _SOURCE,
                    item.id,
                    source_key,
                    items[item.id].source,
                )
                continue
            items[item.id] = item
    return items


# --------------------------------------------------------------------------- #
# Decline-memory (deterministic READ/FILTER only — never written here)
# --------------------------------------------------------------------------- #
def read_declined_ids(declines_path: Path, known_ids: set[str]) -> set[str]:
    """An offer id is declined iff it appears as a whole word in the file.

    Lenient by design so it survives the agent's free-form appends ("no",
    bullets, dates, etc.). Missing file / dir → no declines (never created here).
    """
    try:
        text = declines_path.read_text(encoding="utf-8")
    except (FileNotFoundError, NotADirectoryError):
        return set()
    except (OSError, UnicodeDecodeError):
        logger.warning("%s: could not read declines at %s", _SOURCE, declines_path)
        return set()
    declined: set[str] = set()
    for item_id in known_ids:
        if re.search(rf"\b{re.escape(item_id)}\b", text):
            declined.add(item_id)
    return declined


# --------------------------------------------------------------------------- #
# Seen-memory (promoted-lead rotation): read/select here, write in the hook
# --------------------------------------------------------------------------- #
def read_surfaced(surfaced_path: Path) -> dict[str, dict[str, Any]]:
    """Read the surfaced-lead JSONL into ``{id: {count, last_shown}}``.

    One JSON record per line; the last record for an id wins (so an appended or
    rewritten file both read correctly). Missing file / dir → ``{}`` (never
    created on read). Corrupt lines / malformed records are skipped, never
    raised — same tolerance discipline as the decline file.
    """
    try:
        text = surfaced_path.read_text(encoding="utf-8")
    except (FileNotFoundError, NotADirectoryError):
        return {}
    except (OSError, UnicodeDecodeError):
        logger.warning(
            "%s: could not read surfaced-memory at %s", _SOURCE, surfaced_path
        )
        return {}
    records: dict[str, dict[str, Any]] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except (json.JSONDecodeError, ValueError):
            continue  # tolerate a corrupt line
        if not isinstance(rec, dict):
            continue
        rid = rec.get("id")
        if not isinstance(rid, str) or not rid:
            continue
        raw_count = rec.get("count", 0)
        try:
            count = int(raw_count)
        except (TypeError, ValueError):
            count = 0
        last_shown = rec.get("last_shown", "")
        if not isinstance(last_shown, str):
            last_shown = ""
        records[rid] = {"count": count, "last_shown": last_shown}
    return records


def _select_promoted_lead(
    pool: list[CatalogItem], seen: dict[str, dict[str, Any]]
) -> CatalogItem | None:
    """Freshest-unseen promoted item: lowest count, oldest last_shown, then id.

    An unseen item has count 0 and last_shown "" — so it beats any already-shown
    item (count ≥ 1), and "" sorts before any ISO timestamp (which sort
    lexicographically = chronologically). Stable final tie-break by id.
    """
    if not pool:
        return None

    def sort_key(it: CatalogItem) -> tuple[int, str, str]:
        rec = seen.get(it.id) or {}
        return (int(rec.get("count", 0)), str(rec.get("last_shown", "")), it.id)

    return min(pool, key=sort_key)


# --------------------------------------------------------------------------- #
# Injection text builders (packet shape; point-don't-absorb)
# --------------------------------------------------------------------------- #
def _build_index_block(catalog: SessionCatalog) -> str:
    live = [it for it in catalog.items.values() if it.id not in catalog.declined_ids]
    if not live:
        return ""

    lines = [
        f'<system-reminder source="{_SOURCE}">',
        (
            "wayfinder — offer catalog for this session (DERIVED from content "
            "frontmatter; declined offers already filtered out). A direct user "
            "request matching an item authorizes ordinary in-scope work without a "
            "duplicate Wayfinder ack. Surface unsolicited optional suggestions "
            "below ONLY via propose→show→ack→act, one at a time, in wayfinder's voice."
        ),
        (
            "To show any packet's body, run its `body:` action EXACTLY as written "
            "(including its @namespace prefix — it may point to another bundle). "
            "Never glob/grep/search for the file. This menu is authoritative about "
            "what EXISTS: if an item is listed, it exists — follow its action."
        ),
        "",
        "Offers on the menu:",
    ]
    for it in live:
        cat = f" [{it.category}]" if it.category else ""
        lines.append(f"- {it.id}{cat}: {it.headline}")
        if it.action:
            lines.append(f"    body: {it.action}")

    # Lead: the rotation-chosen promoted item when present (already
    # decline-filtered), else today's on_event:session:start bulletin(s).
    if catalog.promoted_lead is not None:
        start = [catalog.promoted_lead]
    else:
        start = [it for it in catalog.start_items if it.id not in catalog.declined_ids]
    if start:
        lines.append("")
        lines.append(
            "SURFACE NOW — this session's lead (once, commands-first, lead with a "
            "2–3 line summary; read the file on demand for the rest, never paste "
            "the whole thing):"
        )
        for it in start:
            lines.append(f"  {it.id} — {it.headline}")
            if it.try_now:
                lines.append("  Try it now:")
                for n, cmd in enumerate(it.try_now, start=1):
                    lines.append(f"    {n}. {cmd}")
            if it.action:
                lines.append(f"  For the Why / Gotchas / More: {it.action} on demand.")
    lines.append("</system-reminder>")
    return "\n".join(lines)


def _build_hint_block(item: CatalogItem) -> str:
    cmd = f" (would show: {item.action})" if item.action else ""
    return (
        f'<system-reminder source="{_SOURCE}">\n'
        f"Possible fit: the user's message may relate to wayfinder offer "
        f"'{item.id}' — {item.headline}\n"
        f"First distinguish a direct request from optional relevance. If the user "
        f"directly requested work this capability can fulfill, use its curated "
        f"source and carry out the in-scope request without a "
        f"duplicate Wayfinder ack; normal host/tool/safety/destructive approvals "
        f"still apply. If the message merely makes this an optional useful next "
        f"step, PROPOSE it via propose→show→ack→act — show the exact action{cmd}, "
        f"then wait for an explicit ack. Single nudge; never act on an unsolicited "
        f"suggestion unattended. If it doesn't fit, ignore this.\n"
        f"</system-reminder>"
    )


def _build_self_intro_block(item: CatalogItem) -> str:
    """Strong, directive nudge for an ORIENTING query.

    Unlike ``_build_hint_block`` (a soft "possible fit"), this tells the agent
    plainly: the user is orienting to *wayfinder*, so answer by delivering
    wayfinder's own self-introduction in wayfinder's voice — this is a wayfinder
    question, not a generic Amplifier-capabilities one — and lead with it over
    the session-start bulletin this turn. Surfacing the overview IS the answer to
    an orienting question, so no propose→ack gate applies here (the offers listed
    inside the overview stay ack-gated as usual). It still mirrors the bulletin's
    point-don't-absorb discipline: summarise, commands-first, read on demand.
    """
    read_cmd = item.action or f'read_file("{item.source_path}")'
    return (
        f'<system-reminder source="{_SOURCE}">\n'
        f"The user is orienting to WAYFINDER — this is a wayfinder question, "
        f"NOT a generic Amplifier-capabilities question. Answer THIS turn by "
        f"delivering wayfinder's own self-introduction ('{item.id}': "
        f"{item.headline}).\n"
        f"Do it in wayfinder's voice: {read_cmd}, then lead with a 2–3 line "
        f"summary of what wayfinder is and the small curated menu it can point "
        f"you to (commands-first); read the file on demand rather than pasting "
        f"it whole. Prioritise this over the session-start bulletin this turn — "
        f"the bulletin can wait. Offers named in the overview remain optional and "
        f"ack-gated unless the user directly requests one; then fulfill that "
        f"in-scope request without a duplicate Wayfinder ack. Normal "
        f"host/tool/safety/destructive approvals still apply. Never run an "
        f"unsolicited suggestion unattended.\n"
        f"</system-reminder>"
    )


def _build_signal_summon_block(item: CatalogItem) -> str:
    """Direct-summon nudge for a FIRST-PROMPT per-item signal match.

    A signal match establishes relevance and authorizes reading the packet, not
    executing a capability. The emitted instruction tells the model to inspect
    the original prompt: an explicit matching action request authorizes that
    in-scope action without duplicate Wayfinder ack, while a merely topical,
    relevance, or information prompt authorizes only the packet read and answer.
    Optional actions remain offer-gated.
    """
    read_cmd = item.action or f'read_file("{item.source_path}")'
    action_line = f"  body: {item.action}\n" if item.action else ""
    return (
        f'<system-reminder source="{_SOURCE}">\n'
        f"The user's opening matched a topic wayfinder has "
        f"a packet for \u2014 offer '{item.id}': {item.headline}\n"
        f"{action_line}"
        f"A signal match establishes relevance only. It authorizes running the "
        f"packet's `body:` action above ({read_cmd}) to read the packet; it does "
        f"NOT by itself authorize any command, skill, installation, edit, or "
        f"other action described inside. Classify the user's actual request:\n"
        f"- If the user explicitly requested the matching action (for example, "
        f"install, run, use, execute, edit, or implement it), carry out that "
        f"in-scope request without a duplicate Wayfinder ack. Normal "
        f"host/tool/safety/destructive approvals still apply.\n"
        f"- If the prompt is merely topical, relevance-seeking, or informational "
        f"(for example, what/how/whether it fits), read and answer from the packet "
        f"only. Any action or install is then an optional Wayfinder offer: show "
        f"the exact action and wait for explicit ack. Never act on relevance "
        f"alone or on an unsolicited suggestion unattended.\n"
        f"</system-reminder>"
    )


# --------------------------------------------------------------------------- #
# Hook handlers
# --------------------------------------------------------------------------- #
class WayfinderHooks:
    def __init__(self, config: WayfinderConfig, coordinator: Any = None):
        self.config = config
        # Captured at mount; the mention_resolver capability is only reached
        # lazily on the session:start assembly path (it is registered AFTER
        # module mount, so it must never be touched at mount time).
        self._coordinator = coordinator
        self._catalogs: dict[str, SessionCatalog] = {}
        self._surfaced: set[str] = set()
        self._hinted: dict[str, set[str]] = {}
        self._hint_counts: dict[str, int] = {}
        self._source_cache: dict[str, Path] = {}
        # Compile the first-touch (F1) + menu (F3) classifier sets once at mount.
        self._orienting_re = _compile_patterns(list(config.orienting_patterns))
        self._greeting_re = _compile_patterns(list(config.greeting_patterns))
        self._task_re = _compile_patterns(list(config.task_patterns))
        self._menu_re = _compile_patterns(list(config.menu_patterns))

    # -- path / source resolution -------------------------------------------- #
    def _resolve_mention(self, value: str) -> Path | None:
        """Resolve an ``@ns:path`` value via the coordinator's mention_resolver.

        Lazy by contract: the capability is registered AFTER module mount, so
        this is only ever called on the session:start assembly path. A missing
        capability, a resolver error, or an unresolvable value (typo/uncached)
        → ``None`` + a warning; the caller skips that one source rather than
        wedging or fetching at runtime. Successful resolutions are cached.
        """
        cached = self._source_cache.get(value)
        if cached is not None:
            return cached
        resolver = None
        if self._coordinator is not None:
            resolver = self._coordinator.get_capability("mention_resolver")
        if resolver is None:
            logger.warning(
                "%s: mention_resolver capability unavailable; skipping source %r",
                _SOURCE,
                value,
            )
            return None
        try:
            resolved = resolver.resolve(value)
        except Exception:  # noqa: BLE001 — deliberate: skip this one source, never wedge
            logger.warning(
                "%s: mention_resolver failed on %r; skipping source", _SOURCE, value
            )
            return None
        if not resolved:
            logger.warning(
                "%s: could not resolve %r (typo/uncached?); skipping source",
                _SOURCE,
                value,
            )
            return None
        path = Path(resolved).expanduser()
        self._source_cache[value] = path
        return path

    def _resolve_source_value(self, value: str) -> Path | None:
        """Resolve one source value: ``@ns:path`` via the resolver, else a path.

        A literal (non-``@``) path always works with no resolver present.
        """
        value = value.strip()
        if not value:
            return None
        if value.startswith("@"):
            return self._resolve_mention(value)
        return Path(value).expanduser()

    def _resolve_own_dir(self) -> Path | None:
        """Source #0 — the implicit own-dir, unless ``content_dir`` overrides it."""
        if self.config.content_dir:
            path = self._resolve_source_value(self.config.content_dir)
            if path is None:
                return None  # @-mention path already warned
            if not path.is_dir():
                logger.warning(
                    "%s: content_dir %s is not a directory; own content unavailable",
                    _SOURCE,
                    path,
                )
                return None
            return path
        # Auto-detect: this file lives at
        #   <bundle>/modules/hooks-wayfinder/amplifier_module_hooks_wayfinder/__init__.py
        # parents: [0]=pkg [1]=hooks-wayfinder [2]=modules [3]=<bundle root>
        here = Path(__file__).resolve()
        try:
            candidate = here.parents[3] / "content"
        except IndexError:
            return None
        return candidate if candidate.is_dir() else None

    def _resolve_sources(self) -> list[tuple[str, Path]]:
        """Ordered ``(source_key, dir)`` list: own-dir first, then each pack.

        Own content is key ``"default"`` and always leads (unless it fails to
        resolve). Each configured ``content_sources`` pack follows in declared
        (dict) order. Any source that fails to resolve or is not a directory is
        skipped with a warning — never fatal.
        """
        sources: list[tuple[str, Path]] = []
        own = self._resolve_own_dir()
        if own is not None:
            sources.append(("default", own))
        for key, value in self.config.content_sources.items():
            path = self._resolve_source_value(value)
            if path is None:
                continue  # resolution failed; already warned
            if not path.is_dir():
                logger.warning(
                    "%s: content source %r (%s) is not a directory; skipping",
                    _SOURCE,
                    key,
                    path,
                )
                continue
            sources.append((key, path))
        return sources

    def _resolve_declines_path(self) -> Path:
        if self.config.declines_path:
            return Path(self.config.declines_path).expanduser()
        base = os.environ.get("AMPLIFIER_WAYFINDER_DIR") or "~/.amplifier/wayfinder"
        return Path(base).expanduser() / "declines.md"

    def _resolve_surfaced_path(self) -> Path:
        if self.config.surfaced_path:
            return Path(self.config.surfaced_path).expanduser()
        base = os.environ.get("AMPLIFIER_WAYFINDER_DIR") or "~/.amplifier/wayfinder"
        return Path(base).expanduser() / "surfaced.jsonl"

    def _record_surfacing(self, item_id: str) -> None:
        """Bump the seen-memory record for a just-surfaced promoted lead.

        Read-modify-rewrite (one line per id, bounded): re-read at write time so
        the increment reflects any concurrent session's write, bump ``count`` and
        stamp ``last_shown`` (UTC ISO). This is the hook's own deterministic
        bookkeeping — NOT a user decision — so writing it directly is correct.
        Any I/O failure is swallowed with a warning; a session is never wedged on
        a bookkeeping write, and a lost write simply re-surfaces the item later.
        """
        path = self._resolve_surfaced_path()
        try:
            seen = read_surfaced(path)
            prior = int((seen.get(item_id) or {}).get("count", 0))
            seen[item_id] = {
                "count": prior + 1,
                "last_shown": datetime.now(timezone.utc).isoformat(),
            }
            path.parent.mkdir(parents=True, exist_ok=True)
            body = "\n".join(
                json.dumps({"id": rid, **rec}, ensure_ascii=False)
                for rid, rec in seen.items()
            )
            tmp = path.parent / (path.name + ".tmp")
            tmp.write_text(body + "\n", encoding="utf-8")
            os.replace(tmp, path)  # atomic within the same dir; Windows-safe
        except OSError:
            logger.warning("%s: could not write surfaced-memory at %s", _SOURCE, path)

    # -- assembly ------------------------------------------------------------ #
    def _assemble(self, session_id: str) -> SessionCatalog:
        cached = self._catalogs.get(session_id)
        if cached is not None:
            return cached

        catalog = SessionCatalog()
        sources = self._resolve_sources()
        if not sources:
            logger.warning("%s: no content sources resolved; catalog is empty", _SOURCE)
            self._catalogs[session_id] = catalog
            return catalog

        try:
            catalog.items = load_catalog(sources, self.config.curate)
        except OSError:
            logger.warning("%s: failed scanning content sources", _SOURCE)
            catalog.items = {}

        catalog.declined_ids = read_declined_ids(
            self._resolve_declines_path(), set(catalog.items)
        )
        catalog.start_items = [
            it
            for it in catalog.items.values()
            if "session:start" in it.on_events and it.id not in catalog.declined_ids
        ]
        # Promoted-lead rotation: pool = promoted items minus declines (reusing
        # the same decline-filter). Pick the freshest-unseen lead from the
        # persistent seen-memory. Empty pool or rotation-off → promoted_lead stays
        # None and the index builder falls back to today's session:start bulletin.
        if self.config.promoted_rotation:
            pool = [
                it
                for it in catalog.items.values()
                if it.promoted and it.id not in catalog.declined_ids
            ]
            seen = read_surfaced(self._resolve_surfaced_path())
            catalog.promoted_lead = _select_promoted_lead(pool, seen)
        catalog.index_text = _build_index_block(catalog)
        self._catalogs[session_id] = catalog
        return catalog

    # -- events -------------------------------------------------------------- #
    async def on_session_start(self, _event: str, data: dict[str, Any]) -> HookResult:
        """Do the deterministic work at session start: assemble + decline-filter.

        Injects nothing here (delivery is ephemeral, on the first prompt).
        """
        if not self.config.enabled:
            return HookResult(action="continue")
        session_id = data.get("session_id") or "default"
        try:
            self._assemble(session_id)
        except Exception:  # never wedge a session on assembly failure
            logger.exception("%s: session:start assembly failed", _SOURCE)
        return HookResult(action="continue")

    async def on_prompt_submit(self, _event: str, data: dict[str, Any]) -> HookResult:
        if not self.config.enabled:
            return HookResult(action="continue")
        session_id = data.get("session_id") or "default"
        prompt = data.get("prompt") or ""

        try:
            catalog = self._assemble(session_id)  # lazy if session:start didn't run
        except Exception:
            logger.exception("%s: prompt:submit assembly failed", _SOURCE)
            return HookResult(action="continue")

        # F3 re-summonable menu — checked on EVERY turn (incl. the first) BEFORE
        # first-touch/signal routing, so "what else?" never dead-ends and never
        # gets swallowed by a per-item hint. It respects the decline-filter and
        # notes when this rotation's highlights are all seen. Marking the session
        # surfaced keeps the first-touch lead from also firing later.
        if self.config.menu_enabled and self._matches_menu(prompt):
            self._surfaced.add(session_id)
            menu = self._build_menu_block(catalog)
            if menu:
                return HookResult(
                    action="inject_context",
                    context_injection=menu,
                    context_injection_role="system",
                    ephemeral=True,
                )
            return HookResult(action="continue")

        # First prompt of the session. Turn-1 precedence:
        #   menu (F3, above) > per-item signal match > self-intro > F1.
        if session_id not in self._surfaced:
            # Per-item signal match (Defect B): a prompt_matches hit on the
            # opener is user-initiated relevance, so it must not be swallowed by
            # F1's task-QUIET bucket. Summons the packet directly and skips the
            # F1 lead. Self-intro items are excluded here (handled just below,
            # keeping their defer-the-lead behavior).
            signal_hit = self._first_prompt_signal(session_id, prompt, catalog)
            if signal_hit is not None:
                return signal_hit

            # Self-intro signal (identity-orienting query): if one fires, deliver
            # the directive self-intro nudge and DEFER the lead — we deliberately
            # do not mark the session surfaced, so the lead still lands on the
            # next prompt. This is unchanged.
            self_intro = self._match_self_intro(session_id, prompt, catalog)
            if self_intro is not None:
                self._record_hint(session_id, self_intro)
                return HookResult(
                    action="inject_context",
                    context_injection=_build_self_intro_block(self_intro),
                    context_injection_role="system",
                    ephemeral=True,
                )

            # F1 first-touch policy: classify the first prompt and surface
            # accordingly. first_touch=False forces "orienting" = today's
            # always-full-lead behavior.
            bucket = (
                self._classify_first_touch(prompt)
                if self.config.first_touch
                else "orienting"
            )
            # The session's first touch is now handled either way (task included,
            # so a working session is not re-prompted with a lead next turn).
            self._surfaced.add(session_id)

            # task-shaped → QUIET: inject nothing, record nothing (nothing shown).
            # Per-item prompt_matches direct-summon still works on later prompts.
            if bucket == "task":
                return HookResult(action="continue")

            # orienting → today's full lead (index + SURFACE NOW packet).
            if bucket == "orienting":
                if catalog.promoted_lead is not None:
                    self._record_surfacing(catalog.promoted_lead.id)
                if catalog.index_text:
                    return HookResult(
                        action="inject_context",
                        context_injection=catalog.index_text,
                        context_injection_role="system",
                        ephemeral=True,
                    )
                return HookResult(action="continue")

            # greeting / ambiguous → LIGHT: headline-only tease. It still counts
            # as shown, so record the rotation surfacing.
            light = self._build_light_lead_block(catalog)
            if light:
                if catalog.promoted_lead is not None:
                    self._record_surfacing(catalog.promoted_lead.id)
                return HookResult(
                    action="inject_context",
                    context_injection=light,
                    context_injection_role="system",
                    ephemeral=True,
                )
            return HookResult(action="continue")

        # Later prompts → one conservative signal nudge.
        if not self.config.signals_enabled:
            return HookResult(action="continue")
        return self._maybe_hint(session_id, prompt, catalog)

    # -- signal helpers ------------------------------------------------------ #
    def _is_self_intro(self, item: CatalogItem) -> bool:
        return item.id in self.config.self_intro_ids

    def _self_intro_items(self, catalog: SessionCatalog) -> list[CatalogItem]:
        return [it for it in catalog.items.values() if self._is_self_intro(it)]

    def _record_hint(self, session_id: str, item: CatalogItem) -> None:
        """Book a single nudge against the once-per-session + cap guardrails."""
        self._hinted.setdefault(session_id, set()).add(item.id)
        self._hint_counts[session_id] = self._hint_counts.get(session_id, 0) + 1

    def _match_self_intro(
        self, session_id: str, prompt: str, catalog: SessionCatalog
    ) -> CatalogItem | None:
        """Return the self-intro item whose signal matches this prompt, or None.

        Subject to the same conservative guardrails as any other signal:
        respects ``signals_enabled``, declines, the once-per-session hinted set,
        and the hint cap. Patterns are unchanged (already tuned), so this stays
        as quiet as the existing signals on unrelated prompts.
        """
        if not self.config.signals_enabled:
            return None
        if self._hint_counts.get(session_id, 0) >= self.config.max_hints_per_session:
            return None
        hinted = self._hinted.setdefault(session_id, set())
        for item in self._self_intro_items(catalog):
            if item.id in catalog.declined_ids or item.id in hinted:
                continue
            if not item.prompt_patterns:
                continue
            if any(p.search(prompt) for p in item.prompt_patterns):
                return item
        return None

    def _first_prompt_signal(
        self, session_id: str, prompt: str, catalog: SessionCatalog
    ) -> HookResult | None:
        """Turn-1 per-item signal match (non-self-intro items) — Defect B fix.

        A ``prompt_matches`` hit on the FIRST prompt is user-INITIATED relevance
        (the user opened asking about an offer's topic), so it must not be
        suppressed by F1's task-QUIET bucket. On a match: summon that packet
        directly (read it, answer FROM it) and mark the session's first touch
        handled, so the F1 lead is skipped entirely. Self-intro items are
        intentionally excluded here — the dedicated self-intro step handles them
        and keeps its defer-the-lead behavior. The mechanism mirrors
        ``_maybe_hint``: gated by ``signals_enabled``, decline-filtered, respects
        the once-per-session hinted set and the hint cap, records the hint, and
        records NOTHING to the rotation/surfaced seen-memory (same as a later
        ``_maybe_hint`` summon). Additionally gated by ``first_prompt_signals``.
        Returns None when disabled or when no non-self-intro item matches, so the
        caller falls through to the self-intro check and F1 classification.
        """
        if not (self.config.signals_enabled and self.config.first_prompt_signals):
            return None
        if self._hint_counts.get(session_id, 0) >= self.config.max_hints_per_session:
            return None
        hinted = self._hinted.setdefault(session_id, set())
        for item in catalog.items.values():
            if self._is_self_intro(item):
                continue
            if item.id in catalog.declined_ids or item.id in hinted:
                continue
            if not item.prompt_patterns:
                continue
            if any(p.search(prompt) for p in item.prompt_patterns):
                self._record_hint(session_id, item)
                # First touch handled → later turns take the normal signal path;
                # the F1 lead is skipped entirely (never deferred to turn 2).
                self._surfaced.add(session_id)
                return HookResult(
                    action="inject_context",
                    context_injection=_build_signal_summon_block(item),
                    context_injection_role="system",
                    ephemeral=True,
                )
        return None

    def _maybe_hint(
        self, session_id: str, prompt: str, catalog: SessionCatalog
    ) -> HookResult:
        if self._hint_counts.get(session_id, 0) >= self.config.max_hints_per_session:
            return HookResult(action="continue")
        hinted = self._hinted.setdefault(session_id, set())
        # Self-intro items win the turn (an orienting query is the highest-value
        # response), then the remaining offers in catalog order.
        ordered = self._self_intro_items(catalog) + [
            it for it in catalog.items.values() if not self._is_self_intro(it)
        ]
        for item in ordered:
            if item.id in catalog.declined_ids or item.id in hinted:
                continue
            if not item.prompt_patterns:
                continue
            if any(p.search(prompt) for p in item.prompt_patterns):
                self._record_hint(session_id, item)
                block = (
                    _build_self_intro_block(item)
                    if self._is_self_intro(item)
                    else _build_hint_block(item)
                )
                return HookResult(
                    action="inject_context",
                    context_injection=block,
                    context_injection_role="system",
                    ephemeral=True,
                )
        return HookResult(action="continue")

    # -- F1 first-touch classification / F3 menu re-summon ------------------- #
    def _classify_first_touch(self, prompt: str) -> str:
        """Bucket the FIRST prompt: orienting | greeting | task | ambiguous.

        Precedence is deliberate. Orienting is checked first (SPECIFIC
        system-orientation phrasings). Greeting is WHOLE-message anchored, so a
        greeting that also carries work ("hi, help me build X") does NOT match
        here and falls through to task. Task catches work signals (imperatives,
        "I need", errors, a trailing ?). Anything left is ambiguous.
        """
        text = prompt or ""
        if any(p.search(text) for p in self._orienting_re):
            return "orienting"
        if any(p.search(text) for p in self._greeting_re):
            return "greeting"
        if any(p.search(text) for p in self._task_re):
            return "task"
        return "ambiguous"

    def _matches_menu(self, prompt: str) -> bool:
        """True when the prompt is a menu re-summon ("what else / the menu")."""
        text = prompt or ""
        return any(p.search(text) for p in self._menu_re)

    def _lead_for_light(self, catalog: SessionCatalog) -> CatalogItem | None:
        """The one item a light greeting should tease: the rotation lead, else
        the freshest live session:start bulletin."""
        if catalog.promoted_lead is not None:
            return catalog.promoted_lead
        starts = [it for it in catalog.start_items if it.id not in catalog.declined_ids]
        return starts[0] if starts else None

    def _build_light_lead_block(self, catalog: SessionCatalog) -> str:
        """F1 light path: ONE headline line + an invitation to open it on ack.

        Never pastes the packet body or its commands (that is the heavy path).
        Returns "" when there is nothing live to tease.
        """
        lead = self._lead_for_light(catalog)
        if lead is None:
            return ""
        return (
            f'<system-reminder source="{_SOURCE}">\n'
            f"The user opened with a light greeting (no task, no question). "
            f"Reply warmly and briefly in wayfinder's voice, then surface ONE "
            f"line only \u2014 this session's highlight headline \u2014 and invite them "
            f"to open it:\n"
            f"  {lead.id} \u2014 {lead.headline}\n"
            f"Add a light \u201csay the word and I\u2019ll show you the rest \u2014 there\u2019s a "
            f"full menu whenever you want it.\u201d Do NOT paste the packet body or "
            f"its commands now; open it (run its `body:` action) only on an "
            f"explicit ack. If they just want to get to work, drop it.\n"
            f"</system-reminder>"
        )

    def _build_menu_block(self, catalog: SessionCatalog) -> str:
        """F3: the FULL current offer menu (declines filtered), any turn.

        Headline + `body:` action per live item, in wayfinder's voice. Notes
        honestly when this rotation's highlights have all been seen so "what
        else?" never dead-ends. Returns "" only when the catalog is truly empty.
        """
        live = [
            it for it in catalog.items.values() if it.id not in catalog.declined_ids
        ]
        if not live:
            if not catalog.items:
                return ""  # nothing exists at all — stay silent
            return (
                f'<system-reminder source="{_SOURCE}">\n'
                f"The user asked what else is available, but every wayfinder "
                f"offer is dismissed for now. Tell them plainly there\u2019s nothing "
                f"on the menu right now, in wayfinder's voice \u2014 don\u2019t invent "
                f"offers.\n"
                f"</system-reminder>"
            )
        lines = [
            f'<system-reminder source="{_SOURCE}">',
            (
                "The user asked what else is available \u2014 surface the FULL "
                "current wayfinder menu (declined offers already filtered out), "
                "in wayfinder's voice, as a compact list. Showing the list IS "
                "the answer, so no propose\u2192ack gate applies. Do not open or act "
                "on a merely listed item; that would be an optional offer needing "
                "an explicit ack. If the user directly asks to open or use an item, "
                "fulfill that in-scope request without a duplicate Wayfinder ack."
            ),
            (
                "To open any packet, run its `body:` action EXACTLY as written "
                "(including its @namespace prefix); never glob/grep/search for "
                "the file. This menu is authoritative about what EXISTS."
            ),
            "",
            "Offers on the menu:",
        ]
        for it in live:
            cat = f" [{it.category}]" if it.category else ""
            lines.append(f"- {it.id}{cat}: {it.headline}")
            if it.action:
                lines.append(f"    body: {it.action}")
        # Honest "you've seen it all" note: only when EVERY promoted highlight
        # has already been surfaced this rotation (the "what else is new?"
        # dead-end the console review hit).
        promoted = [it for it in live if it.promoted]
        if promoted:
            seen = read_surfaced(self._resolve_surfaced_path())
            if all(int((seen.get(it.id) or {}).get("count", 0)) > 0 for it in promoted):
                lines.append("")
                lines.append(
                    "Note: they\u2019ve already seen all of this rotation\u2019s "
                    "highlights \u2014 say so honestly (nothing brand-new to feature), "
                    "but the full menu above is still open to them."
                )
        lines.append("</system-reminder>")
        return "\n".join(lines)


# --------------------------------------------------------------------------- #
# Mount
# --------------------------------------------------------------------------- #
async def mount(
    coordinator: Any, config: dict[str, Any] | None = None
) -> dict[str, Any]:
    """Mount the wayfinder hook.

    Registers ``session:start`` (assemble + decline-filter) and ``prompt:submit``
    (ephemeral delivery + conservative signal). See the module docstring for the
    session:start-vs-prompt:submit delivery rationale.
    """
    wf_config = WayfinderConfig.from_dict(config)
    hooks = WayfinderHooks(wf_config, coordinator=coordinator)

    coordinator.hooks.register(
        "session:start", hooks.on_session_start, priority=10, name=_SOURCE
    )
    coordinator.hooks.register(
        "prompt:submit", hooks.on_prompt_submit, priority=20, name=_SOURCE
    )

    return {
        "name": _SOURCE,
        "version": "0.1.0",
        "description": "Wayfinder Ring 1 hook: derived catalog, decline-filter, signal nudge.",
        "config": {
            "enabled": wf_config.enabled,
            "content_dir": wf_config.content_dir or "<auto>",
            "content_sources": dict(wf_config.content_sources),
            "declines_path": wf_config.declines_path or "<env/HOME default>",
            "surfaced_path": wf_config.surfaced_path or "<env/HOME default>",
            "promoted_rotation": wf_config.promoted_rotation,
            "signals_enabled": wf_config.signals_enabled,
            "curate": wf_config.curate,
            "max_hints_per_session": wf_config.max_hints_per_session,
            "self_intro_ids": list(wf_config.self_intro_ids),
            "first_touch": wf_config.first_touch,
            "first_prompt_signals": wf_config.first_prompt_signals,
            "orienting_patterns": list(wf_config.orienting_patterns),
            "greeting_patterns": list(wf_config.greeting_patterns),
            "task_patterns": list(wf_config.task_patterns),
            "menu_enabled": wf_config.menu_enabled,
            "menu_patterns": list(wf_config.menu_patterns),
        },
    }
