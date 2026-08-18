# offer catalog

The curated index: when you see the **trigger**, make the **offer** via the propose→show→ack→act loop, then run the **action** on ack. Add entries as new patterns earn their place.

## pinning  *(informational — the current bulletin)*
- **Trigger:** session start (once per session), or the user wonders which model/provider they're on.
- **Offer:** the current bulletin — provider pinning: named pin handles + role routing in `settings.yaml`.
- **Action:** unless `pinning` is in declines, read `wayfinder:content/bulletins/current.md` and lead with a 2-3 line summary of it, offering the detail. Never paste the whole bulletin unprompted.

## goal-batch
- **Trigger:** the user has 2+ independent, parallelizable tasks that won't collide.
- **Offer:** run them as parallel autonomous lanes — each its own worktree/branch/tmux `/goal` session, verified and merged for you.
- **Action:** on ack, `load_skill("goal-batch")`. *(Headless gotcha: a bare `/goal-batch` token does NOT load the skill — name it in prose, e.g. "use the goal-batch skill and run this batch: …".)*

## goalify
- **Trigger:** the user wants to turn the current task into an autonomous run.
- **Offer:** author a proper stop-condition/goal so `/goal` can run it to completion.
- **Action:** on ack, `load_skill("goalify")`.

## ten-lane-highway  *(concept)*
- **Trigger:** the user is curious about scaling parallel lanes.
- **Offer:** the thin concept note on the ~10-lane steady-state practice.
- **Action:** on ack, read `wayfinder:content/concepts/ten-lane-highway.md` (soft ref — load on demand).
