"""Flag verification engine for AgentLab."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .models import Flag, FlagVerifyResult, LabSession

LABS_ROOT = Path(__file__).parent.parent.parent / "labs"


def _load_flags(challenge_id: str) -> list[Flag]:
    """Load flag definitions from lab.json."""
    for subdir in LABS_ROOT.iterdir():
        if subdir.is_dir():
            for lab in subdir.iterdir():
                if lab.is_dir() and lab.name == challenge_id:
                    lab_json = lab / "lab.json"
                    if lab_json.exists():
                        data = json.loads(lab_json.read_text())
                        return [Flag(**f) for f in data.get("flags", [])]
    return []


def verify_flag(session: LabSession, submitted_flag: str) -> FlagVerifyResult:
    """Verify a submitted flag against the challenge's flag list."""
    flags = _load_flags(session.challenge_id)
    submitted_hash = hashlib.sha256(submitted_flag.strip().encode()).hexdigest()

    for flag in flags:
        if flag.hash == submitted_hash:
            if flag.id in session.flags_captured:
                return FlagVerifyResult(
                    correct=True,
                    flag_id=flag.id,
                    points_awarded=0,
                    message="Flag already captured! No additional points.",
                    total_score=session.score,
                )
            session.flags_captured.append(flag.id)
            session.score += flag.points
            return FlagVerifyResult(
                correct=True,
                flag_id=flag.id,
                points_awarded=flag.points,
                message=f"Correct! +{flag.points} points. Total: {session.score}",
                total_score=session.score,
            )

    return FlagVerifyResult(
        correct=False,
        flag_id="",
        points_awarded=0,
        message="Incorrect flag. Keep going — check the hints if needed.",
        total_score=session.score,
    )


def get_hint(challenge_id: str, flag_index: int = 0) -> str:
    """Return a hint for a specific flag in a challenge."""
    flags = _load_flags(challenge_id)
    if flag_index < len(flags) and flags[flag_index].hint:
        return flags[flag_index].hint
    return "No hint available for this flag. Review the SKILL.md workflow steps."
