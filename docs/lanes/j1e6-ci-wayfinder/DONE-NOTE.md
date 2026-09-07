# Lane j1e6 — CI for amplifier-bundle-wayfinder

Item: `model_performance-j1e6` (project `model_performance`)
Repo: `microsoft/amplifier-bundle-wayfinder`
Branch: `lane/j1e6-ci-wayfinder` → PR **#13**
Outcome: **A. RESOLVED** — every deliverable DONE. No deliverable was cap-bound.

---

## Deliverables

| # | Deliverable | State |
|---|---|---|
| 1 | `.github/workflows/ci.yml` running the real suite, ruff pinned, `push:main` + `pull_request`, no path filters / `continue-on-error` / `\|\| true` | **DONE** |
| 2 | BOTH run URLs quoted in the PR body; RED job log shows the suite executing with a genuine test failure | **DONE** |
| 3 | Scratch PR closed, branch deleted — verified, not assumed | **DONE** |
| 4 | Statement of what the suite covers | **DONE** — 152 real tests, no import smoke needed |
| 5 | Clean main red → fixed as separate named commits, never by weakening the workflow | **DONE** — 4 findings, commit `6326156` |
| 6 | Draft PR, marked ready when green; **not merged** | **DONE** — #13 ready, manager merges |

## Shape chosen

**bundle-with-`modules/`** — this repo carries `modules/hooks-wayfinder/` with its own tests, so it takes the context-intelligence shape (per-module install + pytest, ruff pinned, plus a bundle-structure check that YAML-parses `bundle.md` frontmatter and `behaviors/*.yaml`), as the item's template prescribes.

Three job definitions → five checks:

| check | command |
|---|---|
| `Lint` | `uvx ruff@0.16.6 check --isolated --select E4,E7,E9,F .` |
| `Tests (Python 3.11/3.12/3.13)` | the repo's own standing command, verbatim from `AGENTS.md` |
| `Bundle structure (YAML)` | parse `bundle.md` frontmatter + `behaviors/*.yaml`, require `bundle.name` |

There is no `Makefile`, so `AGENTS.md` § *"The standing test command"* is the check target honored verbatim:

```
PYTHONPATH=modules/hooks-wayfinder python3 -m pytest modules/hooks-wayfinder/tests/ ledger/checks -q
```

## Red-then-green gate

| | run | result |
|---|---|---|
| RED (invalid — see below) | [34150005099](https://github.com/microsoft/amplifier-bundle-wayfinder/actions/runs/34150005099) | 5/5 red, but at **setup** |
| **RED (the proof)** | [34150101236](https://github.com/microsoft/amplifier-bundle-wayfinder/actions/runs/34150101236) | 5/5 red; tests show `2 failed, 152 passed` |
| **GREEN** | [34150309649](https://github.com/microsoft/amplifier-bundle-wayfinder/actions/runs/34150309649) | 5/5 green; `152 passed` ×3, `All checks passed!`, `Bundle structure OK.` |

Scratch PR **#12** — closed, branch `ci/red-proof-j1e6` deleted. Verified by remote read (`git ls-remote --heads origin ci/red-proof-j1e6` → empty; `gh pr view 12` → CLOSED), not assumed.

Both test roots proven collected independently: one deliberate failure placed in `modules/hooks-wayfinder/tests/`, a second in `ledger/checks/`; both appear by name in the red log.

## Top finding — the gate caught a defect in my own first workflow

The first red-proof run was red on all five checks and **proved nothing**:

```
##[error]No file matched to [**/uv.lock], make sure you have checked out the target repository
```

`astral-sh/setup-uv` with `enable-cache: true` caches keyed on `**/uv.lock`; this repo commits no lockfile anywhere, so the setup step hard-failed before ruff or pytest ever ran. At the check-mark level that is indistinguishable from a real red. This is exactly the failure mode the non-negotiable gate exists to catch, and it caught it on the first attempt.

`enable-cache` was dropped (with the reason recorded in the workflow file) and the proof re-run.

**Transferable to the sibling CI lanes:** `amplifier-bundle-notify`'s workflow (`lane/nxxf-ci-notify`) writes `enable-caching: true` — not a valid `setup-uv` input name, so it is silently ignored there and never bit. Any sibling lane that "corrects" that typo to `enable-cache: true` in a repo with no lockfile will hard-fail setup. Do not copy `enable-cache` into a lockfile-less repo.

## Second finding — clean main was RED on lint

Four genuine findings at `16e6e25`, all in one file (`docs/lanes/smy5-patch-wayfinder/fidelity_check.py`, a one-off analysis script from the prior lane):

```
:28  E401  Multiple imports on one line
:79  E741  Ambiguous variable name `l`
:83  E702  Multiple statements on one line (semicolon)
:91  E701  Multiple statements on one line (colon)
```

Fixed in a **separate named commit** `6326156`, per the b4xs precedent the item cites — never `continue-on-error`, never a narrowed lint selection.

Proven behavior-neutral: the script's full stdout and exit code are byte-identical before and after against the same base ref (`python3 docs/lanes/smy5-patch-wayfinder/fidelity_check.py origin/main` → exit 0, `MISSING IN LEAN: NONE`, 0 uncovered sentences, both files).

## Suite coverage — 152 real tests, no import smoke

| file | tests |
|---|---:|
| `modules/hooks-wayfinder/tests/test_always_on_head.py` | 66 |
| `ledger/checks/test_ledger.py` | 28 |
| `modules/hooks-wayfinder/tests/test_packet_contract.py` | 27 |
| `modules/hooks-wayfinder/tests/test_prompt_builders.py` | 13 |
| `modules/hooks-wayfinder/tests/test_adoption_aware.py` | 13 |
| `modules/hooks-wayfinder/tests/test_root_only.py` | 5 |
| **total** | **152** |

Nothing skipped, ignored, or deselected. Verified green on Python 3.11, 3.12 and 3.13 both locally and in CI.

## Choices recorded (no human was waited on)

1. **`amplifier-core` installed explicitly in CI.** `modules/hooks-wayfinder/pyproject.toml` deliberately does not declare it (`# amplifier-core is a PEER dependency (provided by the host process) — do NOT declare it.`) while `__init__.py:60` imports `HookResult` from it. CI is not a host process, so CI supplies it. Framed as a convention **honored**, not a packaging defect — unlike the sibling `hooks-notify-push` case, here the omission is documented and intentional. No module change proposed.
2. **Pinning rule:** pin the tools that *define* the gate (`ruff==0.16.6`, `pytest==9.1.1`, `pytest-asyncio==1.4.0`) so it cannot drift red without an edit to the workflow; **float** the peer dependency under test (`amplifier-core>=1.6.1`) so a real break against current core surfaces as a red run.
3. **Python matrix 3.11/3.12/3.13.** The module declares `requires-python = ">=3.11"`; the matrix checks that claim rather than taking it on faith. Cost is ~30s per check.
4. **`ruff format --check` not wired**, reported instead: 2 files would be reformatted at `16e6e25`. Reformatting source is out of scope for a workflow PR and a formatter gate red on day one is worse than none.
5. **ruff's full modern default set not wired**, reported instead: 8 opinion-tier findings (`PLW1510`×2, `I001`, `UP031`, `SIM905`, `RUF100`, `FURB167`, `C408`).
6. **This DONE-NOTE is committed to the PR**, making it a third file alongside the workflow and the lint fix. The item says the real PR "carries the workflow ONLY"; Procedure 4 says lane artifacts go under the artifact root in-repo, and the prior lane (`smy5`) did exactly that in this repo (`docs/lanes/smy5-patch-wayfinder/DONE-NOTE.md`, merged at `16e6e25`). Followed repo precedent + Procedure 4. Docs-only, no CI or source impact.

## Spend

**$0.00** against a $0 authority (`0 runs × 0 arms × $0 / 1.00 = $0.00`, slack $0.00). No API calls, no DTU, no containers, no infrastructure registered and none to tear down. GitHub Actions minutes only: 3 runs × 5 short `ubuntu-latest` checks (~7–11s each).

The cap's arithmetic closes: this deliverable buys no runs, so a $0 authority funds it completely. Nothing was dropped for cap reasons; no deliverable is NOT-POSSIBLE.

## Not done, on purpose

**Not merged.** PR #13 is ready for review with a green run. The manager merges, then confirms `main` HEAD reports a successful check-run (`gh api repos/microsoft/amplifier-bundle-wayfinder/commits/main/check-runs`) — *configured is not installed*.
