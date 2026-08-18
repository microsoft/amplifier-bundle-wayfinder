---
id: goalify
category: practice
headline: "Turn the current task into an autonomous run — author a proper /goal stop-condition."
try_now:
  - 'load_skill("goalify")'
signals:
  prompt_matches:
    - '\b(goalify|stop[- ]?condition|turn (this|it) into (a )?goal)\b'
trigger: "the user wants to turn the current task into an autonomous run"
action: 'load_skill("goalify")'
provenance: "goalify skill"
---

# goalify — author a stop-condition

**Turn the task in front of you into something `/goal` can run to completion — a well-formed, lint-checked stop-condition.**

## Try it now

1. `load_skill("goalify")` — then say what "done" looks like.

## Why it matters

A vague goal either loops forever on ambiguity or accepts a shallow claim as success. `goalify` composes the condition from the current conversation and lints it against known termination-failure patterns before you commit to a run.

## More

- Pairs with `goal-batch` (run many goals as parallel lanes) and the `ten-lane-highway` concept (the steady-state practice).
