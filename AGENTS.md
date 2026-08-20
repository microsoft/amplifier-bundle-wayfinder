# AGENTS.md — working in the wayfinder repo

Conventions for anyone (human or agent) changing this repo. Read `VISION.md`
first — it says *why* wayfinder exists (attention is the scarce resource;
awareness, not capability). This file says *how* to work here without breaking
that.

## What this repo is

A curated in-session guide for Amplifier. Authored markdown + one small Python
hook (`modules/hooks-wayfinder`) wired onto foundation's existing tools. It
surfaces the one thing worth a reader's attention and offers capabilities they
already have — showing the exact command first, acting only on an explicit
"sure."

## The golden rule: a packet is context for the assistant, not final copy

Content files load into an assistant's context and are rendered to the user
live. Give **rich, accurate material and clear intent** — never script verbatim
output, never force a rigid template. If a file reads like data to be echoed,
loosen it. This governs everything under `content/` and `context/`.

## Where things live

| Path | What it is | When it loads |
|------|-----------|---------------|
| `content/bulletins/`, `content/practices/`, `content/concepts/` | Packets (offers). Frontmatter + authored body. | Body on-demand via each packet's `action`; catalog derived from frontmatter |
| `context/wayfinder-voice.md`, `context/propose-and-ack.md` | Always-on channel (voice register + consent floor) — just two files | Every session — keep the pair lean; each < 1000 tok, and prefer smaller |
| `modules/hooks-wayfinder/` | The hook: session:start surfacing, frontmatter-derived catalog, decline-filter, prompt signals | Session lifetime |
| `behaviors/wayfinder.yaml` | Wires context + hook + the authoring skill | Composition |
| `skills/wayfinder-pack/` | The authoring skill — how to write a good packet | On demand (`/wayfinder-pack`) |

## Authoring or editing a packet

**Use the `wayfinder-pack` skill** (`/wayfinder-pack`, or just ask) — it carries
the full contract. In short: name the offer by outcome+mechanism (not vague
jargon); open with the pain, then an in-practice example *before* any how-to;
verify every command at authoring time; be honest about what must be installed
(ask-first, never auto); route body delivery through the packet's `action`;
cover verb stems in `prompt_matches` (`switch(?:ing|ed)?…`, not `switch …`).

The offer catalog is **frontmatter-derived** — a new file with valid frontmatter
becomes a menu item automatically; deleting one removes it. If you rename or
merge a packet, grep for the old id across `content/`, `context/`, `modules/`
and fix every static reference.

## Always-on token budget is sacred

Anything in `context.include` (behavior YAML) lands in every session's system
prompt. Keep each such file < 500 tokens; the whole always-on channel is
~1.1–1.6K on purpose. Heavy material goes on-demand (packet bodies via `action`,
the authoring skill body, soft-referenced concepts) — never always-on.

## Verify in a DTU before shipping

A packet or hook change is not done until it renders live. The standing test
loop (see `SCRATCH.md` in the workspace for the live instance ids):

1. Edit locally.
2. Re-mirror the working tree to the DTU's Gitea (`remirror-wayfinder.sh`).
3. Clear the DTU's `@main` cache so the next run re-pulls:
   `amplifier-digital-twin exec <dtu> -- bash -c 'rm -rf ~/.amplifier/cache/wayfinder.git-*'`
   (reset rotation between checks: `rm -f ~/.amplifier/wayfinder/surfaced.jsonl`).
4. Run a session and read the *actual* output — menu, deep-dive (does it run the
   `action`?), and a signal phrasing.
5. For an isolated pass, delegate to `amplifier-tester:validator`.

Touching hook Python? Run `python_check` and keep it clean before committing.

## Validate the repo

Before a PR, re-run `foundation:recipes/validate-bundle-repo.yaml` on the repo.
It also auto-regenerates a stale `bundle.dot` / `bundle.png`. Fix confirmed
errors; warnings need a justification.

## Guardrails that are non-negotiable

- **propose → show → ack → act** on every write/execute. Never auto-act, never
  auto-install. Show the exact command before asking.
- **wayfinder points, never absorbs** — don't re-implement another domain here;
  point at where it lives.
- **Verified commands only** — never guess syntax; confirm at authoring time.
- **Ephemeral hook injections** — the hook must not accumulate context in message
  history.

## Commits

Conventional commits, with the Amplifier co-author footer:

```
🤖 Generated with [Amplifier](https://github.com/microsoft/amplifier)

Co-Authored-By: Amplifier <240397093+microsoft-amplifier@users.noreply.github.com>
```
