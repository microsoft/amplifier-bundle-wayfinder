# Contract: wayfinder packet format — v1

**Status: FROZEN** — ratified by the owner (bkrabach), 2026-09-03.
**Seam:** packet authors (many, external) × the catalog consumer (`modules/hooks-wayfinder`).
**Procedure that teaches this contract:** `skills/wayfinder-pack/SKILL.md` (authoring
guidance; this document is authoritative on the format itself).

A **packet** is the unit of wayfinder content: one markdown file whose YAML
frontmatter the consumer parses mechanically into the session offer catalog, and
whose body is delivered on demand via its `action`. Multiple independent authors
produce packets; one hook consumes them. The consumer's failure mode is silence
(a malformed packet degrades quietly), which is why this surface is contracted.

---

## Core (frozen once stamped)

1. **One file, one packet.** A packet is a single markdown file under a
   registered content source (today: `content/bulletins/`, `content/practices/`,
   `content/concepts/`). No packet spans files; no file carries two packets.

2. **`id` — required, kebab-case, unique.** `id` is the packet's stable identity
   across every mechanism that references it: decline-memory, rotation
   seen-memory, menu keying, signal hint dedup. Unique across ALL content
   sources composed into a session.

3. **Required frontmatter fields:** `id`, `category`, `headline`, `trigger`,
   `action`. `category` is one of the registered vocabulary (`bulletin`,
   `practice`, `concept`; expansion is Reserved). `headline` is one plain line:
   outcome + why-you-care. `trigger` is prose describing when the offer is
   genuinely relevant.

4. **`action` is the single authoritative body path.** It is an
   `@namespace:`-form mention (e.g. `read_file("@wayfinder:content/practices/goal.md")`),
   never a filesystem path, and it resolves to the packet's own file. Consumers
   and agents deliver the body by running `action` exactly as written — never by
   globbing or searching.

5. **The catalog is derived, never registered.** The consumer assembles the
   session catalog from packet frontmatter alone. Adding a conforming file adds
   the offer; removing the file removes it. No index file exists to update, and
   none may be introduced.

6. **Signals establish relevance, never consent.** `signals.prompt_matches`
   regexes must compile; they use conservative, word-boundary patterns. A signal
   match authorizes reading the packet — it never authorizes executing any
   command, skill, install, or edit the packet describes. (Consent mechanics for
   offers live in the always-on channel guidance: propose → show → ack → act.)

7. **Commands are verified at authoring time.** Every `try_now` entry is
   runnable as written when the packet is authored or revised. `verified_at`
   (ISO date) is required and records that verification; `provenance` records
   its basis (what was checked, against what source).

8. **Unknown frontmatter keys are ignored, never fatal.** Forward compatibility:
   a packet carrying keys this contract does not define still parses and serves.

---

## Backlogged (candidate clauses, each with its named promotion trigger)

| Candidate clause | Promotes when |
|---|---|
| `curated` semantics (curation gate on derived catalog) | curation is switched on for a real audience |
| `promoted` rotation-lead semantics | a second external producer needs lead-eligibility guarantees |
| `pro-tips` category | the first pro-tip packet ships |
| `supersedes` / archive lifecycle | a bulletin actually needs retiring |
| `signals.on_event` beyond `session:start` | a second event type is needed |
| Multi-source `id` collision policy (first-wins today) | a second non-internal content source lands |

---

## Conformance

- **Contributor-runnable (required gate):**
  `modules/hooks-wayfinder/tests/test_packet_contract.py` — imports the
  consumer's own parse functions and validates every real packet under
  `content/**` against the Core clauses, plus **per-clause negative fixtures**
  under `modules/hooks-wayfinder/tests/fixtures/packet_contract/` (each fixture
  fails exactly the clause it targets and passes the rest). Plain pytest: no
  DTU, no network, no model.
- **Maintainer-side behavioral check (worked example):** a DTU live-render pass —
  menu listing, signal match with the consent boundary held, deep-dive via
  `action`, rotation eligibility — retained as a checkable artifact. Current
  worked example: the smart-tools bulletin render pass of 2026-09-02
  (evidence recorded on wayfinder PR #9). In the conformance ledger this check
  is `NOT-ASSERTABLE` in-process, justification: out-of-band DTU procedure.

## Reserved

- `signals.*` extensions (e.g. `tool_sequence`, `absent_capability`)
- `content_sources` keys (cross-bundle packet sources; already exercised by a
  sibling bundle's hook-config layer)
- `category` vocabulary expansion

## Changelog

- **2026-09-03 — v1 initial catch-up encoding (DRAFT).** Derived from shipped
  behavior and the `wayfinder-pack` authoring skill after three independent
  producers had authored against the de facto format. Evidence for the seam:
  externally authored packets (loop-until-proven; smart-tools via PR #9) and one
  observed doc-vs-code drift caught by an external author.
- **2026-09-03 — v1 FROZEN.** Ratified by the owner. Freeze Bar at stamp: spec
  written; machine-checkable kit green (45/45, per-clause discriminating
  fixtures); real implementation passing (the consumer hook + all 12 live
  packets — the kit caught and we fixed one real violation before the stamp);
  worked example end-to-end = the smart-tools DTU render pass (PR #9,
  2026-09-02).
