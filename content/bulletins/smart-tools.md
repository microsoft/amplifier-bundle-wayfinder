---
id: smart-tools
category: bulletin
promoted: true
headline: "Package a workflow as a tool any agent can use. Plain code paths run with no model; smart paths call AI underneath."
try_now:
  - "uv tool install git+https://github.com/microsoft/amplifier-smart-tool-digital-twin-universe"
  - "amplifier-digital-twin-universe manifest"
  - "amplifier-digital-twin-universe check"
signals:
  prompt_matches:
    - '\bsmart[\s-]?tools?\b'
    - '\b(?:tmux-fleet|amplifier-digital-twin-universe)\b'
    - '\b(?:packag(?:e|es|ing|ed)|shar(?:e|es|ing|ed)|reus(?:e|es|ing|able)|distribut(?:e|es|ing|ed))\b[^.?!]{0,40}\b(?:workflow|workflows|process|expertise|know-how|domain\s+knowledge)\b'
    - '\b(?:workflow|workflows|process|expertise|know-how|domain\s+knowledge)\b[^.?!]{0,30}\b(?:reusable|shareable|portable|packageable)\b'
trigger: "the user wonders how to share or package a workflow, process, or hard-won domain expertise so other agents or people can use it; or names a smart tool directly"
action: 'read_file("@wayfinder:content/bulletins/smart-tools.md")'
verified_at: 2026-09-01
provenance: "spec at microsoft/amplifier-smart-tools; commands confirmed against the READMEs and pyproject console scripts of microsoft/amplifier-smart-tool-digital-twin-universe and microsoft/amplifier-smart-tool-tmux"
---

# Smart Tools

You have built up a way of working that is genuinely good. The way you stand up
a test environment that actually mirrors production. The way you read a fleet of
tmux sessions and know which one needs you. That expertise works, and it only
works where you built it. Skills and agent plugins carry a piece of it across,
never the whole thing.

Smart Tools is a format for packaging one domain's expertise into a tool any
agent can use. A smart tool is an ordinary library with a thin CLI over it, and
its straight code paths run with no model provider configured. Alongside those
it exposes higher-level commands that call an AI harness underneath, so a caller
states what it wants instead of loading a domain's worth of context and doing
the work itself.

In practice: you want an isolated environment to test against. Instead of
teaching your agent Incus, you hand it a tool that already knows. Launching,
running commands, moving files, tearing down: deterministic, no credentials
needed. Authoring the profile from one sentence, or working out why the host
cannot launch anything: model-backed.

```bash
uv tool install git+https://github.com/microsoft/amplifier-smart-tool-digital-twin-universe

amplifier-digital-twin-universe manifest   # what it is and what it needs
amplifier-digital-twin-universe check      # what this host can do, and how to fix what it cannot
```

The other reference implementation reads tmux sessions across a machine:

```bash
uv tool install git+https://github.com/microsoft/amplifier-smart-tool-tmux
tmux-fleet doctor
```

Worth knowing before reaching for these:

- These are not Amplifier bundles. Each installs on its own, and nothing here
  changes your session config.
- The digital twin tool is Linux only and needs Incus to launch anything.
  `check` reports what is missing and what to run, so start there.
- Model-backed commands need a provider key in the environment. Without one they
  fail loudly and name the remedy rather than quietly returning a worse answer.
- The spec is new. The shape is settled enough to build against, and the edges
  are still moving.

The specification, and what it deliberately leaves open:
https://github.com/microsoft/amplifier-smart-tools
