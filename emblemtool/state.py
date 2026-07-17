"""Reads and writes the proxy's current mode.

Modes:
  PASSTHROUGH - proxy is transparent, nothing is captured or replaced
  CAPTURE     - emblem slot responses are saved to a new/existing group
  INJECT      - emblem slot responses are replaced with the armed active set
                (or the broadcast slot, if one is armed - see active_set.py)
"""
from . import config

VALID_MODES = ("PASSTHROUGH", "CAPTURE", "INJECT")


def read_state():
    try:
        with open(config.STATE_FILE) as f:
            mode = f.read().strip().upper()
    except FileNotFoundError:
        return "PASSTHROUGH"
    return mode if mode in VALID_MODES else "PASSTHROUGH"


def write_state(mode):
    mode = mode.upper()
    if mode not in VALID_MODES:
        raise ValueError(f"invalid mode: {mode!r}")
    with open(config.STATE_FILE, "w") as f:
        f.write(mode)
