---
id: work-tracker
category: practice
promoted: true
headline: "A shared work queue for parallel agents — claim ready items with PID-bound custody, and capture discovered work mid-session so nothing is lost."
try_now:
  - "amplifier-work-tracker new my_project"
  - 'amplifier-work-tracker add --project my_project "Fix flaky auth test"'
  - "amplifier-work-tracker claim --project my_project --actor me"
signals:
  prompt_matches:
    - '\b(?:work[- ]?tracker|amplifier-work-tracker|shared (?:work )?queue|work queue)\b|\bclaim\b[\w ]{0,20}\bitem\b'
trigger: "the user wants a shared/persistent work queue, to claim work items, or to capture discovered work and lessons mid-session"
action: 'read_file("@wayfinder:content/practices/work-tracker.md")'
verified_at: 2026-08-19
provenance: "installed amplifier-work-tracker CLI --help; commands verified against the live binary"
---

# work-tracker — shared work queue

**A queue multiple agents can pull from without colliding — claiming an item establishes PID-bound custody atomically. Also a first-class SINK for work and lessons you discover mid-session.**

## Try it now (shell)

1. `amplifier-work-tracker new my_project` — create the project first; there is no implicit create-on-add.
2. `amplifier-work-tracker add --project my_project "Fix flaky auth test"` — file an item (`--description`, `--acceptance` optional).
3. `amplifier-work-tracker claim --project my_project --actor me` — claim the next ready item (or `--id <id>` for a specific one).

## Why it matters

Claiming is the claim AND the custody start in one atomic step, so two agents never converge on the same top item. `list` and `status` are read-only — inspect without touching custody.

## Gotchas

- **No create-project op beyond `new`.** Run `new` first; `add` will not conjure a missing project.
- **Project names reject hyphens.** They must match `^[a-z][a-z0-9_]{1,30}$` — use `underscores` (`my_project`, not `my-project`). Dots are rejected too.
- **No edit command.** To correct a bad item, file a NEW item that references the wrong one — items aren't edited in place.

## More

- It shines as a discovered-work / lesson **sink**: when you hit a gap mid-session, `add` it (or file it against the item you hold) so it survives the context window — not only a custody queue for planned work.
- For the safe claim→declare→resolve custody loop (freshness, reaps, empty queue), load the `claiming-work-safely` skill. `amplifier-work-tracker doctor` verifies the CLI's assumptions against the live binary.
