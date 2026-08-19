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

**Seed a disposable instance, walk every screen in a real browser as three personas, and get back a prioritized findings spec where every finding is labeled OBSERVED (a machine checked it) or SIMULATED (a persona judged it).** A pre-filter that makes your first real user session worth running — not a replacement for it.

## Try it now

1. `uv tool install git+https://github.com/microsoft/amplifier-app-simulated-user-research`
2. `amplifier-simulated-user-research doctor` — verifies the host and warns if the persona briefs are still the defaults.

Then `init --dir my-round`, rewrite the persona briefs for your product, and `run --config my-round/project.yaml`.

## Why it matters

It's the SIMULATED (persona) half of a two-sided review. Pair it with reality-check — the OBSERVED, machine-checked half — and a product-council for UX calls: the councils rank and reason, this supplies persona sessions with repro steps.

## Gotchas

- **Gate on OBSERVED; keep SIMULATED advisory.** OBSERVED means machine-checkable and must carry reproduction steps; SIMULATED is persona hypothesis, not testimony ("3/3 personas agreeing is one model in three costumes").
- **Trust artifacts on disk over self-report.** Measured failure: build lanes claimed "PASS" with quoted log lines but wrote no evidence file — a claimed-OBSERVED that was actually SIMULATED. No artifact on disk means treat the claim as a hypothesis.
- **Rewrite the persona briefs.** Unchanged defaults against a different product produce fiction; `doctor` warns you.

## More

- Easiest path: ask a session "Install and run the microsoft/amplifier-app-simulated-user-research and report back findings."
- Pairs with `reality-check` for the observed half (bundle repo: github.com/microsoft/amplifier-bundle-reality-check) — its install command is not verified here.
