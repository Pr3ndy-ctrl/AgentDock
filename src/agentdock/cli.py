from __future__ import annotations

import getpass
from pathlib import Path

import typer

from . import __version__
from .config import AgentConfig
from .evals import run_evals
from .history import History
from .keychain import get_secret, set_secret
from .runtime import run_agent
from .scaffold import create_project

app = typer.Typer(help="Build, run, and evaluate AI agents from your terminal.")


def project_path() -> Path:
    return Path.cwd()


def history(project: Path) -> History:
    return History(project / ".agentdock" / "runs.db")


def execute(project: Path, user_input: str) -> str:
    config = AgentConfig.load(project)
    secret = get_secret(config.api_key_name)
    if config.provider != "ollama" and not secret:
        raise RuntimeError(
            f"Missing {config.api_key_name}. Run: agentdock secret set {config.api_key_name}"
        )
    result = run_agent(config, config.prompt(project), user_input, secret)
    run_id = history(project).add(
        agent=config.name, model=config.model, user_input=user_input,
        output=result.text, latency_ms=result.latency_ms, usage=result.usage,
    )
    typer.echo(f"\n{result.text}\n")
    typer.echo(f"Run #{run_id} · {result.latency_ms} ms", err=True)
    return result.text


@app.command("new")
def new(name: str, directory: Path | None = None) -> None:
    """Create a new agent project."""
    destination = directory or Path(name)
    create_project(destination, name)
    typer.echo(f"Created {name} in {destination}")


@app.command("run")
def run(prompt: str | None = typer.Argument(None)) -> None:
    """Run the current agent once."""
    try:
        execute(project_path(), prompt or typer.prompt("You"))
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


@app.command("version")
def version() -> None:
    typer.echo(f"agentdock {__version__}")


if __name__ == "__main__":
    app()

