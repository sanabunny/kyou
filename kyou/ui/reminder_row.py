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
        self.add_css_class("reminder-row")
        self.set_cursor_from_name("pointer")
        self.check_button.set_cursor_from_name("pointer")

        motion = Gtk.EventControllerMotion()
        motion.connect("enter", lambda *_a: self.add_css_class("row-hover"))
        motion.connect("leave", lambda *_a: self.remove_css_class("row-hover"))
        self.add_controller(motion)

        self.set_title(title)

        if due_time:
            self.set_subtitle(due_time)
            
        if completed:
            self.check_button.set_active(True)
            self.add_css_class("dim-label")
