---
id: goal-batch
category: practice
promoted: true
headline: "Run 2+ independent tasks as parallel autonomous lanes — each its own worktree/branch/tmux /goal session, verified and merged for you."
try_now:
  - 'load_skill("goal-batch")'
signals:
  prompt_matches:
    - '\b(goal[- ]?batch|parallel lanes?|run .* in parallel)\b'
trigger: "the user has 2+ independent, parallelizable tasks that won't collide"
action: 'load_skill("goal-batch")'
provenance: "goal-batch skill + ten-lane-highway practice"
---

# goal-batch — parallel autonomous lanes

**Fan independent work out into parallel `/goal` lanes that can't collide, verified and merged for you.**

## Try it now

1. `load_skill("goal-batch")` — then describe the batch in prose.

## Why it matters

Each lane is its own git worktree + branch + tmux `/goal` session over a disjoint file set. Nothing launches until you approve the lane split; the orchestrating session re-runs the full suite itself after every merge and never trusts a lane's own "done."

## Gotchas

- A bare `/goal-batch` token does **not** load the skill. Name it in prose: "use the goal-batch skill and run this batch: …".
- Not for bounded edits that each end in their own PR — that's `mass-change`.

## Running a batch (hard-won)

- **Plan + a user-review gate BEFORE any lane launches.** You approve the lane split first; nothing spins up unreviewed.
- **Keep a hand lane-manifest** — lane → worktree → branch → goal → status. It's the recovery anchor if tmux crashes and you lose the panes.
- **Detect completion from GIT facts, not session status** — commits-since-base + clean tree + pushed. A killed pane is not "done"; session state lies.
- **Validate ONE lane before going wide.** The tmux dependency is deliberate but blocks non-tmux users — prove a single lane runs end-to-end first.

## More

- Requires `git`, `tmux`, and the `amplifier` CLI on PATH. Pairs with `goalify` (author the stop-conditions) and the `ten-lane-highway` concept (the steady-state practice).
