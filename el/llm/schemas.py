from typing import List, Literal, Union
from pydantic import BaseModel, Field, field_validator


class NoOpRequest(BaseModel):
    action: Literal["noop"]


class ShellLLMRequest(BaseModel):
    action: Literal["shell"]
    command: list[str] = Field(..., min_length=1)

    @field_validator("command", mode="before")
    @classmethod
    def coerce_command(cls, v):
        if isinstance(v, str):
            return [v]
        return v


class PortLLMRequest(BaseModel):
    action: Literal["port"]
    port: int = Field(..., ge=1, le=65535)


class FactExtractionRequest(BaseModel):
    facts: List[str]


# This is the union the LLM is allowed to emit
LLMRequest = Union[NoOpRequest, ShellLLMRequest, PortLLMRequest]
