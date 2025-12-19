from __future__ import annotations

import json
import subprocess
from pydantic import TypeAdapter

from pydantic import BaseModel, ValidationError

from el.llm.prompts import SYSTEM_PROMPT


class LLMError(Exception):
    pass


class LLMClient:
    """
    Thin wrapper over Ollama.
    Responsible ONLY for:
    - prompting
    - parsing JSON
    - validating schema
    """

    def __init__(
        self,
        model: str = "llama3.2",
        timeout: int = 30,
    ) -> None:
        self._model = model
        self._timeout = timeout

    def generate(
        self,
        user_input: str,
        schema: Type[BaseModel],
    ) -> BaseModel:
        """
        Convert user input into a structured request.

        Raises:
            LLMError
        """
        prompt = f"""
{SYSTEM_PROMPT}

User input:
{user_input}
"""

        try:
            completed = subprocess.run(
                ["ollama", "run", self._model],
                input=prompt,
                text=True,
                capture_output=True,
                timeout=self._timeout,
                check=False,
            )
        except Exception as e:
            raise LLMError(f"Ollama execution failed: {e}") from e

        raw = completed.stdout.strip().splitlines()[-1]

        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            raise LLMError(f"Invalid JSON from LLM:\n{raw}") from e

        try:
            adapter = TypeAdapter(schema)
            return adapter.validate_python(data)
        except ValidationError as e:
            raise LLMError(f"Schema validation failed:\n{e}") from e
