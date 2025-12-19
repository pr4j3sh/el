from __future__ import annotations

from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class BaseRequest(BaseModel):
    """
    Base request for all agent actions.
    """

    action: str


class ShellRequest(BaseRequest):
    action: Literal["shell"] = "shell"
    command: List[str] = Field(..., min_length=1)


class HistoryRequest(BaseRequest):
    action: Literal["history"] = "history"
    limit: int = Field(default=10, ge=1, le=100)
