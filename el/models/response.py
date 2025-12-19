from __future__ import annotations

from typing import List
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
