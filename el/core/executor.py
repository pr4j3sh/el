from __future__ import annotations

import subprocess
from dataclasses import dataclass
from typing import List


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


class Executor:
    """
    Centralized, safe command execution layer.

    Rules:
    - No shell=True
    - Explicit command lists only
    - Timeout enforced
    - No privilege escalation
    """

    def __init__(self, timeout: int = 10) -> None:
        self._timeout = timeout

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
        try:
            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=self._timeout,
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
