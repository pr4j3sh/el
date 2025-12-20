# Architecture

Here’s a clean, minimal starting point that fits real-world backend structure and keeps things modular and maintainable.
This is the _base skeleton_ for an agent that can run system commands and return structured results.

### Directory Structure

Use something like:

```
ai/
  core/
    agent.py          # main agent logic: parse intent → run skill → return result
    dispatcher.py     # routes tasks to the right skill/module
    executor.py       # safe command runner (subprocess wrapper)
  skills/
    shell.py          # skill: run system commands safely
  models/
    request.py        # pydantic models for requests
    response.py       # pydantic models for responses
  cli.py              # entrypoint for command-line interface
```

This is the simplest functional design:
one core for routing, one skill that can run commands, and clean request/response models.

### Core Concepts

#### 1. executor.py

This is where you define the actual subprocess executor with safety rules.
The whole agent will rely on _this_ to interact with your Arch system.

Key rules:

- no shell=True
- no root by default
- whitelist or controlled env
- timeouts

#### 2. shell.py

This is the first “skill module”.
It exposes one key function:

```
run_command(command: list[str]) -> ShellResponse
```

Later, you’ll add more skills (containers, network, configs, services, etc.)

#### 3. dispatcher.py

Decides which skill to call based on the task type.
This stays small and predictable.

#### 4. agent.py

The orchestration layer.
Takes raw user text → asks LLM for intent + params (later) → calls dispatcher → returns final output.
For now you skip the LLM step and route commands manually.

#### 5. cli.py

Simple CLI wrapper that:

```
ai run "ls -la"
```

parses → calls agent → prints clean output.

---

### What This Gives You

- **A controllable shell execution layer** (the heart of your agent)
- **A modular codebase** (each skill in its own file)
- **Separation between intent, execution, and presentation**
- **A clean path to scale** (add skills, integrate Ollama, add memory layer, etc.)

---

If you want, next step I can outline the exact minimal API for `executor.py` and the `ShellResponse` data model — without writing code — so you start building cleanly.
