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

try:
    gi.require_version("Granite", "7.0")
    from gi.repository import Granite
except (ValueError, ImportError):
    try:
        gi.require_version("Granite", "7")
        from gi.repository import Granite
    except (ValueError, ImportError):
        Granite = None

if Granite and hasattr(Granite, "init"):
    Granite.init()

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

