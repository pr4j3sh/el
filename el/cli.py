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

        if argv[1] == "port":
            port = int(argv[2])
            resp = self._agent.inspect_port(port)

            for p in resp.processes:
                print(f"{p.protocol} | pid={p.pid} | {p.process}")
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
        elif result:
            print(result)

        if result.stderr:
            print(result.stderr, file=sys.stderr)

        if result.timed_out:
            print("Command timed out", file=sys.stderr)

    def converse(self):
        while True:
            try:
                text = input("el> ").strip()
                if not text:
                    continue

                response = self._agent.handle_input(text)

                if response.message:
                    print(response.message)
                    continue

                if not response.result:
                    print("No result")
                    continue

                # PlanResult
                if hasattr(response.result, "goal") and hasattr(
                    response.result, "steps"
                ):
                    print(f"Goal: {response.result.goal}")
                    for i, step in enumerate(response.result.steps, 1):
                        print(f"Step {i}:")
                        if hasattr(step, "stdout"):
                            print(step.stdout.strip())
                        else:
                            print(step)
                    continue

                # Shell
                if hasattr(response.result, "stdout"):
                    self._render_result(response.result)

                # History
                elif hasattr(response.result, "records"):
                    for r in response.result.records:
                        print(f"{r.timestamp} | {r.command} | {r.return_code}")

                # Port
                elif hasattr(response.result, "processes"):
                    for p in response.result.processes:
                        print(f"{p.protocol} | pid={p.pid} | {p.process}")

            except KeyboardInterrupt:
                print("\nbye")
                break

    @staticmethod
    def _print_usage() -> None:
        print("Usage: el <command> [args...]")
