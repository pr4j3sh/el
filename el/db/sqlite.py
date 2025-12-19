from __future__ import annotations

import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Tuple
from dataclasses import dataclass

from el.config.consts import HISTORY_RECORDS_LIMIT
from el.core.executor import CommandResult


@dataclass(frozen=True)
class ExecutionLogRecord:
    timestamp: str
    command: str
    return_code: int


class SQLiteExecutionLogger:
    """
    Persists command execution history to SQLite.
    """

    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        """
        Crates a table for logging
        """
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS execution_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    command TEXT NOT NULL,
                    return_code INTEGER NOT NULL,
                    stdout TEXT,
                    stderr TEXT,
                    timed_out INTEGER NOT NULL
                )
                """
            )

    def log(self, result: CommandResult) -> None:
        """
        Logs data into the table
        """
        with sqlite3.connect(self._db_path) as conn:
            conn.execute(
                """
                INSERT INTO execution_log (
                    timestamp,
                    command,
                    return_code,
                    stdout,
                    stderr,
                    timed_out
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    datetime.utcnow().isoformat(),
                    " ".join(result.command),
                    result.return_code,
                    result.stdout,
                    result.stderr,
                    int(result.timed_out),
                ),
            )

    def fetch_recent(
        self, limit: int = HISTORY_RECORDS_LIMIT
    ) -> List[ExecutionLogRecord]:
        with sqlite3.connect(self._db_path) as conn:
            rows = conn.execute(
                """
                SELECT timestamp, command, return_code
                FROM execution_log
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
            return [
                ExecutionLogRecord(timestamp=ts, command=cmd, return_code=rc)
                for ts, cmd, rc in rows
            ]
