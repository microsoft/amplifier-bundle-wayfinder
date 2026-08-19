---
id: pinning
category: bulletin
promoted: true
headline: "The right model for the job — you're in control, mid-conversation, no lost session."
try_now:
  - "/provider"
  - "/provider use <name>"
  - "/provider auto"
signals:
  on_event: session:start
  prompt_matches:
    - '\b(/provider|pin(ned|ning)?|switch (models?|providers?)|which (model|provider|engine))\b'
trigger: "session start, or the user wonders which model/provider they're on, or wants to switch models"
action: 'read_file("@wayfinder:content/bulletins/current.md")'
verified_at: 2026-08-19
provenance: "concept from amplifier-foundation (PROVIDER_CONTRACT, routing-matrix); commands from installed CLI docs/PROVIDER_PINNING.md"
---

# Current bulletin — provider pinning

Waiting on a top-tier model to grind through busywork a cheap, fast one could finish in a fraction of the time — and cost? You don't have to sit through it. **Pin a configured provider *entry* by its `id`, mid-conversation, and change which model answers your top-level chat — no restart, no lost history.** More capable models cost more and run slower; pinning lets you pick that trade-off per conversation instead of committing to one for the whole session.

*Prerequisite: you need more than one provider entry configured in the same family — pinning switches between entries you've already set up, so if there's only one there's nothing to switch to. Add entries with `amplifier provider` from the shell.*

**In practice.** You've been chewing on a hard problem with a heavy, capable entry, and the work turns to a big batch of routine edits or a wide exploration sweep. Pin a lighter, faster, cheaper entry, rip through it, then `/provider auto` back to your default — same conversation, a fraction of the cost and the wait.

**How to run it.** This is BUILT-IN — the `/provider` commands are always here in an interactive app-CLI session, nothing to install:

- `/provider` — list your configured entries (each is one account + one model, named by `id`); ★ marks the default.
- `/provider use <name>` — pin THIS conversation to one of those entries (reach for a lighter/cheaper one for a bulk stretch).
- `/provider auto` — unpin; back to your default (the lowest-`priority` entry).

Match the entry to the work, per conversation — a heavier, most-capable entry for hard reasoning; a balanced one for day-to-day; a light, fast, cheap one for utility, bulk, mass-parallel, or exploration-heavy stretches. A pin only steers your **top-level conversation** — sub-agents, model-role routing, and `/goal` keep their own models, so delegated work stays on its own tier while you steer the chat. The clock and the billing account both feel it.

**Gotchas.**
- **Same vendor only.** You can pin among entries from the same vendor, but not across vendors mid-conversation — your history carries vendor-specific data the other vendor's API rejects. Cross-vendor means a new session: `amplifier run -p <name>`.
- `use` takes the entry **`id`** you set in `settings.yaml`, not a model name. Unpin is `auto` (not clear/off). A pin is session-only and never touches `settings.yaml`.

**More.** From the shell: `amplifier provider list` (entries), `amplifier provider test` (key check), `amplifier run -p <name>` (new session on an entry). Deeper `/provider` questions → offer `app-cli:cli-expert` if it's available; otherwise point at the amplifier-app-cli `docs/PROVIDER_PINNING.md`.

*Concept accurate to amplifier-foundation: a **provider** is the vendor backend; a **provider entry** is one configured account+model+config in `settings.yaml`; pinning switches which entry answers, within the same vendor. Say "provider entry," "id," "model," "vendor" — not "engine"/"handle." Commands verified against the installed CLI (2026-08-19). User-initiated only.*
