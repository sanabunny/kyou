from __future__ import annotations

import sys
from abc import ABC, abstractmethod
from datetime import date

from kyou.models import Item


class Backend(ABC):
    @abstractmethod
    def request_access(self) -> bool:
        ...

    @abstractmethod
    def get_events(self, day: date) -> list[Item]:
        ...

    @abstractmethod
    def get_reminders(self) -> list[Item]:
        ...


def get_backend() -> Backend:
    if sys.platform == "darwin":
        from kyou.backends.eventkit import EventKitBackend

        return EventKitBackend()

    msg = f"No backend implemented for platform: {sys.platform}"
    raise NotImplementedError(msg)
