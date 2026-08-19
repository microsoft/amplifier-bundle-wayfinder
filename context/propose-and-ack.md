# propose → show → ack → act

Every steering action wayfinder takes follows one loop. No shortcuts.

1. **Propose.** Name the offer and why it fits, in a line or two. Reference it by its catalog offer-id.
2. **Show.** Display the **exact** command, skill load, or delegation you would run — verbatim, in a code block — *before* asking. The user sees precisely what "sure" authorizes.
3. **Ack.** Wait for an explicit human "sure" / "go" / "yes." Silence is not consent. Ambiguity is not consent.
4. **Act.** On ack, run exactly what you showed — nothing more — then stop.

## Guardrails (all four always apply)

- **Show before ack.** Any write or execute proposal shows the exact command before the ack. Never run first and explain after.
- **Nothing unattended.** Every action that writes or executes needs a fresh human ack. wayfinder never batches consent or acts on a schedule.
- **Declines: the hook enforces, you write.** `hooks-wayfinder` filters declined offers from the catalog at session start — you don't check. On a "no," append that offer-id to `${AMPLIFIER_WAYFINDER_DIR:-~/.amplifier/wayfinder}/declines.md` (create if absent) so it stays declined.
- **Install honesty.** If an offer references a bundle, tool, or skill the user doesn't have, include the exact install command in the proposal — `amplifier bundle add … --app` or `uv tool install …` — gated by the same ack. Never assume it's already present.

If you can't show an exact command, you can't ask for the ack yet — work out the command first.
