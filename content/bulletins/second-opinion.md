---
id: second-opinion
category: bulletin
promoted: true
headline: "Get independent eyes on the work before a small doubt becomes a costly rework."
try_now:
  - "Use Second Opinion to have Astra and Fable independently review this work."
  - "Use Second Opinion to ask for fresh eyes on the design decisions in this session."
signals:
  on_event: session:start
  prompt_matches:
    - '\bsecond\s+opinion\b'
    - '\b(?:fresh\s+eyes|another\s+perspective)\b'
    - '\b(?:independent|multiple|several)\s+reviewers?\b'
    - '\b(?:have|ask|get)\b[^.?!]{0,55}\b(?:review(?:ed|ing)?\b[^.?!]{0,55}\b(?:this|my|the)\s+(?:work|design|plan|change)\b|(?:this|my|the)\s+(?:work|design|plan|change)\b[^.?!]{0,55}\breview(?:ed|ing)?\b)'
trigger: "session start, or the user wants independent feedback from one or more reviewers before acting on current work or a past session"
action: 'read_file("@wayfinder:content/bulletins/second-opinion.md")'
verified_at: 2026-09-09
provenance: "Second Opinion merged in microsoft/amplifier-bundle-skills PR #73 at f5b1bb1f5b0e5653f7a504a95bbd9ec0134d8e39; natural-language invocation verified from the published skill."
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
awkward edge is real or just fatigue. Ask Astra and Fable to review it
independently. You get the shared concern, the distinct concerns, and any real
disagreement with each reviewer's evidence still attached.

Use the **Second Opinion** skill in plain language:

- “Use Second Opinion to have Astra and Fable review this work independently.”
- “Use Second Opinion to get fresh eyes on the design decisions from yesterday's session.”
- “Use Second Opinion to ask several reviewers at once, with up to twenty running at once.”

One useful boundary: the reviewers assess the evidence they receive. A shared
finding is a signal to investigate, not a vote that makes it true. The report
keeps who said what, what they saw, and what was not covered.

For the full workflow, load **Second Opinion**. It can explain which reviewers
are available and ask a plain-language question when a requested reviewer is
ambiguous.