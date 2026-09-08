---
id: memory-bundle
category: practice
promoted: true
headline: "Amplifier forgets you between sessions. This add-on bundle fixes that — it keeps your standing preferences in your own words and loads them into every new session."
try_now:
  - "/memory"
  - "/remember always keep replies short and lead with the command"
  - "amplifier-memory init"
signals:
  prompt_matches:
    - '(?<![\w/])/(?:remember|memory)\b|\bamplifier-memory\b|\bmemory[- ]bundle\b'
    - '\b(?:remember|memoriz(?:e|ing)|memoris(?:e|ing))\b[\w ,-]{0,25}\b(?:my|how i|preferences?|standing)\b'
    - '\bkeeps? forgetting\b[\w ,-]{0,25}\b(?:my|how i|what i|that i)\b|\bforget(?:s|ting)? (?:my|how i)\b'
    - '\b(?:re-?explain(?:ing)?|tell(?:ing)? (?:it|you) (?:the same|again))\b[\w ,-]{0,60}\b(?:every|each|session)\b|\b(?:preferences?|instructions?)\b[\w ,-]{0,25}\b(?:across|between|persist\w*|surviv\w*)\s+sessions?\b'
    - '\b(?:tell me about|what(?:s| is| are)|how does|explain)\b[\w ,-]{0,15}\bmemor(?:y|ies)\b[\w ,-]{0,30}\b(?:bundle|preferences?|amplifier|assistant|sessions?|across|between)\b'
trigger: "the user is tired of restating how they work, wants the assistant to carry preferences between sessions, or asks about /remember, /memory or the memory bundle"
action: 'read_file("@wayfinder:content/practices/memory-bundle.md")'
verified_at: 2026-09-07
provenance: "Ran end-to-end on a real device 2026-09-07 against microsoft/amplifier-bundle-memory@main: bundle add --app, uv tool install, init (interactive), doctor, update, service install/status, --home on the verbs, /remember and /memory in a live session. Cost figure is a measured nightly pass (30 model calls on a small fast model). Configuration keys quoted from the repo's own frozen contracts (store.v3, session.v4, cli.v3)."
---

# memory — standing preferences that survive the session

You told it yesterday to keep replies short. And the day before. Out of the box Amplifier starts every session knowing nothing about how you work — your settings carry your *configuration*, not your *preferences*. **This is a separate bundle you install once. It gives Amplifier a small file of your standing preferences and loads it into every session automatically — so you say a thing once, not once a week.**

The rule that matters: **nothing is remembered unless you said it, and nothing is written unless you agree.** Each memory is one line in your own words, and it carries the sentence you actually typed as its receipt — so when it shapes a reply, you can see exactly what it came from. No inferred personality, no silent profile.

**In practice.** It's the third time this week you've asked for the command first and the prose after. Overnight, the bundle reads *your own* sessions and proposes a memory — with your sentence quoted underneath. Next morning `/memory` shows it waiting; you accept it, and from then on every session starts already knowing. Decline it instead and it's gone for good — a reworded version of the same idea won't come back.

**What it needs.** Not built-in — a separate bundle, installed once:

```
amplifier bundle add 'git+https://github.com/microsoft/amplifier-bundle-memory@main#subdirectory=behaviors/memory-session.yaml' --app
uv tool install git+https://github.com/microsoft/amplifier-bundle-memory@main
amplifier-memory init
```

`init` asks you a single question — the one thing you always end up telling an assistant — and that becomes your first memory. It also sets up the nightly pass. After that: `/remember <text>` to save one on the spot, `/memory` to review, edit or forget, and `amplifier-memory doctor` to see everything at a glance. An explicit ask to install or run it authorizes that here and now; if I raise it as an optional next step instead, I'll show the exact command and wait for your go.

**It's yours, and it's a file.** The store is a plain git repo at `~/.amplifier-memory` — open it, edit it, diff it, back it up. Memories travel in the prompt like anything else you type.

**One store, or several.** Every command takes `--home`, so a project or a client can keep its own collection (`amplifier-memory init --home ~/.amplifier-memory-acme`), with its own file and its own timer. A bundle can name the store its sessions use. `enabled: false` takes a store out of your sessions — nothing injected, nothing written, `/remember` and `/memory` not offered; its timer is separate, so remove that too if you want the nightly pass stopped.

**Gotchas.**
- **Only sessions with a human in them are mined.** Agent lanes, recipes and automation runs still *read* your memories — the work is still yours — but they can't write them and are never mined, so the assistant doesn't quietly learn from itself. Launchers declare this with one environment variable.
- **The nightly pass costs money, so pick the model.** A pass is about 30 model calls, not one — `doctor` names the model it used and the last run's call count.
- **There's a hard cap (200 lines).** Memory can't quietly grow into a context tax — when it's full it says so instead of trimming behind your back.
- **It's new.** Days old, running on a handful of machines. Every promise it makes has an automated check behind it, but you'd be an early user.

**More.** `amplifier-memory update` keeps the CLI, the bundle and the store in step and tells you when they drift. Curious what a specific memory is doing in your session? Ask why it's there — each one traces back to the sentence that created it.
