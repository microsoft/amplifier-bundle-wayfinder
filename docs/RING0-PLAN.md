# wayfinder — Ring 0 Build Plan

**Status:** design, pre-implementation. No YAML written yet. Review this in ~10 min, then we build.
**Decisions this is built on:** `ai-notes/reviews/INDEX.md` § Decision log (2026-08-18). Those 5 decisions + the name are FIXED constraints here, not options.

## What Ring 0 is

The thinnest end-to-end thing Brian can install into his daily sessions and actually kick the tires on. Two things must work for real:

1. **One authored announcement** (the **pinning** feature) surfaces at the right moment, in one curated voice.
2. **One propose-and-ack offer** (e.g. proposing **goal-batch** when Brian is about to do parallelizable work), where "sure" is the consent and the agent then does only what it can already do today.

Everything else waits for a later ring. Ruthless simplicity: **content + guidance over new modules.** Ring 0 ships with **zero new Python** — it's a bundle of authored markdown + behavioral instructions wired onto foundation's existing tools.

---

## 1. Mechanism map

wayfinder is really **one owned mechanism** — a curated set of authored "packets," each with a *trigger*, an authored *headline/body*, and an optional *proposed action*. Informational packets (pinning) carry no action; steering packets (goal-batch) carry an action the user acks. This single channel is the consolidation of the three corpus channels (announcements bundle + in-session JIT offers + app-CLI bundle) that Decision 2 mandated.

| Capability (from the decisions) | Concrete Amplifier mechanism | Exists today? | Ring 0 choice & why |
|---|---|---|---|
| **Authored bulletin content** (curated, one voice, not a changelog) | Curated markdown Brian edits in the bundle (`content/bulletins/current.md`) | ✅ content files | Hand-authored md. The authored voice (Decision 5) is a human writing prose, never a generated feed. |
| **Get the bulletin into a session** | `context.include` in the wayfinder behavior → lands in the system prompt; agent surfaces it per guidance | ✅ | Always-on but tiny. Guaranteed present; Brian edits the file and the next session picks it up. |
| **Fire "at the right moment"** | Ring 0: **bundle guidance** (instruction: "lead with the current bulletin once per session if not declined"). Later: a `session:start` / `tool:pre` hook for deterministic firing + intent detection. | ⚠️ hook mechanism exists but must be authored in Python | Conventional (prose) for Ring 0 — acceptable because Brian is the only user and can feel when it misfires. **Flag:** deterministic firing is the #1 Ring-1 upgrade. |
| **Propose-and-ack protocol** (propose → show → ack → act) | Bundle instructions/content (`context/propose-and-ack.md`) — a standing behavior, always on | ✅ | Content, not a skill: wayfinder must *proactively* offer every session, so it can't wait to be loaded on demand. |
| **Execute on "sure"** | Existing foundation tools — `load_skill`, `delegate`, `bash`, `mode`, `recipes` | ✅ | Reuse. Decision 2: on ack the agent does **only what it can already do today**. No new capability. |
| **Guardrail: show the exact command before ack** | Rule in `propose-and-ack.md` | ✅ | The one corpus pattern that already worked (voice-relay). Structural later; prose now. |
| **Guardrail: decline-memory across sessions** | A per-user file `~/.amplifier/wayfinder/declines.md`; agent reads it at start, appends on "no", never re-offers listed items — via existing `read_file`/`edit_file` + guidance | ❌ no native "remembered no" | **Ring-0 workaround = a plain file.** Lives in `~/.amplifier/` (per-user, survives this ephemeral workspace), not in the repo. A hook enforces it deterministically later. |
| **Guardrail: nothing unattended** | Instruction: every write/execute requires a human ack | ✅ | Pure guidance; nothing in Ring 0 can run unattended anyway. |
| **Offer catalog** (trigger → offer → action → what it runs) | Curated markdown index (`context/offer-catalog.md`), always-on, small | ✅ | This is where Brian encodes "when you see X, offer Y." Grows as he uses it. |
| **Point to goal-batch (not absorb it)** | Pointer: offer it **by name**, `load_skill("goal-batch")` on ack | ✅ skill already exists | wayfinder owns the *communication*; goal-batch stays goal-batch. Zero copying. |
| **Point to ten-lane-highway concept** | Short concept note in wayfinder (`content/concepts/ten-lane-highway.md`), **soft-referenced** (read on demand, NOT always-on) | ⚠️ a concept, not a formal skill | Carry the *context* for the concept (Decision 2) as a thin note; goal-batch already references it. |
| **First test payload: pinning announcement** | One informational packet in `current.md` | ✅ | The Ring-0 proof of the show-me layer. **Needs the real feature details** (open question #3). |

**The one genuine gap:** there is no turnkey mechanism for *deterministic* "fire at session start / on intent" + *enforced* decline-memory. Ring 0 covers both with guidance + a flat file. The clean version is a small `hooks-wayfinder` module in Ring 1 (`session:start` injects the bulletin; `tool:pre` detects parallelizable-work intent; reads/writes the decline file). We deliberately don't build it yet.

**Context economics:** keep always-on content tiny — voice + protocol + guardrails + offer-catalog index + current bulletin ≈ **~1.5–2K tokens/turn**. Concept docs and bulletin archive stay **out** of always-on (soft refs / on-demand). This is a bundle whose entire job is this surface, so that floor is justified.

**Shape:** wayfinder is a **bundle Brian runs** (or composes as a behavior into his default), not a mode. A mode would need re-activating every session (friction, low adoption); wayfinder must be simply *present* in his daily work. That "compose as a behavior" property is also the Ring-1/2 distribution path.

---

## 2. Bundle skeleton

Thin standalone bundle + one behavior (the foundation-recommended pattern). One line per file.

```
wayfinder/
├── bundle.md                          # THIN standalone: includes foundation + wayfinder behavior. Body = authored-voice system prompt.
├── behaviors/
│   └── wayfinder.yaml                 # Wires the behavior: context.include of the four always-on files below. No new tools/hooks in Ring 0.
├── context/
│   ├── wayfinder-voice.md             # The authored-voice principle + how wayfinder talks (curated, opinionated, one voice). Always-on. ~40 ln.
│   ├── propose-and-ack.md             # The propose→show→ack→act protocol + the 3 guardrails + the decline-memory procedure. Always-on. ~60 ln.
│   └── offer-catalog.md               # Curated index: trigger → offer → proposed action → exact command. Always-on, small. Seeded w/ pinning + goal-batch.
├── content/
│   ├── bulletins/
│   │   └── current.md                 # THE authored bulletin surfaced at session start. First payload: the pinning feature. Brian edits this.
│   │   └── archive/                   # (Ring 1+) superseded/deprecated bulletins — multi-year history. Empty in Ring 0.
│   └── concepts/
│       └── ten-lane-highway.md        # Concept note, SOFT-referenced (read on demand, not always-on). Thin; points back to goal-batch.
├── docs/
│   └── RING0-PLAN.md                  # This file.
└── README.md                          # What wayfinder is, the ring model, how to install.
```

Runtime state (NOT in the repo — per-user, survives the ephemeral workspace):

```
~/.amplifier/wayfinder/
└── declines.md                        # Append-only "no" log. Agent reads at start, never re-offers what's listed.
```

`bundle.md` (thin) is essentially:

```yaml
includes:
  - bundle: git+https://github.com/microsoft/amplifier-foundation@main
  - bundle: wayfinder:behaviors/wayfinder
```

…with a short authored-voice system-prompt body. Everything wayfinder *does* comes from the behavior's `context.include`; everything it *can do* comes from foundation (filesystem, bash, delegate, load_skill).

---

## 3. Ring 0 build steps (smallest end-to-end slice first)

Plumbing before polish. Each step ends at a checkable gate.

1. **Scaffold + prove it loads.** Create `wayfinder/bundle.md` (thin standalone) + `behaviors/wayfinder.yaml` (empty `context.include` to start). **Gate:** a session starts with wayfinder composed onto foundation, no load errors.
   ```bash
   amplifier run --bundle /home/bkrabach/dev/tour-guide/wayfinder/bundle.md "hello — what are you?"
   ```
2. **Author the standing behavior.** Write `context/wayfinder-voice.md` (the one-voice principle) and `context/propose-and-ack.md` (propose→show→ack→act + the 3 guardrails + decline-memory procedure). Wire both via `context.include`. **Gate:** in a fresh session, wayfinder describes its own job in-voice and states the ack/guardrail rules when asked.
3. **First real announcement (the show-me proof).** Write `content/bulletins/current.md` — the **pinning** feature, in the authored voice (what it is, why it matters, one thing to try). Wire it via `context.include`; add the instruction "lead with the current bulletin once per session unless it's in declines." **Gate:** Brian starts a session and the pinning announcement surfaces up front, in-voice, not as a changelog dump.
4. **First propose-and-ack offer (the steering proof).** Seed `context/offer-catalog.md` with one entry — *trigger:* user faces 2+ independent parallelizable tasks → *offer:* goal-batch → *action:* `load_skill("goal-batch")` after showing what it will do. Add the thin `content/concepts/ten-lane-highway.md` note as a soft reference. **Gate:** Brian describes parallelizable work; wayfinder proposes goal-batch, **shows what it will run**, waits for "sure," then loads the skill on ack — and does nothing on silence.
5. **Decline-memory.** Establish `~/.amplifier/wayfinder/declines.md`; instruct the agent to read it at session start and append the offer id on a "no." **Gate:** Brian says "no" to the goal-batch offer; a *new* session does not re-offer it.
6. **Daily-drive it.** Brian runs wayfinder for real for a few days, editing `current.md` / `offer-catalog.md` as friction shows up. Optionally, to have it always-on in every session, compose the behavior into his default bundle instead of `--bundle`:
   ```yaml
   includes:
     - bundle: wayfinder:behaviors/wayfinder   # add to your default bundle's includes
   ```

**Definition of done for Ring 0:** steps 1–5 gates pass, and Brian has driven it in real sessions (step 6) long enough to have edited the content at least once.

---

## 4. Out of scope for Ring 0 (explicit)

- **No new autonomy / nothing unattended.** On-ack execution only; every action needs a human "sure." (Decision 2/3.)
- **No hook module.** Firing "at the right moment" and decline-memory are *guidance + a flat file* in Ring 0. The `hooks-wayfinder` module (deterministic session:start injection, intent detection, enforced decline-memory) is a Ring-1 candidate, not now.
- **No team distribution / public bundle.** Ring 2 only. (Decision 4.)
- **No telemetry infrastructure** beyond what Context Intelligence already captures passively. No attention-hours ledger, no per-offer instrumentation build. Observation happens via CI in Ring 1.
- **No personalization engine.** The bulletin is hand-authored, not generated per-user/project.
- **No archive/deprecation machinery.** Just `current.md`; `archive/` stays empty until Ring 1.
- **Not absorbing the pointed-to things.** goal-batch stays a skill loaded by name; ten-lane-highway stays a thin concept note. wayfinder owns *communication*, not the capabilities.
- **Deferred corpus proposals:** app-CLI injection, routine-mining, self-improving-bundle PRs, graduated-friction team protocols, auto-processed shareouts, default attribution. Noted, not built.
- **Mode-switch offers:** only if the modes bundle is already present; otherwise Ring 0 offers stay to skills / commands / concepts (see open question #5).

---

## 5. Open questions for Brian (blockers only)

1. **Install shape for daily driving.** Run wayfinder as its own bundle via `--bundle` (isolated, easy to toggle), **or** compose the wayfinder *behavior* into your default bundle so it's always-on in every session? This changes whether Ring 0 emphasizes a standalone bundle or a drop-in behavior. (Both are cheap; I need to know which is the primary path.)
2. **Pinning feature source.** The authored bulletin must be *accurate*, not invented. Where's the canonical description of the pinning feature (doc, PR, transcript) I should base the first `current.md` on?
3. **ten-lane-highway source.** Is there a canonical write-up of the concept, or should I draft the concept note from the corpus references (it rides alongside goal-batch) for you to edit?
4. **First offer set.** Is goal-batch the single propose-and-ack exemplar you want for Ring 0, or should I seed 2–3 (e.g. also "switch to a mode" or "load skill X") so the catalog shape is exercised more?
5. **Decline-memory home — confirm.** I'll default decline-memory to `~/.amplifier/wayfinder/declines.md` (per-user, survives this workspace's destruction). Say the word if you'd rather it live in the workspace/project instead.

---

## 6. Answers (Brian, 2026-08-18) — build unblocked

1. **Install shape:** proper bundle repo that passes the `validate-bundle-repo` recipe, with a behavior bundle installable via `--app` per conventions. App-agnostic by construction; **amplifier-app-cli will auto-compose it** (like goal/notify) via a separate app-cli change, later ring. No other app-specific coupling allowed.
2. **Pinning source:** mined from Context Intelligence (spark-1) — real config + real usage → `../../mining/pinning-research.md`. Standing intent: wayfinder content is regularly refreshed by CI agents mining *actual current practice*, not hand-maintained folklore. (Announcements paste from Brian still pending.)
3. **Ten-lane-highway source:** drafted from corpus + CI mining of session history (esp. cortex-core workspace) → `../../mining/goal-workflow-evolution.md`. Note: the literal phrase appears nowhere in sessions — the *practice* ("keep 10+ lanes full") is real and heavily documented; the name is ours to author.
4. **Ring 0 offer set:** provider **pinning** (bulletin), **goal-batch**, **goalify**, **ten-lane-highway** (concept). More candidates when Brian pastes recent announcements.
5. **Decline-memory home:** `~/.amplifier/wayfinder/` confirmed-by-precedent — the `~/.amplifier/<component>/` + `AMPLIFIER_<COMPONENT>_DIR` env-override pattern is established (skills: `AMPLIFIER_SKILLS_DIR`; context-intelligence: `AMPLIFIER_CONTEXT_INTELLIGENCE_BASE_PATH` → `~/.amplifier/projects`; team-pulse: `AMPLIFIER_TEAM_PULSE_DIR` → `~/.amplifier/team-pulse/`). `~/.amplifier` is ecosystem-shared, not app-cli-owned. wayfinder uses `AMPLIFIER_WAYFINDER_DIR`, default `~/.amplifier/wayfinder/`.
```
