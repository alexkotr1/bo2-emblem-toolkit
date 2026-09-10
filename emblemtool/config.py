"""Paths, ports, and other fixed settings used across the toolkit."""
import os
import sys

# Where captures and the current mode are written. When running from source
# this is the repo root; when running as a frozen exe (PyInstaller), it's the
# folder the exe itself sits in, so saved emblems survive between runs
# instead of landing in the temp folder the exe unpacks itself into.
if getattr(sys, "frozen", False):
    ROOT_DIR = os.path.dirname(os.path.abspath(sys.executable))
else:
    ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Where read-only bundled resources (shape reference images, LICENSE) live.
# PyInstaller unpacks these into a temp folder at startup (sys._MEIPASS);
# running from source, they're just files in the repo.
RESOURCE_DIR = getattr(sys, "_MEIPASS", ROOT_DIR)

SAVED_DIR = os.path.join(ROOT_DIR, "saved")
SHAPES_DIR = os.path.join(RESOURCE_DIR, "reference_shapes")
STATE_FILE = os.path.join(ROOT_DIR, "state.txt")
LOG_DIR = os.path.join(ROOT_DIR, "logs")  # debug logs, see debuglog.py
SETTINGS_FILE = os.path.join(ROOT_DIR, "settings.json")  # remembered panel settings (debug log on/off)

ACTIVE_NAME = "_active"  # reserved pseudo-group: the currently armed injection set

PROXY_HOST = "0.0.0.0"
PROXY_PORT = 8080
WEB_HOST = "0.0.0.0"
WEB_PORT = 8090

# Emblem requests are recognized by their path (see proxy.PATH_RE) on any
# Demonware host, not by one hardcoded hostname - so a regional host or a
# rename in a game update is still picked up. USUAL_EMBLEM_HOST is only used
# to log it when a different host turns up.
EMBLEM_HOST_SUFFIX = ".demonware.net"
USUAL_EMBLEM_HOST = "ops2-ps3-cs.prod.demonware.net"
