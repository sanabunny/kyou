import locale
import sys

from gi.events import GLibEventLoopPolicy

from .application import Application
from .config import APP_ID

try:
    locale.setlocale(locale.LC_ALL, "")
except locale.Error:
    pass

app = Application(application_id=APP_ID)
with GLibEventLoopPolicy():
    raise SystemExit(app.run(sys.argv))
