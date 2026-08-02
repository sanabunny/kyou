from typing import Any

from gi.repository import Adw, Gtk

from kyou.config import PREFIX


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

    def _update_color_scheme(self, style_manager: Adw.StyleManager) -> None:
        if style_manager.get_dark():
            self.add_css_class("dark-mode")
        else:
            self.remove_css_class("dark-mode")
