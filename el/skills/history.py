from typing import List, Tuple

from el.db.sqlite import SQLiteExecutionLogger


class HistorySkill:
    """
    Read-only skill for execution history.
    """

    def __init__(self, logger: SQLiteExecutionLogger) -> None:
        self._logger = logger

    def run(self, limit: int = 10) -> List[Tuple]:
        return self._logger.fetch_recent(limit)
