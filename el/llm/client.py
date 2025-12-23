from __future__ import annotations

import httpx
import json

from pydantic import BaseModel, ValidationError, TypeAdapter

from el.config.consts import BASE_URL, LLM_MODEL, LLM_TIMEOUT
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
        model: str = LLM_MODEL,
        base_url: str = BASE_URL,
        timeout: int = LLM_TIMEOUT,
    ) -> None:
        self._model = model
        self._url = f"{base_url}/api/generate"
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

        payload = {
            "model": self._model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0,
            },
        }

        try:
            resp = httpx.post(
                self._url,
                json=payload,
                timeout=self._timeout,
            )
            resp.raise_for_status()
        except Exception as e:
            raise LLMError(f"Ollama execution failed: {e}") from e

        data = resp.json()

        if "response" not in data:
            raise LLMError(f"Invalid Ollama response: {data}")

        try:
            parsed = json.loads(data["response"])
        except json.JSONDecodeError as e:
            raise LLMError(f"LLM returned invalid JSON:\n{data['response']}") from e

        print(parsed)
        try:
            adapter = TypeAdapter(schema)
            return adapter.validate_python(parsed)
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

        payload = {
            "model": self._model,
            "prompt": prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0,
            },
        }

        try:
            resp = httpx.post(self._url, json=payload, timeout=self._timeout)
            resp.raise_for_status()
            data = resp.json()
            raw_json = json.loads(data.get("response", "{}"))
            req = FactExtractionRequest.model_validate(raw_json)
            return req.facts
        except Exception:
            return []

    def generate_text(self, prompt: str) -> str:
        payload = {
            "model": self._model,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0},
        }

        try:
            resp = httpx.post(self._url, json=payload, timeout=self._timeout)
            resp.raise_for_status()
            data = resp.json()
            return data.get("response", "").strip()
        except Exception as e:
            raise LLMError(f"Ollama execution failed: {e}") from e
