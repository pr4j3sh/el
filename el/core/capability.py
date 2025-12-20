from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class Capability:
    """
    Describes an action the agent can perform.
    This is injected into the LLM context.
    """

    name: str
    description: str
    arguments: Dict[str, Any]
