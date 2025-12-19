from __future__ import annotations

from typing import List, Literal, Optional
from pydantic import BaseModel, Field

from el.config.consts import HISTORY_RECORDS_LIMIT


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
    limit: int = Field(default=HISTORY_RECORDS_LIMIT, ge=1, le=100)


class PortInspectRequest(BaseRequest):
    action: Literal["port"] = "port"
    port: int = Field(..., ge=1, le=65535)
