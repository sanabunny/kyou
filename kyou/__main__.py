import sys

from gi.events import GLibEventLoopPolicy

from .application import Application
from .config import APP_ID

app = Application(application_id=APP_ID)
with GLibEventLoopPolicy():
    raise SystemExit(app.run(sys.argv))
