# AgentDock

AgentDock is a macOS-first terminal toolkit for creating, running, and evaluating AI agents. It keeps provider credentials in macOS Keychain and records local run history in SQLite.

## Install for development

```bash
git clone https://github.com/Pr3ndy-ctrl/AgentDock.git
cd AgentDock
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```

## Quick start

```bash
agentdock new research-agent
cd research-agent
agentdock secret set OPENAI_API_KEY
agentdock run "Explain the repository in five bullets"
agentdock test
agentdock history
```

Edit `agent.yaml` to use any OpenAI-compatible endpoint. For local Ollama, set:

```yaml
provider: ollama
model: llama3.2
base_url: http://localhost:11434/v1
api_key_name: OLLAMA_API_KEY
```

## Security

- Provider keys are read from environment variables or macOS Keychain.
- Keys are never written into generated projects.
- Run history stays inside `.agentdock/`, which is ignored by Git.
- AgentDock 0.1 does not execute model-generated tools or shell commands.

## License

Apache License 2.0.

