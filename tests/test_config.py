from pathlib import Path

from agentdock.config import AgentConfig
from agentdock.scaffold import create_project


def test_scaffold_loads(tmp_path: Path) -> None:
    project = tmp_path / "demo"
    create_project(project, "demo")
    config = AgentConfig.load(project)
    assert config.name == "demo"
    assert config.provider == "openai"
    assert "reliable AI agent" in config.prompt(project)

