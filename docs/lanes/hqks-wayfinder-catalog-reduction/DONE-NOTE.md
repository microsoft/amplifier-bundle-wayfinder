# hqks — skills catalog reduction: hide wayfinder-pack and wayfinder-scout

**Item:** `model_performance-hqks` · **Repo:** `microsoft/amplifier-bundle-wayfinder`
**Branch:** `lane/hqks-wayfinder-catalog-reduction` · **Spend:** **$0** (authority was $0;
every measurement is static — no `amplifier` process, no session, no provider call)
**Outcome:** **A — RESOLVED at the LANDING STAGE.** Deliverables ship as a **draft PR**;
the merge is the manager's next stage. This lane did not merge and did not touch any
other repo.

---

## 1. What shipped

| File | Change |
|---|---|
| `skills/wayfinder-pack/SKILL.md` | `disable-model-invocation: true` (+ why, in a comment) |
| `skills/wayfinder-scout/SKILL.md` | `disable-model-invocation: true` (+ why, in a comment) |
| `modules/hooks-wayfinder/tests/test_skill_visibility.py` | **new** — 5-test tripwire; runs in the repo's standing test command |
| `AGENTS.md` | new "Skills here are hand-run" section + `skills/wayfinder-scout/` table row |
| `docs/lanes/.../verify_hidden_skills.py` | **new** — end-to-end check against the REAL `amplifier_module_tool_skills` discovery + visibility renderer |
| `docs/lanes/.../measure_index_delta.py` | **new** — measures what hiding actually does to the always-on index |

`user-invocable: true` was left in place on both. The two keys are a pair: hiding a
skill removes it from the auto-invocable index, `user-invocable` is what keeps
`/wayfinder-pack` dispatch and the channel's own availability check working.

---

## 2. wayfinder-scout: **FOUND — and hidden.** (The item asked for one of two answers.)

The item recorded scout as "not locatable anywhere in this workspace checkout as of
cycle 65". **It is in this repo, on `origin/main`, and has been since 2026-09-03.**
The earlier miss is explained below in §5 — the lane's own worktree was 13 commits stale.

```
$ git ls-tree origin/main skills/
040000 tree 43c62b736a2319e2dea69452ea8a17ef91137ebc    skills/wayfinder-pack
040000 tree 59e3b43c456c623d2020585c087b50cd36e301eb    skills/wayfinder-scout

$ git log --all --diff-filter=A --name-only -- '*scout*'
commit f2d592567346589491dd3e6a96cc954a9dbb61a8
Date:   Thu Sep 3 08:09:40 2026 -0700
    feat: adoption-aware offering — wayfinder-scout skill + builds_on ladder + adoption_aware knob
skills/wayfinder-scout/SKILL.md

$ git merge-base --is-ancestor f2d5925 origin/main && echo YES
YES
```

Owner directive (cycle 66, verbatim: *"Wayfinder should be in
microsoft/amplifier-bundle-wayfinder"*) is satisfied by fact, not by creating a stub.
No stub skill was invented.

### Why hiding the scout is safe (the one thing worth checking before shipping this)

`hooks-wayfinder` names the scout in its own injected instruction
(`modules/hooks-wayfinder/amplifier_module_hooks_wayfinder/__init__.py:576`):

> "Before rendering: if a skill named 'wayfinder-scout' is **available** (load_skill),
> load and follow it …"

A hidden skill is **not removed from the injected skills index** — it moves from
`Available skills (use load_skill tool):` to `User-invoked skills (available via
/command):`, still rendered by name with a description
(`amplifier_module_tool_skills/hooks.py:_format_skills_list`). So that availability
check still resolves, and `load_skill(skill_name="wayfinder-scout")` still loads it.
This is asserted, not assumed — check 5/6 in `verify_hidden_skills.py`.

---

## 3. Verification — fail-before / pass-after, both instruments

**(a) Runtime check** (`verify_hidden_skills.py`) runs the shipped
`amplifier_module_tool_skills` discovery, `SkillsDiscovery.find()` (the
`load_skill(skill_name=…)` lookup path), `extract_skill_body()`, and the visibility
hook's own `_format_skills_list()` against this repo's `skills/`.

```
FAIL-BEFORE (skills/ as of 16e6e25)          PASS-AFTER (this branch)
  [FAIL] wayfinder-pack:  disable_model_invocation      [PASS] ×6 wayfinder-pack
  [FAIL] wayfinder-pack:  under 'User-invoked skills'   [PASS] ×6 wayfinder-scout
  [FAIL] wayfinder-pack:  absent from 'Available'       RESULT: PASS
  [FAIL] wayfinder-scout: (same three)                  exit=0
  RESULT: FAIL  exit=1
```
Both runs: `resolvable by name (load_skill lookup)` and `body extracts non-empty`
**PASS** — i.e. the acceptance criterion "it still loads by name after the change" is
verified directly against the changed file, not inferred.

**(b) Repo tripwire** (`test_skill_visibility.py`), run via the repo's standing command
`PYTHONPATH=modules/hooks-wayfinder python3 -m pytest modules/hooks-wayfinder/tests/ ledger/checks -q`:

| | result |
|---|---|
| baseline, before any edit | **152 passed** |
| new tripwire vs. unmodified `skills/` (`git stash push -- skills/`) | **2 failed, 3 passed** — `AssertionError: wayfinder-scout: expected 'disable-model-invocation: true'` |
| full suite, after the change | **157 passed** |

`ruff check` clean on all three new files (the repo at large is not ruff-format-clean;
2 tracked files and 4 pre-existing `ruff check` errors predate this lane and were left
alone).

**Not done, and why:** no live session / DTU verification. Spend authority was $0, and
the live check would only re-observe what (a) proves statically against the same shipped
code path. A reviewer wanting the live proof runs `/wayfinder-pack` in a session built from
this branch.

---

## 4. FINDING (honest negative): hiding a skill **grows** the always-on index by **+4.03%**

*(knob: `disable-model-invocation` on 2 skills · family: n/a, static render · confidence:
**measured** · evidence: `docs/lanes/hqks-wayfinder-catalog-reduction/measure_index_delta.py`,
82-skill host catalog from `~/.amplifier/cache/skills/*/skills`, shipped production config
`visibility_token_budget: 2500` from amplifier-bundle-skills `behaviors/skills.yaml:20`)*

|  | regular section | user-invoked section | total |
|---|---:|---:|---:|
| before (both visible) | 9,996 | 1,230 | **11,271** |
| after (both hidden) | 10,051 | 1,629 | **11,725** |
| delta | **+55** | **+399** | **+454 chars (+4.03%, ~+113 tok)** |

**Mechanism, from the renderer's own code:** the token budget bounds **only** the
regular index — `hooks.py` says so in as many words ("The token budget has never
covered this section … the per-line character cap is the ONLY thing bounding its
growth"). So hiding a skill (1) moves a full-cap line into an *unbudgeted* section
(+399) and (2) frees regular-section budget, which the tier algorithm immediately
spends on **longer descriptions for the skills that remain** (+55, not −N).

**What this means for the program.** `disable-model-invocation` is an
**auto-invocation control, not a head-size lever**. Hiding hand-run skills is still
right on the owner's stated grounds (they are run by hand; keeping them out of the
model's auto-select set reduces spurious invocation and menu noise) — but no lane
should bank a token saving from it. n=1 catalog, one host; the direction is structural
(it follows from the code, not from this sample), the magnitude is not.

Filed as a discovered item against the skills bundle (see §6).

---

## 5. Two corrections to the item's stated facts

1. **The lane worktree was 13 commits behind `origin/main`** (`ffa0f32` vs `16e6e25`),
   which is why cycle 65 could not locate `wayfinder-scout`: it did not exist on the
   stale base. The branch had **no** commits of its own (`git log origin/main..HEAD`
   empty), so it was fast-forwarded to `origin/main` before any edit — nothing was lost
   or reverted. **Manager action: check lane worktree freshness at launch**; a stale
   base silently turns "not present" into a false negative.
2. **CI is NOT on `origin/main`.** The item and GOAL state "This repo already has CI
   (confirmed: `j1e6-ci-wayfinder` merged `16196a1`)". Measured: `git cat-file -t
   16196a1` → *"fatal: Not a valid object name"*; `git merge-base --is-ancestor
   origin/lane/j1e6-ci-wayfinder origin/main` → **NOT-MERGED**; there is no `.github/`
   in `origin/main`. The j1e6 CI work exists only on its own unmerged branch. **The new
   tripwire therefore runs only under the standing test command until that CI lands.**

---

## 6. Discovered / follow-ups

- **`model_performance-c21w`** — the §4 defect: hiding a skill *increases* the
  always-on skills index, because the user-invoked section sits outside
  `visibility_token_budget`. Carries the measurement, the mechanism from the
  renderer's own code, its limits (n=1 catalog), and two untested candidate fixes.
- **`model_performance-napw`** — the §5 defect: lane worktrees can launch behind
  `origin/main`, and a stale base turned a real skill into a published "does not
  exist". Also covers the unverifiable `16196a1` CI claim.
- **Not filed, noted:** `bundle.dot` / `bundle.md` list no skills at all, so neither
  was stale before this change and neither is stale after. `foundation:recipes/validate-bundle-repo.yaml`
  was not run (LLM spend, authority $0); this change adds no module, agent or skill
  directory, so bundle structure is unchanged.

## 7. Census safety

`grep -l /tmp/ ~/.local/share/uv/tools/amplifier/lib/python3.13/site-packages/*.pth`
→ **no output** (checked after the last measurement). No `amplifier` process was run at
any point in this lane; every check imports the module directly.
