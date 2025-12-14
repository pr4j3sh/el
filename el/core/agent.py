from __future__ import annotations

from pathlib import Path
from typing import List

from el.core.dispatcher import Dispatcher
from el.core.executor import ExecutionPolicy, Executor, CommandResult
from el.db.sqlite import SQLiteExecutionLogger


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
                allowed_commands={"ls", "cat", "pwd", "whoami"},
                working_directory=Path.home(),
            )
        self._executor = Executor(policy)
        self._dispatcher = Dispatcher(self._executor)
        self._logger = SQLiteExecutionLogger(
            db_path=Path.home() / ".el_execution_log.db"
        )

    def run_shell_command(self, command: List[str]) -> CommandResult:
        """
        Execute a shell command via the shell skill.

        Args:
            command: Tokenized shell command

        Returns:
            CommandResult
        """
        result = self._dispatcher.dispatch(action="shell", payload=command)

        self._logger.log(result)

        return result

    def get_history(self):
        return self._dispatcher.dispatch("history", None)
