from typing import Any

from gi.repository import GObject, Gtk

from kyou.config import PREFIX


@Gtk.Template(resource_path=f"{PREFIX}/now-card.ui")
class NowCard(Gtk.Overlay):
    __gtype_name__ = "NowCard"

    card_box: Gtk.Box = Gtk.Template.Child()
    time_label: Gtk.Label = Gtk.Template.Child()
    icon_label: Gtk.Label = Gtk.Template.Child()
    title_label: Gtk.Label = Gtk.Template.Child()
    subtitle_label: Gtk.Label = Gtk.Template.Child()
    sticker_box: Gtk.Box = Gtk.Template.Child()
    sticker_label: Gtk.Label = Gtk.Template.Child()

    time_text = GObject.Property(type=str, default="")
    title_text = GObject.Property(type=str, default="")
    subtitle_text = GObject.Property(type=str, default="")
    icon_text = GObject.Property(type=str, default="")
    tilt_class = GObject.Property(type=str, default="tilt-left")
    # one of "washi-tape" / "washi-tape-right" / "pin" / "" (none)
    sticker_type = GObject.Property(type=str, default="")

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.connect("notify", lambda *_a: self._apply())
        self._apply()

    def _apply(self) -> None:
        self.time_label.set_label(self.time_text)
        self.title_label.set_label(self.title_text)
        self.subtitle_label.set_label(self.subtitle_text)
        self.icon_label.set_label(self.icon_text)
        self.card_box.add_css_class(self.tilt_class)

        if self.sticker_type == "pin":
            self.sticker_label.set_visible(True)
        elif self.sticker_type:
            self.sticker_box.add_css_class(self.sticker_type)
            self.sticker_box.set_visible(True)
