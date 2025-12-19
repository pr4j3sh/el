from __future__ import annotations

from pathlib import Path
from typing import List

from el.core.dispatcher import Dispatcher
from el.core.executor import ExecutionPolicy, Executor, CommandResult
from el.config.consts import ALLOWED_COMMANDS, HISTORY_RECORDS_LIMIT, LOG_FILE
from el.db.sqlite import SQLiteExecutionLogger
from el.models.request import HistoryRequest, PortInspectRequest, ShellRequest


class Agent:
    """
    Core orchestration layer.

    Responsibilities:
    - Accept structured input
    - Decide which action to trigger
    - Delegate to dispatcher
    - Return structured output

    This layer will later integrate with the LLM.
    """

    def __init__(self, policy: ExecutionPolicy | None = None) -> None:
        if policy is None:
            policy = ExecutionPolicy(
                allowed_commands=ALLOWED_COMMANDS,
                working_directory=Path.home(),
            )
        self._executor = Executor(policy)
        self._dispatcher = Dispatcher(self._executor)
        self._logger = SQLiteExecutionLogger(db_path=Path.home() / LOG_FILE)

    def run_shell_command(self, command: List[str]):
        """
        Execute a shell command via the shell skill.

        Args:
            command: Tokenized shell command

        Returns:
            CommandResult
        """
        result = self._dispatcher.dispatch(ShellRequest(command=command))

        self._logger.log(result)

        return result

    def get_history(self, limit: int = HISTORY_RECORDS_LIMIT):
        return self._dispatcher.dispatch(HistoryRequest(limit=limit))

    def inspect_port(self, port: int):
        return self._dispatcher.dispatch(PortInspectRequest(port=port))
