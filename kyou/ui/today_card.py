from typing import Any

from gi.repository import Gdk, GObject, Gtk

from kyou.config import PREFIX


@Gtk.Template(resource_path=f"{PREFIX}/today-card.ui")
class TodayCard(Gtk.Overlay):
    __gtype_name__ = "TodayCard"

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
    calendar_color = GObject.Property(type=str, default="")
    done = GObject.Property(type=bool, default=False)

    __gsignals__ = {
        "activated": (GObject.SignalFlags.RUN_FIRST, None, ()),
    }

    def __init__(self, **kwargs: Any) -> None:
        self._color_provider: Gtk.CssProvider | None = None
        super().__init__(**kwargs)
        self.set_cursor_from_name("pointer")
        self.card_box.set_cursor_from_name("pointer")

        motion = Gtk.EventControllerMotion()
        motion.connect("enter", lambda *_a: self.card_box.add_css_class("card-hover"))
        motion.connect(
            "leave", lambda *_a: self.card_box.remove_css_class("card-hover")
        )
        self.card_box.add_controller(motion)

        click = Gtk.GestureClick()
        click.connect("released", lambda *_a: self.emit("activated"))
        self.add_controller(click)
        self.connect("notify", lambda *_a: self._apply())
        self._apply()

    def _apply(self) -> None:
        self.time_label.set_label(self.time_text)
        self.title_label.set_label(self.title_text)
        self.subtitle_label.set_label(self.subtitle_text)
        self.icon_label.set_label(self.icon_text)
        self.card_box.add_css_class(self.tilt_class)
        if self.done:
            self.card_box.add_css_class("card-done")
        else:
            self.card_box.remove_css_class("card-done")

        if self._color_provider:
            self.card_box.get_style_context().remove_provider(self._color_provider)
            self._color_provider = None

        if self.calendar_color:
            css = f".card {{ border-left: 5px solid {self.calendar_color}; }}"
            self._color_provider = Gtk.CssProvider()
            self._color_provider.load_from_string(css)
            self.card_box.get_style_context().add_provider(
                self._color_provider, Gtk.STYLE_PROVIDER_PRIORITY_USER
            )

        if self.sticker_type == "pin":
            self.sticker_label.set_visible(True)
        elif self.sticker_type:
            self.sticker_box.add_css_class(self.sticker_type)
            self.sticker_box.set_visible(True)
