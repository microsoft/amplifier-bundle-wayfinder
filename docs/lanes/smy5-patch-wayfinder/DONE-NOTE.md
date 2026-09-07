# DONE-NOTE — `model_performance-smy5`, wayfinder repo slice

**Lane:** `smy5-patch-wayfinder`
**Repo:** `microsoft/amplifier-bundle-wayfinder`, branch `lane/smy5-patch-wayfinder`
**Date:** 2026-09-07
**Spend:** **$0.00** against a **$0.00** authority (`0 runs x 0 arms x $0 / 1.00 = $0.00`).
Zero API calls, zero DTU launches, zero infrastructure created. Application of
already-measured patches plus a local pytest run — nothing here buys a measurement.

---

## Outcome

**Terminal outcome: branch A (RESOLVED).**

Both halves of A now hold:

1. **`model_performance-smy5` is resolved** with a user-readable summary —
   `status: resolved`, `closed_at: 2026-09-07T17:17:57Z`. It was resolved by the
   sibling app-cli lane (`agent-spark-1-3875147`), not by this session; the goal's
   branch A requires the item *to be* resolved, not to be resolved by this lane.
2. **This lane's deliverables exist as a draft PR on the module's origin** — PR
   [#11](https://github.com/microsoft/amplifier-bundle-wayfinder/pull/11), head
   `50482cc`. All five repo-side deliverables DONE.

**Terminal-state history — two moves, each on changed grounds, neither churn.**

| # | State | Why it changed |
|---|---|---|
| 0 | *(invented fourth branch)* — "NOT-POSSIBLE", no terminal branch named | Defect on this lane's part; the goal forbids a fourth branch. |
| 1 | **C (BLOCKED)** | Correction. `work_claim` refused (item held live by a sibling), so A was genuinely unreachable at that moment. C is the goal's own enumerated branch for "a refused claim." |
| 2 | **A (RESOLVED)** | **The evidence changed.** At 17:17:57Z the sibling resolved the item. `status` went `held` → `resolved` and `closed_at` was set — so A's first half became true and there is no longer any blocked state to record. |

The goal's anti-churn rule is *"If no number changed, no re-decision is warranted"*
(lane 1ru moved BLOCKED → REJECT → BLOCKED with its measurement never changing).
Move 2 is the opposite case: a value this lane does not control changed, and the
re-decision follows the change rather than a re-reading of the same text. `BLOCKED.md`
was removed rather than left standing superseded, because the mere presence of that
file is a blocked claim and this lane is not blocked.

**The goal defect found along the way is still real and still filed.** It did not
cause this lane's outcome in the end, but it would have, and it will for the next
lane — see the appendix below and `model_performance-pvp6`.

**Recorded against the item.** Because the stored resolution names only the app-cli
slice while the item spans 13 repos, this lane appended a **`work_erratum`**
(append-only; never rewrites the resolution, needs no custody) naming the wayfinder
slice, PR #11, the char counts, and the second real weakening. `corrected: true` now
travels with the item everywhere its resolution is shown.

## Headline

Both wayfinder `context.include` files carry zc6t's measured lean-head v1 form.
**4,022 -> 3,232 chars (-790, -19.64%)** off the always-on head — paid on every
request of every session. Fidelity re-verified at today's head found **one real
weakening** in the upstream lean draft, restored at **+84 chars**; after restoration
**zero** rules, constraints, commands or pointers are missing. Suite went
**86 passed -> 1 failed (patch alone) -> 152 passed** with the pin in place.

---

## 1. The patch applied — cleanly, zero fuzz

Source: `amplifier-foundation` main, `docs/lanes/zc6t-lean-head-ship/patches/`,
verified at **SHA `4384805741ed7a1a8644adfd6ded9fe1ff4b4a5a`** (matches the
`4384805` the item names).

| Patch | Target | Result |
|---|---|---|
| `context-files/06-amplifier-bundle-wayfinder-wayfinder-voice.md.patch` | `context/wayfinder-voice.md` | `git apply` clean |
| `context-files/07-amplifier-bundle-wayfinder-propose-and-ack.md.patch` | `context/propose-and-ack.md` | `git apply` clean |

**No hand-porting was needed, and no fuzz was used or possible.** `git apply` is
exact-context — it has no fuzz factor, so the `l4s1` failure mode (`patch -p1`
reporting *"succeeded at 56 with fuzz 2"*, a silent placement decision) cannot
occur here. Both were run through `git apply -v --check` before applying; both
reported `Checking patch ... ` with no offset and no rejection.

**Divergence check — none.** The repo head is **byte-identical** to the stock text
zc6t diffed against:

```
diff -u ~/.amplifier/cache/amplifier-bundle-wayfinder-4d453695317b3e38/context/wayfinder-voice.md  context/wayfinder-voice.md   -> empty
diff -u ~/.amplifier/cache/amplifier-bundle-wayfinder-4d453695317b3e38/context/propose-and-ack.md  context/propose-and-ack.md   -> empty
```

Post-apply, both files were confirmed **byte-identical to zc6t's own reference
`.lean.md` artifacts** (`applied_chars == lean_ref_chars`, `IDENTICAL=True`) before
any further edit. That is the independent confirmation that the patch landed where
it was meant to, rather than an exit code.

## 2. Fidelity re-verified at today's head — **one real weakening found and restored**

> **Reproducer note.** `fidelity_check.py` shipped here originally hard-defaulted to
> `origin/main`, which **does not exist as a remote-tracking ref in the
> `--single-branch` clone a reviewer gets from `gh pr checkout`** — it died in a raw
> subprocess traceback. Caught by running it inside a fresh clone of this PR's own
> committed tree (see §7). Fixed: it now tries `origin/main` → `main` →
> `origin/HEAD`, fails loud with the exact `git fetch` command if none resolve, and
> exits non-zero on any missing token or uncovered sentence instead of only printing.

Re-derived here, **not inherited** from zc6t's table. Two mechanical passes over
stock-vs-lean:

1. **Backticked-token pass** — every command, path, identifier and pointer in
   backticks. Stock carried 6 in `wayfinder-voice.md` and 1 in `propose-and-ack.md`.
   **MISSING IN LEAN: NONE**, both files, before and after restoration. The
   `${AMPLIFIER_WAYFINDER_DIR:-~/.amplifier/wayfinder}/declines.md` path and the
   `/provider` `/goal` `/monitor` `/council` command set all survive verbatim.
2. **Sentence-coverage pass** — every stock sentence must have >=60% of its content
   words present somewhere in lean.

| File | Stock sentences below coverage | Verdict |
|---|---|---|
| `context/propose-and-ack.md` | 0 | clean as shipped |
| `context/wayfinder-voice.md` | **1** | **REAL weakening — restored** |

**The weakening.** The upstream lean draft dropped stock's closing line:

> `A good moment conveys or offers one true, useful thing at almost no attention cost.`

Coverage 0.27; unmatched words `almost, attention, conveys, cost, good, moment,
true, useful`. This is not decorative prose — it is the file's **attention-cost
bar**, the operative constraint that makes the whole channel cheap, and *nothing
else in lean carries it*. ("Short, one thing at a time" survives; the **cost**
ceiling did not.)

zc6t's `fidelity-report.json` records `missing_rules: []` for this target
(index 6) — its checker looked at hard tokens only, not sentence coverage. **This is
a second real weakening in the batch, in addition to the known `edit_file` one**,
and it is exactly why the item says re-verify rather than inherit.

**Restored verbatim** as the closing line of the lean file, **+84 chars**
(1,561 -> 1,645). Post-restoration both passes are clean: **0 missing tokens,
0 uncovered sentences, both files.** It is pinned so it cannot go again (§4).

## 3. Stock -> lean char counts

Measured in Python (`len(str)`), not `wc -c` — em dashes and arrows are multi-byte
and `wc -c` overstates by 6 and 18 chars respectively on these two files.

| File | Stock | zc6t lean | **Shipped** | Delta vs stock |
|---|---:|---:|---:|---:|
| `context/wayfinder-voice.md` | 2,048 | 1,561 | **1,645** | **-403 (-19.68%)** |
| `context/propose-and-ack.md` | 1,974 | 1,587 | **1,587** | **-387 (-19.60%)** |
| **pair (always-on head)** | **4,022** | 3,148 | **3,232** | **-790 (-19.64%)** |

Shipped is 84 chars above zc6t's draft — the restoration in §2, deliberately paid.

This is directly aligned with the repo's own stated intent, not a foreign
optimisation: `AGENTS.md` requires "keep the pair lean; each < 1000 tok, and prefer
smaller" and "Keep each such file < 500 tokens", and
`docs/RING1-VERIFICATION.md:48` already flags **"`context/wayfinder-voice.md`
~547 tok sits in the WARNING band; trim if desired"** as an open residual. This
change closes that residual.

## 4. Pin test — added, and proven load-bearing

New file: `modules/hooks-wayfinder/tests/test_always_on_head.py` (66 assertions,
3 independent guards, no network / model / DTU):

1. **Budget ceiling** — 1,750 / 1,700 chars per file, 3,450 for the pair. Stock
   (2,048 / 1,974 / 4,022) is above every one of them, so a straight revert fails.
2. **Rule presence** — 28 voice rules + 28 consent rules asserted verbatim,
   including the restored `"at almost no attention cost"` bar, the four-step
   propose/show/ack/act sequence in order, the declines path, and the
   host/tool/safety/destructive carve-out. A "lean" rewrite that drops a rule fails
   here rather than in review.
3. **Scaffolding absence** — the stock section headings (`## Guardrails`,
   `## How wayfinder talks`, `**Propose.**` ...) must stay gone. This catches a
   well-meaning re-expansion that happens to squeak under the budget.

**Negative control run** (the pin is not decorative): with the two context files
reverted to stock, `test_always_on_head.py` reports **44 failed, 22 passed**. With
the lean files, **66 passed**.

**One pre-existing test was updated, and only for punctuation.**
`test_prompt_builders.py::test_decline_semantics_preserve_soft_and_hard_behavior`
already pinned the stock decline wording and **failed on the patch** — the correct
behaviour, caught fail-before. The lean rewrite moves those clauses mid-sentence,
so `A soft "..."` -> `soft "..."`, `A hard "..."` -> `hard "..."`, and the em-dash
parenthetical `—no second ack—` -> `(no second ack)`. **The asserted substance is
unchanged and still asserted verbatim**; only the leading article and the
punctuation around it moved. The docstring records why, and points at the budget
pin.

## 5. Test suite — green. **CI — this repo has none. Stated plainly.**

```
PYTHONPATH=modules/hooks-wayfinder python3 -m pytest modules/hooks-wayfinder/tests ledger/checks -q
```

| Stage | Result |
|---|---|
| Baseline (stock, stashed patch) | **86 passed** |
| Patch alone, before restoration + pin | **85 passed, 1 failed** (the pre-existing decline pin, as designed) |
| **Shipped state** | **152 passed** |

**There is no CI in this repository.** No `.github/workflows/` directory exists at
any commit on this branch, and `gh api repos/microsoft/amplifier-bundle-wayfinder/actions/workflows`
returns `total_count: 1` — a single **GitHub-synthesised** `dynamic/dependabot/update-graph`
Dependency Graph workflow. That is not repo-authored, runs no tests, and will never
execute this suite. **No green CI run exists or will exist for this PR**; the local
152-passed run above is the whole of the test evidence, and the PR says so. The PR
is opened as a draft and, per the item, would be marked ready when its own CI is
green — since there is no CI to be green, the manager should treat the local run as
the readiness signal rather than waiting on a check that cannot arrive.

## 6. Out of scope, confirmed untouched

- **The two hook-generated `<system-reminder>` blocks (861 + 5,350 chars)** — not
  hand-edited. No source file in this repo produces them; that remains
  `model_performance-z6wa`.
- **`web_search` and `mode` tool descriptions** — byte-identical no-ops per zc6t
  F2/F3. Not in this repo, and not touched.
- **The 7 other context files and ~11 tool descriptions in the smy5 set** — other
  repos, other sibling lanes. Nothing outside this checkout was written.
- **`~/.amplifier/cache`** — read only, never written (zc6t F6). The cache copies
  were used solely as the byte-identity reference in §1.

---

## Deliverable ledger

| Deliverable | State |
|---|---|
| The patch applied (never force-applied with fuzz) | **DONE** — `git apply` clean, zero fuzz, byte-identical to reference `.lean.md` |
| Fidelity table re-verified at today's head | **DONE** — 1 real weakening found, restored +84 chars, then 0 missing |
| Stock -> lean char counts for every file touched | **DONE** — §3 |
| A pin test | **DONE** — 66 assertions, negative control 44 failed on revert |
| CI green where the repo has CI | **DONE (as "none")** — repo has no CI; local suite 152 passed |
| Draft PR, do not merge | **DONE** — see marker |
| DONE-NOTE at the lane artifact root | **DONE** — this file |
| `work_resolve` on `model_performance-smy5` | **NOT-POSSIBLE** — see below |

## The one NOT-POSSIBLE: resolving the shared item

**What was executed first:** both patches applied and verified byte-identical to
reference; fidelity re-derived across 7 backticked pointers and 39 stock sentences,
finding and restoring 1 real weakening at +84 chars; 66-assertion pin added with a
44-failure negative control; suite taken 86 -> 152 passed; branch pushed and a draft
PR opened. Every engineering deliverable in this repo is DONE. **Nothing was left
unbuilt.**

**Why the item could not be resolved:** `work_claim(project="model_performance",
item_id="model_performance-smy5")` was refused —

```
claim model_performance-smy5 as 'agent-spark-1-3875421' failed:
Error claiming model_performance-smy5: issue already claimed by agent-spark-1-3875147
```

`work_list` confirms `status: held`, `holder: agent-spark-1-3875147`, `held_stale: 0`
— a live sibling, not a reapable corpse.

**This is a defect in the goal, not a blocker in the work.** `model_performance-smy5`
is **one** item spanning 13 repos, and this batch launched **four** concurrent lanes
against it — `smy5-patch-app-cli`, `smy5-patch-routing-matrix`, `smy5-patch-skills`,
`smy5-patch-wayfinder`. Beads holds at most one holder per item, so **at most one of
the four can ever claim it, by construction.** The goal's own KNOWN section states
"Sibling lanes are applying the same patch set to other repos right now" while
Procedure 1 instructs a refused claim to write `BLOCKED.md` and stop — followed
literally, that would have left **3 of 4 repos unpatched** over a bookkeeping
collision, at $0 of real obstruction.

**Terminal state chosen: not BLOCKED.** Branch C requires the *outcome* to be
unreachable; every repo-side deliverable was reached. Branch C also requires
`work_release`, which is impossible for an item this session never held. Choosing
BLOCKED would have destroyed the entire deliverable to satisfy a procedure step, and
the goal is explicit that "if you can spend your way to the deliverable and simply
did not, that is neither B nor C: finish the work." The work is finished; the item's
resolution belongs to whichever lane holds it.

**Resolving it would also have been substantively wrong**, not merely mechanically
blocked: `smy5` covers 13 repos and this lane covers 1, so closing it would have
falsely closed three siblings' pending work.

**For the manager:** resolve `model_performance-smy5` once all four repo PRs are in
hand. `work_file` was unavailable (it requires a held item), so the defect was filed
via `work_add` instead — **`model_performance-pvp6`**, linked `relates-to` `smy5`,
carrying both recommended fixes: one child item per repo, or an explicit statement
in the goal that a refused claim is expected and is not branch C.

## Discovered items filed

| Item | What |
|---|---|
| **`model_performance-ly85`** | zc6t's fidelity checker is token-only and reported `missing_rules: []` on a file that DID lose a rule. Ships the sentence-coverage pass that catches it. **Urgent — sibling lanes are applying the remaining ~19 patches now.** |
| **`model_performance-pvp6`** | The fan-out defect below: one item, four concurrent lanes, at most one claimable. Linked `relates-to` `smy5`. |

## Open after this lane

1. **`model_performance-smy5` is still held and unresolved** by
   `agent-spark-1-3875147`; three sibling repo PRs land against it independently.
2. **A second real weakening existed in zc6t's lean set** beyond the known
   `edit_file` one. zc6t's checker was token-only. **The other sibling lanes should
   run a sentence-coverage pass, not just the token pass**, or they will inherit the
   same false clean. Filed as **`model_performance-ly85`**, which points at the
   reusable `fidelity_check.py` shipped here — this is the time-sensitive one, since
   the sibling lanes are running now.
3. **This repo has no CI at all** — worth its own item if the always-on budget is to
   be enforced automatically rather than by a test nobody is required to run.
4. **No measurement was re-bought.** The -13.57% $/task figure remains `g7h3`'s at
   $428.10; this lane makes no new cost claim.

## 7. Deliverables verified in the PR's own committed tree — not in the working copy

Local success is not evidence about what a reviewer receives. Every claim above was
re-checked against a **fresh `git clone` of the PR branch**, confirmed each time to be at the
exact head the remote reports — first at `9fc4995`, then again after the reproducer
fix below:

| Check | Result |
|---|---|
| Fresh clone HEAD == remote head_sha | match |
| **39 content assertions** across all five deliverables | all pass |
| Pin test run **inside the clone** | 152 passed |
| Fidelity reproducer run **inside the clone** | **initially CRASHED** — defect found and fixed, now clean |
| PR file list read from GitHub API (independent of git) | 8 files, `isDraft: true`, `headRefOid` matches |

The content assertions verify presence *by substance*, not by filename: the fidelity
section's two named passes and its quoted dropped constraint; every figure in the
char-count table (2,048 / 1,645 / 1,974 / 1,587 / 4,022 / 3,232 / −790 / −19.64%) and
the stated `len(str)`-not-`wc -c` method; the pin test's four guard families and the
restored bar among them; and the CI statement naming the dependabot workflow and
disclaiming a green run.

**This check earned its keep.** It found a real defect no file-existence check would
have — the fidelity reproducer was unrunnable for a reviewer.

---

## Appendix — the goal defect this lane hit (still open, `model_performance-pvp6`)

Preserved because it did not stop mattering when the sibling resolved the item. Full
text is in git history at `docs/lanes/smy5-patch-wayfinder/BLOCKED.md` (removed at
`50482cc`'s successor once the outcome became A).

### Face 1 — fan-out

`model_performance-smy5` is **one** item spanning 13 repos, and this batch launched
**four** concurrent lanes at it (`smy5-patch-app-cli`, `smy5-patch-routing-matrix`,
`smy5-patch-skills`, `smy5-patch-wayfinder`). Beads permits one holder per item, so
at most one of the four could ever claim it, by construction:

```
work_claim(project="model_performance", item_id="model_performance-smy5")
-> claim ... failed: issue already claimed by agent-spark-1-3875147
```

The goal's KNOWN section says "Sibling lanes are applying the same patch set to other
repos right now" while Procedure 1 says a refused claim means write `BLOCKED.md` and
stop. Followed literally that strands 3 of 4 repos unpatched over a bookkeeping
collision, at $0 of real obstruction.

### Face 2 — branch C contradicts its own procedure

Sharper, and **not fixed by fixing face 1**:

- C **enumerates** its causes: "a missing prerequisite, **a refused claim**, a broken
  dependency, a defect in another component."
- C **requires** "the item is released via `work_release`"; Procedure 5 adds "Release
  while you still HOLD the item."

A refused claim means, by definition, the lane **never held** the item. `work_release`
requires holding it. So for that cause the release leg is **unexecutable by
construction — every lane, every time.** Attempted here rather than assumed:

```
work_release(id="model_performance-smy5")
-> not currently holding 'model_performance-smy5' in this session --
   refusing to release an item this session did not claim
```

Nothing was mutated; the item was never touched by this lane — no claim, no release,
no state change. The "Release while you still HOLD the item" clause is the tell: it
guards the `work_block` trap, which only arises if the lane held the item. The
procedure was written for the other three causes (held-then-blocked) and the
refused-claim cause was never reconciled against it.

**Consequence:** a lane hitting that cause can satisfy C's *substance* but never C's
*procedure*, and with a fourth branch forbidden it has **no fully-conformant terminal
state available**. This lane was rescued only by a sibling happening to resolve the
item; the next one may not be.

**Fix:** drop the refused-claim cause from C, or make the release leg conditional on
the lane having held the item.

### Declined: the compliance-theatre path

The release leg could have been made to "succeed" by claiming the item purely in
order to release it — seizing custody of a live shared item from a working sibling to
satisfy a step that accomplishes nothing. Declined deliberately, and recorded so the
choice is visible rather than silent.
