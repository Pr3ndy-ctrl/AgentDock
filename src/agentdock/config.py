from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class AgentConfig:
    name: str
    provider: str
    model: str
    base_url: str
    api_key_name: str
    temperature: float = 0.2
    max_tokens: int = 1000
    system_prompt: str = "prompt.md"

    @classmethod
    def load(cls, project: Path) -> "AgentConfig":
        path = project / "agent.yaml"
        if not path.exists():
            raise FileNotFoundError(f"No agent.yaml found in {project}")
        raw: dict[str, Any] = yaml.safe_load(path.read_text()) or {}
        required = {"name", "provider", "model", "base_url", "api_key_name"}
        missing = sorted(required - raw.keys())
        if missing:
            raise ValueError(f"Missing agent.yaml fields: {', '.join(missing)}")
        return cls(**raw)

    def prompt(self, project: Path) -> str:
        path = project / self.system_prompt
        if not path.exists():
            raise FileNotFoundError(f"System prompt not found: {path}")
        return path.read_text().strip()

