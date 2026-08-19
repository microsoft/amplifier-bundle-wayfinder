---
id: about-wayfinder
category: concept
headline: "What wayfinder is and what it can point you to — the orienting overview."
try_now:
  - '(ask) "what can you help with?"'
signals:
  prompt_matches:
    - '\bwhat (is|are|does) (the )?wayfinder\b'
    - '\bwhat can (you|wayfinder) (do|help)\b'
    - '\bwho are you\b'
    - '\bhow (do|can|should) i (use (this|it|wayfinder|here)|get ?started)\b'
trigger: "the user is orienting — asks what wayfinder is, what it can help with, who you are, how to use it, or how to get started"
action: 'read_file("@wayfinder:content/concepts/about-wayfinder.md")'
verified_at: 2026-08-19
provenance: "self-describing from wayfinder's own bundle.md, wayfinder-voice.md, propose-and-ack.md, and the live content/** catalog"
---

# About wayfinder

**wayfinder is an authored awareness + propose-and-ack steering channel: it points you to the workflow, tool, or bundle that fits — it never does the work itself.** It surfaces the offer, shows the exact command, and you decide. It points; it never absorbs.

## What it helps with

A small, curated menu — derived live from `content/`, with anything you've declined already filtered out. The categories:

1. **Bulletins** — the one current thing worth knowing. Live: switch models mid-conversation (`/provider use <name>`).
2. **Practices** — a workflow you can run now. Live: `goal-batch` (parallel autonomous lanes).
3. **Concepts** — a thin note plus the real source. Live: `ten-lane-highway` (the steady-state parallel practice).

Pro-tips ride the same rails when there are any. The menu is small on purpose — curated, not a feed.

## How to use it

- **Offers are ack-gated.** Say "yes" / "go" to run the shown command; ignore it and nothing happens. Nothing runs unattended.
- **Say "no" once.** A declined offer is remembered and never re-offered.
- **Ask anytime.** "what can you help with?" re-surfaces the menu.

## More

- The voice and the propose→show→ack→act loop it follows live in `context/wayfinder-voice.md` and `context/propose-and-ack.md`. wayfinder owns the *communication* about capabilities — never the capabilities themselves.
