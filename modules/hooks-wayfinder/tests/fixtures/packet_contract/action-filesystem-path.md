---
id: action-filesystem-path
category: practice
headline: "Fixture: every other clause conforms, only action's form is bad."
trigger: "used only by the packet-contract conformance test suite"
action: 'modules/hooks-wayfinder/tests/fixtures/packet_contract/action-filesystem-path.md'
verified_at: 2026-09-03
provenance: "synthetic fixture for the packet contract conformance kit"
---
Fixture body -- never delivered by anything real. Targets C4 only:
`action` is a bare filesystem path (no `@namespace:` mention form at all),
which C4 forbids outright.
