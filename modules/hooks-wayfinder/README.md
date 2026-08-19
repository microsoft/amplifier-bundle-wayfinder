# hooks-wayfinder

Wayfinder's Ring 1 hook — its first Python. Three deterministic jobs, all
config-tunable, all ephemeral (nothing is ever written to the permanent message
history):

1. **session:start** — resolve the content dir, scan per-item frontmatter, and
   assemble the *derived* offer catalog (killing the hand-maintained
   `offer-catalog.md`). Reads the decline file and filters it here — the
   decline *enforcement* is deterministic.
2. **prompt:submit (first prompt)** — deliver the catalog index + the current
   bulletin, in packet shape, as an **ephemeral** injection. (Delivery rides
   `prompt:submit` because that is the confirmed ephemeral-injection path in
   `loop-streaming`; see `__init__.py` for the note.)
3. **prompt:submit (later prompts)** — one conservative `prompt_matches` signal
   per offer, rate-limited, declines-filtered. A nudge only — it can never act.

The **write** of a new decline stays agent-mediated (propose→ack protocol). This
hook never writes the decline file.

See `docs/RING1-DESIGN.md` in the bundle for the full design.

## Config knobs (set under the hook's `config:` in `behaviors/wayfinder.yaml`)

| Key | Default | Meaning |
|-----|---------|---------|
| `enabled` | `true` | Master switch for the whole hook. |
| `content_dir` | auto-detect | **Own-dir override.** Default: the implicit `<bundle>/content` (auto-detected from the module's own location), which is source #0 and **always loads first**. Set this to OVERRIDE that own-dir. `@`-aware: accepts an `@ns:path` (resolved via the coordinator's `mention_resolver` capability) or a literal filesystem path. |
| `content_sources` | `{}` | **Additive, keyed map** of EXTRA content packs, e.g. `{ my-pack: "@other-bundle:content" }`. Each value is an `@ns:path` (bundle-namespaced, resolved lazily at `session:start` via the `mention_resolver` capability) or a literal filesystem path. A **map** (not a list) so hook config deep-merges packs additively by key across composition — two bundles can each add a pack. Consumers ADD packs here; they never restate the always-first own-dir. Load order: own-dir (source key `default`) first, then these in declared order; **first-id-wins** on collision (own/public content wins; a shadowed id is logged). A source that fails to resolve (missing resolver, typo/uncached mention, or non-directory) is skipped with a warning — never fatal, never fetched at runtime. |
| `declines_path` | `${AMPLIFIER_WAYFINDER_DIR:-~/.amplifier/wayfinder}/declines.md` | Decline-memory file the filter reads. |
| `signals_enabled` | `true` | On/off for the `prompt_matches` signal layer. |
| `curate` | `false` | Derive-vs-curate line. `false` = derive-first (all items). `true` = only items with `curated: true` frontmatter. |
| `max_hints_per_session` | `3` | Per-session cap on signal nudges (on top of one-per-offer-per-session). |
