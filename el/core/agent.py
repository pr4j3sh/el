from __future__ import annotations

from typing import List

from el.core.dispatcher import Dispatcher
from el.core.executor import Executor, CommandResult


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

    def __init__(self) -> None:
        self._executor = Executor()
        self._dispatcher = Dispatcher(self._executor)

    def run_shell_command(self, command: List[str]) -> CommandResult:
        """
        Execute a shell command via the shell skill.

        Args:
            command: Tokenized shell command

        Returns:
            CommandResult
        """
        return self._dispatcher.dispatch(action="shell", payload=command)
