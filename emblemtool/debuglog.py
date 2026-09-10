"""Optional debug log: a detailed, timestamped record of what the toolkit does
and everything that goes wrong, written to logs/ in the toolkit folder (next
to the exe for the standalone build) so users can attach it to a bug report.

Off by default. Turned on from the control panel's Troubleshooting section,
or with `python run.py --debug`, and remembered between runs in
settings.json. While it's off, every logging call here is a cheap no-op.

The file is meant to be shared, so it never contains URL query strings (they
can carry session tickets), header values beyond a few harmless framing ones,
or emblem data. Player IDs (the u<hex> in emblem URLs) are swapped for stable
aliases - player-1, player-2, ... - and the user's home folder becomes ~.
"""
import json
import logging
import os
import platform
import re
import socket
import subprocess
import sys
import threading
import time
from logging.handlers import RotatingFileHandler

from . import __version__, config

MAX_BYTES = 5 * 1024 * 1024  # per file; with 2 rotated backups a log tops out around 15 MB

_logger = logging.getLogger("emblemtool.debug")
_logger.propagate = False
_logger.addHandler(logging.NullHandler())
_logger.setLevel(logging.CRITICAL + 1)  # everything off until set_enabled(True)

_lock = threading.Lock()
_handler = None
_path = None

_PLAYER_RE = re.compile(r"\bu[0-9a-fA-F]{8,}\b")
_aliases = {}
_alias_lock = threading.Lock()
_home = os.path.expanduser("~")
# Paths show up plain, with forward slashes, and doubled-up inside exception reprs.
_HOME_RES = [re.compile(re.escape(h), re.IGNORECASE)
             for h in sorted({_home, _home.replace("\\", "/"), _home.replace("\\", "\\\\")}, key=len, reverse=True)
             if len(h) > 3]


def _alias(match):
    with _alias_lock:
        return _aliases.setdefault(match.group(0).lower(), f"player-{len(_aliases) + 1}")


class _SafeFormatter(logging.Formatter):
    """Applies the privacy rules above to every line, tracebacks included."""

    def format(self, record):
        text = super().format(record)
        for home in _HOME_RES:
            text = home.sub("~", text)
        return _PLAYER_RE.sub(_alias, text)


class _DefaultCategory(logging.Filter):
    def filter(self, record):
        record.cat = getattr(record, "cat", "-")
        return True


def enabled():
    return _handler is not None


def log_file():
    """The current log file - or, once logging is turned off, the last one."""
    return _path


def debug(cat, msg):
    _logger.debug(msg, extra={"cat": cat})


def info(cat, msg):
    _logger.info(msg, extra={"cat": cat})


def warning(cat, msg):
    _logger.warning(msg, extra={"cat": cat})


def error(cat, msg, exc=False):
    """exc=True appends the traceback of the exception being handled."""
    _logger.error(msg, exc_info=exc, extra={"cat": cat})


def set_enabled(on):
    """Start a fresh log file, or stop logging - and remember the choice.
    Raises OSError if the logs folder or file can't be created."""
    global _handler, _path
    with _lock:
        if on and _handler is None:
            os.makedirs(config.LOG_DIR, exist_ok=True)
            path = os.path.join(config.LOG_DIR, time.strftime("debug-%Y-%m-%d_%H-%M-%S.log"))
            handler = RotatingFileHandler(path, maxBytes=MAX_BYTES, backupCount=2, encoding="utf-8")
            handler.setFormatter(_SafeFormatter(
                "%(asctime)s.%(msecs)03d %(levelname)-7s %(cat)-8s [%(threadName)s] %(message)s", "%Y-%m-%d %H:%M:%S"))
            handler.addFilter(_DefaultCategory())
            with _alias_lock:
                _aliases.clear()
            _path = path
            _handler = handler
            _logger.addHandler(handler)
            _logger.setLevel(logging.DEBUG)
            _write_header()
        elif not on and _handler is not None:
            info("DEBUG", "debug logging turned off")
            _logger.setLevel(logging.CRITICAL + 1)
            _logger.removeHandler(_handler)
            _handler.close()
            _handler = None
    _remember(on)


def remembered():
    """Whether debug logging was left on last time."""
    try:
        with open(config.SETTINGS_FILE) as f:
            return bool(json.load(f).get("debug"))
    except (OSError, ValueError, AttributeError):
        return False


def _remember(on):
    try:
        with open(config.SETTINGS_FILE) as f:
            settings = json.load(f)
        if not isinstance(settings, dict):
            settings = {}
    except (OSError, ValueError):
        settings = {}
    settings["debug"] = bool(on)
    try:
        with open(config.SETTINGS_FILE, "w") as f:
            json.dump(settings, f)
    except OSError as e:
        warning("DEBUG", f"couldn't save the debug setting to settings.json: {e}")


def _local_ipv4s():
    try:
        infos = socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET)
    except OSError:
        return []
    return sorted({ai[4][0] for ai in infos})


def _write_header():
    try:
        import PIL
        pillow = PIL.__version__
    except Exception as e:  # the log should still start if Pillow itself is what's broken
        pillow = f"not available ({e})"
    build = "exe" if getattr(sys, "frozen", False) else "source"
    for line in (
        "==== BO2 Emblem Toolkit debug log ====",
        f"toolkit {__version__} ({build}), Python {platform.python_version()}, {platform.platform()}, Pillow {pillow}",
        f"folder: {config.ROOT_DIR}",
        f"proxy on {config.PROXY_HOST}:{config.PROXY_PORT}, control panel on {config.WEB_HOST}:{config.WEB_PORT}",
        f"this PC's IPv4 addresses: {', '.join(_local_ipv4s()) or 'none found'}",
        "privacy: no URL query strings, login/cookie headers or emblem data; player IDs -> player-1, player-2, ...",
    ):
        info("START", line)


def install_crash_hooks():
    """Also record crashes nothing else catches - in any thread - which would
    otherwise only ever be a traceback in the console window."""
    previous_thread_hook = threading.excepthook

    def thread_hook(args):
        if args.exc_type is not SystemExit:
            name = args.thread.name if args.thread else "?"
            _logger.error(f"uncaught error in thread {name}", extra={"cat": "CRASH"},
                          exc_info=(args.exc_type, args.exc_value, args.exc_traceback))
        previous_thread_hook(args)

    threading.excepthook = thread_hook
    previous_hook = sys.excepthook

    def main_hook(exc_type, exc_value, tb):
        if not issubclass(exc_type, KeyboardInterrupt):
            _logger.critical("uncaught error - the toolkit stopped", extra={"cat": "CRASH"},
                             exc_info=(exc_type, exc_value, tb))
        previous_hook(exc_type, exc_value, tb)

    sys.excepthook = main_hook


def open_log_folder():
    """Show the logs folder in Explorer/Finder, with the newest log selected
    when there is one. Raises OSError if that can't be done."""
    os.makedirs(config.LOG_DIR, exist_ok=True)
    target = _path if _path and os.path.exists(_path) else None
    if sys.platform == "win32":
        if target:
            subprocess.Popen(f'explorer /select,"{target}"')
        else:
            os.startfile(config.LOG_DIR)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", "-R", target] if target else ["open", config.LOG_DIR])
    else:
        subprocess.Popen(["xdg-open", config.LOG_DIR])
