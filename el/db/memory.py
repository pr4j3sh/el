from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from enum import Enum, IntEnum

from el.config.consts import HISTORY_RECORDS_LIMIT, MIN_MEMORY_IMPORTANCE


class MemoryKind(str, Enum):
    COMMAND = "command"  # 3 - 3600s
    NOOP = "noop"  # 1 - 300s
    ERROR = "error"  # 4 - 1800s
    FACT = "fact"  # 5 - None


class MemoryImportance(IntEnum):
    NOOP = 1
    COMMAND = 3
    ERROR = 4
    FACT = 5


class MemoryTTL(IntEnum):
    NOOP = 300
    COMMAND = 3600
    ERROR = 1800


@dataclass(frozen=True)
class MemoryRecord:
    timestamp: datetime
    kind: MemoryKind  # "shell", "port", "noop", "system"
    input: str
    output: Optional[str]
    success: bool
    importance: MemoryImportance  # 1–5
    ttl: MemoryTTL | None


class MemoryStore:
    """
    Agent-owned memory.
    Append-only. No logic.
    """

    def __init__(self) -> None:
        self._records: List[MemoryRecord] = []

    def add(self, record: MemoryRecord) -> None:
        self._records.append(record)

    def recent(
        self,
        limit: int = HISTORY_RECORDS_LIMIT,
        min_importance: int = MIN_MEMORY_IMPORTANCE,
    ) -> List[MemoryRecord]:
        now = datetime.utcnow()

        valid = [
            r
            for r in self._records
            if not self._is_expired(r, now) and r.importance >= min_importance
        ]

        return valid[-limit:]

    def all(self) -> List[MemoryRecord]:
        return list(self._records)

    def _is_expired(self, record: MemoryRecord, now: datetime) -> bool:
        if record.ttl is None:
            return False
        return (now - record.timestamp).total_seconds() > record.ttl

    def retrieve_for_llm(
        self,
        limit: int,
        min_importance: int,
    ) -> list[MemoryRecord]:
        now = datetime.utcnow()
        selected: list[MemoryRecord] = []

        for r in reversed(self._records):
            # TTL check
            if r.ttl is not None:
                age = (now - r.timestamp).seconds
                if age > r.ttl:
                    continue

            # Importance check
            if r.importance.value < min_importance:
                continue

            # Noise filter
            if r.kind == MemoryKind.NOOP:
                continue

            selected.append(r)

            if len(selected) >= limit:
                break

        return list(reversed(selected))
