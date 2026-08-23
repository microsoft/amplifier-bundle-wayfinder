---
id: loop-until-proven
category: practice
headline: "Stop re-running the tests yourself — put the fix-retry loop behind a gate that reads evidence, so it can't call itself done until a real command passes."
try_now:
  - 'use attractor-scout to show me where this would help my own work'
  - 'use attractorify to turn this into a pipeline'
signals:
  prompt_matches:
    - '\b(attractor(?:s|ify|[- ]?scout)?|convergence[- ](?:loops?|pipelines?)|loop[- ]until[- ]proven)\b'
    - '\buntil (the |all )?(tests?|ci|build|suite|checks?)\b.{0,24}\b(pass|passes|passing|green)\b'
    - '\b(?:keeps?|kept) (fixing|retrying|iterating|re-?running)\b|\b(?:keeps?|kept)\s+running\s+(?:the\s+)?(?:tests?|suite|build|ci|checks?)\b'
    - '\b(babysit|hand[- ]?hold)\w*\b.{0,40}\b(loop|tests?|build|ci|pipeline|agent)\b'
    - '\btest\W{0,3}fix\W{0,3}(retry|loop|again|repeat)'
    - '\bhill[- ]?climb'
    - '\b(scout|mine)\s+(my|our)\s+(own\s+)?(sessions?|history|work)\b'
    - '\bwhat\s+(should|could)\s+i\s+automate\b|\bworth\s+automating\b|\b(keep|keeps|always)\s+(do(?:es|ing)?|runs?|running|repeat(?:s|ing)?)\b.{0,40}\b(by\s+hand|manually|over\s+and\s+over|again\s+and\s+again|same\s+thing)\b'
    - '\bwhere\s+(\w+\s+){0,3}?(appl(y|ies)|(?:would|could|does|do|will|can|might)\s+(?:this|it|that|attractor\w*)\s+helps?|would\s+help|could\s+help|pays?\s+off|fits?)\b.{0,30}\bmy\s+(own\s+)?(work|workflow|sessions?|projects?|repos?)\b'
trigger: "the user is driving a fix-retry loop by hand, wants a run that converges unattended or in CI, or is sizing attractor up for the first time and asking whether it fits their own work"
action: 'read_file("@wayfinder:content/practices/loop-until-proven.md")'
verified_at: 2026-08-20
provenance: "amplifier-bundle-attractor README, docs/ISSUE_PIPELINE.md, skills/attractor-scout/SKILL.md (own-data-only + honest-NO contract); re-verified 2026-08-20 against origin/main 4e1ba02 — the ROOT bundle.md is what registers skills/ (via tool-skills), behaviors/attractor-core.yaml does not; skill names confirmed against this session's visible skills list, where neither is slash-wired; `amplifier bundle add` syntax from the installed CLI's --help"
---

# loop until proven — the attractor practice

Ever watched an agent announce "all fixed!" on a suite that's still red — then spent the next hour running the tests yourself, pasting the errors back, asking it to try again? **That loop, run properly, is an attractor: a graph with a corrective back-edge whose exit gate reads *evidence* — an exit code, a diff, a file on disk — instead of the model's own claim that it finished.** A wrong-but-plausible answer can't walk out the front door, and when the budget runs out it abandons loudly with a postmortem rather than reporting a green it never earned. Worth the setup because a straight chain multiplies its failure rate at every step; a loop with a back-edge divides it.

**In practice.** Your suite is half-red and you're on your fourth "try again" — that's the loop, and it wants a gate: *"use attractorify to turn this into a pipeline."* Earlier than that — you've heard attractor is interesting but have no idea whether your work is even shaped like it — start with the scout instead: *"use attractor-scout to show me where this would help my own work."* It reads **your own** local context-intelligence session history, finds the units of work you keep repeating, ranks the genuinely attractor-shaped ones, and writes a self-contained HTML map you open locally. **Own data only; nothing leaves the machine.** And it's just as willing to tell you *no* — honest-NOs are first-class output, each carrying the sub-test it failed (*recipe* / *one-shot* / *fragile*) and what would change the answer.

**Does the job even want one?** Three questions — the same three the scout applies to every recurring unit it finds:

1. **Is there a cycle?** — can the work route back and try again?
2. **Is the exit gated on evidence**, rather than on step-completion?
3. **Does it survive one node having a bad day?**

Three yeses → attractor. Anything less and a pipeline is the wrong tool.

**How to run it.** Both are skills from the attractor bundle, so both are per-session — check your visible skills list first. If they aren't there, use this command:

`amplifier bundle add git+https://github.com/microsoft/amplifier-bundle-attractor@main --app`

An explicit request to install the bundle or run one of these skills authorizes that in-scope action without duplicate Wayfinder ack; native host, tool, safety, and destructive-action approvals still apply. If Wayfinder introduces installation or skill use as an optional next step, show the exact action and wait for explicit ack; never act unsolicited.

That's the bundle's **root**, which is what registers `skills/` — the narrower `behaviors/attractor-core.yaml` install adds the expert agent, tools and hooks but **not** the skills. Invoke in natural language (*"use attractor-scout on my sessions"*, *"use attractorify on this"*); the slash forms work only if your app wires skills to commands, which the app-CLI doesn't guarantee — so prefer the ask.

**Gotchas.**
- **One-shot? Just ask.** If a single competent pass is likely right, the loop costs more than the work.
- **Staged steps with a human sign-off between them are a recipe, not an attractor** — and recipes are the right tool there. A gate a person clears is not machine-checkable convergence.
- **No cycle, or no machine-checkable "done" → fix that first.** If you can't name the command that proves it, the gate ends up reading the model's own say-so, which is the exact failure this exists to prevent.
- **The scout needs history to mine.** On a brand-new machine there's nothing there yet, and it fails loud (`looked in <root>, found 0`) rather than inventing a count. It flags a unit seen in only two or three sessions as `provisional`, and never renders an untested one as a failure — "no bad day observed" isn't "wouldn't survive one."
- **Early-stage — pin a SHA.** No semver, high churn; if you depend on it, pin a commit SHA rather than `@main`.

**More.** One good next step: the published explainer, still the best ten minutes on *why* the gate matters — <https://microsoft.github.io/amplifier-bundle-attractor/attractor-explained.html> (it lives in the bundle repo, <https://github.com/microsoft/amplifier-bundle-attractor>). There's plenty past that — a standalone pipeline runner, copy-me exemplars, a labelled-issue lane that proposes a definition of done as a reviewable PR before any fix is written — ask and I'll walk you through whichever one you actually need.
