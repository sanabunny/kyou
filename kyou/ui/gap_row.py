from typing import Any

from gi.repository import GObject, Gtk

from kyou.config import PREFIX


@Gtk.Template(resource_path=f"{PREFIX}/gap-row.ui")
class GapRow(Gtk.Box):
    __gtype_name__ = "GapRow"

    emoji_label: Gtk.Label = Gtk.Template.Child()
    text_label: Gtk.Label = Gtk.Template.Child()

    emoji_text = GObject.Property(type=str, default="")
    text_text = GObject.Property(type=str, default="")

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.connect("notify", lambda *_a: self._apply())
        self._apply()

    def _apply(self) -> None:
        self.emoji_label.set_label(self.emoji_text)
        self.text_label.set_label(self.text_text)
