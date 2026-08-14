from __future__ import annotations

import os
import platform
import subprocess

SERVICE = "com.agentdock.cli"


def set_secret(name: str, value: str) -> None:
    if platform.system() != "Darwin":
        raise RuntimeError("Keychain storage is available on macOS only")
    subprocess.run(
        ["security", "add-generic-password", "-U", "-s", SERVICE, "-a", name, "-w", value],
        check=True,
        capture_output=True,
        text=True,
    )


def get_secret(name: str) -> str | None:
    env_value = os.getenv(name)
    if env_value:
        return env_value
    if platform.system() != "Darwin":
        return None
    result = subprocess.run(
        ["security", "find-generic-password", "-s", SERVICE, "-a", name, "-w"],
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else None

