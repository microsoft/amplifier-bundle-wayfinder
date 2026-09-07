#!/usr/bin/env python3
"""Measure what hiding these two skills actually does to the always-on skills index.

Renders the REAL visibility hook (`_format_skills_list`) twice over the same host
catalog -- once with `wayfinder-pack` / `wayfinder-scout` hidden, once with them
visible -- under the SHIPPED production config (`visibility_token_budget: 2500`,
from amplifier-bundle-skills `behaviors/skills.yaml`). Reports per-section char
counts so the direction of the delta is attributable, not just asserted.

Static: no `amplifier` process, no session, no provider call. $0.

Usage:
    python3 docs/lanes/hqks-wayfinder-catalog-reduction/measure_index_delta.py
    python3 ... measure_index_delta.py --tool-skills PATH --skills-cache PATH
"""

from __future__ import annotations

import argparse
import copy
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
UNDER_TEST = ("wayfinder-pack", "wayfinder-scout")
# The shipped default, amplifier-bundle-skills behaviors/skills.yaml:20.
PROD_CONFIG = {
    "enabled": True,
    "inject_role": "user",
    "visibility_token_budget": 2500,
    "ephemeral": True,
    "priority": 20,
}


def split_sections(
    rendered: str, regular_header: str, user_header: str
) -> tuple[str, str]:
    regular, _, user = rendered.partition(user_header)
    if regular_header not in regular:
        regular = ""
    return regular, user


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--tool-skills", default=None)
    ap.add_argument(
        "--skills-cache",
        default=str(Path.home() / ".amplifier" / "cache" / "skills"),
        help="dir whose */skills children form the host catalog",
    )
    args = ap.parse_args()

    ts = args.tool_skills
    if ts is None:
        cands = sorted(
            (Path.home() / ".amplifier" / "cache").glob(
                "*/modules/tool-skills/amplifier_module_tool_skills"
            )
        )
        if not cands:
            sys.exit("FAIL: pass --tool-skills <path/to/modules/tool-skills>")
        ts = str(cands[0].parent)
    sys.path.insert(0, ts)

    from amplifier_module_tool_skills.discovery import discover_skills  # noqa: PLC0415
    from amplifier_module_tool_skills.hooks import (  # noqa: PLC0415
        DEFAULT_VISIBILITY_TOKEN_BUDGET,
        REGULAR_SKILLS_HEADER,
        USER_INVOKED_SKILLS_HEADER,
        SkillsVisibilityHook,
    )

    dirs = sorted(Path(args.skills_cache).glob("*/skills"))
    catalog: dict = {}
    for d in dirs:
        for name, meta in discover_skills(d).items():
            catalog.setdefault(name, meta)
    for name, meta in discover_skills(REPO_ROOT / "skills").items():
        catalog[name] = meta  # this repo is authoritative for the two under test

    missing = [n for n in UNDER_TEST if n not in catalog]
    if missing:
        sys.exit(f"FAIL: not in catalog: {missing}")

    after = dict(catalog)
    before = dict(catalog)
    for n in UNDER_TEST:
        m = copy.copy(before[n])
        m.disable_model_invocation = False
        before[n] = m

    rendered = {}
    for label, cat in (("before", before), ("after", after)):
        hook = SkillsVisibilityHook(skills=cat, config=dict(PROD_CONFIG))
        rendered[label] = hook._format_skills_list(cat)  # noqa: SLF001

    print(
        f"catalog        : {len(catalog)} skills from {len(dirs)} source dirs + {REPO_ROOT.name}/skills"
    )
    print(
        f"config         : visibility_token_budget={PROD_CONFIG['visibility_token_budget']} "
        f"(module default is {DEFAULT_VISIBILITY_TOKEN_BUDGET})"
    )
    print(
        f"hidden (after) : {sum(1 for m in after.values() if m.disable_model_invocation)} skills\n"
    )

    print(f"{'':<10}{'regular':>12}{'user-invoked':>16}{'total':>12}")
    rows = {}
    for label in ("before", "after"):
        reg, usr = split_sections(
            rendered[label], REGULAR_SKILLS_HEADER, USER_INVOKED_SKILLS_HEADER
        )
        rows[label] = (len(reg), len(usr), len(rendered[label]))
        print(f"{label:<10}{len(reg):>12}{len(usr):>16}{len(rendered[label]):>12}")
    d = tuple(a - b for a, b in zip(rows["after"], rows["before"], strict=True))
    print(f"{'delta':<10}{d[0]:>+12}{d[1]:>+16}{d[2]:>+12}   chars")
    pct = d[2] / rows["before"][2] * 100
    print(
        f"\ntotal index: {rows['before'][2]} -> {rows['after'][2]} chars "
        f"({d[2]:+d}, {pct:+.2f}%; ~{d[2] // 4:+d} tok at 4 chars/tok)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
