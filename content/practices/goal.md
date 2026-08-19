---
id: goal
category: practice
promoted: true
headline: "Hand the agent a finish line it can check itself — it keeps working, turn after turn, until the check passes."
try_now:
  - "/goal <condition>"
  - "/goal --max-turns 5 <condition>"
  - "/goal clear"
signals:
  prompt_matches:
    - '/goal\b|\bautonomous (?:run|continuation)\b|\brun\b[\w ]{0,20}to completion\b|\bkeep (?:working|going) until\b|\brun (?:it|this)?\s*until (?:done|green|it passes)\b'
    - '\b(goalify|stop[- ]?condition|turn (this|it) into (a )?goal)\b'
trigger: "the user wants Amplifier to keep working turn-after-turn toward a checkable condition without approving each turn — or wants help wording that finish line so it actually holds"
action: 'read_file("@wayfinder:content/practices/goal.md")'
verified_at: 2026-08-19
provenance: "installed CLI docs/GOAL_COMMAND.md (unlimited-by-default per ADR-0005); goalify skill"
---

# goal — autonomous continuation

Tired of approving turn after turn just to keep it moving — and tired of the agent announcing "done" on something that plainly isn't? `/goal` fixes both ends. **You hand it a finish line it can check itself: after each turn a separate evaluator asks "is this done?" against your condition and, if not, kicks off another turn — until the check actually passes.**

The load-bearing idea: **you specify the evidence that proves "done," and that becomes the bar it's held to.** It won't come back until it has shown that evidence in the transcript — or shown that the condition can't be met. Its own optimism doesn't count; the check does. You keep control; you just stop approving every single turn.

**In practice.** Your test suite is half-red and you don't want to babysit each fix. Give it a finish line it can verify: ``/goal Done when `cd /abs/proj && pytest -q` exits 0``. It works turn after turn — fix, run, read the output, fix again — and stops when the tests genuinely pass, not when it decides it's finished.

**How to run it.** BUILT-IN — always here in an interactive session, nothing to install:

- `/goal <condition>` — set the finish line and start. Unlimited turns by default.
- `/goal --max-turns 5 <condition>` — same, with a hard, Python-enforced turn cap.
- `/goal clear` — clear it (aliases: `stop`, `off`, `reset`, `none`, `cancel`). `/goal` with no args shows the condition, turns, continuations, and the evaluator's last reason.

**Wording the finish line.** The sharpness of the condition is the whole game — a vague one loops forever on ambiguity or waves through a shallow claim as "done." The **`goalify`** skill is THE way to get it right: it reads what you're already doing and writes a well-formed, lint-checked `/goal` condition — a measurable end state plus a transcript-visible check — flagging the weak spots before you commit to a run. Invoke it in natural language — *"use goalify to turn this into a goal condition"* — or `/goalify` if your app wires skills to slash commands (the app-CLI doesn't guarantee it, so prefer the ask). It's a skill, so it's per-session: check the visible skills list; if it isn't there I can name the bundle that provides it and add it on your go — never automatically. Want the wording tightened? Just ask and I'll walk you through it.

**Gotchas.**
- **The evaluator reads only the TRANSCRIPT — it has no tools.** Work it never sees is invisible, so force proof into the transcript: name the exact artifacts AND a transcript-visible check (`cat` the file, or `cd ./x && pytest`). "Show the real output" beats "the end state should be X."
- **cwd mismatch is the #1 silent failure.** Work roots at the process cwd; pin the literal path in the condition (`cd /abs/path && pytest -q`), don't assume it.
- **Unlimited is the default (ADR-0005), not a cap.** `--max-turns 0` is explicit-unlimited; a cap hit means "unconfirmed," not "failed."

**More.** Headless too: `amplifier run --mode single "/goal <condition>"`. Going wide, for the adventurous: `goal-batch` fans several goals into parallel autonomous lanes at once — ask if you want to hear how it works.
