---
id: attractor
category: practice
headline: "Stop babysitting test-fix-retry loops — run them as pipelines gated on evidence, not the model's say-so; attractor-scout finds where that pays off in your own work."
try_now:
  - 'use attractor-scout to show me where this would help my own work'
  - 'use attractorify to turn this into a pipeline'
signals:
  prompt_matches:
    - '\b(attractor(ify)?|convergence (loop|pipeline))\b'
    - '\buntil (the |all )?(tests?|ci|build|suite|checks?)\b.{0,24}\b(pass|passes|passing|green)\b'
    - '\bkeep (fixing|retrying|iterating|re-?running)\b'
    - '\b(babysit|hand[- ]?hold)\w*\b.{0,40}\b(loop|tests?|build|ci|pipeline|agent)\b'
    - '\btest\W{0,3}fix\W{0,3}(retry|loop|again|repeat)'
    - '\bhill[- ]?climb'
    - '\battractor[- ]?scout\b|\b(scout|mine)\s+(my|our)\s+(own\s+)?(sessions?|history|work)\b'
    - '\bwhat\s+(should|could)\s+i\s+automate\b|\bworth\s+automating\b|\b(keep|keeps|always)\s+(doing|running|repeating)\b.{0,40}\b(by\s+hand|manually|over\s+and\s+over|again\s+and\s+again|same\s+thing)\b'
    - '\bwhere\s+(\w+\s+){0,3}?(appl(y|ies)|would\s+help|could\s+help|pays?\s+off|fits?)\b.{0,30}\bmy\s+(own\s+)?(work|workflow|sessions?|projects?|repos?)\b'
trigger: "the user is re-running tests or builds after each AI fix (\"run it again\", pasting the errors back), hill-climbing a metric, asking for unattended or CI convergence — OR is sizing attractor up for the first time: \"what should I automate?\", \"would this help me?\", \"where does this apply to my work?\", \"I keep doing the same thing by hand\""
action: 'read_file("@wayfinder:content/practices/attractor.md")'
verified_at: 2026-08-19
provenance: "amplifier-bundle-attractor README, docs/ISSUE_PIPELINE.md, skills/attractor-scout/SKILL.md (own-data-only + honest-NO contract) @ main 4aaedcf; install paths re-verified against origin/main 2026-08-19 (behaviors/attractor-core.yaml, profiles/attractor-profile-{anthropic,openai,gemini}, skills/attractorify, skills/attractor-scout all present)"
---

# attractor — convergence pipelines

Ever watched an agent announce "all fixed!" on a suite that's still red — then spent the next hour running the tests yourself, pasting the errors back, asking it to try again? **An attractor is that loop run properly: a graph with a corrective back-edge, whose exit gate reads *evidence* — an exit code, a diff, a file on disk — instead of the model's own claim that it finished.** A wrong-but-plausible answer can't walk out the front door, and when the budget runs out it abandons loudly with a postmortem rather than reporting a green it never earned. The reason it's worth the setup: a straight chain multiplies its failure rate at every step; a loop with a back-edge divides it.

**Not sure it's for you? Let it check your own work first.** This is the honest way in, and it's where most people should start. The **`attractor-scout`** skill reads **your own** local context-intelligence session history — the record of what you've actually been doing, session after session — finds the recurring units of work, and ranks the ones that are genuinely attractor-shaped. It writes a self-contained HTML map you open locally. **Own data only; nothing leaves the machine.** Best part: it's just as willing to tell you *no*. Honest-NOs are first-class output, each one carrying the sub-test it failed (*recipe* / *one-shot* / *fragile*) and what would change the answer — so you find out where attractor fits your work, and where it plainly doesn't, from your evidence rather than someone's pitch.

**In practice.** Your suite is half-red and you're on your fourth "try again" — that's the loop, and it wants a gate: *"use attractorify to turn this into a pipeline."* Or you're earlier than that — you've heard attractor is interesting but have no idea whether your work is shaped like it: *"use attractor-scout to show me where this would help my own work."* What comes back is a ranked local page saying *these recurring things are worth a pipeline, these are not, and here's the sub-test each one failed.*

**How to run it.** Both are skills, so both are per-session — check your visible skills list first, and if they're not there I can name the bundle and add it on your go, never automatically. Invoke in natural language (*"use attractor-scout on my sessions"*, *"use attractorify on this"*); the slash forms `/attractor-scout` and `/attractorify` also work **if your app wires skills to slash commands** — the app-CLI doesn't guarantee it, so prefer the ask. They come from the attractor bundle's root `bundle.md` (which registers `skills/`) — note that the `behaviors/attractor-core.yaml` install below registers the expert agent, tools, and hooks but **not** the skills.

**Does the job even want one?** Three questions, and `attractor-scout` applies exactly these to every recurring unit it finds:

1. **Is there a cycle?** — can the work route back and try again?
2. **Is the exit gated on evidence**, rather than on step-completion?
3. **Does it survive one node having a bad day?**

Three yeses → attractor. Anything less and a pipeline is the wrong tool.

**Gotchas.**
- **One-shot? Just ask.** If a single competent pass is likely right, the loop costs more than the work.
- **Staged steps with a human sign-off between them are a recipe, not an attractor** — and recipes are the right tool there. A gate a person clears is not machine-checkable convergence.
- **No cycle, or no machine-checkable "done" → fix that first.** If you can't name the command that proves it, the gate ends up reading the model's own say-so, which is the exact failure this exists to prevent.
- **`attractor-scout` needs history to mine.** It reads your local context-intelligence sessions; on a brand-new machine there's nothing there yet and it fails loud (`looked in <root>, found 0`) rather than inventing a count. It also flags a unit seen in only two or three sessions as `provisional`, and never renders an untested one as a failure — "no bad day observed" isn't "wouldn't survive one."
- **Early-stage — pin a SHA.** No semver, high churn; if you depend on it, pin a commit SHA rather than `@main`.

**More.** The published explainer is the best 10-minute read on *why* the gate matters: <https://microsoft.github.io/amplifier-bundle-attractor/attractor-explained.html> (bundle repo: <https://github.com/microsoft/amplifier-bundle-attractor>). For DOT authoring, routing, and debugging, delegate to `attractor:attractor-expert`. To add the expert + pipeline tools to a session: `amplifier bundle add git+https://github.com/microsoft/amplifier-bundle-attractor@main#subdirectory=behaviors/attractor-core.yaml --app`; to actually *run* provider-routed pipelines, add a profile to your config instead (`profiles/attractor-profile-anthropic`, `-openai`, or `-gemini` — needs the matching API key). There's a standalone CLI too, installed separately: `uv tool install git+https://github.com/microsoft/amplifier-bundle-attractor@main#subdirectory=modules/pipeline-runner`. Copy-me exemplars live in `examples/pipelines/practical/`, and on a repo a labelled issue can run the whole lane — proposing a definition of done as a reviewable PR before any fix is written (`docs/ISSUE_PIPELINE.md`).
