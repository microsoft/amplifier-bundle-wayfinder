---
id: action-wrong-target
category: practice
headline: "Fixture: every other clause conforms, only action's target is wrong."
trigger: "used only by the packet-contract conformance test suite"
action: 'read_file("@wayfinder:modules/hooks-wayfinder/tests/fixtures/packet_contract/action-filesystem-path.md")'
verified_at: 2026-09-03
provenance: "synthetic fixture for the packet contract conformance kit"
---
Fixture body -- never delivered by anything real. Targets C4 only:
`action` IS a well-formed `@namespace:` mention, but it points at a
*different* fixture file (`action-filesystem-path.md`) instead of resolving
to this packet's own file.
