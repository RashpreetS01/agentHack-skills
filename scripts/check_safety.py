#!/usr/bin/env python3
"""
Check all skill files for required safety disclaimers.
CI enforcement — every skill MUST contain the safety notice.
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
SKILLS_DIR = REPO_ROOT / "skills"

REQUIRED_PHRASES = [
    "Educational Use Only",
    "authorized",
]


def check_skill(skill_dir: Path) -> list[str]:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return []

    text = skill_md.read_text(encoding="utf-8")
    errors = []

    for phrase in REQUIRED_PHRASES:
        if phrase not in text:
            errors.append(f"{skill_dir.name}: missing safety phrase '{phrase}'")

    return errors


def main() -> int:
    all_errors = []
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        if skill_dir.is_dir():
            all_errors.extend(check_skill(skill_dir))

    if all_errors:
        print(f"[FAIL] Safety check failed:\n")
        for err in all_errors:
            print(f"  • {err}")
        return 1
    print(f"[OK] Safety check passed — all skills contain required disclaimers.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
