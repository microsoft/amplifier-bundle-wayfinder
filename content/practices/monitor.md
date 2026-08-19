---
id: monitor
category: practice
headline: "Watch a long job and get pinged the moment it's done, fails, or needs you — a bounded sleep-check-decide loop that holds the turn open."
try_now:
  - '/monitor the CI run for PR 412, check every 2m, stop after 1h'
signals:
  prompt_matches:
    - '\b(/monitor|monitor (the )?(ci|build|run|deploy|log|job|pipeline)|poll(ing)? (loop|until)|sleep[- ]?check[- ]?decide|watch (the )?(ci|build|run|job|deploy))\b'
trigger: "the user is about to wait on a long-running job (CI, build, deploy, background run) and wants to be pinged when it finishes or genuinely needs them"
action: 'read_file("@wayfinder:content/practices/monitor.md")'
provenance: "monitor skill (announcements 2026-08) + spark-1 session measurements"
verified_at: 2026-08-19
---

# monitor — hold the turn open until it's done

**A bounded sleep-check-decide loop that keeps the turn open until the thing you're watching is done, fails, or genuinely needs you — so the end-of-turn ping fires at the right moment.** Zero install.

## Try it now

1. `/monitor the CI run for PR 412, check every 2m, stop after 1h` — then walk away.

## Why it matters

Watches anything checkable from the shell — CI, log files, HTTP endpoints, background jobs, long builds. You pin the check, the done-condition, what counts as needing you, and the interval + max duration (defaults: 60s, 2h cap).

## Gotchas (each bought with a real failure)

- **Keep checks genuinely paced.** A delegated monitor can compress its polls and fabricate elapsed time — one run did 34 checks in 324s while claiming "24 checks over 2h." Near-simultaneous checks can't observe a state change between them.
- **Watch facts, not TUI text.** Gate on git state and artifacts on disk, not on-screen words. "Processing…" vanishes while a sub-agent runs, and a monitor once read that gap as an idle lane.
- **Distrust metrics built on files that may not exist yet.** A check that reads a not-yet-written status file reports confident nonsense. Verify the file exists before trusting the number.

## More

- Runs the poll loop on a fast sub-agent (~1.2 cents/check, so an 8-hour watch stays under $2), or inline when you want to steer mid-flight. Set up the ping with `amplifier notify`. Model-invocable, so an agent reaches for it instead of promising "I'll let you know."
