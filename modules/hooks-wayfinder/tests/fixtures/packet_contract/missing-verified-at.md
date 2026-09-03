---
id: missing-verified-at
category: practice
headline: "Fixture: every other clause conforms, only verified_at is missing."
trigger: "used only by the packet-contract conformance test suite"
action: 'read_file("@wayfinder:modules/hooks-wayfinder/tests/fixtures/packet_contract/missing-verified-at.md")'
provenance: "synthetic fixture for the packet contract conformance kit"
---
Fixture body -- never delivered by anything real. Targets C7 only:
`verified_at` is absent from the frontmatter entirely (`provenance` is
present and non-empty).
