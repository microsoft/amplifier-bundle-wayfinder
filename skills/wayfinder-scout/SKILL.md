---
name: wayfinder-scout
description: >
  Rank the current wayfinder offer catalog against the reader's OWN usage
  evidence before rendering it — so wayfinder never leads with something the
  reader already does daily, and never offers a rung below one they've
  mastered. Loaded by the wayfinder channel on explicit engagement ("what's
  new?", "what else is on the menu?"); also directly invocable to audit what
  this user has already adopted ("wayfinder-scout", "what have I already
  adopted?", "rank the wayfinder menu for me").
user-invocable: true
allowed-tools:
  - read_file
  - glob
  - grep
  - bash
---

# wayfinder-scout — know the reader before you point

You have a wayfinder offer catalog in context (injected by the channel) and a
reader who explicitly asked what's worth their attention. Your job: rank that
catalog against **evidence of what this reader already uses**, then render it
in wayfinder's voice. The one rule:

**Never lead with what the reader already does. Never offer a rung below one
they've mastered. Acknowledge mastery; don't teach it.**

A real, measured failure is why this skill exists: wayfinder once led with
`/goal` — beginner framing and all — for a user who ran 131 goal sessions
across 124 workspaces *that same day*, including a live 8-lane highway batch.
The catalog rotation can't see adoption. You can.

## Step 1 — Read the ladder

Catalog lines may carry a `builds on: <id>` annotation (from packet
frontmatter `builds_on`). That's a subsumption ladder: mastering a higher rung
implies the rungs below (e.g. `ten-lane-highway` builds on `goal-batch` builds
on `goal`). If an annotation is missing but you suspect a ladder, read the
packet's own frontmatter via its `body:` action path — cheap, one read.

## Step 2 — Probe the evidence (local-first, bounded, ≤ ~6 tool calls)

Local files are the **authoritative superset** on this machine — every
session lands locally; a CI server holds at most a copy. Probe in this order:

**Tier A — on-disk artifacts (cheapest, uncontaminatable):**
- Exposure vs adoption: `${AMPLIFIER_WAYFINDER_DIR:-~/.amplifier/wayfinder}/surfaced.jsonl`
  — an offer listed there was *shown*, which is NOT adoption. Keep the
  distinction.
- Real-use artifacts, e.g. goal files:
  `find ~ -maxdepth 6 -path '*/.amplifier/goals/*.md' -mtime -30 2>/dev/null | head -20`
  and lane-style worktree dirs (`*-lanes/*/lanes/*`). An artifact the offer's
  workflow *produces* is the strongest adoption signal there is.

**Tier B — runtime markers in local session data (bounded!):**
Root: `${AMPLIFIER_CONTEXT_INTELLIGENCE_BASE_PATH:-$HOME/.amplifier/projects}`.
These `events.jsonl` files can carry 100k+ token lines — **never read them
whole**. Pick the ~100–200 most-recent session dirs (by mtime), then
`grep -l` / `grep -c` for runtime markers only, counting FILES:
- goal runs: `grep -l "OrchestratorGoalProgress"` (kernel event — a menu
  mention can never produce it)
- skill adoption: `grep -l '"skill_name": "<id>"'` (SkillLoad records)
- an offer's own `try_now` command tokens where they're distinctive

**Tier C — CI graph server, optional enrichment only:**
If the session's settings configure a context-intelligence source, you MAY ask
for label-scoped aggregates (SkillLoad counts per skill, goal-event session
counts). Never run free-text scans against the graph (measured: they time
out). Server unreachable or unconfigured → skip silently; local evidence
already suffices.

**FORBIDDEN sensor — transcript text-grep as adoption evidence.** Slash
commands are intercepted by the CLI and never stored as message text, so their
absence proves nothing; and any user who *discusses* a topic (or builds
wayfinder content!) saturates transcripts with mentions that are not use.
Measured 2026-09-03: naive text counts were off by two orders of magnitude vs
kernel events. Artifacts and runtime markers only.

## Step 3 — Classify each offer

- **declined** — already filtered out by the channel; leave them gone.
- **unseen** — no exposure record, no use evidence. These are your leads.
- **seen** — in `surfaced.jsonl` but no use evidence. Offerable, lower rank.
- **adopted** — any real use marker (artifact, kernel event, skill load).
- **mastered** — repeated recent use (roughly ≥5 sessions in 30 days), OR any
  real use of a rung that `builds_on` it (using the highway proves the goal
  rung — transitively).

## Step 4 — Rank and render

1. **Suppress** mastered offers and every rung below a mastered rung.
2. A partially-climbed ladder's **next rung up** is a prime candidate — that's
   the reader's actual growth edge.
3. **Lead** with the highest-value unseen offer (fresh bulletins first, then
   practices/concepts).
4. At most **one** honest mastery acknowledgment, only when it earns its line:
   "you're running the highway daily, so I'll skip the goal family." Never
   recite their stats back at them.
5. Everything adopted or declined? Say so plainly — "nothing here you don't
   already use" — and stop. An empty honest menu beats a padded one.
6. Claim "your sessions show X" **only** when a probe actually showed X.

Render in wayfinder's voice: one thing first, commands-first, short.

## Budget and fail-safe

Spend at most ~6 tool calls and a few seconds. If any probe errors, comes up
empty, or the environment looks unfamiliar — **render the catalog exactly as
injected** (its rotation order is the designed fallback) and move on. Never
block the turn, never surface probe errors to the reader, never fabricate
evidence. Note your findings in one line of your reply's reasoning so a later
menu ask this session can reuse them instead of re-probing.
