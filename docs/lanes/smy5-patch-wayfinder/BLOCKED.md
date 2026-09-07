# BLOCKED — `model_performance-smy5`, lane `smy5-patch-wayfinder`

**Terminal outcome: branch C (BLOCKED).** Chosen once. Recorded 2026-09-07.

## What is blocked

**Exactly one thing: the item's resolution.** The goal defines OUTCOME A as
"`model_performance-smy5` is resolved with a user-readable summary **AND** the
deliverables exist as a draft PR." The second half is satisfied. The first half is
not, and cannot be reached from this session.

**Everything else is DONE and shipped.** This file is not a report of failed work —
see `DONE-NOTE.md` beside it and PR
[microsoft/amplifier-bundle-wayfinder#11](https://github.com/microsoft/amplifier-bundle-wayfinder/pull/11).
Read the two together or this file will mislead you.

## Why — a refused claim

The goal enumerates **"a refused claim"** as a branch-C reason. That is precisely
what happened, twice-verified:

```
work_claim(project="model_performance", item_id="model_performance-smy5")
-> claim model_performance-smy5 as 'agent-spark-1-3875421' failed:
   Error claiming model_performance-smy5: issue already claimed by agent-spark-1-3875147
```

`work_list` at 17:13Z: `status: held`, `holder: agent-spark-1-3875147`,
`held_stale: 0`, `updated_at: 2026-09-07T17:11:47Z` — a **live** sibling renewing
custody, not a reapable corpse. Re-checked after all engineering work completed; the
hold had not moved.

## Root cause: a fan-out defect in the goal, not an engineering blocker

`model_performance-smy5` is **one** item spanning 13 repos. This batch launched
**four** concurrent lanes against it:

- `smy5-patch-app-cli`
- `smy5-patch-routing-matrix`
- `smy5-patch-skills`
- `smy5-patch-wayfinder` (this lane)

Beads permits **one holder per item**, so **at most one of the four can ever claim
it, by construction.** Three lanes are forced into this state no matter how well
they execute. The goal's own KNOWN section states "Sibling lanes are applying the
same patch set to other repos right now" while Procedure 1 says a refused claim
means write `BLOCKED.md` and stop — the two cannot both be satisfied without
stranding 3 of 4 repos.

Filed as **`model_performance-pvp6`** (linked `relates-to` `smy5`), with two
proposed fixes: one child item per repo, or an explicit statement in the goal that a
refused claim is expected here and is not branch C.

## `work_release` is inapplicable — attempted and refused, not skipped

Branch C's procedure says "the item is released via `work_release`." That leg cannot
execute: this session **never held** the item, so there is nothing to release. The
attempt was made rather than assumed, so the refusal is on the record:

```
work_release(id="model_performance-smy5")
-> not currently holding 'model_performance-smy5' in this session --
   refusing to release an item this session did not claim
```

Nothing was mutated. **The item remains held by `agent-spark-1-3875147` and is
untouched by this lane** — no claim, no release, no resolution, no state change of
any kind.

## What was executed before this file was written

Not "nothing ran." The full repo-side slice landed first:

| Deliverable | State |
|---|---|
| Both patches applied, `git apply`, zero fuzz, byte-identical to zc6t's reference `.lean.md` | DONE |
| Fidelity re-verified at today's head — **1 real weakening found**, restored verbatim at +84 chars | DONE |
| Stock → lean char counts: **4,022 → 3,232 (−790, −19.64%)** | DONE |
| Pin test — 66 assertions, negative control 44 failed on revert | DONE |
| CI — repo has none; stated plainly, no green run implied | DONE |
| Draft PR #11, head `9be55c1`, verified by remote read | DONE |
| `DONE-NOTE.md` at the lane artifact root | DONE |
| **`work_resolve` on `model_performance-smy5`** | **BLOCKED — this file** |

Two discovered items filed via `work_add` (`work_file` was unavailable — it requires
a held item): **`model_performance-ly85`** (zc6t's fidelity checker is token-only and
scored a genuinely-weakened file clean — urgent, the sibling lanes are applying the
remaining ~19 patches now) and **`model_performance-pvp6`** (this fan-out defect).

**Spend: $0.00 against a $0.00 authority.** Zero API calls, zero DTU launches, zero
infrastructure created. Nothing was left unbuilt for want of budget.

## What the manager needs to do

1. **Resolve `model_performance-smy5`** once all four repo PRs are in hand — this
   lane's slice is PR #11 and needs no further work.
2. **Fix the fan-out** per `model_performance-pvp6` before the next multi-repo item.
3. **Route `model_performance-ly85` to the sibling lanes now** — they are applying
   the remaining patches against a fidelity report whose clean rows are not evidence
   of cleanliness.

## Placement note

Written to the lane **artifact root** (`docs/lanes/smy5-patch-wayfinder/`) rather
than the repo root, per `artifact-path/v1` and the goal's scope-out against
repo-root lane files. It is committed on `lane/smy5-patch-wayfinder`. A byte-identical
copy sits at `/home/bkrabach/dev/hw-model-performance/lanes/smy5-patch-wayfinder/BLOCKED.md`
beside `DONE.json`, for a manager scanning the lane directory outside the repo.
