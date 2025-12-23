from __future__ import annotations

from typing import List, Optional, Union
from pydantic import BaseModel


class BaseResponse(BaseModel):
    success: bool


class ShellResponse(BaseResponse):
    command: List[str]
    return_code: int
    stdout: str
    stderr: str
    timed_out: bool


class HistoryRecord(BaseModel):
    timestamp: str
    command: str
    return_code: int


class HistoryResponse(BaseResponse):
    records: List[HistoryRecord]


class PortProcess(BaseModel):
    protocol: str
    pid: int | None
    process: str | None


class PortInspectResponse(BaseResponse):
    port: int
    processes: list[PortProcess]


class PlanResult(BaseModel):
    goal: str
    steps: list[
        Union[
            ShellResponse,
            HistoryResponse,
            PortInspectResponse,
        ]
    ]


class AgentResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    result: Optional[
        Union[ShellResponse, HistoryResponse, PortInspectResponse, PlanResult]
    ] = None
