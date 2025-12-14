from __future__ import annotations

from typing import Dict, List

from el.core.executor import CommandResult, Executor
from el.skills.shell import ShellSkill


class Dispatcher:
    """
    Routes actions to the appropriate skill.

    This layer must stay simple and deterministic.
    No business logic, no parsing, no side effects.
    """

    def __init__(self, executor: Executor) -> None:
        self._skills = self._register_skills(executor)

    def _register_skills(self, executor: Executor) -> Dict[str, object]:
        """
        Register all available skills here.
        """
        return {"shell": ShellSkill(executor)}

    def dispatch(self, action: str, payload: List[str]) -> CommandResult:
        """
        Dispatch an action to the correct skill.

        Args:
            action: Skill name (e.g. "shell")
            payload: Skill-specific input

        Returns:
            CommandResult
        """
        if action not in self._skills:
            raise ValueError(f"Unknown action: {action}")

        skill = self._skills[action]
        return skill.run(payload)
