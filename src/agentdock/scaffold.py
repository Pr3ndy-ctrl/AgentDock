from __future__ import annotations

from pathlib import Path


AGENT_YAML = """name: {name}
provider: openai
model: gpt-4.1-mini
base_url: https://api.openai.com/v1
api_key_name: OPENAI_API_KEY
temperature: 0.2
max_tokens: 1000
system_prompt: prompt.md
"""

PROMPT = """You are a focused, reliable AI agent.

Complete the user's request accurately. State uncertainty and never invent results.
"""

EVALS = """cases:
  - name: follows-instructions
    input: "Reply with exactly: READY"
    contains: "READY"
"""


def create_project(destination: Path, name: str) -> None:
    if destination.exists() and any(destination.iterdir()):
        raise FileExistsError(f"Destination is not empty: {destination}")
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "agent.yaml").write_text(AGENT_YAML.format(name=name))
    (destination / "prompt.md").write_text(PROMPT)
    (destination / "evals.yaml").write_text(EVALS)
    (destination / ".gitignore").write_text(".agentdock/\n__pycache__/\n*.pyc\n.env\n")

