from datetime import datetime, timedelta
from gettext import gettext as _
from typing import Any

from gi.repository import Adw, Gio, GLib, Gtk

from kyou.config import PREFIX
from kyou.ui.add_item_dialog import AddItemDialog
from kyou.ui.gap_row import GapRow
from kyou.ui.now_card import NowCard
from kyou.ui.today_card import TodayCard
from kyou.ui.reminder_list_section import ReminderListSection
from kyou.ui.reminder_row import ReminderRow


_WEEKDAYS = [
    _("Monday"),
    _("Tuesday"),
    _("Wednesday"),
    _("Thursday"),
    _("Friday"),
    _("Saturday"),
    _("Sunday"),
]

_MONTHS = [
    _("January"),
    _("February"),
    _("March"),
    _("April"),
    _("May"),
    _("June"),
    _("July"),
    _("August"),
    _("September"),
    _("October"),
    _("November"),
    _("December"),
]

_SHORT_MONTHS = [
    _("Jan"),
    _("Feb"),
    _("Mar"),
    _("Apr"),
    _("May"),
    _("Jun"),
    _("Jul"),
    _("Aug"),
    _("Sep"),
    _("Oct"),
    _("Nov"),
    _("Dec"),
]


def _format_due_date(due: datetime | None, all_day: bool = False) -> str | None:
    if not due:
        return None
    today = datetime.now().date()
    due_date = due.date()
    has_time = not all_day and not (due.hour == 0 and due.minute == 0)
    time_str = due.strftime("%H:%M") if has_time else ""

    if due_date == today:
        return _("Today · {}").format(time_str) if has_time else _("Today")
    elif due_date == today + timedelta(days=1):
        return _("Tomorrow · {}").format(time_str) if has_time else _("Tomorrow")
    elif due_date == today - timedelta(days=1):
        return _("Yesterday · {}").format(time_str) if has_time else _("Yesterday")
    elif due_date.year == today.year:
        m_str = _SHORT_MONTHS[due.month - 1]
        date_str = _("{day} {month}").format(day=due.day, month=m_str)
        return _("{date} · {time}").format(date=date_str, time=time_str) if has_time else date_str
    else:
        m_str = _SHORT_MONTHS[due.month - 1]
        date_str = _("{day} {month} {year}").format(day=due.day, month=m_str, year=due.year)
        return _("{date} · {time}").format(date=date_str, time=time_str) if has_time else date_str


@Gtk.Template(resource_path=f"{PREFIX}/window.ui")
class Window(Adw.ApplicationWindow):
    """The main window."""

    __gtype_name__ = __qualname__

    greeting_label: Any = Gtk.Template.Child()
    date_label: Gtk.Label = Gtk.Template.Child()
    reminder_list_container: Gtk.Box = Gtk.Template.Child()
    today_list_container: Gtk.Box = Gtk.Template.Child()
    no_reminders_page: Adw.StatusPage = Gtk.Template.Child()
    no_events_page: Adw.StatusPage = Gtk.Template.Child()
    view_stack: Adw.ViewStack = Gtk.Template.Child()
    today_page: Any = Gtk.Template.Child()
    reminders_page: Any = Gtk.Template.Child()
    main_menu_button: Gtk.MenuButton = Gtk.Template.Child()
    reminders_menu_button: Gtk.MenuButton = Gtk.Template.Child()
    create_item_button: Gtk.Button = Gtk.Template.Child()
    add_item_button: Gtk.Button = Gtk.Template.Child()

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        self.today_page.set_title(_("Today"))
        self.reminders_page.set_title(_("Reminders"))

        menu = Gio.Menu()
        menu.append(_("About Kyou"), "app.about")
        self.main_menu_button.set_menu_model(menu)
        self.main_menu_button.set_tooltip_text(_("Main Menu"))
        self.reminders_menu_button.set_menu_model(menu)
        self.reminders_menu_button.set_tooltip_text(_("Main Menu"))

        self.create_item_button.set_tooltip_text(_("Create Item (coming soon)"))
        self.add_item_button.set_tooltip_text(_("Create Item (coming soon)"))

        self.no_events_page.set_title(_("Nothing Scheduled"))
        self.no_events_page.set_description(_("You have nothing on today 🌸"))
        self.no_reminders_page.set_title(_("No Reminders"))
        self.no_reminders_page.set_description(_("You have no reminders set up yet."))

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
        weekday_name = _WEEKDAYS[now.weekday()]
        month_name = _MONTHS[now.month - 1]
        date_formatted = _("{weekday}, {day} {month}").format(
            weekday=weekday_name,
            day=now.day,
            month=month_name,
        )
        self.date_label.set_label(date_formatted)
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

        has_reminders = len(reminders) > 0
        self.no_reminders_page.set_visible(not has_reminders)

        today_date = datetime.today().date()
        has_today_items = bool(today_events) or any(
            r.due_date and r.due_date.date() == today_date and not r.completed
            for r in reminders
        )
        self.no_events_page.set_visible(not has_today_items)

        from kyou.models import Priority
        from gi.repository import Granite
        
        lists = {}
        for item in reminders:
            list_name = item.list_name or _("Other")
            if list_name not in lists:
                lists[list_name] = {}
            prio = item.priority
            if prio not in lists[list_name]:
                lists[list_name][prio] = []
            lists[list_name][prio].append(item)
            
        order = [Priority.HIGH, Priority.MEDIUM, Priority.LOW, Priority.NONE]
        
        for list_name, prio_dict in lists.items():
            list_header = Granite.HeaderLabel(label=list_name, size=Granite.HeaderLabelSize.H2)
            list_header.set_halign(Gtk.Align.START)
            self.reminder_list_container.append(list_header)
            
            for prio in order:
                if prio not in prio_dict:
                    continue
                    
                section = ReminderListSection(priority=prio)
                for item in prio_dict[prio]:
                    due_time = _format_due_date(item.due_date, item.all_day)
                    row = ReminderRow(title=item.title, due_time=due_time, completed=item.completed)
                    row.connect("activated", lambda _row, i=item: self.on_item_activated(i))
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
                        gap_str = _("{}h {}m").format(gap_hours, gap_mins)
                    elif gap_hours > 0:
                        gap_str = _("{}h").format(gap_hours)
                    else:
                        gap_str = _("{}m").format(gap_mins)
                    is_gap_now = last_end_time <= now < event.start
                    gap_label = _("{} free time").format(gap_str)
                    gap_text = f"{gap_label} · " + _("NOW") if is_gap_now else gap_label
                    gap_row = GapRow(emoji_text="☕", text_text=gap_text, is_now=is_gap_now)
                    self.today_list_container.append(gap_row)
                    
            is_active = False
            if event.start and event.end:
                is_active = event.start <= now <= event.end

            if event.all_day:
                time_text = _("All Day")
            elif event.start:
                time_text = event.start.strftime("%H:%M")
                if event.end and not event.all_day:
                    time_text += " – " + event.end.strftime("%H:%M")
                if is_active:
                    time_text += "  · " + _("NOW")

            subtitle_text = ""
            if event.start and event.end and not event.all_day:
                dur_delta = event.end - event.start
                dur_minutes = int(dur_delta.total_seconds() / 60)
                dur_hours = dur_minutes // 60
                dur_mins = dur_minutes % 60
                if dur_hours > 0 and dur_mins > 0:
                    subtitle_text = _("{}h {}m").format(dur_hours, dur_mins)
                elif dur_hours > 0:
                    subtitle_text = _("{}h").format(dur_hours)
                else:
                    subtitle_text = _("{}m").format(dur_mins)
                    
            if event.kind.name == "REMINDER":
                emoji_text = "✅"
            else:
                emoji_text = "📅" if not event.all_day else "🏖️"

            cal_color = event.list_color or ""

            if event.kind.name == "REMINDER":
                is_done = event.completed
            else:
                is_done = bool(event.end and event.end < now)
            
            if is_active:
                card = NowCard(
                    icon_text=emoji_text,
                    time_text=time_text,
                    title_text=event.title,
                    subtitle_text=subtitle_text,
                    tilt_class=next(tilt_iter),
                    sticker_type=next(sticker_iter),
                    calendar_color=cal_color,
                    done=is_done,
                )
            else:
                card = TodayCard(
                    icon_text=emoji_text,
                    time_text=time_text,
                    title_text=event.title,
                    subtitle_text=subtitle_text,
                    tilt_class=next(tilt_iter),
                    sticker_type=next(sticker_iter),
                    calendar_color=cal_color,
                    done=is_done,
                )
            
            card.connect("activated", lambda _card, ev=event: self.on_item_activated(ev))
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
                    gap_str = _("{}h {}m").format(gap_hours, gap_mins)
                elif gap_hours > 0:
                    gap_str = _("{}h").format(gap_hours)
                else:
                    gap_str = _("{}m").format(gap_mins)
                is_gap_now = last_end_time <= now < end_of_day
                gap_label = _("{} → time left of day").format(gap_str)
                gap_text = f"{gap_label} · " + _("NOW") if is_gap_now else gap_label
                gap_row = GapRow(emoji_text="🌙", text_text=gap_text, is_now=is_gap_now)
                self.today_list_container.append(gap_row)

    def on_item_activated(self, item: Any) -> None:
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
