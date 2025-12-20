from __future__ import annotations

from pathlib import Path
from typing import List
from datetime import datetime

from el.core.dispatcher import Dispatcher
from el.core.executor import ExecutionPolicy, Executor, CommandResult
from el.config.consts import (
    ALLOWED_COMMANDS,
    HISTORY_RECORDS_LIMIT,
    LOG_FILE,
    MIN_MEMORY_IMPORTANCE,
)
from el.db.memory import (
    MemoryImportance,
    MemoryKind,
    MemoryRecord,
    MemoryStore,
    MemoryTTL,
)
from el.db.sqlite import SQLiteExecutionLogger
from el.llm.client import LLMClient, LLMError
from el.llm.prompts import SUMMARY_PROMPT
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
        self._memory = MemoryStore()
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
        memory_context = self._memory_context()

        context = f"""
Capabilities:
{capabilities}

Recent memory:
{memory_context}
        """

        try:
            request = self._llm.generate(
                user_input=text, schema=LLMRequest, context=context
            )

            if request.action == "noop":
                self._memory.add(
                    MemoryRecord(
                        timestamp=datetime.utcnow(),
                        kind=MemoryKind.NOOP,
                        input=text,
                        output="No action taken.",
                        success=True,
                        importance=MemoryImportance.NOOP,
                        ttl=MemoryTTL.NOOP,
                    )
                )
                return AgentResponse(
                    success=True,
                    message="I don't know how to do that yet.",
                )

            command_result = self._dispatcher.dispatch(request)
            facts = self._llm.extract_facts(
                user_input=text,
                output=str(command_result),
            )

            for fact in facts:
                if len(fact) < 10:
                    continue

                self._memory.add(
                    MemoryRecord(
                        timestamp=datetime.utcnow(),
                        kind=MemoryKind.FACT,
                        input=fact,
                        output=None,
                        success=True,
                        importance=MemoryImportance.FACT,
                        ttl=None,
                    )
                )

            self._memory.add(
                MemoryRecord(
                    timestamp=datetime.utcnow(),
                    kind=MemoryKind.COMMAND,
                    input=text,
                    output=f"{request.action} executed successfully",
                    success=True,
                    importance=MemoryImportance.COMMAND,
                    ttl=MemoryTTL.COMMAND,
                )
            )
            self._maybe_summarize_memory()

            return AgentResponse(
                success=True,
                result=command_result,
            )
        except LLMError as e:
            request = NoOpRequest(action="noop")
            self._memory.add(
                MemoryRecord(
                    timestamp=datetime.utcnow(),
                    kind=MemoryKind.ERROR,
                    input=text,
                    output=str(e),
                    success=False,
                    importance=MemoryImportance.ERROR,
                    ttl=MemoryTTL.ERROR,
                )
            )
            return AgentResponse(
                success=False,
                message="LLM failed to process input.",
            )

        except Exception as e:
            self._memory.add(
                MemoryRecord(
                    timestamp=datetime.utcnow(),
                    kind=MemoryKind.ERROR,
                    input=text,
                    output=str(e),
                    success=False,
                    importance=MemoryImportance.ERROR,
                    ttl=MemoryTTL.ERROR,
                )
            )
            return AgentResponse(
                success=False,
                message=f"Failed to process input: {str(e)}",
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

    def _memory_context(
        self,
        limit: int = HISTORY_RECORDS_LIMIT,
        min_importance: int = MIN_MEMORY_IMPORTANCE,
    ) -> str:
        records = self._memory.retrieve_for_llm(limit, min_importance)

        if not records:
            return "No relevant prior context."

        lines = []
        for r in records:
            if r.kind == MemoryKind.FACT:
                lines.append(f"- FACT: {r.input}")
            else:
                lines.append(f"- {r.kind.value}: {r.input}")

        return "\n".join(lines)

    def _maybe_summarize_memory(self) -> None:
        commands = [
            r for r in self._memory.all() if r.kind == MemoryKind.COMMAND and r.success
        ]

        if len(commands) < 10:
            return

        oldest = commands[0].timestamp
        if (datetime.utcnow() - oldest).seconds < 600:
            return

        bullets = "\n".join(f"- {r.input}" for r in commands)

        prompt = f"""
{SUMMARY_PROMPT}

Commands:
{bullets}
"""

        summary = self._llm.generate_text(prompt)

        self._memory.add(
            MemoryRecord(
                timestamp=datetime.utcnow(),
                kind=MemoryKind.FACT,
                input="command_history",
                output=summary,
                success=True,
                importance=MemoryImportance.FACT,
                ttl=None,
            )
        )
