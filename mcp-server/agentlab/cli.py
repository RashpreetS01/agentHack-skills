"""
AgentLab CLI — manage ethical hacking labs from the terminal.

⚠️  EDUCATIONAL USE ONLY
"""

from __future__ import annotations

import asyncio
import sys

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(
    name="agentlab",
    help="AgentHack-Skills lab manager — ethical hacking labs for AI agents and students.",
    add_completion=False,
)
console = Console()

SAFETY_NOTICE = (
    "[bold red]⚠️  EDUCATIONAL USE ONLY[/bold red]\n"
    "All labs are isolated Docker sandboxes. No internet access.\n"
    "Never use these techniques outside authorized lab environments.\n"
)


@app.command("serve")
def serve() -> None:
    """Start the MCP server (stdio transport for Claude Code integration)."""
    from .server import run_server
    console.print(SAFETY_NOTICE)
    console.print("[green]Starting AgentLab MCP server...[/green]")
    asyncio.run(run_server())


@app.command("list")
def list_labs(
    category: str = typer.Option(None, "--category", "-c", help="Filter by category"),
    difficulty: str = typer.Option(None, "--difficulty", "-d", help="Filter by difficulty"),
) -> None:
    """List all available lab challenges."""
    from .challenge_registry import list_challenges

    challenges = list_challenges(category=category, difficulty=difficulty)

    if not challenges:
        console.print("[yellow]No challenges found with those filters.[/yellow]")
        raise typer.Exit(1)

    table = Table(title="AgentHack-Skills Lab Challenges", show_lines=True)
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Name", style="bold")
    table.add_column("Difficulty", style="yellow")
    table.add_column("Category", style="green")
    table.add_column("Points", style="magenta")

    for c in challenges:
        points = sum(f.points for f in c.flags)
        table.add_row(c.id, c.name, c.difficulty.value, c.category.value, str(points))

    console.print(SAFETY_NOTICE)
    console.print(table)
    console.print(f"\n[dim]{len(challenges)} challenge(s) found.[/dim]")


@app.command("start")
def start_lab(
    challenge_id: str = typer.Argument(..., help="Challenge ID to start"),
    agent_id: str = typer.Option("cli-user", "--agent", "-a", help="Agent/student ID"),
) -> None:
    """Start a lab environment."""
    from .challenge_registry import get_challenge
    from .lab_manager import LabManager

    console.print(SAFETY_NOTICE)

    challenge = get_challenge(challenge_id)
    if not challenge:
        console.print(f"[red]Challenge '{challenge_id}' not found.[/red]")
        console.print("Run [bold]agentlab list[/bold] to see available challenges.")
        raise typer.Exit(1)

    console.print(f"[green]Starting lab: {challenge.name}...[/green]")
    manager = LabManager()
    try:
        session = manager.start_lab(challenge, agent_id)
        console.print(f"[bold green]✅ Lab started![/bold green]")
        console.print(f"Session ID: [bold cyan]{session.session_id}[/bold cyan]")
        console.print(f"Expires at: {session.expires_at}")
        console.print(f"\nRun commands: [bold]agentlab exec {session.session_id} 'your-command'[/bold]")
        console.print(f"Stop lab:     [bold]agentlab stop {session.session_id}[/bold]")
    except Exception as e:
        console.print(f"[red]Failed to start lab: {e}[/red]")
        console.print("Make sure Docker is running: [bold]docker info[/bold]")
        raise typer.Exit(1)


@app.command("exec")
def exec_command(
    session_id: str = typer.Argument(..., help="Session ID"),
    command: str = typer.Argument(..., help="Command to run"),
    container: str = typer.Option("attacker", "--container", "-c"),
) -> None:
    """Execute a command inside an active lab."""
    from .lab_manager import LabManager

    manager = LabManager()
    result = manager.execute_in_lab(session_id, command, container)
    if result.stdout:
        console.print(result.stdout)
    if result.stderr:
        console.print(f"[red]{result.stderr}[/red]", err=True)
    sys.exit(result.exit_code)


@app.command("stop")
def stop_lab(
    session_id: str = typer.Argument(..., help="Session ID to stop"),
) -> None:
    """Stop and destroy a lab environment."""
    from .lab_manager import LabManager

    manager = LabManager()
    if manager.stop_lab(session_id):
        console.print("[green]✅ Lab stopped. Containers removed.[/green]")
    else:
        console.print("[yellow]Session not found or already stopped.[/yellow]")


@app.command("version")
def version() -> None:
    """Show version information."""
    from . import __version__
    console.print(f"AgentLab v{__version__}")
    console.print("AgentHack-Skills — Ethical Hacking Lab Manager")
    console.print("https://github.com/mukul975/agentHack-skills")


if __name__ == "__main__":
    app()
