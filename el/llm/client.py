from __future__ import annotations

import json
import subprocess

from pydantic import BaseModel, ValidationError, TypeAdapter

from el.llm.prompts import SYSTEM_PROMPT
from el.llm.schemas import FactExtractionRequest, LLMRequest


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

    def generate(self, user_input: str, schema: LLMRequest, context: str) -> BaseModel:
        """
        Convert user input into a structured request.

        Raises:
            LLMError
        """
        prompt = f"""
{SYSTEM_PROMPT}

{context}

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

        stdout = completed.stdout.strip()
        print("=================prompt===================")
        print(prompt)
        print("=================output===================")
        print(stdout)

        if not stdout:
            raise LLMError("LLM returned empty output")

        lines = [l for l in stdout.splitlines() if l.strip().startswith("{")]

        if not lines:
            raise LLMError(f"No JSON object found in LLM output:\n{stdout}")

        raw = lines[-1]

        try:
            data = json.loads(raw)
        except json.JSONDecodeError as e:
            raise LLMError(f"Invalid JSON from LLM:\n{raw}") from e

        try:
            adapter = TypeAdapter(schema)
            return adapter.validate_python(data)
        except ValidationError as e:
            raise LLMError(f"Schema validation failed:\n{e}") from e

    def extract_facts(self, user_input: str, output: str) -> list[str]:
        prompt = f"""
Extract durable facts worth remembering.

Rules:
- Only stable facts
- No commands
- No transient output
- If none, return empty list

User input:
{user_input}

Output:
{output}

Return JSON:
{{ "facts": [] }}
"""

        completed = subprocess.run(
            ["ollama", "run", self._model],
            input=prompt,
            text=True,
            capture_output=True,
            timeout=self._timeout,
            check=False,
        )

        stdout = completed.stdout.strip()
        lines = [l for l in stdout.splitlines() if l.strip().startswith("{")]
        if not lines:
            return []

        data = json.loads(lines[-1])
        req = FactExtractionRequest.model_validate(data)
        return req.facts

    def generate_text(self, prompt: str) -> str:
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

        stdout = completed.stdout.strip()
        if not stdout:
            raise LLMError("LLM returned empty output")

        return stdout
