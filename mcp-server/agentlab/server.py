"""
AgentLab MCP Server

Exposes ethical hacking lab environments as MCP tools for Claude and other
MCP-compatible AI agents.

⚠️  EDUCATIONAL USE ONLY
All labs are isolated Docker sandboxes. No internet access. No host filesystem access.
Use only in authorized educational contexts.

Tools exposed:
    - list_challenges
    - get_challenge
    - start_lab
    - execute_in_lab
    - verify_flag
    - get_progress
    - get_hint
    - stop_lab
"""

from __future__ import annotations

import json
import uuid
from typing import Any

import mcp.types as types
from mcp.server import Server
from mcp.server.stdio import stdio_server

from .challenge_registry import get_challenge, list_challenges
from .flag_verifier import get_hint, verify_flag
from .lab_manager import LabManager
from .models import ProgressState

app = Server("agentlab")
lab_manager = LabManager()

# In-memory progress tracking (persists for session duration)
_progress: dict[str, ProgressState] = {}

SAFETY_NOTICE = (
    "\n\n---\n"
    "⚠️ SAFETY REMINDER: This lab runs in an isolated Docker network with no internet "
    "access. All techniques practiced here are for educational purposes only. "
    "Never apply these techniques outside of authorized lab environments or "
    "explicitly authorized penetration testing engagements.\n"
    "---"
)


def _get_or_create_progress(agent_id: str) -> ProgressState:
    if agent_id not in _progress:
        _progress[agent_id] = ProgressState(agent_id=agent_id)
    return _progress[agent_id]


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="list_challenges",
            description=(
                "List all available ethical hacking lab challenges. "
                "Filter by category (web-application, network, privilege-escalation, "
                "cryptography, osint, forensics) and/or difficulty (beginner, intermediate, advanced)."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Filter by category",
                        "enum": ["web-application", "network", "privilege-escalation", "cryptography", "osint", "forensics"],
                    },
                    "difficulty": {
                        "type": "string",
                        "description": "Filter by difficulty level",
                        "enum": ["beginner", "intermediate", "advanced"],
                    },
                },
            },
        ),
        types.Tool(
            name="get_challenge",
            description=(
                "Get full details for a specific lab challenge including description, "
                "learning objectives, difficulty, and hints about what to do. "
                "Use this before starting a lab to understand the goal."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "challenge_id": {
                        "type": "string",
                        "description": "Challenge ID (from list_challenges)",
                    }
                },
                "required": ["challenge_id"],
            },
        ),
        types.Tool(
            name="start_lab",
            description=(
                "Start an isolated Docker lab environment for a challenge. "
                "Returns a session_id to use with execute_in_lab and verify_flag. "
                "The lab auto-destructs after the timeout (default 60 minutes)."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "challenge_id": {
                        "type": "string",
                        "description": "Challenge ID to start",
                    },
                    "agent_id": {
                        "type": "string",
                        "description": "Unique identifier for this agent/student session",
                    },
                },
                "required": ["challenge_id"],
            },
        ),
        types.Tool(
            name="execute_in_lab",
            description=(
                "Execute a shell command inside the attacker container of an active lab. "
                "Commands run in complete isolation — no internet, no host access. "
                "Use this to run nmap, sqlmap, hydra, or any pre-installed security tool."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Active session ID from start_lab",
                    },
                    "command": {
                        "type": "string",
                        "description": "Shell command to execute inside the attacker container",
                    },
                    "container": {
                        "type": "string",
                        "description": "Container to exec into: 'attacker' (default) or 'target'",
                        "default": "attacker",
                    },
                    "timeout": {
                        "type": "integer",
                        "description": "Command timeout in seconds (default 30, max 120)",
                        "default": 30,
                    },
                },
                "required": ["session_id", "command"],
            },
        ),
        types.Tool(
            name="verify_flag",
            description=(
                "Submit a captured flag for verification. "
                "Returns whether it's correct and how many points were awarded."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Active session ID",
                    },
                    "flag": {
                        "type": "string",
                        "description": "The flag string to verify (e.g. FLAG{...})",
                    },
                },
                "required": ["session_id", "flag"],
            },
        ),
        types.Tool(
            name="get_hint",
            description=(
                "Get a progressive hint for the current challenge. "
                "Each call may reveal a more specific hint. "
                "Hint usage is tracked and slightly reduces score."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Active session ID",
                    },
                    "flag_index": {
                        "type": "integer",
                        "description": "Index of the flag to get a hint for (default 0)",
                        "default": 0,
                    },
                },
                "required": ["session_id"],
            },
        ),
        types.Tool(
            name="get_progress",
            description=(
                "Get current skill progression — completed challenges, total score, "
                "skill levels by category, and active session status."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "agent_id": {
                        "type": "string",
                        "description": "Agent/student ID",
                    }
                },
                "required": ["agent_id"],
            },
        ),
        types.Tool(
            name="stop_lab",
            description=(
                "Stop and destroy the lab environment for a session. "
                "All containers are removed. Do this when finished with a challenge."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "session_id": {
                        "type": "string",
                        "description": "Session ID to stop",
                    }
                },
                "required": ["session_id"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict[str, Any]) -> list[types.TextContent]:

    if name == "list_challenges":
        challenges = list_challenges(
            category=arguments.get("category"),
            difficulty=arguments.get("difficulty"),
        )
        if not challenges:
            text = "No challenges found matching those filters."
        else:
            lines = ["# Available Lab Challenges\n"]
            for c in challenges:
                lines.append(
                    f"## {c.name} (`{c.id}`)\n"
                    f"- **Difficulty:** {c.difficulty.value}\n"
                    f"- **Category:** {c.category.value}\n"
                    f"- **Points:** {sum(f.points for f in c.flags)}\n"
                    f"- **Description:** {c.description}\n"
                )
            text = "\n".join(lines)

    elif name == "get_challenge":
        challenge = get_challenge(arguments["challenge_id"])
        if not challenge:
            text = f"Challenge '{arguments['challenge_id']}' not found. Use list_challenges to see available challenges."
        else:
            objectives = "\n".join(f"  - {o}" for o in challenge.learning_objectives)
            text = (
                f"# {challenge.name}\n\n"
                f"**ID:** `{challenge.id}`\n"
                f"**Difficulty:** {challenge.difficulty.value}\n"
                f"**Category:** {challenge.category.value}\n"
                f"**Timeout:** {challenge.timeout_minutes} minutes\n"
                f"**Total Points:** {sum(f.points for f in challenge.flags)}\n\n"
                f"## Description\n{challenge.description}\n\n"
                f"## Learning Objectives\n{objectives}\n\n"
                f"## How to Start\n"
                f"```\nagentlab start {challenge.id}\n```\n"
                f"Or via MCP: call `start_lab` with challenge_id='{challenge.id}'"
            )
            if challenge.skill_ref:
                text += f"\n\n**Skill Reference:** `{challenge.skill_ref}`"

    elif name == "start_lab":
        agent_id = arguments.get("agent_id", str(uuid.uuid4()))
        challenge = get_challenge(arguments["challenge_id"])
        if not challenge:
            text = f"Challenge '{arguments['challenge_id']}' not found."
        else:
            try:
                session = lab_manager.start_lab(challenge, agent_id)
                progress = _get_or_create_progress(agent_id)
                progress.active_session = session
                if challenge.id not in progress.challenges_attempted:
                    progress.challenges_attempted.append(challenge.id)

                text = (
                    f"# Lab Started: {challenge.name}\n\n"
                    f"**Session ID:** `{session.session_id}`\n"
                    f"**Expires:** {session.expires_at}\n\n"
                    f"## What to Do Next\n"
                    f"Use `execute_in_lab` with session_id=`{session.session_id}` to run commands.\n\n"
                    f"**Target:** `target` (inside the lab network)\n"
                    f"**Attacker shell:** Use container='attacker'\n\n"
                    f"## Learning Objectives\n"
                    + "\n".join(f"- {o}" for o in challenge.learning_objectives)
                    + SAFETY_NOTICE
                )
            except Exception as e:
                text = f"Failed to start lab: {e}\n\nMake sure Docker is running: `docker info`"

    elif name == "execute_in_lab":
        timeout = min(int(arguments.get("timeout", 30)), 120)
        container = arguments.get("container", "attacker")
        result = lab_manager.execute_in_lab(
            session_id=arguments["session_id"],
            command=arguments["command"],
            container_name=container,
            timeout=timeout,
        )
        text = (
            f"**Exit Code:** {result.exit_code}\n\n"
            f"**Output:**\n```\n{result.stdout or '(no output)'}\n```\n"
        )
        if result.stderr:
            text += f"\n**Stderr:**\n```\n{result.stderr}\n```"
        if result.truncated:
            text += "\n\n⚠️ Output was truncated. Use `| head -50` or `> /tmp/out.txt` for large outputs."

    elif name == "verify_flag":
        session = lab_manager.get_session(arguments["session_id"])
        if not session:
            text = "Session not found. Has the lab been stopped or expired?"
        else:
            result = verify_flag(session, arguments["flag"])
            if result.correct:
                text = (
                    f"✅ **Correct flag!**\n\n"
                    f"**Points awarded:** +{result.points_awarded}\n"
                    f"**Total score:** {result.total_score}\n\n"
                    f"Well done! You've understood the vulnerability. "
                    f"Now think about how you would fix it — that's the real learning."
                )
            else:
                text = (
                    f"❌ **Incorrect flag.**\n\n"
                    f"Keep going! Re-read the SKILL.md workflow steps for this challenge. "
                    f"Use `get_hint` if you're stuck."
                )

    elif name == "get_hint":
        session = lab_manager.get_session(arguments["session_id"])
        if not session:
            text = "Session not found."
        else:
            session.hints_used += 1
            hint = get_hint(session.challenge_id, arguments.get("flag_index", 0))
            text = (
                f"**Hint** (hint #{session.hints_used} used this session):\n\n{hint}\n\n"
                f"*Note: Using hints slightly reduces your final score for this challenge.*"
            )

    elif name == "get_progress":
        agent_id = arguments["agent_id"]
        progress = _get_or_create_progress(agent_id)

        category_scores = {}
        for cid in progress.challenges_completed:
            challenge = get_challenge(cid)
            if challenge:
                cat = challenge.category.value
                category_scores[cat] = category_scores.get(cat, 0) + 1

        text = (
            f"# Progress: {agent_id}\n\n"
            f"**Total Score:** {progress.total_score} points\n"
            f"**Challenges Attempted:** {len(progress.challenges_attempted)}\n"
            f"**Challenges Completed:** {len(progress.challenges_completed)}\n\n"
            f"## Completed Challenges\n"
            + ("\n".join(f"- ✅ `{cid}`" for cid in progress.challenges_completed) or "None yet!")
            + f"\n\n## Category Progress\n"
            + ("\n".join(f"- {cat}: {count} challenge(s)" for cat, count in category_scores.items()) or "No categories completed yet.")
            + ("\n\n**Active Session:** `" + progress.active_session.session_id + "`" if progress.active_session else "")
        )

    elif name == "stop_lab":
        success = lab_manager.stop_lab(arguments["session_id"])
        text = (
            "✅ Lab stopped. Containers removed. No trace left."
            if success
            else "Session not found or already stopped."
        )

    else:
        text = f"Unknown tool: {name}"

    return [types.TextContent(type="text", text=text)]


async def run_server() -> None:
    """Run the AgentLab MCP server over stdio."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())
