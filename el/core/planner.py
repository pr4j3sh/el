from pydantic import BaseModel
from typing import List

from el.llm.client import LLMClient
from el.llm.prompts import PLANNER_PROMPT


class Step(BaseModel):
    action: str  # "shell", "port", "noop"
    command: list[str] | None = None
    port: int | None = None
    description: str | None = None


class Plan(BaseModel):
    goal: str
    steps: List[Step]


class Planner:
    def __init__(self, llm: LLMClient):
        self._llm = llm

    def generate_plan(self, user_input: str, context: str) -> Plan:
        prompt = f"""
{PLANNER_PROMPT}

Context:
{context}

User request:
{user_input}
"""
        return self._llm.generate(user_input=prompt, schema=Plan, context="")
