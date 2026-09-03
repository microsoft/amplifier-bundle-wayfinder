---
id: unknown-keys-ok
category: practice
headline: "Fixture: fully conformant, plus unknown frontmatter keys."
trigger: "used only by the packet-contract conformance test suite"
action: 'read_file("@wayfinder:modules/hooks-wayfinder/tests/fixtures/packet_contract/unknown-keys-ok.md")'
signals:
  prompt_matches:
    - '\bfixture\b'
verified_at: 2026-09-03
provenance: "synthetic fixture for the packet contract conformance kit"
totally_unknown_key: 42
another_bogus_key: "the contract does not define this -- must be ignored"
nested_unknown:
  foo: bar
  baz: [1, 2, 3]
---
Fixture body -- never delivered by anything real. Positive fixture for C8:
carries several unknown frontmatter keys (`totally_unknown_key`,
`another_bogus_key`, `nested_unknown`) that the contract does not define.
It must still parse and validate fully clean.
