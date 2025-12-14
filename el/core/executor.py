from __future__ import annotations

import subprocess
from dataclasses import dataclass
from typing import List, Set, Optional
from pathlib import Path


@dataclass(frozen=True)
class ExecutionPolicy:
    """
    Defines what the executor is allowed to do.
    """

    allowed_commands: Set[str]
    working_directory: Path
    timeout_seconds: int = 10


@dataclass
class CommandResult:
    """
    Represents the result of a system command execution.
    This is intentionally structured so higher layers
    never parse raw subprocess output.
    """

    command: List[str]
    return_code: int
    stdout: str
    stderr: str
    timed_out: bool = False


class CommandExecutionError(Exception):
    """
    Raised when a command fails to execute properly.
    """

    pass


class CommandNotAllowedError(CommandExecutionError):
    """
    Raised when a command is not allowed.
    """

    pass


class Executor:
    """
    Centralized, safe command execution layer.

    Rules:
    - No shell=True
    - Explicit command lists only
    - Timeout enforced
    - No privilege escalation
    """

    def __init__(self, policy: ExecutionPolicy) -> None:
        self._policy = policy

    def run(self, command: List[str]) -> CommandResult:
        """
        Execute a system command safely.

        Args:
            command: Command as a list (e.g. ["ls", "-la"])

        Returns:
            CommandResult

        Raises:
            CommandExecutionError
        """
        if not command:
            raise ValueError("Command cannot be empty")

        binary = Path(command[0]).name

        if binary not in self._policy.allowed_commands:
            raise CommandNotAllowedError(f"Command {binary} is not allowed")

        try:
            completed = subprocess.run(
                command,
                cwd=self._policy.working_directory,
                capture_output=True,
                text=True,
                timeout=self._policy.timeout_seconds,
                check=False,
            )

            return CommandResult(
                command=command,
                return_code=completed.returncode,
                stdout=completed.stdout.strip(),
                stderr=completed.stderr.strip(),
            )
        except subprocess.TimeoutExpired as e:
            return CommandResult(
                command=command,
                return_code=-1,
                stdout="",
                stderr=str(e),
                timed_out=True,
            )
        except Exception as e:
            raise CommandExecutionError(str(e)) from e
