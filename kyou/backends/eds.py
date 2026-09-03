from __future__ import annotations

import sys
from datetime import date, datetime, timedelta

from gi.repository import GLib
import gi

try:
    gi.require_version("ECal", "2.0")
    gi.require_version("EDataServer", "1.2")
    gi.require_version("ICalGLib", "3.0")
    from gi.repository import ECal, EDataServer, ICalGLib
except (ValueError, ImportError) as exc:
    msg = (
        f"Evolution Data Server (ECal 2.0 / EDataServer 1.2 / ICalGLib 3.0) "
        f"is required on Linux: {exc}"
    )
    raise ImportError(msg) from exc

from kyou.backends import Backend
from kyou.models import Item, ItemKind, Priority, RecurrenceRule


def _priority_from_eds(value: int) -> Priority:
    if value == 0:
        return Priority.NONE
    if 1 <= value <= 4:
        return Priority.HIGH
    if value == 5:
        return Priority.MEDIUM
    return Priority.LOW


def _ical_time_to_datetime(t: object | None) -> datetime | None:
    if t is None:
        return None
    try:
        if hasattr(t, "is_null_time") and t.is_null_time():
            return None
        return datetime(
            t.get_year(),
            t.get_month(),
            t.get_day(),
            t.get_hour(),
            t.get_minute(),
            t.get_second(),
        )
    except (ValueError, AttributeError):
        return None


class EDSBackend(Backend):
    def __init__(self) -> None:
        self._registry = EDataServer.SourceRegistry.new_sync(None)

    def request_access(self) -> bool:
        return self._registry is not None

    def get_events(self, day: date) -> list[Item]:
        if self._registry is None:
            return []

        day_start = datetime.combine(day, datetime.min.time())
        day_end = day_start + timedelta(days=1)

        iso_start = day_start.strftime("%Y%m%dT%H%M%SZ")
        iso_end = day_end.strftime("%Y%m%dT%H%M%SZ")
        sexp = f'(occur-in-time-range? (make-time "{iso_start}") (make-time "{iso_end}"))'

        sources = self._registry.list_sources(EDataServer.SOURCE_EXTENSION_CALENDAR)
        items: list[Item] = []

        for source in sources:
            if not source.get_enabled():
                continue

            cal_ext = None
            if source.has_extension(EDataServer.SOURCE_EXTENSION_CALENDAR):
                cal_ext = source.get_extension(EDataServer.SOURCE_EXTENSION_CALENDAR)
                if not cal_ext.get_selected():
                    continue

            try:
                client = ECal.Client.connect_sync(
                    source, ECal.ClientSourceType.EVENTS, 3, None
                )
            except (GLib.Error, Exception):
                continue

            comps: list[object] = []
            try:
                _, comps = client.get_object_list_as_comps_sync(sexp, None)
            except (GLib.Error, Exception):
                try:
                    _, comps = client.get_object_list_as_comps_sync("#t", None)
                except (GLib.Error, Exception):
                    comps = []

            list_name = source.get_display_name()
            list_color = cal_ext.dup_color() if cal_ext else None

            for comp in comps:
                try:
                    icalcomp = comp.get_icalcomponent()
                    dtstart_val = icalcomp.get_dtstart()
                    dtend_val = icalcomp.get_dtend()

                    start_dt = _ical_time_to_datetime(dtstart_val)
                    end_dt = _ical_time_to_datetime(dtend_val)

                    all_day = False
                    if dtstart_val and hasattr(dtstart_val, "is_date"):
                        all_day = dtstart_val.is_date()

                    items.append(
                        Item(
                            id=str(icalcomp.get_uid() or ""),
                            kind=ItemKind.EVENT,
                            title=str(icalcomp.get_summary() or ""),
                            start=start_dt,
                            end=end_dt,
                            all_day=all_day,
                            notes=str(icalcomp.get_description() or "") or None,
                            location=str(icalcomp.get_location() or "") or None,
                            list_name=list_name,
                            list_color=list_color,
                            priority=_priority_from_eds(icalcomp.get_priority()),
                            has_recurrence_rules=bool(comp.has_recurrences()),
                        )
                    )
                except (AttributeError, Exception):
                    continue

        return items

    def get_reminders(self) -> list[Item]:
        print("kyou: get_reminders called")
        if self._registry is None:
            print("kyou: _registry is None")
            return []

        sources = self._registry.list_sources(EDataServer.SOURCE_EXTENSION_TASK_LIST)
        print(f"kyou: found {len(sources)} task list sources")
        items: list[Item] = []

        for source in sources:
            name = source.get_display_name()
            enabled = source.get_enabled()
            print(f"kyou: source '{name}', enabled={enabled}")
            if not enabled:
                continue

            task_ext = None
            if source.has_extension(EDataServer.SOURCE_EXTENSION_TASK_LIST):
                task_ext = source.get_extension(EDataServer.SOURCE_EXTENSION_TASK_LIST)
                selected = task_ext.get_selected()
                print(f"kyou: source '{name}' has task_ext, selected={selected}")

            try:
                client = ECal.Client.connect_sync(
                    source, ECal.ClientSourceType.TASKS, 3, None
                )
                print(f"kyou: connected to ECal Client for '{name}'")
            except (GLib.Error, Exception) as e:
                print(f"kyou: failed to connect to ECal Client for '{name}': {e}")
                continue

            comps: list[object] = []
            try:
                _, comps = client.get_object_list_as_comps_sync("#t", None)
                print(f"kyou: fetched {len(comps)} components using '#t' for '{name}'")
            except (GLib.Error, Exception) as e:
                print(f"kyou: failed to fetch components for '{name}': {e}")
                comps = []

            list_name = name
            list_color = task_ext.dup_color() if task_ext else None

            for comp in comps:
                try:
                    icalcomp = comp.get_icalcomponent()
                    summary = str(icalcomp.get_summary() or "")
                    
                    percent = icalcomp.get_percent_complete()
                    
                    status_prop = icalcomp.get_first_property(ICalGLib.PropertyKind.STATUS)
                    status_val = status_prop.get_status() if status_prop else None
                    is_completed_status = (status_val == ICalGLib.PropertyStatus.COMPLETED)
                    
                    completed_time = icalcomp.get_completed()
                    is_completed_time = (completed_time is not None and not completed_time.is_null_time())

                    if percent == 100 or is_completed_status or is_completed_time:
                        continue

                    due_val = icalcomp.get_due()
                    due_dt = _ical_time_to_datetime(due_val)

                    print(f"kyou: found incomplete task: '{summary}'")
                    items.append(
                        Item(
                            id=str(icalcomp.get_uid() or ""),
                            kind=ItemKind.REMINDER,
                            title=summary,
                            start=due_dt,
                            due_date=due_dt,
                            completed=False,
                            priority=_priority_from_eds(icalcomp.get_priority()),
                            notes=str(icalcomp.get_description() or "") or None,
                            list_name=list_name,
                            list_color=list_color,
                            has_recurrence_rules=bool(comp.has_recurrences()),
                        )
                    )
                except (AttributeError, Exception) as e:
                    print(f"kyou: failed to parse a task: {e}")
                    continue

        return items

