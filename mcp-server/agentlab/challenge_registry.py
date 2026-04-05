"""Challenge registry — loads all lab.json files and indexes available challenges."""

from __future__ import annotations

import json
from pathlib import Path

from .models import Category, Difficulty, Flag, LabChallenge

LABS_ROOT = Path(__file__).parent.parent.parent / "labs"

_REGISTRY: dict[str, LabChallenge] | None = None


def _load_registry() -> dict[str, LabChallenge]:
    registry: dict[str, LabChallenge] = {}
    if not LABS_ROOT.exists():
        return registry

    for category_dir in sorted(LABS_ROOT.iterdir()):
        if not category_dir.is_dir():
            continue
        for lab_dir in sorted(category_dir.iterdir()):
            lab_json = lab_dir / "lab.json"
            if not lab_json.exists():
                continue
            try:
                data = json.loads(lab_json.read_text())
                challenge = LabChallenge(
                    id=data["id"],
                    name=data["name"],
                    description=data["description"],
                    difficulty=Difficulty(data.get("difficulty", "beginner")),
                    category=Category(data.get("category", "web-application")),
                    flags=[Flag(**f) for f in data.get("flags", [])],
                    timeout_minutes=data.get("timeout_minutes", 60),
                    learning_objectives=data.get("learning_objectives", []),
                    skill_ref=data.get("skill_ref", ""),
                    compose_file=str(lab_dir / "docker-compose.yml"),
                    tags=data.get("tags", []),
                )
                registry[challenge.id] = challenge
            except Exception as e:
                print(f"Warning: Could not load {lab_json}: {e}")

    return registry


def get_registry() -> dict[str, LabChallenge]:
    global _REGISTRY
    if _REGISTRY is None:
        _REGISTRY = _load_registry()
    return _REGISTRY


def get_challenge(challenge_id: str) -> LabChallenge | None:
    return get_registry().get(challenge_id)


def list_challenges(
    category: str | None = None,
    difficulty: str | None = None,
) -> list[LabChallenge]:
    challenges = list(get_registry().values())
    if category:
        challenges = [c for c in challenges if c.category.value == category]
    if difficulty:
        challenges = [c for c in challenges if c.difficulty.value == difficulty]
    return sorted(challenges, key=lambda c: (c.difficulty.value, c.name))
