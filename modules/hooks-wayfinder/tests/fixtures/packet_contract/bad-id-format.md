---
id: Bad_ID-Not-Kebab
category: practice
headline: "Fixture: every other clause conforms, only id's format is bad."
trigger: "used only by the packet-contract conformance test suite"
action: 'read_file("@wayfinder:modules/hooks-wayfinder/tests/fixtures/packet_contract/bad-id-format.md")'
verified_at: 2026-09-03
provenance: "synthetic fixture for the packet contract conformance kit"
---
Fixture body -- never delivered by anything real. Targets C2 only: `id`
carries an uppercase letter and an underscore, so it fails
`^[a-z0-9][a-z0-9-]*$`.
