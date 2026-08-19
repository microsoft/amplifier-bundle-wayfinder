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
provenance: "installed amplifier-work-tracker CLI --help; commands + name regex verified against the live binary"
---

# work-tracker — shared work queue

Two parallel sessions quietly redoing each other's work — and the half-finished item lost the moment you close the laptop. **`amplifier-work-tracker` is a shared, persistent work queue multiple agents pull from without colliding: claiming an item is the claim AND a PID-bound custody start in one atomic step, so two agents never converge on the same top item.** It's also a first-class sink for the work and lessons you turn up mid-session.

**In practice.** You're running a couple of agents against one repo and you keep tripping over each other. Stand up a project, file the known items, and let each agent `claim` the next ready one — custody binds to the claiming process, so nobody double-claims, and `list`/`status` let you inspect without touching custody. Then mid-session you notice an unrelated bug: `add` it right there, so it survives the context window instead of evaporating when the session ends.

**Try it (shell):**
1. `amplifier-work-tracker new my_project` — create the project first; there is no implicit create-on-add.
2. `amplifier-work-tracker add --project my_project "Fix flaky auth test"` — file an item (`--description`, `--acceptance` optional).
3. `amplifier-work-tracker claim --project my_project --actor me` — claim the next ready item (or `--id <id>` for a specific one).

**What it needs.** This one isn't built-in — it's a separate CLI plus a background service (a shared dolt server + reap/notify sweep loops). Confirm it's present in this session before offering commands: `amplifier-work-tracker doctor` checks the CLI's assumptions against the live binary (`which amplifier-work-tracker` is a quick presence check; the `work_tracker_status` tool reports the same if your session has it). If it's missing, installing or starting the service is a state change — say what's needed and get a go first, never automatically.

**Gotchas.**
- **No create-project op beyond `new`.** Run `new` first; `add` won't conjure a missing project.
- **Project names reject hyphens (and dots).** They must match `^[a-z][a-z0-9_]{1,30}$` — use underscores (`my_project`, not `my-project`). Dots are rejected deliberately: they'd produce a project that reports "created" and then fails every later command.
- **No `edit` command.** To correct a bad item, file a NEW item that references the wrong one — items aren't edited in place. (`unclaim` releases a held item without resolving it; `resolve` closes one with a reason.)

**More.** It shines as a discovered-work / lesson **sink** — not only a custody queue for planned work: when you hit a gap mid-session, `add` it (or file it against the item you hold) so it outlives the context window. For the safe claim → declare → resolve custody loop (freshness, reaps, empty queue), load the `claiming-work-safely` skill.
