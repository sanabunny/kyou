from __future__ import annotations

import threading
from datetime import date, datetime, timedelta

from kyou.backends import Backend
from kyou.models import Alarm, Item, ItemKind, Priority, RecurrenceRule

try:
    from EventKit import (
        EKEntityTypeEvent,
        EKEntityTypeReminder,
        EKEventStore,
        EKRecurrenceFrequencyDaily,
        EKRecurrenceFrequencyMonthly,
        EKRecurrenceFrequencyWeekly,
        EKRecurrenceFrequencyYearly,
    )
except ImportError as exc:
    msg = (
        "pyobjc-framework-EventKit is required on macOS. "
        "Install it with: pip install pyobjc-framework-EventKit"
    )
    raise ImportError(msg) from exc


_FREQUENCY_NAMES = {
    EKRecurrenceFrequencyDaily: "daily",
    EKRecurrenceFrequencyWeekly: "weekly",
    EKRecurrenceFrequencyMonthly: "monthly",
    EKRecurrenceFrequencyYearly: "yearly",
}


def _priority_from_ek(value: int) -> Priority:
    if value == 0:
        return Priority.NONE
    if 1 <= value <= 4:
        return Priority.HIGH
    if value == 5:
        return Priority.MEDIUM
    return Priority.LOW


def _to_datetime(nsdate: object | None) -> datetime | None:
    if nsdate is None:
        return None
    timestamp = nsdate.timeIntervalSince1970()
    return datetime.fromtimestamp(timestamp)


def _recurrence_rules(ek_item: object) -> list[RecurrenceRule]:
    rules = ek_item.recurrenceRules() or []
    result: list[RecurrenceRule] = []
    for rule in rules:
        end = rule.recurrenceEnd()
        result.append(
            RecurrenceRule(
                frequency=_FREQUENCY_NAMES.get(rule.frequency(), None),
                interval=int(rule.interval()) if rule.interval() else None,
                end_date=_to_datetime(end.endDate()) if end is not None else None,
                occurrence_count=(
                    int(end.occurrenceCount())
                    if end is not None and end.occurrenceCount()
                    else None
                ),
            )
        )
    return result


def _alarms(ek_item: object) -> list[Alarm]:
    alarms = ek_item.alarms() or []
    result: list[Alarm] = []
    for alarm in alarms:
        offset = alarm.relativeOffset()
        result.append(
            Alarm(
                trigger_date=_to_datetime(alarm.absoluteDate()),
                relative_offset=(
                    timedelta(seconds=offset) if offset else None
                ),
            )
        )
    return result


def _calendar_color(ek_item: object) -> str | None:
    calendar = ek_item.calendar()
    if calendar is None:
        return None
    color = calendar.color()
    if color is None:
        return None
    try:
        r, g, b = color.redComponent(), color.greenComponent(), color.blueComponent()
        return f"#{int(r * 255):02x}{int(g * 255):02x}{int(b * 255):02x}"
    except AttributeError:
        return None


class EventKitBackend(Backend):
    def __init__(self) -> None:
        self._store = EKEventStore.alloc().init()

    def request_access(self) -> bool:
        events_granted = self._request_full_access(EKEntityTypeEvent, "requestFullAccessToEventsWithCompletion_")
        reminders_granted = self._request_full_access(EKEntityTypeReminder, "requestFullAccessToRemindersWithCompletion_")
        return events_granted and reminders_granted

    def _request_full_access(self, entity_type: int, modern_selector: str) -> bool:
        result: dict[str, bool] = {}
        done = threading.Event()

        def completion(granted: bool, _error: object) -> None:
            result["granted"] = granted
            done.set()

        if hasattr(self._store, modern_selector):
            method = getattr(self._store, modern_selector)
            method(completion)
        else:
            self._store.requestAccessToEntityType_completion_(entity_type, completion)
            
        done.wait(timeout=30)
        return result.get("granted", False)

    def get_events(self, day: date) -> list[Item]:
        start = datetime.combine(day, datetime.min.time())
        end = start + timedelta(days=1)

        predicate = self._store.predicateForEventsWithStartDate_endDate_calendars_(
            start, end, None
        )
        ek_events = self._store.eventsMatchingPredicate_(predicate)

        items: list[Item] = []
        
        if ek_events is None:
            return items
        
        for ek_event in ek_events:
            items.append(
                Item(
                    id=str(ek_event.eventIdentifier()),
                    kind=ItemKind.EVENT,
                    title=str(ek_event.title() or ""),
                    start=_to_datetime(ek_event.startDate()),
                    end=_to_datetime(ek_event.endDate()),
                    all_day=bool(ek_event.isAllDay()),
                    notes=str(ek_event.notes()) if ek_event.notes() else None,
                    location=str(ek_event.location()) if ek_event.location() else None,
                    url=str(ek_event.URL()) if ek_event.URL() else None,
                    list_name=(
                        str(ek_event.calendar().title())
                        if ek_event.calendar()
                        else None
                    ),
                    list_color=_calendar_color(ek_event),
                    created_date=_to_datetime(ek_event.creationDate()),
                    last_modified_date=_to_datetime(ek_event.lastModifiedDate()),
                    has_recurrence_rules=bool(ek_event.hasRecurrenceRules()),
                    recurrence_rules=_recurrence_rules(ek_event),
                    alarms=_alarms(ek_event),
                )
            )
        return items

    def get_reminders(self) -> list[Item]:
        predicate = self._store.predicateForRemindersInCalendars_(None)

        result: dict[str, list] = {}
        done = threading.Event()

        def completion(ek_reminders: list) -> None:
            result["reminders"] = ek_reminders or []
            done.set()

        self._store.fetchRemindersMatchingPredicate_completion_(predicate, completion)
        done.wait(timeout=30)

        items: list[Item] = []
        for reminder in result.get("reminders", []):
            due_date = None
            components = reminder.dueDateComponents()
            if components is not None:
                calendar = __import__("Foundation").NSCalendar.currentCalendar()
                due_date = calendar.dateFromComponents_(components)

            items.append(
                Item(
                    id=str(reminder.calendarItemIdentifier()),
                    kind=ItemKind.REMINDER,
                    title=str(reminder.title() or ""),
                    start=_to_datetime(due_date),
                    due_date=_to_datetime(due_date),
                    completed=bool(reminder.isCompleted()),
                    completed_date=_to_datetime(reminder.completionDate()),
                    priority=_priority_from_ek(reminder.priority()),
                    notes=str(reminder.notes()) if reminder.notes() else None,
                    url=str(reminder.URL()) if reminder.URL() else None,
                    list_name=(
                        str(reminder.calendar().title())
                        if reminder.calendar()
                        else None
                    ),
                    list_color=_calendar_color(reminder),
                    flagged=bool(getattr(reminder, "isFlagged", lambda: False)()),
                    created_date=_to_datetime(reminder.creationDate()),
                    last_modified_date=_to_datetime(reminder.lastModifiedDate()),
                    has_recurrence_rules=bool(reminder.hasRecurrenceRules()),
                    recurrence_rules=_recurrence_rules(reminder),
                    alarms=_alarms(reminder),
                )
            )
        return items
