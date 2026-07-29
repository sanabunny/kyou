from gettext import gettext as _
from typing import override

from gi.repository import Adw, Gdk, Gtk

from .config import APP_ID, PREFIX
from .ui.window import Window


class Application(Adw.Application):
    """The main application."""

    @override
    def do_startup(self) -> None:
        Adw.Application.do_startup(self)

        self.add_action_entries((
            ("about", lambda *_: self._present_about_dialog()),
            ("quit", lambda *_: self.quit()),
        ))
        self.set_accels_for_action("app.quit", ("<Control>q",))

        self._load_stylesheet()

    def _load_stylesheet(self) -> None:
        provider = Gtk.CssProvider()
        provider.load_from_resource(f"{PREFIX}/style.css")
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
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
