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

You've got several independent things to do, and doing them one at a time is the slow part — each `/goal` run is unattended, but you're still running them in a line. **`goal-batch` fans independent work out into parallel `/goal` lanes that can't collide — each its own git worktree + branch + tmux `/goal` session over a disjoint file set — then verifies and merges them for you.**

**In practice.** Three unrelated fixes across different corners of the repo, no shared files. Instead of a serial queue, say: *"run all this through goal-batch."* It proposes a lane split, you approve it, and the lanes run at once — then the orchestrating session re-runs the full suite itself after every merge and never trusts a lane's own "done."

**How to invoke.** `goal-batch` is a **skill**, invoked in natural language — "use the goal-batch skill and run this batch: …". A bare `/goal-batch` token does **not** load it; name it in prose. (A slash form works only if your app wires skills to slash commands.)

**Is it here?** Check the visible skills list for `goal-batch`. It also needs `git`, `tmux`, and the `amplifier` CLI on PATH — the tmux dependency is deliberate but blocks non-tmux users. If the skill or a dependency is missing, say what's needed and set it up on your go, never automatically.

**Running a batch (hard-won).**
- **Plan + a user-review gate BEFORE any lane launches.** You approve the lane split first; nothing spins up unreviewed.
- **Keep a hand lane-manifest** — lane → worktree → branch → goal → status. It's the recovery anchor if tmux crashes and you lose the panes.
- **Detect completion from GIT facts, not session status** — commits-since-base + clean tree + pushed. A killed pane is not "done"; session state lies.
- **Validate ONE lane end-to-end before going wide.**

**Not this** for bounded edits that each end in their own PR — that's `mass-change`. Pairs with `goalify` (author the stop-conditions) and the `ten-lane-highway` concept (the steady-state practice).
