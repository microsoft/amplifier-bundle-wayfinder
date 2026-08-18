"""hooks-wayfinder — Wayfinder's Ring 1 hook (its first Python).

Three deterministic, config-tunable, ephemeral jobs:

1. ``session:start`` — resolve the content dir, scan per-item frontmatter, and
   assemble the DERIVED offer catalog (replacing the hand-maintained
   ``offer-catalog.md``). Read the decline file and filter it here — decline
   *enforcement* is deterministic. This handler does the deterministic WORK and
   caches the result; it injects nothing (so nothing persistent is ever added).

2. ``prompt:submit`` (first prompt of the session) — deliver the catalog index +
   the current bulletin, in packet shape, as an EPHEMERAL injection.

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

import logging
import os
import re
from dataclasses import dataclass, field
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
    content_dir: str | None = None  # default: auto-detect <bundle>/content
    declines_path: str | None = None  # default: env/HOME wayfinder dir
    signals_enabled: bool = True
    curate: bool = False  # False = derive-first (all items); True = only curated: true
    max_hints_per_session: int = 3

    @classmethod
    def from_dict(cls, raw: dict[str, Any] | None) -> WayfinderConfig:
        raw = raw or {}
        return cls(
            enabled=bool(raw.get("enabled", True)),
            content_dir=raw.get("content_dir") or None,
            declines_path=raw.get("declines_path") or None,
            signals_enabled=bool(raw.get("signals_enabled", True)),
            curate=bool(raw.get("curate", False)),
            max_hints_per_session=int(raw.get("max_hints_per_session", 3)),
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
    source_path: str = ""


@dataclass
class SessionCatalog:
    items: dict[str, CatalogItem] = field(default_factory=dict)
    declined_ids: set[str] = field(default_factory=set)
    index_text: str = ""
    start_items: list[CatalogItem] = field(default_factory=list)


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


def _item_from_meta(meta: dict[str, Any], source_path: str) -> CatalogItem | None:
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
        source_path=source_path,
    )


def load_catalog(content_dir: Path, curate: bool) -> dict[str, CatalogItem]:
    """Scan ``content_dir`` recursively and derive the catalog from frontmatter.

    First-id-wins on collision (matches the design's source precedence). When
    ``curate`` is true, only items carrying ``curated: true`` are included.
    """
    items: dict[str, CatalogItem] = {}
    for md_path in sorted(content_dir.rglob("*.md")):
        try:
            text = md_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            logger.warning("%s: could not read %s; skipping", _SOURCE, md_path)
            continue
        meta, _ = parse_frontmatter(text)
        item = _item_from_meta(meta, str(md_path))
        if item is None:
            continue
        if curate and not item.curated:
            continue
        if item.id in items:
            logger.warning("%s: duplicate offer id %r; keeping first", _SOURCE, item.id)
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

    start = [it for it in catalog.start_items if it.id not in catalog.declined_ids]
    if start:
        lines.append("")
        lines.append(
            "SURFACE NOW — current bulletin (once, commands-first, lead with a "
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


# --------------------------------------------------------------------------- #
# Hook handlers
# --------------------------------------------------------------------------- #
class WayfinderHooks:
    def __init__(self, config: WayfinderConfig):
        self.config = config
        self._catalogs: dict[str, SessionCatalog] = {}
        self._surfaced: set[str] = set()
        self._hinted: dict[str, set[str]] = {}
        self._hint_counts: dict[str, int] = {}

    # -- path resolution ----------------------------------------------------- #
    def _resolve_content_dir(self) -> Path | None:
        if self.config.content_dir:
            p = Path(self.config.content_dir).expanduser()
            return p if p.is_dir() else None
        # Auto-detect: this file lives at
        #   <bundle>/modules/hooks-wayfinder/amplifier_module_hooks_wayfinder/__init__.py
        # parents: [0]=pkg [1]=hooks-wayfinder [2]=modules [3]=<bundle root>
        here = Path(__file__).resolve()
        try:
            candidate = here.parents[3] / "content"
        except IndexError:
            return None
        return candidate if candidate.is_dir() else None

    def _resolve_declines_path(self) -> Path:
        if self.config.declines_path:
            return Path(self.config.declines_path).expanduser()
        base = os.environ.get("AMPLIFIER_WAYFINDER_DIR") or "~/.amplifier/wayfinder"
        return Path(base).expanduser() / "declines.md"

    # -- assembly ------------------------------------------------------------ #
    def _assemble(self, session_id: str) -> SessionCatalog:
        cached = self._catalogs.get(session_id)
        if cached is not None:
            return cached

        catalog = SessionCatalog()
        content_dir = self._resolve_content_dir()
        if content_dir is None:
            logger.warning("%s: no content dir resolved; catalog is empty", _SOURCE)
            self._catalogs[session_id] = catalog
            return catalog

        try:
            catalog.items = load_catalog(content_dir, self.config.curate)
        except OSError:
            logger.warning("%s: failed scanning %s", _SOURCE, content_dir)
            catalog.items = {}

        catalog.declined_ids = read_declined_ids(
            self._resolve_declines_path(), set(catalog.items)
        )
        catalog.start_items = [
            it
            for it in catalog.items.values()
            if "session:start" in it.on_events and it.id not in catalog.declined_ids
        ]
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

        # First prompt of the session → deliver the index + current bulletin.
        if session_id not in self._surfaced:
            self._surfaced.add(session_id)
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

    def _maybe_hint(
        self, session_id: str, prompt: str, catalog: SessionCatalog
    ) -> HookResult:
        if self._hint_counts.get(session_id, 0) >= self.config.max_hints_per_session:
            return HookResult(action="continue")
        hinted = self._hinted.setdefault(session_id, set())
        for item in catalog.items.values():
            if item.id in catalog.declined_ids or item.id in hinted:
                continue
            if not item.prompt_patterns:
                continue
            if any(p.search(prompt) for p in item.prompt_patterns):
                hinted.add(item.id)
                self._hint_counts[session_id] = self._hint_counts.get(session_id, 0) + 1
                return HookResult(
                    action="inject_context",
                    context_injection=_build_hint_block(item),
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
    hooks = WayfinderHooks(wf_config)

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
            "declines_path": wf_config.declines_path or "<env/HOME default>",
            "signals_enabled": wf_config.signals_enabled,
            "curate": wf_config.curate,
            "max_hints_per_session": wf_config.max_hints_per_session,
        },
    }
