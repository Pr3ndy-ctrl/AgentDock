from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass(frozen=True)
class RunRecord:
    id: int
    created_at: str
    agent: str
    model: str
    input: str
    output: str
    latency_ms: int
    usage: dict


class History:
    def __init__(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(path)
        self.connection.execute(
            """CREATE TABLE IF NOT EXISTS runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                created_at TEXT NOT NULL,
                agent TEXT NOT NULL,
                model TEXT NOT NULL,
                input TEXT NOT NULL,
                output TEXT NOT NULL,
                latency_ms INTEGER NOT NULL,
                usage_json TEXT NOT NULL
            )"""
        )

    def add(self, *, agent: str, model: str, user_input: str, output: str,
            latency_ms: int, usage: dict) -> int:
        cursor = self.connection.execute(
            "INSERT INTO runs(created_at,agent,model,input,output,latency_ms,usage_json) VALUES(?,?,?,?,?,?,?)",
            (datetime.now(timezone.utc).isoformat(), agent, model, user_input, output,
             latency_ms, json.dumps(usage)),
        )
        self.connection.commit()
        return int(cursor.lastrowid)

    def recent(self, limit: int = 10) -> list[RunRecord]:
        rows = self.connection.execute(
            "SELECT id,created_at,agent,model,input,output,latency_ms,usage_json FROM runs ORDER BY id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [RunRecord(*row[:-1], usage=json.loads(row[-1])) for row in rows]

