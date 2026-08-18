# wayfinder

A curated in-session guide for Amplifier. It does two small, specific things:

1. **Surfaces one authored bulletin** — the single thing worth your attention right now, in one honest voice (not a changelog feed).
2. **Offers capabilities you already have** — when the conversation hits a known trigger, it proposes a next step, **shows you the exact command first**, and acts only on your "sure." Nothing runs unattended.

wayfinder **points; it never absorbs.** It owns the *communication* about what's new and possible — the capabilities themselves stay where they live (skills load by name, app-CLI questions route to `app-cli:cli-expert`, concepts get a thin note and a pointer to the real source).

## How it's built (Ring 0)

Zero new Python. wayfinder is authored markdown + behavioral guidance wired onto foundation's existing tools (filesystem, bash, delegate, load_skill). Everything it *does* comes from a tiny always-on channel; everything it *can do* comes from foundation.

Always-on content (kept deliberately small, ~1.6K tokens total):

- `context/wayfinder-voice.md` — the one-voice principle
- `context/propose-and-ack.md` — the propose→show→ack→act protocol + guardrails
- `context/offer-catalog.md` — the curated trigger→offer→action index
- `content/bulletins/current.md` — the current authored bulletin (Brian edits this)

On-demand (soft-referenced, not always loaded):

- `content/concepts/ten-lane-highway.md` — a thin concept note, read only when offered

## The ring model

wayfinder widens only as each ring proves out:

- **Ring 0 — Brian.** The thinnest end-to-end thing, daily-driven by one person (this).
- **Ring 1 — observed testers.** A small group. Deterministic firing (a `hooks-wayfinder` module) and enforced decline-memory become candidates here.
- **Ring 2 — public.** Team distribution / public bundle.

## Install

**Run it as its own bundle** (isolated, easy to toggle):

```bash
amplifier run --bundle "file:///path/to/wayfinder/bundle.md" "hello — what are you?"
```

**Or compose the behavior into your default bundle** so it's present in every session — add to that bundle's `includes:`:

```yaml
includes:
  - bundle: wayfinder:behaviors/wayfinder
```

**Later (Ring 1+), install it into the app** the way other behaviors ship:

```bash
amplifier bundle add git+https://github.com/…/wayfinder@main#subdirectory=behaviors/wayfinder.yaml --app
```

(App-CLI auto-compose — like goal/notify — is a separate change in that repo, a later ring. wayfinder itself is app-agnostic.)

## Runtime state

Decline-memory (the "don't re-offer this" log) lives per-user, outside the repo, so it survives an ephemeral workspace:

```
${AMPLIFIER_WAYFINDER_DIR:-~/.amplifier/wayfinder}/declines.md
```

Set `AMPLIFIER_WAYFINDER_DIR` to relocate it. wayfinder reads this file at session start and appends an offer-id whenever you decline that offer.
