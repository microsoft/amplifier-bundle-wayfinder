---
id: bad-regex
category: practice
headline: "Fixture: every other clause conforms, only one signal regex is bad."
trigger: "used only by the packet-contract conformance test suite"
action: 'read_file("@wayfinder:modules/hooks-wayfinder/tests/fixtures/packet_contract/bad-regex.md")'
signals:
  prompt_matches:
    - '\bfixture\b'
    - '['
verified_at: 2026-09-03
provenance: "synthetic fixture for the packet contract conformance kit"
---
Fixture body -- never delivered by anything real. Targets C6 only: the
second `signals.prompt_matches` entry (`[`) is an unterminated character
class and does not compile as a regex.
