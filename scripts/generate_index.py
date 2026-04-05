#!/usr/bin/env python3
"""
Generate index.json from all skills in the skills/ directory.

[WARN]  Run this whenever you add a new skill:
    python scripts/generate_index.py

The index.json enables fast scanning by AI agents without loading all SKILL.md files.
"""

import json
import re
from datetime import UTC, datetime
from pathlib import Path

try:
    import yaml
    USE_YAML = True
except ImportError:
    USE_YAML = False

REPO_ROOT = Path(__file__).parent.parent
SKILLS_DIR = REPO_ROOT / "skills"
INDEX_FILE = REPO_ROOT / "index.json"

FRONTMATTER_RE = re.compile(r"^---\r?\n(.*?)\r?\n---", re.DOTALL)


def parse_frontmatter(text: str) -> dict:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return {}
    raw = match.group(1)
    if USE_YAML:
        return yaml.safe_load(raw) or {}
    # Fallback: handle >- multi-line scalars manually
    result = {}
    lines = raw.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        if ":" in line and not line.startswith(" "):
            key, _, val = line.partition(":")
            key = key.strip()
            val = val.strip()
            if val in (">-", ">", "|", "|-"):
                # Collect indented continuation lines
                parts = []
                i += 1
                while i < len(lines) and (lines[i].startswith(" ") or lines[i].startswith("\t")):
                    parts.append(lines[i].strip())
                    i += 1
                result[key] = " ".join(parts)
                continue
            result[key] = val.strip('"').strip("'")
        i += 1
    return result
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
            print(f"  [WARN]  Skipping {skill_dir.name}: no name in frontmatter")
            continue
        skills.append(
            {
                "name": fm["name"],
                "description": fm.get("description", "").replace("\n  ", " ").strip(),
                "domain": fm.get("domain", "cybersecurity"),
                "subdomain": fm.get("subdomain", ""),
                "difficulty": fm.get("difficulty", "beginner"),
                "mitre_techniques": (
                    fm["mitre_techniques"] if isinstance(fm.get("mitre_techniques"), list)
                    else [t.strip() for t in str(fm.get("mitre_techniques", "")).split(",") if t.strip()]
                ),
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
    print(f"[OK] Generated index.json with {len(skills)} skills")


if __name__ == "__main__":
    main()
