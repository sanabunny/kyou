from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto


class ItemKind(Enum):
    EVENT = auto()
    REMINDER = auto()


class Priority(Enum):
    NONE = auto()
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()


@dataclass(slots=True)
class Alarm:
    trigger_date: datetime | None = None
    relative_offset: timedelta | None = None


@dataclass(slots=True)
class RecurrenceRule:
    frequency: str | None = None
    interval: int | None = None
    end_date: datetime | None = None
    occurrence_count: int | None = None


@dataclass(slots=True)
class Item:
    id: str
    kind: ItemKind
    title: str
    start: datetime | None = None
    end: datetime | None = None
    all_day: bool = False
    completed: bool = False
    completed_date: datetime | None = None
    priority: Priority = Priority.NONE
    notes: str | None = None

    location: str | None = None
    url: str | None = None
    list_name: str | None = None
    list_color: str | None = None
    flagged: bool = False

    created_date: datetime | None = None
    last_modified_date: datetime | None = None
    due_date: datetime | None = None
    has_recurrence_rules: bool = False
    recurrence_rules: list[RecurrenceRule] = field(default_factory=list)
    alarms: list[Alarm] = field(default_factory=list)

    @property
    def duration(self) -> timedelta | None:
        if self.start is None or self.end is None:
            return None
        return self.end - self.start
