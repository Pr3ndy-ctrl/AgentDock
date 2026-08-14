from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import yaml


@dataclass(frozen=True)
class EvalResult:
    name: str
    passed: bool
    expected: str
    output: str


def run_evals(path: Path, runner: Callable[[str], str]) -> list[EvalResult]:
    raw = yaml.safe_load(path.read_text()) or {}
    results = []
    for case in raw.get("cases", []):
        output = runner(case["input"])
        expected = case["contains"]
        results.append(EvalResult(case["name"], expected in output, expected, output))
    return results

