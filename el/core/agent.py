from __future__ import annotations

from pathlib import Path
from typing import List

from el.core.dispatcher import Dispatcher
from el.core.executor import ExecutionPolicy, Executor, CommandResult
from el.config.consts import ALLOWED_COMMANDS, HISTORY_RECORDS_LIMIT, LOG_FILE
from el.db.sqlite import SQLiteExecutionLogger
from el.llm.client import LLMClient, LLMError
from el.llm.schemas import LLMRequest, NoOpRequest
from el.models.request import HistoryRequest, PortInspectRequest, ShellRequest
from el.models.response import AgentResponse


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
        self._llm = LLMClient()
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

    def handle_input(self, text: str):
        """
        Conversational entrypoint.
        """
        capabilities = self._build_capability_context()

        try:
            request = self._llm.generate(
                user_input=text, schema=LLMRequest, capabilities=capabilities
            )

        except LLMError:
            # Deterministic fallback for non-actionable input
            request = NoOpRequest(action="noop")

        if request.action == "noop":
            return AgentResponse(
                success=True,
                message="I don't know how to do that yet.",
            )

        command_result = self._dispatcher.dispatch(request)

        return AgentResponse(
            success=True,
            result=command_result,
        )

    def _build_capability_context(self) -> str:
        """
        Build a human-readable capability manifest for the LLM.
        """
        lines = ["Available actions:"]

        for cap in self._dispatcher.capabilities():
            lines.append(f"- {cap.name}: {cap.description}")
            for arg, desc in cap.arguments.items():
                lines.append(f"    - {arg}: {desc}")

        return "\n".join(lines)
