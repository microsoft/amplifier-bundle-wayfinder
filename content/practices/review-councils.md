---
id: review-councils
category: practice
headline: "Three review panels — code, design, product — that fan out to independent lenses, disagree on purpose, and hand back a synthesized verdict with dissent preserved."
try_now:
  - '/council <path>'
  - '/design-council <path>'
  - '/product-council <path>'
signals:
  prompt_matches:
    - '\b(/(design[- ]?|product[- ]?)?council|(design|product|code) council|review council|council review|multi[- ]?perspective (review|critique)|ship[- ]?gate)\b'
trigger: "the user wants a multi-perspective review or ranking gate on code, a design/UX, or a product decision — especially before committing to a direction"
action: 'read_file("@wayfinder:content/practices/review-councils.md")'
provenance: "council / design-council / product-council skills (announcements 2026-08)"
verified_at: 2026-08-19
---

# review councils — code, design, product

You shipped something that felt done — and a day later someone points at the obvious thing a fresh set of eyes would've caught before it went out. The trouble is that asking one AI "is this good?" usually gets you a way to say yes. A council is the fix: three review panels (code, design, product) that fan out to independent lenses, each writing its verdict *before* seeing the others', then synthesize — dissent kept, never averaged into mush. Each lens owns one question, so the objection you'd otherwise hit three weeks into build shows up now.

**In practice:** you've got a checkout redesign mostly settled and you're about to commit to the direction. You run `/design-council ./designs/checkout-flow.md` and get back a 7-lens adversarial read — hierarchy, edge-case states, accessibility, and so on — ranked, with the disagreements intact, as a named ship-gate you can actually act on before anyone writes code.

The three panels:

- `/council <path>` — code review (reuse, quality, efficiency).
- `/design-council <path>` — a 7-lens adversarial UX panel: multi-perspective critique, not one opinion.
- `/product-council <path>` — product-decision review: is the problem real, does anyone want it, what does it cost to land.

Each also has a `-here` variant (`/council-here`, `/design-council-here`, `/product-council-here`) that reviews the work in your current session instead of a path.

**How to invoke:** these are real user-invocable slash commands — the slash form is the intended way in (natural language like *"convene the design council on this mockup"* also works). **No install:** they ride in the standard skills bundle, so there's nothing to add ask-first — they're already available in this session. If a stripped-down app doesn't surface them, confirm the skills bundle is composed in (`amplifier bundle list`) or that the council skills appear in your skills list.

Two things to hold onto:

- **A verdict is advisory input to an owner decision, not an auto-decision.** Use it as a named ship-gate checkpoint and read it skeptically — a council is a reviewer, not the decider.
- **Pair with real-user evidence for UX calls.** Design and product councils are often run alongside simulated-user-research: the council ranks and reasons, the research supplies the observed evidence.
