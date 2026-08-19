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

2. ``prompt:submit`` (first prompt of the session) — deliver the catalog index +
   the rotation lead, in packet shape, as an EPHEMERAL injection, and record the
   surfacing in the seen-memory (the hook's own deterministic bookkeeping). Zero
   promoted items (or ``promoted_rotation: false``) falls back to surfacing the
   single ``on_event: session:start`` bulletin, as before.

3. ``prompt:submit`` (later prompts) — one conservative ``prompt_matches`` signal
   per offer, rate-limited and declines-filtered. A single nudge only — the hook
   can never act.

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

The WRITE of a new decline stays agent-mediated (the propose→ack protocol). This
hook never writes the decline file.
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
            "frontmatter; declined offers already filtered out). Surface anything "
            "below ONLY via propose→show→ack→act, one at a time, in wayfinder's voice."
        ),
        "",
        "Offers on the menu:",
    ]
    for it in live:
        cat = f" [{it.category}]" if it.category else ""
        lines.append(f"- {it.id}{cat}: {it.headline}")

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
        f"If it genuinely fits, PROPOSE it via propose→show→ack→act — show the "
        f"exact command{cmd}, then wait for an explicit ack. This is a single "
        f"nudge: do not repeat it, and never act unattended. If it doesn't fit, "
        f"ignore this.\n"
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
        f"the bulletin can wait. The offers named in the overview stay ack-gated: "
        f"surface, don't run anything unattended.\n"
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

        # First prompt of the session → normally deliver the index + current
        # bulletin. But if the very first prompt is an ORIENTING query, the
        # bulletin and the self-intro concept would compete for salience on the
        # same turn (the observed bug). So: check for a self-intro signal FIRST;
        # if one fires, deliver the directive self-intro nudge and DEFER the
        # bulletin — we deliberately do not mark the session surfaced, so the
        # bulletin still lands on the next prompt.
        if session_id not in self._surfaced:
            self_intro = self._match_self_intro(session_id, prompt, catalog)
            if self_intro is not None:
                self._record_hint(session_id, self_intro)
                return HookResult(
                    action="inject_context",
                    context_injection=_build_self_intro_block(self_intro),
                    context_injection_role="system",
                    ephemeral=True,
                )
            self._surfaced.add(session_id)
            # Record the surfacing ONLY now that the lead actually lands (the
            # self-intro defer path returns above without reaching here, so a
            # deferred lead is never recorded). Rotation-only bookkeeping.
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
        },
    }
