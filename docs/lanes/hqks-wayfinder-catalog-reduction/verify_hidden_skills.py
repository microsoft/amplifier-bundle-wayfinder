#!/usr/bin/env python3
"""Verify this repo's skills are hidden from the auto-invocable index AND still
loadable by name.

Runs the REAL `amplifier_module_tool_skills` code (discovery + the visibility
hook's own formatter) against this repo's `skills/` directory. No `amplifier`
process is started, no session is created, no provider is called -- so it costs
$0 and cannot touch the host install (see the lane's census-safety note).

Checks, per skill:
  1. discovered at all
  2. `disable_model_invocation is True`      -> hidden from "Available skills"
  3. `user_invocable is True`                -> `/name` still dispatches
  4. `SkillsDiscovery.find(name)` resolves   -> `load_skill(skill_name=...)` path
  5. body extracts non-empty                 -> there is content to load
  6. the visibility hook renders it under "User-invoked skills", NOT under
     "Available skills"

Check 6 is why hiding `wayfinder-scout` is safe: hooks-wayfinder's
`_SCOUT_INSTRUCTION` says "if a skill named 'wayfinder-scout' is available
(load_skill)" -- a hidden skill is still named in the injected index, just in
the other section, so that availability check still resolves.

Usage:
    python3 docs/lanes/hqks-wayfinder-catalog-reduction/verify_hidden_skills.py
    python3 ... verify_hidden_skills.py --tool-skills /path/to/modules/tool-skills

Exit code 0 = every check passed.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
EXPECTED_HIDDEN = ("wayfinder-pack", "wayfinder-scout")


def find_tool_skills(explicit: str | None) -> Path:
    """Locate an importable `modules/tool-skills` package directory."""
    if explicit:
        p = Path(explicit).expanduser().resolve()
        if not (p / "amplifier_module_tool_skills").is_dir():
            sys.exit(f"FAIL: {p} does not contain amplifier_module_tool_skills/")
        return p
    cache = Path.home() / ".amplifier" / "cache"
    candidates = sorted(
        cache.glob("*/modules/tool-skills/amplifier_module_tool_skills")
    )
    if not candidates:
        sys.exit(
            "FAIL: could not locate amplifier_module_tool_skills under "
            f"{cache}. Pass --tool-skills <path/to/modules/tool-skills>."
        )
    return candidates[0].parent


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--tool-skills", default=None, help="path to modules/tool-skills")
    args = ap.parse_args()

    sys.path.insert(0, str(find_tool_skills(args.tool_skills)))
    from amplifier_module_tool_skills import SkillsDiscovery  # noqa: PLC0415
    from amplifier_module_tool_skills.discovery import (  # noqa: PLC0415
        discover_skills,
        extract_skill_body,
    )
    from amplifier_module_tool_skills.hooks import (  # noqa: PLC0415
        REGULAR_SKILLS_HEADER,
        USER_INVOKED_SKILLS_HEADER,
        SkillsVisibilityHook,
    )

    skills_dir = REPO_ROOT / "skills"
    skills = discover_skills(skills_dir)
    discovery = SkillsDiscovery(skills)
    hook = SkillsVisibilityHook(skills=skills, config={})
    rendered = hook._format_skills_list(skills)  # noqa: SLF001 -- the real formatter

    regular_block, _, user_block = rendered.partition(USER_INVOKED_SKILLS_HEADER)
    if REGULAR_SKILLS_HEADER not in regular_block:
        regular_block = ""  # no auto-invocable section rendered at all

    failures: list[str] = []
    print(f"skills dir : {skills_dir}")
    print(f"discovered : {sorted(skills)}\n")

    for name in EXPECTED_HIDDEN:
        meta = skills.get(name)
        if meta is None:
            failures.append(f"{name}: NOT DISCOVERED under {skills_dir}")
            continue
        checks = {
            "hidden from auto-invocation (disable_model_invocation)": meta.disable_model_invocation
            is True,
            "still user-invocable (/command)": bool(meta.user_invocable),
            "resolvable by name (load_skill lookup)": discovery.find(name) is not None,
            "body extracts non-empty": bool(
                (extract_skill_body(Path(meta.path)) or "").strip()
            ),
            "rendered under 'User-invoked skills'": f"**{name}**" in user_block,
            "absent from 'Available skills'": f"**{name}**" not in regular_block,
        }
        for label, ok in checks.items():
            print(f"  [{'PASS' if ok else 'FAIL'}] {name}: {label}")
            if not ok:
                failures.append(f"{name}: {label}")
        print()

    if failures:
        print("RESULT: FAIL")
        for f in failures:
            print(f"  - {f}")
        return 1
    print(
        f"RESULT: PASS ({len(EXPECTED_HIDDEN)} skills hidden and still loadable by name)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
