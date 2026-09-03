---
id: bad-category
category: widget
headline: "Fixture: every other clause conforms, only category is bad."
trigger: "used only by the packet-contract conformance test suite"
action: 'read_file("@wayfinder:modules/hooks-wayfinder/tests/fixtures/packet_contract/bad-category.md")'
verified_at: 2026-09-03
provenance: "synthetic fixture for the packet contract conformance kit"
---
Fixture body -- never delivered by anything real. Targets C3 only:
`category` is present and non-empty but not one of the registered
vocabulary (`bulletin`, `practice`, `concept`).
