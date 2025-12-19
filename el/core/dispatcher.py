from __future__ import annotations

from pathlib import Path
from typing import Dict, List

from el.core.executor import CommandResult, Executor
from el.db.sqlite import SQLiteExecutionLogger
from el.models.request import BaseRequest, HistoryRequest, ShellRequest
from el.models.response import HistoryRecord, HistoryResponse, ShellResponse
from el.skills.history import HistorySkill
from el.skills.shell import ShellSkill


class Dispatcher:
    """
    Routes actions to the appropriate skill.

    This layer must stay simple and deterministic.
    No business logic, no parsing, no side effects.
    """

    def __init__(self, executor: Executor) -> None:
        self._logger = SQLiteExecutionLogger(
            db_path=Path.home() / ".el_execution_log.db"
        )
        self._skills = self._register_skills(executor)

    def _register_skills(self, executor: Executor) -> Dict[str, object]:
        """
        Register all available skills here.
        """
        return {"shell": ShellSkill(executor), "history": HistorySkill(self._logger)}

    def dispatch(self, request: BaseRequest):
        """
        Dispatch an action to the correct skill.

        Args:
            action: Skill name (e.g. "shell")
            payload: Skill-specific input

        Returns:
            CommandResult
        """
        if request.action == "shell":
            req = ShellRequest.model_validate(request)
            result = self._skills["shell"].run(req.command)
            return ShellResponse(
                success=True,
                command=result.command,
                return_code=result.return_code,
                stdout=result.stdout,
                stderr=result.stderr,
                timed_out=result.timed_out,
            )

        if request.action == "history":
            req = HistoryRequest.model_validate(request)
            records = self._skills["history"].run(req.limit)

            return HistoryResponse(
                success=True,
                records=[
                    HistoryRecord(
                        timestamp=r.timestamp,
                        command=r.command,
                        return_code=r.return_code,
                    )
                    for r in records
                ],
            )

        raise ValueError(f"Unknown action: {request.action}")
