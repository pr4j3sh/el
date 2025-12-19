from __future__ import annotations

from typing import List
from el.core.executor import Executor
from el.models.response import PortProcess


class NetworkSkill:
    """
    Network inspection skill (ports, listeners).
    """

    def __init__(self, executor: Executor) -> None:
        self._executor = executor

    def inspect_port(self, port: int) -> List[PortProcess]:
        """
        Inspect what is listening on a given port using ss.
        """
        cmd = ["ss", "-tulpn", f"sport = :{port}"]

        result = self._executor.run(cmd)

        processes: List[PortProcess] = []

        for line in result.stdout.splitlines():
            if "users:" not in line:
                continue

            # Example fragment:
            # users:(("sshd",pid=742,fd=3))
            proto = line.split()[0]

            pid = None
            proc = None

            if "pid=" in line:
                try:
                    proc = line.split("((")[1].split(",")[0].strip('"')
                    pid = int(line.split("pid=")[1].split(",")[0])
                except Exception:
                    pass

            processes.append(
                PortProcess(
                    protocol=proto,
                    pid=pid,
                    process=proc,
                )
            )

        return processes
