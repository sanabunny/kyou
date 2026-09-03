from typing import Any

from gi.repository import Adw, Gtk

from kyou.config import PREFIX


@Gtk.Template(resource_path=f"{PREFIX}/reminder-row.ui")
class ReminderRow(Adw.ActionRow):
    __gtype_name__ = "ReminderRow"

    check_button: Gtk.CheckButton = Gtk.Template.Child()

    def __init__(
        self,
        title: str,
        due_time: str | None = None,
        completed: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(**kwargs)
        self.set_title(title)

        if due_time:
            self.set_subtitle(due_time)
            
        if completed:
            self.check_button.set_active(True)
            self.add_css_class("dim-label")
