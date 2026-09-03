from datetime import datetime
from gettext import gettext as _
from typing import Any

from gi.repository import Adw, GLib, Gtk

from kyou.config import PREFIX
from kyou.ui.add_item_dialog import AddItemDialog
from kyou.ui.gap_row import GapRow
from kyou.ui.now_card import NowCard
from kyou.ui.today_card import TodayCard


@Gtk.Template(resource_path=f"{PREFIX}/window.ui")
class Window(Adw.ApplicationWindow):
    """The main window."""

    __gtype_name__ = __qualname__

    greeting_label: Any = Gtk.Template.Child()
    date_label: Gtk.Label = Gtk.Template.Child()

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        style_manager = Adw.StyleManager.get_default()
        self._update_color_scheme(style_manager)
        style_manager.connect(
            "notify::dark", lambda mgr, *_a: self._update_color_scheme(mgr)
        )
        self.add_item_dialog = AddItemDialog()

        self._update_datetime_header()
        GLib.timeout_add_seconds(60, self._update_datetime_header)

        self._load_system_data()

    def _update_datetime_header(self) -> bool:
        now = datetime.now()
        hour = now.hour

        if 5 <= hour < 12:
            greeting = _("good morning! 🌸")
        elif 12 <= hour < 18:
            greeting = _("good afternoon! ☀️")
        elif 18 <= hour < 22:
            greeting = _("good evening! 🌆")
        else:
            greeting = _("good night! 🌙")

        self.greeting_label.set_label(greeting)
        self.date_label.set_label(now.strftime("%A, %-d %B").lower())
        return GLib.SOURCE_CONTINUE

    def _load_system_data(self) -> None:
        try:
            from kyou.backends import get_backend

            backend = get_backend()
        except (NotImplementedError, ImportError) as exc:
            print(f"kyou: backend unavailable: {exc}")
            return

        if not backend.request_access():
            print("kyou: calendar/reminders access was not granted")
            return

        reminders = backend.get_reminders()
        print(f"kyou: fetched {len(reminders)} reminder(s) from the system")
        for item in reminders:
            self._print_item(item)

    def _print_item(self, item: object) -> None:
        print(f"--- {item.title!r} ---")
        print(f"  id: {item.id}")
        print(f"  kind: {item.kind.name}")
        print(f"  start: {item.start}")
        print(f"  end: {item.end}")
        print(f"  due_date: {item.due_date}")
        print(f"  all_day: {item.all_day}")
        print(f"  completed: {item.completed}")
        print(f"  completed_date: {item.completed_date}")
        print(f"  priority: {item.priority.name}")
        print(f"  flagged: {item.flagged}")
        print(f"  notes: {item.notes!r}")
        print(f"  location: {item.location!r}")
        print(f"  url: {item.url!r}")
        print(f"  list_name: {item.list_name!r}")
        print(f"  list_color: {item.list_color!r}")
        print(f"  created_date: {item.created_date}")
        print(f"  last_modified_date: {item.last_modified_date}")
        print(f"  has_recurrence_rules: {item.has_recurrence_rules}")
        for rule in item.recurrence_rules:
            print(
                f"    recurrence: freq={rule.frequency} interval={rule.interval} "
                f"end_date={rule.end_date} occurrence_count={rule.occurrence_count}"
            )
        for alarm in item.alarms:
            print(
                f"    alarm: trigger_date={alarm.trigger_date} "
                f"relative_offset={alarm.relative_offset}"
            )

    def _update_color_scheme(self, style_manager: Adw.StyleManager) -> None:
        if style_manager.get_dark():
            self.add_css_class("dark-mode")
        else:
            self.remove_css_class("dark-mode")

    @Gtk.Template.Callback()
    def on_add_item_clicked(self, *_args: object) -> None:
        self.add_item_dialog.present(self)
