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
verified_at: 2026-09-02
provenance: "installed amplifier-work-tracker CLI --help + per-subcommand --help (new/add/claim/edit); try_now commands, name regex, and the verb list verified against the live binary. Enumerated capability claims deliberately removed after a stale 'no edit command' gotcha misled a first-time setup -- the packet now points at --help for the command surface and states only non-drifting invariants."
---

# work-tracker — shared work queue

Two parallel sessions quietly redoing each other's work — and the half-finished item lost the moment you close the laptop. **`amplifier-work-tracker` is a shared, persistent work queue multiple agents pull from without colliding: claiming an item is the claim AND a PID-bound custody start in one atomic step, so two agents never converge on the same top item.** It's also a first-class sink for the work and lessons you turn up mid-session.

**In practice.** You're running a couple of agents against one repo and you keep tripping over each other. Stand up a project, file the known items, and let each agent `claim` the next ready one — custody binds to the claiming process, so nobody double-claims, and `list`/`status` let you inspect without touching custody. Then mid-session you notice an unrelated bug: `add` it right there, so it survives the context window instead of evaporating when the session ends.

**Try it (shell):**
1. `amplifier-work-tracker new my_project` — create the project first; there is no implicit create-on-add.
2. `amplifier-work-tracker add --project my_project "Fix flaky auth test"` — file an item (`--description`, `--acceptance` optional).
3. `amplifier-work-tracker claim --project my_project --actor me` — claim the next ready item (or `--id <id>` for a specific one).

**What it needs.** This one isn't built-in — it's a separate CLI plus a background service (a shared dolt server + reap/notify sweep loops). Confirm it's present in this session before offering commands: `amplifier-work-tracker doctor` checks the CLI's assumptions against the live binary (`which amplifier-work-tracker` is a quick presence check; the `work_tracker_status` tool reports the same if your session has it). An explicit request to install, start, or use it authorizes that in-scope action without duplicate Wayfinder ack; native host, tool, safety, and destructive-action approvals still apply. If Wayfinder introduces setup or use as an optional next step, show the exact action and wait for explicit ack; never act unsolicited.

**Gotchas.** Only the things that don't change — for the command surface itself, ask the binary, not this packet.
- **`amplifier-work-tracker --help` is the source of truth for verbs.** The verb set grows faster than any note about it (items *are* edited in place with `edit`; projects can be `rename`d and `remove`d; items `move` between projects; `defer`/`block`/`dep` exist). If a capability list — including one a previous session remembers — disagrees with `--help`, `--help` wins.
- **`new` first.** There is no implicit create-on-add; `add` won't conjure a missing project.
- **Project names reject hyphens and dots.** They must match `^[a-z][a-z0-9_]{1,30}$` — use underscores (`my_project`, not `my-project`). Not cosmetic: a project name becomes a dolt database name, and hyphens/dots aren't valid unquoted SQL identifiers. Dots are rejected deliberately: they'd produce a project that reports "created" and then fails every later command.
- **Custody has semantics you should not guess at.** Claiming is atomic and PID-bound; custody is a liveness signal (renewals), not a timer; a reported write failure means re-read before retrying. Load the `claiming-work-safely` skill before driving the claim → declare → resolve loop.

**More.** It shines as a discovered-work / lesson **sink** — not only a custody queue for planned work: when you hit a gap mid-session, `add` it (or file it against the item you hold) so it outlives the context window. For the safe claim → declare → resolve custody loop (freshness, reaps, empty queue), load the `claiming-work-safely` skill.
