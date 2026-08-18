# Ring 1 — build + DTU verification record (2026-08-18)

Autonomous build-and-verify run against goal
`.amplifier/goals/wayfinder-ring1-dtu-passable.md`. All seven checks reached a
terminal state; the goal is met.

## What was built (Ring 1 spine)

- **B1 — per-item frontmatter** on `content/bulletins/current.md`,
  `content/concepts/ten-lane-highway.md`, and new `content/practices/goal-batch.md`
  + `goalify.md` (`id`, `category`, `headline`, `try_now`, `trigger`, `signals`,
  `action`).
- **B2 — derived catalog (hybrid).** `hooks-wayfinder` assembles the offer index
  from frontmatter and injects it ephemerally; `context/offer-catalog.md` reduced
  to a thin "catalog is derived" note. `curate` knob (derive-first default).
- **B3 — `modules/hooks-wayfinder`** (wayfinder's first Python): `session:start`
  deterministic decline-FILTER (read-only; the decline *write* stays
  agent-mediated) + assembles the derived index + ephemeral packet-shaped
  surfacing on first `prompt:submit` + one conservative `prompt_matches` signal
  per item. Config knobs: `enabled`, `content_dir`, `declines_path`,
  `signals_enabled`, `curate`, `max_hints_per_session`.

## Check results

| Check | Verdict | Evidence |
|---|---|---|
| **Q1 VALIDATES** | PASS | `validate-bundle-repo` v3.6.1 → PASS WITH WARNINGS, **0 confirmed errors** (the lone `context_tokens_excessive` reclassified to WARNING: per-file rubric, largest file 547 tok, aggregate ~1,161). |
| **Q2 LOADS** | PASS | After a first-round FAIL (module source path) was fixed (036a0e9), DTU session starts clean; `hooks-wayfinder` activates; its `session:start` system-reminder appears in `events.jsonl`. |
| **Q3 PACKET SHAPE** | PASS | `"what's new?"` → in-voice, commands-first (`1. /provider  2. /provider use haiku  3. /provider auto`), single closing ask. Not a prose wall. |
| **Q4 STEERING** | PASS | 3-parallel-refactors prompt → proposes goal-batch, shows exact `load_skill("goal-batch")`, stops at "Want me to load it?" — skill NOT executed (nothing unattended). |
| **Q5 DECLINE-MEMORY** | PASS | Baseline: pinning surfaces. After `pinning` appended to declines.md, a NEW session no longer surfaces it — "no" persists across sessions. |
| **Q6 HOOK FIRES / filter** | PASS | Same before(present)/after(absent) contrast + injected "declined offers already filtered out" reminder = hook fired at session:start and deterministically suppressed the declined id. |
| **Q7 NO HARD DEFECTS** | PASS | `amplifier-tester:validator` full behavioral pass returned **0 defects** after the Q2 fix. (Browser-based simulated-user-research is **N/A** — wrong tool class for a headless CLI bundle.) |

**One real defect was found by the DTU run and fixed** — the exact class local
validation cannot catch: `source: ./modules/hooks-wayfinder` resolved to
`behaviors/modules/…` under the `#subdirectory=behaviors/wayfinder.yaml` install
(behaviors/ is the base dir). Fixed to `../modules/hooks-wayfinder` (036a0e9);
re-verified green.

## Residuals / for-human workshopping (non-gating)

- **Voice/content still wants Brian's workshopping** — offers miss the point of
  some; human-led, deliberately not gated here.
- **W1 dual-authority (validator):** `context/propose-and-ack.md` prose still
  describes decline-memory that the hook now enforces deterministically —
  reconcile so prose defers to the hook.
- **`context/wayfinder-voice.md` ~547 tok** sits in the WARNING band; trim if
  desired.
- **`curate: true` currently yields an empty catalog** (derive-first default; no
  item marked `curated` yet) — intended; revisit when curation lands.
- **Fast-follows (not built, by scope):** multi-source content resolver,
  `wayfinder-dig-deeper` skill, `wayfinder-mine-practice` recipe, deterministic
  decline *capture* (write stays agent-mediated by decision).
