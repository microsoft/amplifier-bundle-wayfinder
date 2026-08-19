---
id: goalify
category: practice
promoted: true
headline: "Turn the current task into an autonomous run — author a proper /goal stop-condition."
try_now:
  - 'use goalify to turn this into a /goal condition'
signals:
  prompt_matches:
    - '\b(goalify|stop[- ]?condition|turn (this|it) into (a )?goal)\b'
trigger: "the user wants to turn the current task into an autonomous run"
action: 'read_file("@wayfinder:content/practices/goalify.md")'
provenance: "goalify skill"
---

# goalify — author a stop-condition

You know you want to hand this off to `/goal`, but you're not sure how to word the condition so it actually holds — vague conditions either loop forever on ambiguity or wave through a shallow claim as success. **`goalify` writes the condition for you: it composes a well-formed stop-condition from what you're already doing and lint-checks it against known termination-failure patterns before you commit to a run.**

**In practice.** You've spent twenty minutes narrowing down what "finished" means for a refactor, and now you want it to run unattended. Rather than hand-crafting the `/goal` wording yourself, say: *"use goalify to turn this into a goal condition."* It reads the conversation, drafts the condition, flags the weak spots (no measurable end state, no transcript-visible check), and hands you something ready to run.

**How to invoke.** `goalify` is a **skill**, so you invoke it in natural language — "use goalify to tighten this into a goal," or just "goalify this." (The slash form `/goalify` works only if your app wires skills to slash commands; the app-CLI doesn't guarantee it, so prefer the natural-language ask.)

**Is it here?** Skills are per-session — check the visible skills list for `goalify`. If it's there, just ask for it in prose. If it isn't, the bundle that provides it isn't composed into this session; I can identify it and add it on your go — installing is a state change, so never automatically, always ask first.

**The ladder (validated).** Don't jump straight to a batch. `goalify` the condition → prove it on ONE `/goal` run → look at what the evaluator actually accepted → THEN scale to a `goal-batch`. A condition that hasn't survived one real run isn't ready to be fanned across lanes. Pairs with `goal-batch` (run many goals as parallel lanes) and the `ten-lane-highway` concept (the steady-state practice).
