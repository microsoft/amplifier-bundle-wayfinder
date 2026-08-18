# The ten-lane highway

> **On the name:** "ten-lane highway" is *our* coined label. The exact phrase appears nowhere in the actual sessions — but the practice it names is real, heavily used, and documented below. What Brian actually types is *"keep the lanes as close to 10 lanes as possible at all times."*

A concept note, not a skill. It rides alongside `goal-batch`, which is the tool that runs it.

## The ladder

The practice grew in rungs, each a real step:

1. **`/goal`** — run one autonomous session to a stop-condition; a cheap evaluator judges done/not-done after each turn and continues until it's satisfied (or a hard turn cap is hit).
2. **`/goalify`** — author the stop-condition itself: *"something that creates the goal for you to pass via `/goal`."*
3. **`/goal-batch`** — fan independent work out into parallel `/goal` lanes that can't collide, verified and merged for you.
4. **The highway** — keep ~10 lanes full at all times, refilling from a work queue, largely unattended.

## What a lane is

**One git worktree + one branch + one tmux/muxplex pane running an autonomous `/goal` session.** Lanes own disjoint file sets. A cross-lane conflict gets its *own* dedicated resolution lane that honors both intents ("no fallbacks, unknown stays loud") — integration is a first-class lane, not an afterthought.

## The disciplines that keep it honest

- **Verified merges, never assumed.** Per-lane definition of done: zero conflict markers, full suite green, commit the merge, do **not** push, report the SHA in the pane.
- **"Done" is structural, not optimistic.** *"If a tmux session still exists, that lane is NOT done — no matter what else you observe."*

## That it's real

In one week on the cortex project: **332 distinct lane-worktrees**, and **238 work-items resolved in 7 days** through the lanes. Of `/goal` runs that reached a terminal state, **~70% reached "achieved"** (119 of ~169). These are traceable numbers — but they're one person's practice on one set of projects, not a general benchmark.

To run it: `load_skill("goal-batch")` and start with 2–3 lanes. There's no cap, but nobody should meet the failure modes at width six on a first run.
