from __future__ import annotations

from typing import List

from el.core.capability import Capability
from el.core.executor import CommandResult, Executor


class ShellSkill:
    """
    Skill responsible for executing basic shell commands.

    This skill does NOT:
    - parse natural language
    - manage privileges
    - interact with subprocess directly

    It only validates and delegates.
    """

    CAPABILITY = Capability(
        name="shell",
        description="Execute a simple shell command",
        arguments={"command": "list of strings (command and args)"},
    )

    def __init__(self, executor: Executor) -> None:
        self._executor = executor

    def run(self, command: List[str]) -> CommandResult:
        """
        Execute a shell command via the Executor.

        Args:
            command: Command split into tokens
                     Example: ["ls", "-la"]

        Returns:
            CommandResult
        """
        if not command:
            raise ValueError("Command cannot be empty")

        return self._executor.run(command)
