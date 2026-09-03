---
id: bad-verified-at
category: practice
headline: "Fixture: every other clause conforms, only verified_at's format is bad."
trigger: "used only by the packet-contract conformance test suite"
action: 'read_file("@wayfinder:modules/hooks-wayfinder/tests/fixtures/packet_contract/bad-verified-at.md")'
verified_at: "not-a-date"
provenance: "synthetic fixture for the packet contract conformance kit"
---
Fixture body -- never delivered by anything real. Targets C7 only:
`verified_at` is present but does not parse as an ISO date.
