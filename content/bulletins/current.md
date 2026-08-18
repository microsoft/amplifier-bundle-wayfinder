# Current bulletin — provider pinning

**Pin this conversation to a specific engine by handle; unpin to go back to routing.**

## Try it now (interactive session)

1. `/provider` — list your handles (11 configured: `opus`, `haiku`, `fable`, local boxes, more); ★ marks the default
2. `/provider use haiku` — pin THIS conversation to a cheap engine for a bulk stretch
3. `/provider auto` — unpin; back to default routing

## Why it matters

Pins are scoped: they steer only your top-level conversation. Sub-agents, model-role routing, and `/goal` keep using the configured routing matrix — delegated work stays on the right engines while you steer the chat. Pins are per-session and never touch `settings.yaml`.

## Gotchas

- `use` takes the handle **id** from `settings.yaml` (e.g. `haiku`), not a model name.
- Switching vendors mid-conversation is refused — start fresh instead: `amplifier run -p <name>`.
- Unpin is `auto` (not clear/off). The anthropic pins degrade under overload (sonnet/haiku fallback + retry) instead of erroring.

## More

- From the shell: `amplifier provider list` (handles), `amplifier provider test` (key check), `amplifier run -p <name>` (new session on a handle).
- Deeper `/provider` questions → offer to pull in `app-cli:cli-expert`.

*Commands verified against the installed CLI's PROVIDER_PINNING.md (2026-08-18). Model-initiated pinning was intentionally deferred — user-initiated only.*
