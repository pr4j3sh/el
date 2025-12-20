# Executor

Perfect. Structure is solid and **industry-grade**. I’ll treat this as _locked_ and build on top of it.

We’ll proceed **vertically**, one core layer at a time, and I’ll explicitly explain _why_ each design choice is made.

---

## Phase 1: The Absolute Core — `executor`

Everything in **el** eventually becomes:

> _“run something on the system and return a safe, structured result”_

So we start with **`core/executor.py`**.

### Design goals

- Single authority for command execution
- No `shell=True`
- Timeouts
- Structured output (not raw strings)
- Clear error semantics
- Reusable by all skills

This is **Command Pattern + Facade**:

- Skills don’t care _how_ commands run
- They just ask the executor

---

## `el/core/executor.py`

```python
from __future__ import annotations

import subprocess
from dataclasses import dataclass
from typing import List, Optional


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
    """Raised when a command fails to execute properly."""
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

        except subprocess.TimeoutExpired as exc:
            return CommandResult(
                command=command,
                return_code=-1,
                stdout="",
                stderr=str(exc),
                timed_out=True,
            )

        except Exception as exc:
            raise CommandExecutionError(str(exc)) from exc
```

---

## Why this design (important learning points)

### 1. **No raw subprocess leakage**

Higher layers **never touch subprocess**.
This prevents:

- accidental privilege misuse
- inconsistent output parsing
- security drift

### 2. **Structured result**

We return `CommandResult`, not strings.

This lets:

- skills reason on return codes
- agent explain failures
- future LLM layers consume clean data

### 3. **Explicit command list**

This blocks:

- shell injection
- ambiguous parsing
- quoting bugs

### 4. **Timeout by default**

System agents **must never hang**.
This is non-negotiable in production tools.

---

## What we’ll do next

Next logical step is **`skills/shell.py`**, which:

- validates user input
- converts text → command list
- calls `Executor`
- returns a domain-level response

After that:

```
CLI → Agent → Dispatcher → Shell Skill → Executor
```

When you’re ready, say **“next: shell skill”** and we’ll build it cleanly.
