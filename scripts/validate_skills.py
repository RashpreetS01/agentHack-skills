#!/usr/bin/env python3
"""
Validate all skill files against the agentskills.io format requirements.

Run: python scripts/validate_skills.py

Exit code 0 = all valid, 1 = validation errors found.
"""

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
SKILLS_DIR = REPO_ROOT / "skills"

REQUIRED_FRONTMATTER = ["name", "description", "domain", "subdomain", "tags", "difficulty", "version", "author", "license"]
REQUIRED_SECTIONS = ["## When to Use", "## Prerequisites", "## Workflow", "## Key Concepts", "## Tools", "## Output"]
SAFETY_DISCLAIMER = "Educational Use Only"
VALID_DIFFICULTIES = {"beginner", "intermediate", "advanced"}
VALID_DOMAINS = {"cybersecurity"}
VALID_LICENSES = {"Apache-2.0"}

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)


def parse_frontmatter(text: str) -> dict:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}
    result = {}
    for line in match.group(1).splitlines():
        if ":" in line and not line.startswith(" "):
            key, _, val = line.partition(":")
            result[key.strip()] = val.strip().strip('"').strip("'")
    return result


def validate_skill(skill_dir: Path) -> list[str]:
    errors = []
    skill_md = skill_dir / "SKILL.md"
    license_file = skill_dir / "LICENSE"

    if not skill_md.exists():
        return [f"{skill_dir.name}: missing SKILL.md"]

    if not license_file.exists():
        errors.append(f"{skill_dir.name}: missing LICENSE file")

    text = skill_md.read_text(encoding="utf-8")

    # Frontmatter
    fm = parse_frontmatter(text)
    if not fm:
        errors.append(f"{skill_dir.name}: no YAML frontmatter found")
        return errors

    for field in REQUIRED_FRONTMATTER:
        if field not in fm or not fm[field]:
            errors.append(f"{skill_dir.name}: missing frontmatter field '{field}'")

    if fm.get("difficulty") and fm["difficulty"] not in VALID_DIFFICULTIES:
        errors.append(f"{skill_dir.name}: invalid difficulty '{fm['difficulty']}' (must be one of {VALID_DIFFICULTIES})")

    if fm.get("domain") and fm["domain"] not in VALID_DOMAINS:
        errors.append(f"{skill_dir.name}: invalid domain '{fm['domain']}'")

    if fm.get("license") and fm["license"] not in VALID_LICENSES:
        errors.append(f"{skill_dir.name}: invalid license '{fm['license']}' (must be Apache-2.0)")

    # Sections
    for section in REQUIRED_SECTIONS:
        if section not in text:
            errors.append(f"{skill_dir.name}: missing required section '{section}'")

    # Safety disclaimer
    if SAFETY_DISCLAIMER not in text:
        errors.append(f"{skill_dir.name}: missing safety disclaimer ('Educational Use Only')")

    # Name consistency
    if fm.get("name") and fm["name"] != skill_dir.name:
        errors.append(f"{skill_dir.name}: frontmatter name '{fm['name']}' doesn't match directory name")

    return errors


def main() -> int:
    all_errors = []
    skill_count = 0

    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        if skill_dir.is_dir():
            errors = validate_skill(skill_dir)
            all_errors.extend(errors)
            skill_count += 1

    if all_errors:
        print(f"❌ Validation failed ({len(all_errors)} error(s) in {skill_count} skills):\n")
        for err in all_errors:
            print(f"  • {err}")
        return 1
    else:
        print(f"✅ All {skill_count} skills valid.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
