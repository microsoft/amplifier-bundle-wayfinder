---
id: autocompletion
category: bulletin
promoted: true
headline: "Discover Amplifier slash commands and argument choices with / and Tab — plus Bash/Zsh/Fish shell completion."
try_now:
  - "amplifier --install-completion"
signals:
  on_event: session:start
  prompt_matches:
    # Noun completion questions exclude nearby code/editor/form generation,
    # except when a terminal, shell, slash, or command qualifier makes the CLI intent clear.
    - '\bamplifier(?:[''’]s)?\s+(?:(?:auto[- ]?completion|tab[- ]?completion|command[- ]?completion|slash[- ]?command[- ]?completion|completions?)\b(?:(?=[^.?!]{0,48}\b(?:terminal|shell|slash|commands?)\b)|(?![^.?!]{0,48}\b(?:code(?:\s+editor)?|editor|python|search\s+form)\b))|auto[- ]?complet(?:e|es|ed|ing)\s+(?:slash\s+)?command(?:\s+names?)?\b)'
    - '\bslash(?:[- ]commands?)?\s+(?:completions?|menus?|suggestions?|pop[- ]?ups?)\b[^.?!]{0,40}\b(?:in|for)\s+amplifier\b'
    - '\b(?:shell|bash|zsh|fish|cli)\s+(?:auto[- ]?complet(?:e|es|ed|ing|ion)|tab[- ]completion|completion)\b[^.?!]{0,40}\b(?:in|for)\s+amplifier\b'
    - '\b(?:command|argument)\s+(?:suggestions?|pop[- ]?ups?)\b[^.?!]{0,40}\b(?:in|for)\s+amplifier\b'
    - '\bamplifier(?:[''’]s)?\s+(?:slash[- ]?commands?|slash\s+(?:completions?|menus?|suggestions?|pop[- ]?ups?))\b'
    - '\b(?:argument|option|choice)s?\b[^.?!]{0,40}\bamplifier(?:[''’]s)?\b[^.?!]{0,40}/[a-z][a-z0-9-]*\b'
trigger: "The user asks about Amplifier autocompletion, finding slash commands or their arguments, completion popups, or shell Tab completion."
action: 'read_file("@wayfinder:content/bulletins/autocompletion.md")'
verified_at: 2026-09-10
provenance: "amplifier-app-cli PRs #334–336 and #338, merged to main; README sections Shell Completion and Interactive Slash Completion at 2adb7ddb424f2219cbe08d01ddff653ed2dfc901. app-cli:cli-expert confirmed the no-argument --install-completion flag in main.py and popup settings/key semantics on 2026-09-10."
---

# Discover commands instead of remembering them

You know what you want to do, but not the exact slash command or its next
argument. **Type `/` at the start of the Amplifier prompt and see the choices.**
The menu includes descriptions for available built-ins, modes, user-invocable
skills, and aliases. Known argument suggestions appear as you continue typing.

In practice: type `/prov`, press Tab, and—when it is the only match—you get
`/provider ` with a space and the known argument menu. You can keep typing your
own value instead of choosing a suggestion. If two names share a prefix, Tab
fills only what they share and waits for you to disambiguate.

This is **built into the updated Amplifier CLI**, not a bundle to install.
The changes were verified on `main`; don't assume an older installed CLI has
them or claim a particular tagged release. The menus reflect the commands,
modes, skills, and providers available in that session.

The useful keyboard distinction is **completing text is not executing it**:

- With nothing selected, Tab finishes a unique match and adds a space, or
  extends the shared prefix and stops. Repeated Tab does not cycle.
- Up/Down or Shift-Tab selects an open menu item. Tab, Enter, or Space accepts
  that selection without submitting the command.
- In a command-name menu, unselected Enter accepts an exact or unique match;
  an ambiguous prefix stays open. In an argument menu, unselected Enter submits
  exactly what you typed. Suggestions don't replace normal command validation.
- Esc closes the menu and restores the typed prefix. With no selection,
  Space is literal: finish a name yourself and move on to arguments.

For **Bash, Zsh, or Fish**, the same discovery extends outside the app. At your
shell prompt, `amplifier bundle use ` followed by Tab suggests local bundle
names; `amplifier run --provider ` followed by Tab suggests provider instances.
Enable that shell integration with:

```bash
amplifier --install-completion
```

Follow the activation command it prints. Setup is repeat-safe; it preserves
custom Fish completion files. Zsh needs its normal `compinit` setup. PowerShell
is not supported. Your shell keeps its own key and menu behavior—the in-app
no-cycling rule doesn't redefine shell Tab.

Shell candidates cover commands, flags, fixed choices, local top-level bundles,
configured provider instance IDs, and the newest 100 matching top-level sessions
in the current project. Lookup is local and read-only, without model/API calls,
bundle downloads, or session-transcript reads.

Prefer manual Tab to automatic popups? In `~/.amplifier/settings.yaml`:

```yaml
ui:
  slash_popup:
    enabled: false
```

Use the boolean `false` and restart the interactive session. This applies to
fresh and resumed sessions; manual Tab stays available. It doesn't disable
shell completion. No setting is needed for the default-on behavior.

An explicit request to install shell completion or change the popup setting
authorizes that in-scope action without another Wayfinder ack. If Wayfinder
offers either as an optional next step, show the exact command or edit and wait
for the user's go. A topical question is not permission to change shell files.
Native host, tool, safety, and destructive-action approvals still apply.

For the full keyboard reference and setup details, point to the CLI docs rather
than turning this into a settings tutorial:
https://github.com/microsoft/amplifier-app-cli#interactive-slash-completion

Skill authors can advertise optional literal argument choices too. For deeper
CLI or configuration questions, use `app-cli:cli-expert` when available;
otherwise use the linked docs.