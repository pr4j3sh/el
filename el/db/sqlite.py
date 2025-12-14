from __future__ import annotations

import sqlite3
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Tuple

from el.core.executor import CommandResult


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

    def fetch_recent(self, limit: int = 10) -> List[Tuple]:
        with sqlite3.connect(self._db_path) as conn:
            cursor = conn.execute(
                """
                SELECT timestamp, command, return_code
                FROM execution_log
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            )
            return cursor.fetchall()
