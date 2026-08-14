from __future__ import annotations

import getpass
from pathlib import Path
from typing import Optional

import typer

from . import __version__
from .config import AgentConfig
from .evals import run_evals
from .gmail import connect_gmail, format_messages, list_messages
from .history import History
from .keychain import get_secret, set_secret
from .runtime import run_agent
from .scaffold import create_project

app = typer.Typer(help="Build, run, and evaluate AI agents from your terminal.")


def project_path() -> Path:
    return Path.cwd()


def history(project: Path) -> History:
    return History(project / ".agentdock" / "runs.db")


def execute(project: Path, user_input: str, context: str = "") -> str:
    config = AgentConfig.load(project)
    secret = get_secret(config.api_key_name)
    if config.provider != "ollama" and not secret:
        raise RuntimeError(
            f"Missing {config.api_key_name}. Run: agentdock secret set {config.api_key_name}"
        )
    system_prompt = config.prompt(project)
    if context:
        system_prompt += "\n\nApproved external context:\n" + context
    result = run_agent(config, system_prompt, user_input, secret)
    run_id = history(project).add(
        agent=config.name, model=config.model, user_input=user_input,
        output=result.text, latency_ms=result.latency_ms, usage=result.usage,
    )
    typer.echo(f"\n{result.text}\n")
    typer.echo(f"Run #{run_id} · {result.latency_ms} ms", err=True)
    return result.text


@app.command("new")
def new(name: str, directory: Optional[Path] = None) -> None:
    """Create a new agent project."""
    destination = directory or Path(name)
    create_project(destination, name)
    typer.echo(f"Created {name} in {destination}")


@app.command("run")
def run(
    prompt: Optional[str] = typer.Argument(None),
    allow: str = typer.Option("", help="Comma-separated permissions, for example gmail.read"),
) -> None:
    """Run the current agent once."""
    try:
        permissions = {item.strip() for item in allow.split(",") if item.strip()}
        context = ""
        if "gmail.read" in permissions:
            messages = list_messages(query="is:unread", limit=10)
            context = "Unread Gmail messages:\n" + format_messages(messages)
        execute(project_path(), prompt or typer.prompt("You"), context)
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(1)


@app.command("test")
def test(evals_file: Path = Path("evals.yaml")) -> None:
    """Run repeatable agent evaluations."""
    project = project_path()
    try:
        results = run_evals(project / evals_file, lambda value: execute(project, value))
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(1)
    for result in results:
        mark = "PASS" if result.passed else "FAIL"
        typer.echo(f"[{mark}] {result.name}")
    if any(not result.passed for result in results):
        raise typer.Exit(1)


@app.command("history")
def show_history(limit: int = 10) -> None:
    """Show recent local runs."""
    for record in history(project_path()).recent(limit):
        typer.echo(f"#{record.id} {record.created_at} {record.model} {record.latency_ms}ms")
        typer.echo(f"  {record.input[:80]}")


secret_app = typer.Typer(help="Store provider keys in macOS Keychain.")
app.add_typer(secret_app, name="secret")

email_app = typer.Typer(help="Read Gmail with explicit, read-only permission.")
app.add_typer(email_app, name="email")


@secret_app.command("set")
def secret_set(name: str) -> None:
    value = getpass.getpass(f"{name}: ")
    if not value:
        raise typer.BadParameter("Secret cannot be empty")
    try:
        set_secret(name, value)
    except RuntimeError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(1)
    typer.echo(f"Stored {name} in macOS Keychain")


@app.command("connect")
def connect(
    provider: str,
    client_secrets: Path = typer.Option(..., exists=True, readable=True),
) -> None:
    """Connect an external provider using OAuth."""
    if provider.lower() != "gmail":
        typer.echo(f"Error: unsupported provider: {provider}", err=True)
        raise typer.Exit(1)
    try:
        connect_gmail(client_secrets)
    except RuntimeError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(1)
    typer.echo("Connected Gmail with read-only access")


@email_app.command("list")
def email_list(
    unread: bool = typer.Option(False, help="Only unread messages"),
    limit: int = typer.Option(10, min=1, max=100),
) -> None:
    """List recent Gmail messages."""
    try:
        messages = list_messages(query="is:unread" if unread else "", limit=limit)
    except RuntimeError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(1)
    typer.echo(format_messages(messages))


@email_app.command("search")
def email_search(query: str, limit: int = typer.Option(10, min=1, max=100)) -> None:
    """Search Gmail using Gmail search syntax."""
    try:
        messages = list_messages(query=query, limit=limit)
    except RuntimeError as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(1)
    typer.echo(format_messages(messages))


@email_app.command("summarize")
def email_summarize(
    since: str = typer.Option("7d", help="Gmail duration such as 7d or 2w"),
    limit: int = typer.Option(20, min=1, max=100),
) -> None:
    """Summarize recent messages with the current agent."""
    try:
        messages = list_messages(query=f"newer_than:{since}", limit=limit)
        context = "Gmail messages:\n" + format_messages(messages)
        execute(project_path(), "Summarize these emails and list required actions.", context)
    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        typer.echo(f"Error: {exc}", err=True)
        raise typer.Exit(1)


@app.command("version")
def version() -> None:
    typer.echo(f"agentdock {__version__}")


if __name__ == "__main__":
    app()
