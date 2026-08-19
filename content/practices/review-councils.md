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

**One packet, three panels. Each convenes orthogonal review lenses that write their verdicts before seeing each other's, then synthesize — dissent kept, never averaged away.** Zero install; already in the skills bundle.

## Try it now

1. `/council <path>` — code review (reuse, quality, efficiency).
2. `/design-council <path>` — a 7-lens adversarial UX panel: multi-perspective critique, not one opinion.
3. `/product-council <path>` — product-decision review: is the problem real, does anyone want it, what does it cost to land.

## Why it matters

Ask one AI whether your plan is good and it usually finds a way to say yes. A panel where each lens owns one question surfaces the objection you'd otherwise hit three weeks in.

## Gotchas

- **A verdict is advisory input to an owner decision, not an auto-decision.** Use it as a named ship-gate checkpoint and read it skeptically — a council is a reviewer, not the decider.
- **Pair with real-user evidence for UX calls.** Design/product councils are often run alongside simulated-user-research: the council ranks and reasons, the research supplies observed evidence.

## More

- Each has a `-here` variant (`/council-here`, `/design-council-here`, `/product-council-here`) that reviews the work in your current session instead of a path.
