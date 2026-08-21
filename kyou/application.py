from gettext import gettext as _
from typing import override

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

try:
    gi.require_version("Granite", "7.0")
    from gi.repository import Granite

    HAS_GRANITE = True
except (ValueError, ImportError):
    try:
        gi.require_version("Granite", "7")
        from gi.repository import Granite

        HAS_GRANITE = True
    except (ValueError, ImportError):
        Granite = None
        HAS_GRANITE = False

from gi.repository import Adw, Gdk, GObject, Gtk

from .config import APP_ID, PREFIX
from .ui.window import Window


class Application(Adw.Application):
    """The main application."""

    @override
    def do_startup(self) -> None:
        Adw.Application.do_startup(self)

        if HAS_GRANITE and hasattr(Granite, "init"):
            Granite.init()

        if HAS_GRANITE:
            GObject.type_ensure(Granite.HeaderLabel.__gtype__)
            GObject.type_ensure(Granite.ListItem.__gtype__)

        self.add_action_entries(
            (
                ("about", lambda *_: self._present_about_dialog()),
                ("quit", lambda *_: self.quit()),
            )
        )

        self.set_accels_for_action("app.quit", ("<Control>q",))

        self._load_stylesheet()

    def _load_stylesheet(self) -> None:
        display = Gdk.Display.get_default()
        if not display:
            return

        if HAS_GRANITE:
            self._granite_provider = Gtk.CssProvider()
            self._granite_dark_provider = Gtk.CssProvider()
            try:
                self._granite_provider.load_from_resource(
                    "/io/elementary/granite/Granite.css"
                )
                Gtk.StyleContext.add_provider_for_display(
                    display,
                    self._granite_provider,
                    Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
                )
            except Exception:
                pass

            try:
                self._granite_dark_provider.load_from_resource(
                    "/io/elementary/granite/Granite-dark.css"
                )
            except Exception:
                pass

            style_manager = Adw.StyleManager.get_default()
            style_manager.connect("notify::dark", self._on_dark_mode_changed)
            self._on_dark_mode_changed(style_manager)

        provider = Gtk.CssProvider()
        provider.load_from_resource(f"{PREFIX}/style.css")
        Gtk.StyleContext.add_provider_for_display(
            display,
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION + 10,
        )

    def _on_dark_mode_changed(
        self, style_manager: Adw.StyleManager, *_: object
    ) -> None:
        display = Gdk.Display.get_default()
        if not display or not hasattr(self, "_granite_dark_provider"):
            return

        if style_manager.props.dark:
            Gtk.StyleContext.add_provider_for_display(
                display,
                self._granite_dark_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION + 1,
            )
        else:
            Gtk.StyleContext.remove_provider_for_display(
                display,
                self._granite_dark_provider,
            )

    @override
    def do_activate(self) -> None:
        window = self.props.active_window or Window(application=self)
        window.present()

    def _present_about_dialog(self) -> None:
        about = Adw.AboutDialog(appdata_resource_path=f"{PREFIX}/{APP_ID}.metainfo.xml")
        # Translators: Replace "translator-credits" with your name/username,
        # and optionally a URL or an email in <me@example.org> format.
        about.props.translator_credits = _("translator-credits")
        about.present(self.props.active_window)
