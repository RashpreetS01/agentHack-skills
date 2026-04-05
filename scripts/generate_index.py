#!/usr/bin/env python3
"""
Generate index.json from all skills in the skills/ directory.

⚠️  Run this whenever you add a new skill:
    python scripts/generate_index.py

The index.json enables fast scanning by AI agents without loading all SKILL.md files.
"""

import json
import re
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
SKILLS_DIR = REPO_ROOT / "skills"
INDEX_FILE = REPO_ROOT / "index.json"

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)


def parse_frontmatter(text: str) -> dict:
    """Parse YAML frontmatter without a YAML dependency."""
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}
    result = {}
    for line in match.group(1).splitlines():
        if ":" in line and not line.startswith(" "):
            key, _, val = line.partition(":")
            result[key.strip()] = val.strip().strip('"').strip("'")
    return result


def main() -> None:
    skills = []
    for skill_dir in sorted(SKILLS_DIR.iterdir()):
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue
        text = skill_md.read_text(encoding="utf-8")
        fm = parse_frontmatter(text)
        if not fm.get("name"):
            print(f"  ⚠️  Skipping {skill_dir.name}: no name in frontmatter")
            continue
        skills.append(
            {
                "name": fm["name"],
                "description": fm.get("description", "").replace("\n  ", " ").strip(),
                "domain": fm.get("domain", "cybersecurity"),
                "subdomain": fm.get("subdomain", ""),
                "difficulty": fm.get("difficulty", "beginner"),
                "mitre_techniques": [
                    t.strip().strip("[]").strip()
                    for t in fm.get("mitre_techniques", "").split(",")
                    if t.strip()
                ],
                "path": f"skills/{skill_dir.name}",
            }
        )

    index = {
        "version": "1.0.0",
        "generated_at": datetime.now(UTC).isoformat(),
        "repository": "https://github.com/mukul975/agentHack-skills",
        "companion_repo": "https://github.com/mukul975/Anthropic-Cybersecurity-Skills",
        "domain": "cybersecurity",
        "focus": "ethical-hacking-education",
        "total_skills": len(skills),
        "safety_notice": "ALL skills and labs are for educational use in isolated environments only.",
        "skills": skills,
    }

    INDEX_FILE.write_text(json.dumps(index, indent=2), encoding="utf-8")
    print(f"✅ Generated index.json with {len(skills)} skills")


if __name__ == "__main__":
    main()
