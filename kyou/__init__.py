import gettext
import importlib.resources
import locale
import signal
import sys

import gi

gi.require_versions({
    "Gtk": "4.0",
    "Adw": "1",
})

from gi.repository import Gio

from .config import LOCALEDIR

signal.signal(signal.SIGINT, signal.SIG_DFL)

if sys.platform.startswith("linux"):
    locale.bindtextdomain("kyou", LOCALEDIR)
    locale.textdomain("kyou")

gettext.bindtextdomain("kyou", LOCALEDIR)
gettext.textdomain("kyou")

for file in importlib.resources.files("kyou.resources").iterdir():
    with importlib.resources.as_file(file) as path:
        resource = Gio.Resource.load(str(path))
        Gio.resources_register(resource)
