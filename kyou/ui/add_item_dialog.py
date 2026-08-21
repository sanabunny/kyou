from typing import Any

from gi.repository import Adw, Gtk

from kyou.config import PREFIX


@Gtk.Template(resource_path=f"{PREFIX}/add-item-dialog.ui")
class AddItemDialog(Adw.Dialog):
    __gtype_name__ = "AddItemDialog"

    item_type: Gtk.ComboRow = Gtk.Template.Child()
    title_entry: Gtk.Entry = Gtk.Template.Child()
    date_entry: Gtk.Entry = Gtk.Template.Child()
    time_entry: Gtk.Entry = Gtk.Template.Child()
    priority: Gtk.ComboRow = Gtk.Template.Child()

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

    @Gtk.Template.Callback()
    def on_add_clicked(self, *_args: object) -> None:
        self.close()
