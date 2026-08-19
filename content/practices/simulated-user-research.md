---
id: simulated-user-research
category: practice
headline: "Run scripted personas through a real browser against your real app and get back an evidence-tiered findings spec — OBSERVED (machine-checked) vs SIMULATED (persona judgment)."
try_now:
  - 'uv tool install git+https://github.com/microsoft/amplifier-app-simulated-user-research'
  - 'amplifier-simulated-user-research doctor'
signals:
  prompt_matches:
    - '\b(simulated[- ]?user[- ]?research|persona (research|testing|round|session|audit)|user research round|first[- ]?run (session|research)|product audit)\b'
trigger: "the user wants persona-driven UX/product research against a running app, or an evidence-tiered findings spec before a real user session"
action: 'read_file("@wayfinder:content/practices/simulated-user-research.md")'
provenance: "amplifier-app-simulated-user-research announcement (2026-08) + spark-1 build-lane evidence-file failure"
verified_at: 2026-08-19
---

# simulated user research — personas, real browser, tiered findings

You want to know how a real user would hit your app before you ship — the confusion, the dead-ends, the "wait, where do I click" — but recruiting an actual person for a first pass is slow and expensive. This runs scripted personas through a real browser against your real app and hands back a prioritized findings spec, where every finding is labeled OBSERVED (a machine checked it) or SIMULATED (a persona judged it). Think of it as a pre-filter that makes your first real user session worth running — not a replacement for it.

**In practice:** you've got a new onboarding flow and a real user session booked for next week. Rather than burn that hour discovering the obvious, you seed a disposable instance, let three personas walk every screen in a real browser, and get back findings with repro steps — so the human session starts from "here are the five rough spots" instead of cold.

**How to run it:**

1. `uv tool install git+https://github.com/microsoft/amplifier-app-simulated-user-research`
2. `amplifier-simulated-user-research doctor` — verifies the host and warns if the persona briefs are still the defaults.

Then `init --dir my-round`, rewrite the persona briefs for *your* product, and `run --config my-round/project.yaml`. Or just ask a session: *"install and run microsoft/amplifier-app-simulated-user-research and report the findings."*

**Install — a separate standalone app, ask-first.** It's not a built-in or a bundle; it's its own CLI installed via `uv tool`. Check whether it's already here with `which amplifier-simulated-user-research` (or run its `doctor`); if it's missing, the `uv tool install` above adds it. That's a state change — confirm before running it.

It's the SIMULATED (persona) half of a two-sided review. Pair it with reality-check — the OBSERVED, machine-checked half — and a product-council for UX calls: the councils rank and reason, this supplies persona sessions with repro steps.

Three things to hold onto:

- **Gate on OBSERVED; keep SIMULATED advisory.** OBSERVED means machine-checkable and must carry reproduction steps; SIMULATED is persona hypothesis, not testimony ("3/3 personas agreeing is one model in three costumes").
- **Trust artifacts on disk over self-report.** Measured failure: build lanes claimed "PASS" with quoted log lines but wrote no evidence file — a claimed-OBSERVED that was actually SIMULATED. No artifact on disk means treat the claim as a hypothesis.
- **Rewrite the persona briefs.** Unchanged defaults against a different product produce fiction; `doctor` warns you.

Deeper: reality-check lives at `github.com/microsoft/amplifier-bundle-reality-check` — its exact install command isn't verified here, so confirm it before offering it.
