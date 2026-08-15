# AgentDock

AgentDock is a macOS-first terminal toolkit for creating, running, and evaluating AI agents. It keeps provider credentials in macOS Keychain and records local run history in SQLite.

## Install for development

```bash
git clone https://github.com/Pr3ndy-ctrl/AgentDock.git
cd AgentDock
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -e '.[dev]'
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

## Read Gmail (optional)

Install the read-only Gmail connector:

```bash
python3 -m pip install -e '.[gmail]'
```

The Gmail extra pins `cryptography` below version 46 so Python 3.9 Intel Macs
use a prebuilt wheel instead of requiring a local Rust/OpenSSL build.

In Google Cloud, enable the Gmail API and create an OAuth client for a Desktop app.
Download its JSON file, then connect:

```bash
agentdock connect gmail --client-secrets ~/Downloads/client_secret.json
agentdock email list --unread --limit 10
agentdock email search "invoice"
agentdock email summarize --since 7d
agentdock run --allow gmail.read "Summarize important unread emails"
```

AgentDock requests only `gmail.readonly`. OAuth tokens are stored in macOS
Keychain. It cannot send, delete, label, or modify messages.

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
