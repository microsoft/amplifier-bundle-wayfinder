# wayfinder — Ring 1 Design Proposal

**Status:** design proposal for discussion. No implementation. YAML/frontmatter blocks below are *illustrative sketches*, not files to ship.
**Builds on:** `RING0-PLAN.md` (§1 mechanism map, §6 answers, §7 directives). Ring 0 is built + validated: thin bundle + behavior, 3 always-on context files (~1.1–1.6K tokens), on-demand `content/`, flat-file decline-memory, zero Python. Repo: `microsoft/amplifier-bundle-wayfinder` (private).

Ring 1 turns four Ring-0 stopgaps into their clean mechanisms. The fixed constraints still bind: **point-don't-absorb**, authored voice, packet shape, the drift rule (verify at authoring/fetch time), the ~1.1–1.6K always-on floor, app-agnostic.

**The spine (read this first).** The four asks are not independent — they share two primitives and one schema:

- **One fetch primitive** (shallow git clone → cache, modeled on tool-skills `sources.py`) serves **both** ask #1 (fetch a whole guidance corpus) and ask #4 (fetch one bundle's live docs). Same code, two granularities.
- **One hook** assembling the catalog **from configured sources**, **filtered by declines**, unifies ask #1 (configurability) and ask #2 (determinism). The catalog moves from static `context.include` → hook-assembled ephemeral index. Floor-neutral or better.
- **One schema** — per-item YAML frontmatter — makes the catalog a *derived index* (ask #3), killing today's dual-maintenance of `current.md` + `offer-catalog.md`, and carries the machine-detectable signals the hook reads (ask #2).

Design each ask knowing it leans on these three shared pieces.

---

## Ask #1 — Content sourceable from configurable locations

**Want:** wayfinder's corpus (bulletins, catalog entries, concept notes, pro-tips) sourceable from other git repos / local paths / team-shared repos, so a team points wayfinder at its own guidance. Precedent: tool-skills `config.skills`.

**Mechanism choice: config-driven content resolution — a small resolver (code) consumed by the Ring-1 hook, NOT `context.include`, NOT a tool.**

Why not content/`context.include`: it's resolved at bundle-compose time against fixed namespaces — it cannot fetch a remote repo or merge by runtime config. The fetch *requires* code. Why not a tool: source resolution is deterministic infra, not an LLM decision. It belongs to the hook (ask #2), which already reads content deterministically.

**Deliberate scoping decision:** the always-on *voice* and *propose-and-ack protocol* stay **bundle-intrinsic** (static `context.include`). Those files ARE the wayfinder mechanism, not team-customizable guidance — making them source-able would let a bad source break the machine. **Only the corpus + catalog entries are sourceable.** Wayfinder's own bundled `content/` is simply the first (default) source.

Resolution reuses the proven tool-skills primitive verbatim in spirit: ordered list, **first-wins precedence**, `--depth 1 --branch <ref>` clone to `~/.amplifier/cache/wayfinder/…`, atomic tmp-rename publish, `.amplifier_cache_meta.json` (commit SHA + `cached_at` + ref), `GIT_TERMINAL_PROMPT=0` (never prompt — the REPL-freeze fix), 120s timeout with process-tree kill, `http://` rejected (encrypted transport only).

**Config sketch** (on the hook, in the behavior YAML):
```yaml
hooks:
  - module: hooks-wayfinder
    config:
      sources:                                  # ordered; first wins on id collision
        - "@wayfinder:content"                  # default: wayfinder's own bundled corpus
        - "~/wayfinder-corpus"                  # a local path the team edits
        - "git+https://github.com/acme/team-guidance@main#subdirectory=wayfinder"
      cache_ttl_hours: 24                        # never block session start on network
```
Each source contributes the same directory shape (`bulletins/`, `practices/`, `concepts/`, `pro-tips/`). The hook merges by item `id`; earlier sources win.

**Ring 1:** default (bundled) source + **one** configurable extra (local path or git URL). Prove the merge + precedence + graceful degrade on fetch failure. **Later:** `@bundle` refs via foundation's resolver, per-source auth for private team repos, source-level enable/disable.

**Risks:** (1) Remote content becomes near-always-on injected guidance → **prompt-injection surface** (see open Q2). Mitigation: only the *compact index* is injected; bodies stay on-demand; treat remote as untrusted. (2) Network at session start → never block; fall back to cache, then to bundled, and say so (unknown stays loud, but don't wedge the session). (3) Staleness → TTL + manifest shows `cached_at`/SHA (drift rule).

---

## Ask #2 — `hooks-wayfinder`: proactive injection + signal detection + enforced decline-memory

**Want:** deterministic firing (surface the bulletin at session:start), signal detection (session events → "user would benefit from hint X"), budget-conscious ephemeral injection, and decline-memory the hook *enforces* deterministically instead of trusting prose.

**Mechanism choice: a hook.** Decision-tree top branch: "must it always apply regardless of the LLM's choice?" → yes → hook. This was the acknowledged #1 Ring-1 upgrade in RING0 §1. The hook does three things, all deterministic:

1. **session:start** — resolve sources (#1), scan frontmatter → assemble the catalog index, read + filter the declines file, surface the current bulletin headline once (if not declined). Inject **ephemerally**.
2. **Signal detection** (`prompt:submit`, later `tool:pre`) — match machine-detectable signals → surface one matching offer headline ("you might benefit from X"). Rate-limited, declines-filtered.
3. **Decline enforcement** — the hook is the deterministic **reader/filter** of the declines file. A declined `id` never surfaces, no matter what any prose says.

**The trigger→hint matching model (Brian's explicit question).** Two-layer triggers in each item's frontmatter:

- **`signals:`** — machine-evaluable predicates the hook checks (deterministic, coarse). Ring 1 supports `on_event` and `prompt_matches`.
- **`trigger:`** — prose the *LLM* evaluates on-path (nuanced, the Ring-0 path). Unchanged.

```yaml
# frontmatter on content/bulletins/pinning.md (illustrative)
id: pinning
category: bulletin
headline: "Pin a conversation to an engine by handle; unpin to go back to routing."
signals:
  on_event: session:start                       # deterministic surface
  prompt_matches: ['\bwhich (model|provider)\b', '\bpin(ned|ning)?\b']
trigger: "session start, or the user wonders which model/provider they're on"   # prose, for the LLM
action: 'render headline + Try-it-now from content/bulletins/pinning.md'
```

The hook fires only the **coarse ephemeral nudge**. The agent still runs propose→show→ack→act; the human ack still gates every action. **The hook can never act** — its ceiling is one injected hint. That preserves "nothing unattended."

**Decline-memory — what's deterministic in Ring 1.** The **enforcement** (never re-offer a declined `id`) lives in the hook's read/filter path — the guarantee that matters, now reliable. The **write** (recording a fresh "no") stays agent-mediated in Ring 1 (append `id` on "no"), because detecting a decline deterministically from free text is unreliable. Making the *read* deterministic is ~80% of the value; deterministic decline-capture is a later refinement (open Q4).

**Floor impact:** the hook *replaces* the static `offer-catalog.md` `context.include` with a hook-assembled, source-merged, decline-filtered, ephemeral index. Net **floor-neutral or better**, and now configurable + filtered. Voice + protocol stay static.

**Ring 1:** session:start firing (bulletin + catalog index) + decline READ/FILTER + **one** signal type (`prompt_matches`) proving the model. **Later:** `tool_sequence` signals, `absent_capability` (offer install when a referenced thing isn't present), deterministic decline-capture, more aggressive session-observing jump-in (RING0 §7.2 left aggressiveness open).

**Risks:** (1) Over-firing → nagging erodes the whole point. Mitigation: rate-limit (one hint per `id` per session), declines respected, conservative patterns (favor false negatives). (2) Signal false positives → the nudge is only a nudge; on-path judgment + ack is the real gate. (3) Injection surface shared with #1.

---

## Ask #3 — Bigger corpus: categories, file convention, mining recipe

**Want:** a bigger "pro tips"/workflow-guidance corpus mined from real session patterns, catalogued like the others, refreshed by a repeatable pipeline (done by hand for Ring 0 = `mining/goal-workflow-evolution.md`).

**Mechanism choice: content (categories + frontmatter schema) + a staged recipe (the mining pipeline).** Categories/files are passive content; a multi-step, checkpointed, human-gated refresh is textbook recipe.

**Four categories** (from RING0 §7.6 "two content streams" + the mining evidence), one directory each:

| Category | What it is | Lifecycle | Ring-0 exemplar |
|---|---|---|---|
| `bulletins/` | feature/capability announcements | supersede + archive | pinning |
| `practices/` | "how we work" methodology, session-mined | durable | ten-lane-highway workflow |
| `concepts/` | thin note naming an idea, points to real source | durable | ten-lane-highway note |
| `pro-tips/` | atomic, high-leverage gotchas | many, cheap | "bare `/goal-batch` token doesn't load the skill"; "write-to-file, don't paste lane reports" |

**File convention: one markdown file per item, YAML frontmatter carries all catalog metadata.** The **catalog becomes a derived index** — the hook scans frontmatter across all sources and assembles it. No more hand-maintaining `offer-catalog.md` alongside the content. Frontmatter fields: `id`, `category`, `headline`, `trigger` (prose), `signals` (machine), `action`, `verified_at`, `provenance`, `supersedes`.

**The mining recipe** (staged, reproduces `goal-workflow-evolution.md` mechanically):
```yaml
name: wayfinder-mine-practice
stages:
  - name: mine        # graph-analyst → Context Intelligence; every claim traceable (workspace+timestamp)
  - name: verify      # drift rule: repo exists? command shape current? skill present?
  - name: author      # writing-role → packet in wayfinder voice + packet shape + frontmatter
    approval:
      required: true   # authored voice = human-curated. Recipe DRAFTS; Brian CURATES.
  - name: land        # write to corpus source, open PR
```
The approval gate before `land` is load-bearing: it keeps "authored voice" human-owned — the recipe drafts from *current* practice (drift-verified, provenance-tagged); Brian approves before anything enters the corpus.

**Ring 1:** define categories + frontmatter schema + derived-catalog convention; convert the 4 existing items; seed `pro-tips/` from gotchas already mined. Ship the recipe through the `author`+approval stage; `land` stays manual. **Later:** scheduled CI refresh, auto-PR, supersede/archive automation.

**Risks:** (1) Mining → folklore/stale claims. Mitigation: `verify` stage + `provenance`/`verified_at` frontmatter + human gate; **never auto-land**. (2) Corpus bloat → bodies never always-on; only the frontmatter-derived index is. (3) Schema churn → keep frontmatter minimal in Ring 1.

---

## Ask #4 — Dig-deeper: fetch the LIVE bundle repo, never a stale copy

**Want:** on ack of interest in bundle X, fetch X's live repo (@main README/docs/bundle.md) and answer from *that* — fresh, not maintained apart from its repo.

**Mechanism choice: a skill (`wayfinder-dig-deeper`) that shallow-fetches to a temp cache and reads — not a tool, not `amplifier bundle add`.**

Weighing the three Brian named:

| Option | Freshness | Cost | Safety | Verdict |
|---|---|---|---|---|
| **Skill** (bash `git clone --depth 1` @main → temp, `read_file`) | @main at ack time = max | seconds, one README | reads md only, never executes; ack-gated | **chosen** — zero new Python, reuses foundation tools, "point-don't-absorb" + drift rule by construction |
| Tool module | same | same | same | new Python for no UX gain over the skill |
| `amplifier bundle add` | good | heavier | mutates the user's install for a *read* | wrong — pollutes cache/config with a bundle they only wanted to read about; app-cli-coupled |

The skill's fetch mechanics are **the same primitive as ask #1** (shallow clone, `GIT_TERMINAL_PROMPT=0`, temp/atomic, timeout, cite commit SHA + `fetched_at`). If #1's resolver is built as a shared lib, the skill reuses it; if Ring 1 stays zero-Python, the skill body drives `git` directly with the same safety flags (open Q5).

**Freshness / cost / safety (as asked):** *Freshness* — reading current HEAD and citing the SHA satisfies the drift rule structurally. *Cost* — `--depth 1` of a README is cheap per-ack; optional short TTL cache within a session. *Safety* — clone lands code but we only READ `*.md`/`bundle.md`, never execute; `GIT_TERMINAL_PROMPT=0`; timeout + tree-kill; **allowlist to catalog-referenced repos**; ack shows the exact clone command before it runs (propose→show→ack→act).

**Ring 1:** on ack, fetch one catalog-referenced bundle's repo @main (README + bundle.md), answer + cite SHA/`fetched_at`. **Later:** shared fetch lib with the hook, TTL tuning, deeper doc traversal, offer-install-after-dig.

**Risks:** (1) Arbitrary-URL clone → allowlist + ack shows the command. (2) Private repos → clone fails fast (no prompt); report honestly + point at the URL. (3) Over-use cost → `--depth 1` + short TTL + explicit-ack only.

---

## Proposed Ring 1 scope cut (thinnest end-to-end slice)

The load-bearing piece that #1, #2, #3 all touch is **the hook assembling a frontmatter-derived catalog and filtering by declines.** Build that spine first; the rest are fast-follows on it.

**MUST-build spine (proves determinism #2, the schema #3, and the resolver seam for #1/#4):**
1. **Frontmatter schema** on content items; convert the 4 Ring-0 items (ask #3 schema).
2. **`hooks-wayfinder`** at `session:start`: read the **default bundled source**, scan frontmatter → assemble catalog index, read + **filter declines deterministically**, surface the current bulletin, + **one** `prompt_matches` signal (asks #2, part of #1).

**Fast-follows, in order, still Ring 1:**
3. **One configurable extra source** (local path or git URL) → prove merge/precedence/graceful-degrade (completes ask #1).
4. **`wayfinder-dig-deeper` skill** for one allowlisted catalog bundle (ask #4).
5. **`wayfinder-mine-practice` recipe** through `author`+approval; `land` manual (completes ask #3 pipeline).

Everything past the spine is independently shippable, so Ring 1 can land incrementally and stay daily-drivable throughout.

---

## Open questions for Brian (≤5)

1. **Derived catalog vs hand-authored.** Move the catalog from static `context.include` → hook-assembled-from-frontmatter (kills dual-maintenance, requires every item to carry frontmatter)? This is the load-bearing decision the whole spine rests on. I recommend **yes**.
2. **Trust boundary for sources.** Ring 1: restrict configurable sources to ones *you* control (your repos / local paths), treated as trusted — defer untrusted/public-team sources + prompt-injection hardening to Ring 2? Or is untrusted-source safety needed in Ring 1?
3. **Signal aggressiveness (RING0 §7.2 left open).** Ring 1 default = conservative: `prompt_matches` only, one hint per `id` per session, favor false negatives. Right starting posture, or do you want tool-sequence "jump-in" watching sooner?
4. **Decline-capture determinism.** Ring 1 makes *enforcement* (never re-offer) deterministic but keeps the *write* (recording a new "no") agent-mediated. Acceptable, or do you want the hook to detect declines deterministically now (harder, less reliable)?
5. **Dig-deeper fetch: zero-Python skill vs shared lib.** Thinnest Ring 1 = the skill drives `git` in its body (no new module). If #1's resolver is built as a small lib, the skill can share it. Prefer zero-new-Python for Ring 1, or build the shared fetch lib now (used by hook + skill)?
