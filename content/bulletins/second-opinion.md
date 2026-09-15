---
id: second-opinion
category: bulletin
promoted: true
headline: "Get independent eyes on the work before a small doubt becomes a costly rework."
try_now:
  - "Use Second Opinion for an independent review of this work. Ask me which configured reviewers to use before launching any review."
signals:
  on_event: session:start
  prompt_matches:
    - '\bsecond(?:[-\s]+)opinion\b'
    # Natural review requests must not override an explicitly named council.
    - '^(?![^.?!]*\bcouncil\b)[^.?!]*\b(?:fresh\s+eyes|another\s+perspective)\b'
    - '^(?![^.?!]*\bcouncil\b)[^.?!]*\bindependent\s+reviewers?\b'
trigger: "session start, or the user wants independent feedback from one or more reviewers before acting on current work or a past session"
action: 'read_file("@wayfinder:content/bulletins/second-opinion.md")'
verified_at: 2026-09-15
provenance: "Second Opinion merged in microsoft/amplifier-bundle-skills PR #73 at f5b1bb1f5b0e5653f7a504a95bbd9ec0134d8e39; natural-language invocation rechecked against https://github.com/microsoft/amplifier-bundle-skills/blob/f5b1bb1f5b0e5653f7a504a95bbd9ec0134d8e39/skills/second-opinion/SKILL.md."
---

# Second Opinion

Second Opinion is now in the Skills bundle. A session that has that bundle can
use it; a session that does not recognize it yet needs its usual bundle refresh.
This bulletin does not install or change anything for you.

You have spent long enough staring at a change that every decision now looks
inevitable. That is exactly when a small assumption slips through. Second
Opinion brings in one independent reviewer, or several, to look at the same
work without inheriting one another's conclusions. It is useful before a
commit, after a design choice that still feels wobbly, or when a past session
needs a fresh reading rather than another round of self-justification.

In practice: you have a change ready to send, but you cannot tell whether the
awkward edge is real or just fatigue. Use Second Opinion to independently
review it. If you do not name reviewers, ask it to confirm which configured
reviewers to use before launching a review.

Use the **Second Opinion** skill in plain language:

- “Use Second Opinion for an independent review of this work. Ask me which configured reviewers to use before launching any review.”
- “Use Second Opinion to get fresh eyes on the design decisions from yesterday's session.”
- “Use Second Opinion to have Astra and Fable review this work independently, if those names are configured here.”
- “Use Second Opinion to ask several configured reviewers, with up to twenty running at once.”

“Astra” and “Fable” are conditional examples, not verified universal aliases or
defaults. Asking for up to twenty means at most twenty reviewer delegations
running at once; it is not the default or a promise that twenty reviewers are
available.

For multiple reviewers, each gets the same bounded evidence brief without
another reviewer's response. The skill can review current work or an exactly
identified past session, and the report keeps each finding, its evidence, and
what was not covered. Agreement is a signal to investigate, not a vote that
makes a finding true.

For the full workflow, load **Second Opinion**. It can check a configured
reviewer selection and ask a plain-language question when the choice is missing
or ambiguous. Configuration selection is not proof of an account, model
availability, routing, or actual execution.