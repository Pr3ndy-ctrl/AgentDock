from typer.testing import CliRunner

from agentdock.cli import app


def test_version_command_starts() -> None:
    result = CliRunner().invoke(app, ["version"])
    assert result.exit_code == 0
    assert result.stdout.strip() == "agentdock 0.2.1"
