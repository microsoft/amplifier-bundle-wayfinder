---
id: goal
category: practice
promoted: true
headline: "Set a completion condition and let Amplifier work turn-after-turn on its own until it's met — unlimited by default, not capped."
try_now:
  - "/goal <condition>"
  - "/goal --max-turns 5 <condition>"
  - "/goal clear"
signals:
  prompt_matches:
    - '/goal\b|\bautonomous (?:run|continuation)\b|\brun\b[\w ]{0,20}to completion\b|\bkeep (?:working|going) until\b|\brun (?:it|this)?\s*until (?:done|green|it passes)\b'
trigger: "the user wants Amplifier to keep working turn-after-turn toward a checkable condition without approving each turn"
action: 'read_file("@wayfinder:content/practices/goal.md")'
verified_at: 2026-08-19
provenance: "installed CLI docs/GOAL_COMMAND.md (unlimited-by-default per ADR-0005)"
---

# goal — autonomous continuation

**Set a completion condition; after each turn a separate evaluator asks "is this done?" and, if not, starts another turn on its own. Auto mode drops per-tool prompts; `/goal` drops per-turn prompts.**

## Try it now (interactive session)

1. `/goal <condition>` — set the condition and start working. Unlimited turns by default.
2. `/goal --max-turns 5 <condition>` — same, with a hard Python-enforced turn cap.
3. `/goal clear` — clear it (aliases: `stop`, `off`, `reset`, `none`, `cancel`).

## Why it matters

`/goal` is a completion *gate*: it catches an agent that stops too early, restarting until the condition is genuinely met. `/goal` with no args shows the condition, turns, continuations, and the evaluator's last reason.

## Gotchas

- **The evaluator only reads the TRANSCRIPT — it has no tools.** Work it never sees is invisible. Force proof into the transcript: name the exact artifacts AND a transcript-visible check (e.g. `cat the file`, or `cd ./x && pytest`). "Show the real output" beats "the end state should be X."
- **cwd mismatch is the #1 silent failure.** Box-node work roots at the process cwd; pin the literal path in the condition (`cd /abs/path && pytest -q`), don't assume it.
- **Rate-limit storm → switch the routed model, don't serialize.** Re-point the model at unchanged concurrency (see the `pinning` bulletin) instead of dropping to one-at-a-time.
- **Unlimited is the default (ADR-0005), NOT a cap.** `--max-turns 0` is explicit-unlimited. A cap hit means "unconfirmed," not "failed."

## More

- Headless too: `amplifier run --mode single "/goal <condition>"`. To author a well-formed, lint-checked condition first, load the `goalify` skill; to fan many goals into parallel lanes, see `goal-batch`.
