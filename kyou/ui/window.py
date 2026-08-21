from typing import Any

from gi.repository import Adw, Gtk

from kyou.config import PREFIX
from kyou.ui.add_item_dialog import AddItemDialog
from kyou.ui.gap_row import GapRow
from kyou.ui.now_card import NowCard
from kyou.ui.today_card import TodayCard


@Gtk.Template(resource_path=f"{PREFIX}/window.ui")
class Window(Adw.ApplicationWindow):
    """The main window."""

    __gtype_name__ = __qualname__

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

        style_manager = Adw.StyleManager.get_default()
        self._update_color_scheme(style_manager)
        style_manager.connect(
            "notify::dark", lambda mgr, *_a: self._update_color_scheme(mgr)
        )
        self.add_item_dialog = AddItemDialog()

    def _update_color_scheme(self, style_manager: Adw.StyleManager) -> None:
        if style_manager.get_dark():
            self.add_css_class("dark-mode")
        else:
            self.remove_css_class("dark-mode")

    @Gtk.Template.Callback()
    def on_add_item_clicked(self, *_args: object) -> None:
        self.add_item_dialog.present(self)
