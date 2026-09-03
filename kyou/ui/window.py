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
    today_list_container: Gtk.Box = Gtk.Template.Child()

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
        today_events = backend.get_events(datetime.today().date())
        today_events.sort(key=lambda e: e.start or datetime.min)
        
        while child := self.reminder_list_container.get_first_child():
            self.reminder_list_container.remove(child)

        while child := self.today_list_container.get_first_child():
            self.today_list_container.remove(child)
            
        self._populate_today_tab(today_events, reminders)

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

    def _populate_today_tab(self, today_events: list, reminders: list) -> None:
        import itertools
        tilt_iter = itertools.cycle(["tilt-left", "tilt-right"])
        sticker_iter = itertools.cycle(["washi-tape", "washi-tape-right", "pin"])
        
        now = datetime.now()
        today = now.date()
        last_end_time = datetime.combine(today, datetime.min.time())
        
        for r in reminders:
            if r.due_date and r.due_date.date() == today and not r.completed:
                today_events.append(r)
                
        today_events.sort(key=lambda e: e.start or datetime.min)
        
        for event in today_events:
            if event.start and event.start > last_end_time:
                gap_delta = event.start - last_end_time
                gap_minutes = int(gap_delta.total_seconds() / 60)
                if gap_minutes > 0:
                    gap_hours = gap_minutes // 60
                    gap_mins = gap_minutes % 60
                    if gap_hours > 0 and gap_mins > 0:
                        gap_str = f"{gap_hours}h {gap_mins}m"
                    elif gap_hours > 0:
                        gap_str = f"{gap_hours}h"
                    else:
                        gap_str = f"{gap_mins}m"
                    gap_row = GapRow(emoji_text="☕", text_text=f"{gap_str} free time")
                    self.today_list_container.append(gap_row)
                    
            is_active = False
            if event.start and event.end:
                is_active = event.start <= now <= event.end
            
            time_text = ""
            if event.all_day:
                time_text = _("All Day")
            elif event.start:
                time_text = event.start.strftime("%H:%M")
                if is_active:
                    time_text += " · NOW"
            
            subtitle_text = ""
            if event.start and event.end and not event.all_day:
                dur_delta = event.end - event.start
                dur_minutes = int(dur_delta.total_seconds() / 60)
                dur_hours = dur_minutes // 60
                dur_mins = dur_minutes % 60
                if dur_hours > 0 and dur_mins > 0:
                    subtitle_text = f"{dur_hours}h {dur_mins}m"
                elif dur_hours > 0:
                    subtitle_text = f"{dur_hours}h"
                else:
                    subtitle_text = f"{dur_mins}m"
                    
            if event.kind.name == "REMINDER":
                emoji_text = "✅"
            else:
                emoji_text = "📅" if not event.all_day else "🏖️"
            
            if is_active:
                card = NowCard(
                    icon_text=emoji_text,
                    time_text=time_text,
                    title_text=event.title,
                    subtitle_text=subtitle_text,
                    tilt_class=next(tilt_iter),
                    sticker_type=next(sticker_iter)
                )
            else:
                card = TodayCard(
                    icon_text=emoji_text,
                    time_text=time_text,
                    title_text=event.title,
                    subtitle_text=subtitle_text,
                    tilt_class=next(tilt_iter),
                    sticker_type=next(sticker_iter)
                )
            
            self.today_list_container.append(card)
            
            if not event.all_day:
                end_t = event.end or event.start
                if end_t:
                    last_end_time = max(last_end_time, end_t)
        
        end_of_day = datetime.combine(now.date(), datetime.max.time().replace(second=0, microsecond=0))
        if last_end_time < end_of_day:
            gap_delta = end_of_day - last_end_time
            gap_minutes = int(gap_delta.total_seconds() / 60)
            if gap_minutes > 0:
                gap_hours = gap_minutes // 60
                gap_mins = gap_minutes % 60
                if gap_hours > 0 and gap_mins > 0:
                    gap_str = f"{gap_hours}h {gap_mins}m"
                elif gap_hours > 0:
                    gap_str = f"{gap_hours}h"
                else:
                    gap_str = f"{gap_mins}m"
                gap_row = GapRow(emoji_text="🌙", text_text=f"{gap_str} → time left of day")
                self.today_list_container.append(gap_row)

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
