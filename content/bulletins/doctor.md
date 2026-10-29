---
id: doctor
category: bulletin
promoted: true
headline: "Something wrong—or just checking? /doctor gives your Amplifier CLI a setup check-up, not a health verdict."
try_now:
  - "/doctor"
  - "/doctor Inspect my provider configuration and model routing. Do not change settings, load credentials, or run live probes."
signals:
  on_event: session:start
  prompt_matches:
    # A short, explicit slash request; do not borrow another host's doctor.
    - '^(?=[\s\S]{1,240}$)(?![\s\S]*\b(?:unified|homebrew|claude[\s-]*code|medical|agents?|projects?)\b)\s*(?:(?:please\s+)?(?:run|use|explain)\s+|(?:tell\s+me\s+about|what\s+is)\s+)?/doctor\b'
    # Name the CLI's own setup as the object, not a project it helps debug.
    - '^\s*(?:please\s+)?(?:inspect|check|diagnos(?:e|ing|is))\s+(?:my\s+|the\s+)?amplifier\s+cli(?:[''’]s)?\s+(?:config(?:uration)?|setup|provider\s+(?:config(?:uration)?|setup)|model\s+routing|startup|health)\b'
    - '^\s*(?:my\s+)?amplifier\s+cli(?:[''’]s)?\s+(?:(?:config(?:uration)?|setup|provider\s+(?:config(?:uration)?|setup)|model\s+routing|startup)\s+(?:(?:is\s+)?(?:broken|confusing|failing)|(?:is\s+)?behaving\s+unexpectedly|(?:isn[''’]t|is\s+not)\s+working|keeps\s+failing)|is\s+(?:reading|using)\s+(?:the\s+)?(?:wrong|unexpected)\s+(?:settings|config(?:uration)?|setup))\b'
    # Naming Wayfinder's offer asks for its packet, not a diagnostic run.
    - '\b(?:doctor\s+(?:offer|bulletin)\s+(?:in|from)\s+wayfinder|wayfinder(?:[''’]s)?\s+doctor\s+(?:offer|bulletin))\b'
    # Troubleshooting or a routine check-up, explicitly about this CLI.
    - '^\s*(?:something\s+(?:is|feels)\s+wrong\s+with\s+(?:my|the)\s+amplifier\s+cli\b(?!\s+(?:projects?|apps?|agents?)\b)|(?:please\s+)?give\s+(?:my|the)\s+amplifier\s+cli\s+(?:a\s+)?(?:routine\s+)?(?:health\s+)?check[- ]?up\b)'
    # Also cover the natural "health of my CLI" word order.
    - '^\s*(?:i\s+(?:want|need|would\s+like)\s+to\s+)?(?:please\s+)?(?:check|inspect)\s+(?:the\s+)?health\s+of\s+(?:my\s+|the\s+)?amplifier\s+cli\b(?!\s+(?:projects?|apps?|agents?)\b)'
trigger: "session start, an explicit /doctor request, or troubleshooting and routine check-ups of the Amplifier CLI's own setup, configuration, providers, model routing, or startup"
action: 'read_file("@wayfinder:content/bulletins/doctor.md")'
verified_at: 2026-10-28
provenance: "CLI doctor shipped in microsoft/amplifier-app-cli PR #385 (c2dd3da). Checked packaged amplifier_app_cli/data/skills/doctor/SKILL.md and commands/doctor.py; installed-package verification and version-matched app-cli:cli-expert confirmed CLI slash wiring and optional natural-language focus on 2026-10-28."
---

# Something wrong—or time for a check-up?

Your Amplifier CLI is behaving oddly—or you just want to check on its setup
before your next task. **Start with /doctor.** It inspects the CLI environment
and helps you work out what to check next.

In practice: a capability seems to be missing, or you changed provider settings
and the next session still behaves unexpectedly. Give doctor the symptom.
Nothing obviously wrong? Run it without a focus for a routine setup check.
Either way, start with evidence rather than another speculative settings edit.

Doctor is a manually invoked skill packaged with the current Amplifier CLI,
not a separate bundle. That app wires `/doctor`; other hosts need not expose
it. Before offering execution, check that doctor is visible here. If it or its
agent is unavailable, report the gap and point to the normal CLI update path;
do not guess an update command or install a replacement.

Try `/doctor`, or give it a focus:

> /doctor Inspect my provider configuration and model routing. Do not change settings, load credentials, or run live probes.

Optional text is diagnostic input, not shell arguments. The skill delegates
to `app-cli:cli-doctor`, which loads `amplifier-config` when needed. Let those
own the workflow.

The shell command `amplifier doctor` is different: a deterministic checklist
with no model. Neither is a health certificate or repair engine. Passive
collection means **Health not assessed; no repair verdict from passive
collection.** Saved declarations are not resolved effective settings or live
state. Successful collection, even with no issues listed, does not mean
"healthy" or "no changes needed." Use evidence to choose the next observation,
not an automatic repair or probe.

An explicit request to run doctor authorizes inspection within the asked bounds,
without duplicate Wayfinder ack. If Wayfinder introduces execution as an optional next step,
show the exact action and wait for explicit ack. Diagnosis alone never
authorizes settings changes, credential loading, initializing providers or
models as a diagnostic probe, live probes, or capability installation.
Native host, tool, safety, and destructive-action approvals
still apply. This is for the CLI setup, not project bugs or other hosts.
