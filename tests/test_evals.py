from pathlib import Path

from agentdock.evals import run_evals


def test_eval_contains(tmp_path: Path) -> None:
    path = tmp_path / "evals.yaml"
    path.write_text("cases:\n  - name: demo\n    input: ping\n    contains: pong\n")
    result = run_evals(path, lambda _: "pong!")[0]
    assert result.passed

