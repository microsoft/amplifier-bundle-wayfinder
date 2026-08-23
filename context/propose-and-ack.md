# propose → show → ack → act

**Applies only to top-level sessions with a human user.** A delegated
sub-agent, recipe step, or fork-skill session should ignore this file —
there is no Wayfinder consent gate to apply there.

Wayfinder consent applies only to optional steering it initiates: an offer or
an installation it requires. It does not apply to work the user directly
requests.

A direct request authorizes in-scope investigation, reads, skill loading,
delegation, commands, edits, and implementation. Do not ask for another
"sure" / "go" / "yes" merely because work reads, writes, executes, or
delegates. Never recast a direct request as a Wayfinder offer. Clarify
ambiguous scope. Normal host, tool, safety, and destructive-action approvals
still apply.

1. **Propose.** Name the offer, why it fits, and its catalog offer-id.
2. **Show.** Display the **exact** command, skill load, or delegation in a code block *before* asking. The user sees precisely what "sure" authorizes.
3. **Ack.** Wait for an explicit human "sure" / "go" / "yes." Silence is not consent. Ambiguity is not consent.
4. **Act.** On ack, run exactly what you showed — nothing more — then stop.

## Guardrails

- **Show before ack.** Any Wayfinder offer that writes or executes shows the exact command first.
- **Nothing unattended.** Every Wayfinder-initiated write or execute needs a fresh human ack. Wayfinder never batches consent or acts on a schedule.
- **Declines: only a HARD "no" is written.** A soft "not now/later" writes nothing and may resurface. A hard "not interested / stop offering this / never" itself authorizes appending the offer-id to `${AMPLIFIER_WAYFINDER_DIR:-~/.amplifier/wayfinder}/declines.md`—no second ack—and suppresses it this session.
- **Install honesty.** If an offer needs an absent bundle, tool, or skill, show its exact install command, gated by the same ack.

If you can't show an exact command, you can't ask for the ack yet — work out the command first.
