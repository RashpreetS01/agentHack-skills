"""Data models for AgentLab."""

from __future__ import annotations

from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class Difficulty(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class Category(str, Enum):
    WEB_APPLICATION = "web-application"
    NETWORK = "network"
    PRIVILEGE_ESCALATION = "privilege-escalation"
    CRYPTOGRAPHY = "cryptography"
    OSINT = "osint"
    FORENSICS = "forensics"


class Flag(BaseModel):
    id: str
    hash: str  # SHA-256 of the flag value
    points: int = 100
    hint: str = ""


class LabChallenge(BaseModel):
    id: str
    name: str
    description: str
    difficulty: Difficulty
    category: Category
    flags: list[Flag]
    timeout_minutes: int = 60
    learning_objectives: list[str]
    skill_ref: str = ""  # Path to companion SKILL.md
    compose_file: str = ""  # Path to docker-compose.yml
    tags: list[str] = Field(default_factory=list)


class LabSession(BaseModel):
    session_id: str
    challenge_id: str
    started_at: str
    expires_at: str
    container_ids: list[str] = Field(default_factory=list)
    flags_captured: list[str] = Field(default_factory=list)
    score: int = 0
    hints_used: int = 0


class CommandResult(BaseModel):
    exit_code: int
    stdout: str
    stderr: str
    truncated: bool = False

    @property
    def success(self) -> bool:
        return self.exit_code == 0


class FlagVerifyResult(BaseModel):
    correct: bool
    flag_id: str
    points_awarded: int
    message: str
    total_score: int


class ProgressState(BaseModel):
    agent_id: str
    challenges_attempted: list[str] = Field(default_factory=list)
    challenges_completed: list[str] = Field(default_factory=list)
    total_score: int = 0
    skill_levels: dict[str, int] = Field(default_factory=dict)
    active_session: LabSession | None = None
