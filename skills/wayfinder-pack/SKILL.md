---
name: wayfinder-pack
description: >
  Author or refine a wayfinder content packet (a bulletin, practice, or concept
  offer) that surfaces through the wayfinder channel. Use when creating a new
  wayfinder pack/packet/offer, editing an existing one, adding an internal
  content pack, or when someone says "wayfinder-pack", "write a wayfinder
  offer", "add a packet to wayfinder", "make a wayfinder bulletin", or "author
  wayfinder content". Carries the packet contract (frontmatter + body shape),
  the authored-voice rules, install-awareness, and how to verify a packet in a
  DTU before shipping.
user-invocable: true
allowed-tools:
  - read_file
  - write_file
  - edit_file
  - glob
  - grep
  - bash
model_role: writing
---

# Authoring a wayfinder pack

A **wayfinder pack** is one markdown file — a *packet* — that surfaces to a user
through the wayfinder channel: a bulletin, a practice, or a concept. This skill
captures what a *good* one looks like, because a packet is not documentation —
it is **context handed to an assistant that renders it live, in the moment**.
Get the material and the intent right; trust the assistant to say it well.

The finished artifact: a packet file with correct frontmatter and a body in the
authored voice, whose commands are verified, whose signals fire on real user
phrasing, and which has been surfaced once in a DTU to confirm it renders.

## Inputs

- `$ARGUMENTS`: (Optional) The offer to author — a tool, workflow, command, or
  concept — and where it lives (built-in CLI, a skill, or a separate bundle).
  If absent, ask what the packet is for and what it needs to run.

## The one idea that governs everything

**A packet is context for the assistant, not final copy.** It loads into an
assistant's context and is rendered to the user live. So give *rich, accurate
material and clear intent* — do not script verbatim output, do not force a rigid
template, do not write anything that reads like data to be echoed. Good context
plus high-level guidance beats tight control of the words. Everything below
serves that idea.

## Steps

### 1. Establish what the offer is and what it needs

Before writing, pin down three things:

- **The outcome + mechanism**, in the user's terms — not vague jargon. Name the
  packet by *what it does for them and how*. (Lesson from real use: "pinning"
  was too vague; "switch models mid-conversation — pick the provider entry that
  fits the job" is the offer.)
- **The pain it removes** — the one-line frustration a reader will nod at.
- **What it needs to run** — one of: **built-in** (a CLI slash command, always
  present), a **skill** (present only if composed; invoked in natural language),
  or a **separate bundle** (must be installed). This decides the invocation and
  install-awareness lines later.

**Success criteria**: You can state the offer's outcome, its mechanism, the pain
it removes, and its install class in four sentences.

### 2. Verify the commands at authoring time

Never guess syntax. Confirm every command the packet will show, *now*, so the
packet always carries runnable actions:

- Built-in CLI commands → consult `app-cli:cli-expert` when available, or the
  installed CLI docs; run `--help` if needed.
- Skill invocation → check the visible skills list for the exact name.
- Bundle install → get the exact `amplifier bundle add …` / `uv tool install …`
  incantation.

Record what you verified and when — it becomes the `verified_at` and
`provenance` frontmatter.

**Rules**: If you cannot verify a command, do not invent it — say so in the body
and offer to fetch it. A packet that shows a wrong command is worse than one
that admits a gap.

**Success criteria**: Every command destined for the packet has been confirmed
against a real source, with the date and source noted.

### 3. Write the frontmatter

The hook derives the offer catalog from this frontmatter, so it is load-bearing,
not decoration. Match the field set of the sibling packets in `content/`:

```yaml
---
id: switch-models            # kebab-case, unique; names the outcome, not jargon
category: bulletin           # bulletin | practice | concept
promoted: true               # true = eligible to lead a session (rotation pool)
headline: "…"                # one line: outcome + why-you-care, in plain words
try_now:                     # exact, verified commands or NL invocations
  - "/provider"
  - "/provider use <name>"
signals:
  on_event: session:start    # optional; when the packet may lead
  prompt_matches:            # conservative, word-boundary regexes (see step 5)
    - '…'
trigger: "prose: when this offer is genuinely relevant to the user"
action: 'read_file("@wayfinder:content/<dir>/<file>.md")'   # authoritative body path
verified_at: 2026-08-19
provenance: "where the concept + commands came from"
---
```

The `action` is the **one authoritative way to show the packet body** — it may
point into another bundle's namespace (`@made-support:…`). Never write a packet
whose body can only be found by globbing; the `action` is how the assistant
fetches it verbatim.

**Success criteria**: Frontmatter parses, `id` is unique across `content/`,
`action` resolves to this file, and every `prompt_matches` regex compiles.

### 4. Write the body in the authored voice

Shape follows the point — most offers open the same way, but this is a guide,
not a form. Keep it skimmable and honest:

1. **Empathy/challenge line** the reader feels — the pain, so they care *why*
   this exists.
2. **What it is + why it helps**, in a line.
3. **An in-practice example** — a real "you're doing X, so you reach for this"
   scenario — *before* any how-to.
4. **How to run it** — the verified commands, or the natural-language way to
   invoke a skill. Never show an action without its command.
5. **Honest gotchas** and one deeper pointer, offered not dumped.

Voice: plain and concrete, short, opinionated (lead with the one thing worth
trying), honest about newness. A workflow packet that stitches several tools is
**open prose** — let the shape follow the point; don't wrap it in rigid headings.

**Invocation accuracy**: built-in slash commands are always available in the
app-CLI; **skills are invoked in natural language** ("use goalify to …"), with
the slash form working *only if the app wires it* — prefer the NL form. A
separate bundle must be installed first.

**Install-awareness**: state plainly what the packet needs, and if it is not
built-in, that installing is **ask-first, never automatic** — show the command,
wait for the user's go.

**Success criteria**: The body opens with a pain the reader recognizes, shows an
example before the how-to, carries only verified commands, is honest about what
must be installed, and reads like one person talking — not a filled-in template.

### 5. Get the signals right

`prompt_matches` is what lets a packet answer a directly-relevant question. Two
lessons from real misses:

- **Cover the verb stems.** `switch (models?)` does NOT match "switch**ing**
  models." Use stems: `switch(?:ing|ed)?\s+(?:models?|providers?)`.
- **Match user phrasing, conservatively.** Word-boundary anchors; avoid
  over-reaching (don't swallow "the" or unrelated topics). Test each regex
  against 3–4 real phrasings a user would type, and one that should NOT match.

**Success criteria**: Every `prompt_matches` regex matches the phrasings a real
user would type for this offer and rejects an unrelated one — verified, not
assumed.

### 6. Wire and place the packet

- Save under `content/<category-dir>/` (e.g. `content/bulletins/`,
  `content/practices/`, `content/concepts/`) so the hook discovers it.
- The catalog is **frontmatter-derived** — no separate registration needed; a
  new file with valid frontmatter becomes a menu item automatically, and
  deleting a file removes its item.
- **Internal/team packs** live in another bundle and are surfaced via
  wayfinder's `content_sources` config (a bundle-namespaced mention like
  `@made-support:content/wayfinder`) — the pack files still follow this same
  contract.
- Fix any static prose that names the old id if you renamed/merged a packet
  (`grep -rn '<old-id>' .` across `content/`, `context/`, `modules/`).

**Success criteria**: The file is in the right `content/` subdir, no dangling
references to a renamed/removed id remain, and (for an internal pack) the
`content_sources` wiring points at it.

### 7. Verify in a DTU before shipping

A packet is not done until it has rendered live. Mirror the working tree to the
standing DTU and surface the packet:

- Re-mirror + cache-clear (project convention): run the repo's mirror script,
  then clear the DTU's `@main` cache so the next run re-pulls
  (`rm -rf ~/.amplifier/cache/<repo>.git-*`), and reset rotation
  (`rm -f ~/.amplifier/wayfinder/surfaced.jsonl`) between checks.
- Surface it three ways and read the actual output:
  1. **Menu** — "what else can you help with?" → the item appears (or, if
     renamed, the new name and not the old).
  2. **Deep dive** — a first prompt naming the offer → the assistant runs the
     `action` (reads *this* file) and renders the body, including any merged
     section.
  3. **Signal** — a natural user phrasing → `prompt_matches` fires and summons
     the packet.
- For an isolated pass, delegate to `amplifier-tester:validator` with the DTU
  id and the checks above; it restores the environment as-found.

**Human checkpoint**: Present the rendered output and the packet before
committing — the user is the authority on voice and whether the offer "hits the
point."

**Success criteria**: The packet renders in the DTU via its own `action` (not a
guessed file search), its signals fire, and the user has confirmed the voice.

## The failure modes this skill exists to prevent

- **Template-shaped copy** the assistant echoes verbatim instead of rendering.
- **Vague item names** ("pinning") that hide the outcome.
- **Unverified commands** that ship wrong, or **guessed** skill/bundle syntax.
- **A body only findable by globbing** — always route delivery through `action`.
- **Signals that miss real phrasing** (verb-stem gaps) or over-match.
- **Silent auto-install** — installing anything is always ask-first.
- **"Looks fine" without a DTU render** — a packet unproven live is unproven.
