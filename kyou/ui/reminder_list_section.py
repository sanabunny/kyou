from typing import Any

from gi.repository import Adw, Gtk

from kyou.config import PREFIX
from kyou.models import Priority


@Gtk.Template(resource_path=f"{PREFIX}/reminder-list-section.ui")
class ReminderListSection(Gtk.Box):
    __gtype_name__ = "ReminderListSection"

    header_button: Gtk.Button = Gtk.Template.Child()
    preferences_group: Adw.PreferencesGroup = Gtk.Template.Child()

    def __init__(self, priority: Priority, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        
        if priority == Priority.HIGH:
            self.header_button.set_label("▲ HIGH")
            self.header_button.add_css_class("destructive-action")
        elif priority == Priority.MEDIUM:
            self.header_button.set_label("● MEDIUM")
            self.header_button.add_css_class("warning")
        elif priority == Priority.LOW:
            self.header_button.set_label("▼ LOW")
            self.header_button.add_css_class("success")
        else:
            self.header_button.set_label("▪ OTHER")

    def add_row(self, row: Gtk.Widget) -> None:
        self.preferences_group.add(row)
