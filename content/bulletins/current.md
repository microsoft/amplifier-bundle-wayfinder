# Current bulletin — provider pinning

*One session, many engines. Pin the one you want; let roles handle the rest.*

## What it is

Your `~/.amplifier/settings.yaml` defines **named providers you pin to by handle** — 11 right now: `opus-4.8`, `opus`, `sonnet`, `openai`, `gemini`, `ghcp`, `qwen-3.6`, `azure-openai`, `ornith`, `haiku`, `fable`. Each is a real engine with its own model and priority. You switch the active one mid-session by its handle (the app-CLI's `/provider` command — for exact syntax, ask `app-cli:cli-expert`).

Underneath sits the **routing matrix**. Agents request an abstract *role* — `general`, `fast`, `coding`, `reasoning`, and 9 more (13 total) — and the active matrix (`routing.matrix: anthropic`) maps each role to a concrete model with glob patterns: `reasoning → claude-opus-*`, `fast → claude-haiku-*`, `coding → claude-sonnet-*`.

## Why it matters

**One rule ties the two layers together: a defined model role wins; a pinned provider is the fallback.** Roles keep the common case hands-off — the matrix auto-picks per task — while a pin is your deliberate override when you want a specific engine for cost, capability, or availability.

Two things worth knowing:

- **Local models are first-class pins**, right alongside the frontier ones — `ornith` (a LAN box) and `qwen-3.6` (a local gguf) sit in the same list.
- **Pins degrade instead of failing** — the anthropic pins carry fallback-on-overload with sonnet/haiku fallbacks and retry, so an overloaded pin steps down rather than erroring out.

## One thing to try

Look up. Every session already prints its active routing matrix and roles — the live map your delegations use right now. Then pin a cheaper engine for a bulk stretch and pin back.

*Scope: user-initiated pinning; model-initiated pinning was intentionally deferred. No verified per-engine usage breakdown here — this describes the setup, not how often each pin is used.*
