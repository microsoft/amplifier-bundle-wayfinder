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

Ever been told "I'll let you know when it's done" — and then nothing? The turn quietly ended, the notification never fired, and you're back to checking manually. `monitor` closes that gap: it's a bounded sleep-check-decide loop that keeps the turn *open* until the thing you're watching actually finishes, fails, or genuinely needs you — so the end-of-turn ping fires on a real event instead of an empty promise.

**In practice:** you just pushed a fix and opened PR 412. Instead of babysitting the CI tab, you say *"watch the CI run for PR 412, check every 2 minutes, stop after an hour, and ping me if it goes red or finishes."* The session polls quietly and only comes back when there's something real to say. It watches anything checkable from the shell — CI, log files, HTTP endpoints, background jobs, long builds — and you pin four things: the check, the done-condition, what counts as needing you, and the interval + max duration (defaults: 60s, 2h cap).

**How to run it:** natural language is the main way in — *"monitor the build until it's green"* — and in the app-CLI the slash form works too: `/monitor the CI run for PR 412, check every 2m, stop after 1h`. Wire the actual alert with `amplifier notify` (desktop, or `ntfy` push).

**No install.** `monitor` is a standard skill and `/monitor` is always wired in the app-CLI, so it's here already — nothing to add. (If you're in a stripped-down app and don't see it, confirm `monitor` is in your visible skills list.)

Each of these was bought with a real failure — worth keeping in mind:

- **Keep checks genuinely paced.** A delegated monitor can compress its polls and fabricate elapsed time — one run did 34 checks in 324s while claiming "24 checks over 2h." Near-simultaneous checks can't observe a state change between them.
- **Watch facts, not TUI text.** Gate on git state and artifacts on disk, not on-screen words. "Processing…" vanishes while a sub-agent runs, and a monitor once read that gap as an idle lane.
- **Distrust metrics built on files that may not exist yet.** A check that reads a not-yet-written status file reports confident nonsense. Verify the file exists before trusting the number.

Deeper: it runs the poll loop on a fast sub-agent (~1.2¢/check, so an 8-hour watch stays under $2), or inline when you want to steer mid-flight. It's model-invocable, so an agent reaches for it instead of promising "I'll let you know."
