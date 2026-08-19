---
id: pinning
category: bulletin
headline: "Switch which model answers you mid-conversation — same vendor, no lost session."
try_now:
  - "/provider"
  - "/provider use haiku"
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

**Switch which model and configuration answers you, mid-conversation, without losing the session — pin a configured provider *entry* by its `id`.**

## Try it now (interactive session)

1. `/provider` — list your configured provider entries (each is one account + one model, named by `id`); ★ marks the default
2. `/provider use haiku` — pin THIS conversation to that entry (e.g. a cheaper model) for a bulk stretch
3. `/provider auto` — unpin; back to your default (the lowest-`priority` entry)

## Why it matters

A pin changes which model/config answers your **top-level conversation** — no restart, no lost history. It's session-only and never touches `settings.yaml`. Sub-agents, model-role routing, and `/goal` are unaffected — they keep using your configuration, so delegated work stays on its own models while you steer the chat.

## Gotchas

- **Same vendor only.** You can move Anthropic→Anthropic or OpenAI→OpenAI, but not across vendors mid-conversation — your history carries vendor-specific data the other vendor's API rejects. Cross-vendor means a new session: `amplifier run -p <name>`.
- `use` takes the entry **`id`** from `settings.yaml` (e.g. `haiku`), not a model name.
- Unpin is `auto` (not clear/off).

## More

- From the shell: `amplifier provider list` (entries), `amplifier provider test` (key check), `amplifier run -p <name>` (new session on an entry).
- Deeper `/provider` questions → offer `app-cli:cli-expert` if it's available; otherwise point at the amplifier-app-cli `docs/PROVIDER_PINNING.md`.

*Concept accurate to amplifier-foundation: a **provider** is the vendor backend (anthropic/openai/gemini); a **provider entry** is one configured account+model+config in `settings.yaml`; pinning switches which entry answers, within the same vendor. Terms: "provider entry," "id," "model," "vendor" — not "engine"/"handle." Commands verified against the installed CLI (2026-08-19). User-initiated only.*
