from datetime import datetime
from gettext import gettext as _
from typing import Any

from gi.repository import Adw, GLib, Gtk

from kyou.config import PREFIX
from kyou.ui.add_item_dialog import AddItemDialog
from kyou.ui.gap_row import GapRow
from kyou.ui.now_card import NowCard
from kyou.ui.today_card import TodayCard
from kyou.ui.reminder_list_section import ReminderListSection
from kyou.ui.reminder_row import ReminderRow


@Gtk.Template(resource_path=f"{PREFIX}/window.ui")
class Window(Adw.ApplicationWindow):
    """The main window."""

    __gtype_name__ = __qualname__

    greeting_label: Any = Gtk.Template.Child()
    date_label: Gtk.Label = Gtk.Template.Child()
    reminder_list_container: Gtk.Box = Gtk.Template.Child()

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
        
        while child := self.reminder_list_container.get_first_child():
            self.reminder_list_container.remove(child)

        from kyou.models import Priority
        from gi.repository import Granite
        
        lists = {}
        for item in reminders:
            list_name = item.list_name or "Other"
            if list_name not in lists:
                lists[list_name] = {}
            prio = item.priority
            if prio not in lists[list_name]:
                lists[list_name][prio] = []
            lists[list_name][prio].append(item)
            
        order = [Priority.HIGH, Priority.MEDIUM, Priority.LOW, Priority.NONE]
        
        for list_name, prio_dict in lists.items():
            list_header = Granite.HeaderLabel(label=list_name)
            list_header.set_halign(Gtk.Align.START)
            self.reminder_list_container.append(list_header)
            
            for prio in order:
                if prio not in prio_dict:
                    continue
                    
                section = ReminderListSection(priority=prio)
                for item in prio_dict[prio]:
                    due_time = item.due_date.strftime("%H:%M") if item.due_date else None
                    row = ReminderRow(title=item.title, due_time=due_time, completed=item.completed)
                    row.connect("activated", lambda _row, i=item: self.on_reminder_activated(i))
                    section.add_row(row)
                self.reminder_list_container.append(section)

    def on_reminder_activated(self, item: Any) -> None:
        from kyou.ui.reminder_info_dialog import ReminderInfoDialog
        dialog = ReminderInfoDialog(item=item)
        dialog.present(self)

    def _update_color_scheme(self, style_manager: Adw.StyleManager) -> None:
        if style_manager.get_dark():
            self.add_css_class("dark-mode")
        else:
            self.remove_css_class("dark-mode")

    @Gtk.Template.Callback()
    def on_add_item_clicked(self, *_args: object) -> None:
        self.add_item_dialog.present(self)
