from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from dataclasses import dataclass

from .config import AgentConfig


@dataclass(frozen=True)
class Result:
    text: str
    latency_ms: int
    usage: dict


def run_agent(config: AgentConfig, system_prompt: str, user_input: str, api_key: str | None) -> Result:
    url = config.base_url.rstrip("/") + "/chat/completions"
    body = json.dumps({
        "model": config.model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input},
        ],
        "temperature": config.temperature,
        "max_tokens": config.max_tokens,
    }).encode()
    headers = {"Content-Type": "application/json"}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    request = urllib.request.Request(url, data=body, headers=headers, method="POST")
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            payload = json.loads(response.read())
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode(errors="replace")
        raise RuntimeError(f"Provider returned HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise RuntimeError(f"Could not reach provider: {exc.reason}") from exc
    latency_ms = round((time.perf_counter() - started) * 1000)
    try:
        text = payload["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError("Provider response did not contain an assistant message") from exc
    return Result(text=text, latency_ms=latency_ms, usage=payload.get("usage", {}))

