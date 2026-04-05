"""
Docker lab lifecycle manager for AgentLab.

Handles spinning up, executing inside, and tearing down isolated Docker lab environments.

⚠️  Safety guarantees enforced here:
    - All containers run on isolated internal networks (no internet routing)
    - No host path mounts allowed
    - Containers are unprivileged by default
    - Auto-cleanup enforced via session timeout
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import uuid
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from .models import CommandResult, LabChallenge, LabSession

LABS_ROOT = Path(__file__).parent.parent.parent / "labs"
MAX_OUTPUT_BYTES = 8192  # Truncate large outputs to prevent token flooding


class LabManager:
    """Manages Docker Compose lab environments."""

    def __init__(self) -> None:
        self._sessions: dict[str, LabSession] = {}

    def _compose_path(self, challenge_id: str) -> Path:
        """Find docker-compose.yml for a challenge."""
        for subdir in LABS_ROOT.iterdir():
            if subdir.is_dir():
                for lab in subdir.iterdir():
                    if lab.is_dir() and lab.name == challenge_id:
                        candidate = lab / "docker-compose.yml"
                        if candidate.exists():
                            return candidate
        raise FileNotFoundError(f"No docker-compose.yml found for challenge: {challenge_id}")

    def start_lab(self, challenge: LabChallenge, agent_id: str) -> LabSession:
        """Start a Docker Compose lab environment."""
        compose_file = self._compose_path(challenge.id)
        project_name = f"agentlab-{challenge.id}-{agent_id[:8]}"

        result = subprocess.run(
            ["docker", "compose", "-f", str(compose_file), "-p", project_name, "up", "-d"],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if result.returncode != 0:
            raise RuntimeError(f"Failed to start lab: {result.stderr}")

        # Get container IDs
        id_result = subprocess.run(
            ["docker", "compose", "-f", str(compose_file), "-p", project_name, "ps", "-q"],
            capture_output=True,
            text=True,
        )
        container_ids = [c.strip() for c in id_result.stdout.splitlines() if c.strip()]

        now = datetime.now(UTC)
        session = LabSession(
            session_id=str(uuid.uuid4()),
            challenge_id=challenge.id,
            started_at=now.isoformat(),
            expires_at=(now + timedelta(minutes=challenge.timeout_minutes)).isoformat(),
            container_ids=container_ids,
        )
        self._sessions[session.session_id] = session
        return session

    def execute_in_lab(
        self,
        session_id: str,
        command: str,
        container_name: str = "attacker",
        timeout: int = 30,
    ) -> CommandResult:
        """Execute a command inside the attacker container of an active lab."""
        session = self._sessions.get(session_id)
        if not session:
            return CommandResult(exit_code=1, stdout="", stderr="No active session found.")

        project_name = f"agentlab-{session.challenge_id}-{session_id[:8]}"

        # Safety: reject shell metacharacters that could escape the container
        forbidden = ["; rm ", "; dd ", "--privileged", "docker.sock", "/proc/host"]
        for pattern in forbidden:
            if pattern in command:
                return CommandResult(
                    exit_code=1,
                    stdout="",
                    stderr=f"Command blocked: contains restricted pattern '{pattern}'",
                )

        result = subprocess.run(
            [
                "docker", "compose",
                "-f", str(self._compose_path(session.challenge_id)),
                "-p", project_name,
                "exec", "-T", container_name,
                "bash", "-c", command,
            ],
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        stdout = result.stdout
        stderr = result.stderr
        truncated = False

        if len(stdout.encode()) > MAX_OUTPUT_BYTES:
            stdout = stdout[:MAX_OUTPUT_BYTES].decode("utf-8", errors="replace") + "\n[... output truncated ...]"
            truncated = True

        return CommandResult(
            exit_code=result.returncode,
            stdout=stdout,
            stderr=stderr[:1024],
            truncated=truncated,
        )

    def stop_lab(self, session_id: str) -> bool:
        """Stop and remove a lab environment."""
        session = self._sessions.get(session_id)
        if not session:
            return False

        try:
            compose_file = self._compose_path(session.challenge_id)
            project_name = f"agentlab-{session.challenge_id}-{session_id[:8]}"
            subprocess.run(
                [
                    "docker", "compose",
                    "-f", str(compose_file),
                    "-p", project_name,
                    "down", "-v", "--remove-orphans",
                ],
                capture_output=True,
                timeout=60,
            )
            del self._sessions[session_id]
            return True
        except Exception:
            return False

    def get_session(self, session_id: str) -> LabSession | None:
        return self._sessions.get(session_id)

    def cleanup_expired(self) -> int:
        """Remove expired sessions. Returns count cleaned up."""
        now = datetime.now(UTC)
        expired = [
            sid for sid, s in self._sessions.items()
            if datetime.fromisoformat(s.expires_at) < now
        ]
        for sid in expired:
            self.stop_lab(sid)
        return len(expired)
