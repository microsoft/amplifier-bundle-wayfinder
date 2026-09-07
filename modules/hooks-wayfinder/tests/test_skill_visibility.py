"""Skill-catalog pin: this repo's skills are hand-run, and stay hand-run.

Both skills this bundle ships are invoked *deliberately*, never auto-selected
by a model:

* `wayfinder-pack` -- the authoring skill, run by a human writing a packet
  (`/wayfinder-pack`, or `load_skill(skill_name="wayfinder-pack")`).
* `wayfinder-scout` -- named explicitly by the channel's own injected
  instruction (`hooks-wayfinder`'s `_SCOUT_INSTRUCTION`) and directly runnable
  by a reader auditing what they have already adopted.

Neither should sit in the auto-invocable "Available skills" index that every
session pays for, so both carry `disable-model-invocation: true`
(`model_performance-hqks`, owner-approved 2026-09-07).

The two frontmatter keys are a PAIR and both are load-bearing:

* dropping `disable-model-invocation` puts the skill back in the auto-invocable
  index;
* dropping `user-invocable` breaks `/wayfinder-pack` dispatch AND the
  availability check in `_SCOUT_INSTRUCTION` -- a hidden skill still renders by
  name under "User-invoked skills", which is precisely why hiding the scout is
  safe. A skill that is neither auto-invocable nor user-invocable is reachable
  only by an agent that already knows its exact name.

Depends on nothing but stdlib + PyYAML, so it runs in CI without the
`tool-skills` module present. The end-to-end check against the real
`amplifier_module_tool_skills` discovery + visibility renderer lives at
`docs/lanes/hqks-wayfinder-catalog-reduction/verify_hidden_skills.py`.

Run:
    PYTHONPATH=modules/hooks-wayfinder python3 -m pytest modules/hooks-wayfinder/tests -q
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[3]
SKILLS_DIR = ROOT / "skills"

# Every skill this bundle ships is hand-run. If a future skill is genuinely
# meant to be model-selected, add it here as an explicit exception with a
# reason -- do not silently loosen the rule.
HAND_RUN_SKILLS = ("wayfinder-pack", "wayfinder-scout")


def _frontmatter(name: str) -> dict:
    path = SKILLS_DIR / name / "SKILL.md"
    assert path.is_file(), f"{path} is missing"
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---\n"), f"{path} has no YAML frontmatter"
    _, _, rest = text.partition("---\n")
    body, sep, _ = rest.partition("\n---")
    assert sep, f"{path} has an unterminated frontmatter block"
    data = yaml.safe_load(body)
    assert isinstance(data, dict), f"{path} frontmatter did not parse to a mapping"
    return data


def test_every_shipped_skill_is_covered_by_this_pin():
    """A new skill directory must make a deliberate visibility decision."""
    on_disk = sorted(p.name for p in SKILLS_DIR.iterdir() if (p / "SKILL.md").is_file())
    assert on_disk == sorted(HAND_RUN_SKILLS), (
        "skills/ changed. Decide the new skill's visibility and update "
        "HAND_RUN_SKILLS (with a reason if it is deliberately model-invocable)."
    )


@pytest.mark.parametrize("name", HAND_RUN_SKILLS)
def test_hand_run_skill_is_hidden_from_the_auto_invocable_index(name: str):
    fm = _frontmatter(name)
    assert fm.get("disable-model-invocation") is True, (
        f"{name}: expected `disable-model-invocation: true` -- this skill is "
        "run by hand and must not sit in the always-on auto-invocable index."
    )


@pytest.mark.parametrize("name", HAND_RUN_SKILLS)
def test_hand_run_skill_stays_reachable_by_name(name: str):
    fm = _frontmatter(name)
    assert fm.get("user-invocable") is True, (
        f"{name}: expected `user-invocable: true` -- hiding a skill from the "
        "auto-invocable index must never make it unreachable."
    )
    assert fm.get("name") == name, (
        f"{name}: frontmatter `name` must match its directory"
    )
