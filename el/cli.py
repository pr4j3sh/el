from __future__ import annotations

import sys
from typing import List

from el.core.agent import Agent
from el.core.executor import CommandResult


class CLI:
    """
    Command Line Interface for el.

    Responsibilities:
    - Parse command-line arguments
    - Invoke the agent
    - Render output to stdout/stderr
    """

    def __init__(self) -> None:
        self._agent = Agent()

    def run(self, argv: List[str]) -> None:
        """
        Entry point for CLI execution.

        Args:
            argv: sys.argv-style list
        """
        if len(argv) < 2:
            self._print_usage()
            sys.exit(1)

        if argv[1] == "history":
            res = self._agent.get_history()

            for r in res.records:
                print(f"{r.timestamp} | {r.command} | {r.return_code}")
            return
        command = argv[1:]
        result = self._agent.run_shell_command(command)
        self._render_result(result)

    def _render_result(self, result: CommandResult) -> None:
        """
        Render CommandResult to the console.
        """
        if result.stdout:
            print(result.stdout)

        if result.stderr:
            print(result.stderr, file=sys.stderr)

        if result.timed_out:
            print("Command timed out", file=sys.stderr)

    @staticmethod
    def _print_usage() -> None:
        print("Usage: el <command> [args...]")
