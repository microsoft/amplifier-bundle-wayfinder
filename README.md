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

## Contributing

> [!NOTE]
> This project is not currently accepting external contributions, but we're actively working toward opening this up. We value community input and look forward to collaborating in the future. For now, feel free to fork and experiment!

Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit [Contributor License Agreements](https://cla.opensource.microsoft.com).

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft
trademarks or logos is subject to and must follow
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.
