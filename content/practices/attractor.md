---
id: attractor
category: practice
headline: "Stop babysitting test-fix-retry loops — run them as convergence pipelines with machine-checkable gates."
try_now:
  - '/attractorify'
  - 'amplifier bundle add git+https://github.com/microsoft/amplifier-bundle-attractor@main#subdirectory=behaviors/attractor-core.yaml --app'
signals:
  prompt_matches:
    - '\b(attractor(ify)?|convergence (loop|pipeline))\b'
    - '\buntil (the |all )?(tests?|ci|build|suite|checks?)\b.{0,24}\b(pass|passes|passing|green)\b'
    - '\bkeep (fixing|retrying|iterating|re-?running)\b'
    - '\b(babysit|hand[- ]?hold)\w*\b.{0,40}\b(loop|tests?|build|ci|pipeline|agent)\b'
    - '\btest\W{0,3}fix\W{0,3}(retry|loop|again|repeat)'
    - '\bhill[- ]?climb'
trigger: "the user is re-running tests or builds after each AI fix (\"run it again\", pasting the errors back), hill-climbing a metric, asking for unattended or CI convergence, or wiring issue-to-fix automation on a repo"
action: 'read_file("@wayfinder:content/practices/attractor.md")'
verified_at: 2026-08-19
provenance: "amplifier-bundle-attractor README + docs/ISSUE_PIPELINE.md; commands checked against the installed CLI and a live attractor-core install; install paths re-verified against origin/main 2026-08-19 (behaviors/attractor-core.yaml, profiles/attractor-profile-{anthropic,openai,gemini}, skills/attractorify all present)"
---

# attractor — convergence pipelines

**A loop with a gate the model cannot talk past: "done" stays structurally unreachable until machine-checkable evidence says otherwise.**

## Try it now

1. `/attractorify` — describe the job in prose. It diagnoses attractor vs recipe vs one-shot first, and authors a lint-clean pipeline only if one is actually warranted.
2. Don't have it? `amplifier bundle add git+https://github.com/microsoft/amplifier-bundle-attractor@main#subdirectory=behaviors/attractor-core.yaml --app` — that adds the `attractor:attractor-expert` agent and the pipeline tools. See Gotchas for where `/attractorify` itself lives.

## Why it matters

A straight chain multiplies its failure rate at every step; a loop with a corrective back-edge divides it. An attractor is a graph whose exit gate reads **evidence** — an exit code, a diff, a file on disk — instead of the model's own claim that it finished, so a wrong-but-plausible answer can't walk out the front door. When the budget runs out it abandons loudly, with a postmortem, rather than reporting a green it didn't earn.

Three questions decide whether a job wants one:

1. **Is there a cycle?** — can the work route back and try again?
2. **Is the exit gated on evidence**, rather than on step-completion?
3. **Does it survive one node having a bad day?**

Three yeses → attractor. Anything less and a pipeline is the wrong tool — see Gotchas.

## Gotchas

- **One-shot? Just ask.** If a single competent pass is likely right, the loop costs more than the work.
- **Staged steps with a human sign-off between them are a recipe, not an attractor** — and recipes are the right tool there. A gate a person clears is not machine-checkable convergence.
- **No cycle, or no machine-checkable "done" → fix that first.** If you can't name the command that proves it, the gate ends up reading the model's own say-so, which is the exact failure this exists to prevent.
- **`/attractorify` ships in the attractor bundle's root `bundle.md`** (which registers `skills/`); the `attractor-core` behavior above registers the expert agent, tools, and hooks — not the skill. If `/attractorify` isn't in your skills list, delegate to `attractor:attractor-expert` instead.

## More

- **The expert** — `delegate to attractor:attractor-expert` for DOT authoring, routing, and debugging.
- **Standalone CLI** (separate from the bundle): `uv tool install git+https://github.com/microsoft/amplifier-bundle-attractor@main#subdirectory=modules/pipeline-runner`, then `attractor run <graph.dot> --cwd .`, `attractor lint <graph.dot>`, and — on current `main` — `attractor resume <run-dir> --cwd .`.
- **Copy-me exemplars** — `examples/pipelines/practical/` (bug-fix, refactor, test-gen; each ships a runnable sample) and `examples/authoring/`.
- **On a repo** — a labelled issue can run the whole lane: it proposes a definition of done as a reviewable PR before any fix is written (`docs/ISSUE_PIPELINE.md`).
- **Run a whole pipeline, not just the tools** — the `--app` line above adds the expert + pipeline tools to your session; to actually run provider-routed pipelines, add a profile to your config instead: `includes: [ - bundle: git+https://github.com/microsoft/amplifier-bundle-attractor@main#subdirectory=profiles/attractor-profile-anthropic ]` (or `-openai` / `-gemini`; needs the matching API key).
- **Early-stage — pin a SHA.** No semver, high churn; if you depend on it, pin a commit SHA instead of `@main`.
