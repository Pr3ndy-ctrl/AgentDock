from pathlib import Path

from agentdock.history import History


def test_history_round_trip(tmp_path: Path) -> None:
    db = History(tmp_path / "runs.db")
    run_id = db.add(agent="demo", model="test", user_input="hello", output="world",
                    latency_ms=12, usage={"total_tokens": 2})
    record = db.recent()[0]
    assert record.id == run_id
    assert record.output == "world"
    assert record.usage["total_tokens"] == 2

