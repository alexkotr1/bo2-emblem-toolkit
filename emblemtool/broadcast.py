"""The single emblem currently selected to load into your own editor.

Exactly one captured emblem can be selected at a time. While in Show mode,
opening your own emblem editor on the PS5 triggers a request for one of your
saved emblem slots - the proxy answers with the selected emblem's data
instead of your real saved data, regardless of which numbered slot your
console happens to ask for. From there you save it in the editor like
anything else, and it's permanently yours.
"""
import json
import os

from . import config
from .storage import group_dir


def _data_path():
    return os.path.join(group_dir(config.ACTIVE_NAME), "selected.bin")


def _meta_path():
    return os.path.join(group_dir(config.ACTIVE_NAME), "selected_meta.json")


def read_selection():
    """{'group': ..., 'slot': ...} for the currently selected emblem, or None."""
    try:
        with open(_meta_path()) as f:
            return json.load(f)
    except FileNotFoundError:
        return None


def select_emblem(group, slot):
    """Select one captured emblem to load into your own editor next."""
    os.makedirs(group_dir(config.ACTIVE_NAME), exist_ok=True)
    with open(os.path.join(group_dir(group), f"slot_{slot}.bin"), "rb") as f:
        data = f.read()
    with open(_data_path(), "wb") as f:
        f.write(data)
    with open(_meta_path(), "w") as f:
        json.dump({"group": group, "slot": slot}, f)


def clear_selection():
    for p in (_data_path(), _meta_path()):
        if os.path.exists(p):
            os.remove(p)


def read_selected_data():
    """Raw bytes (HTTP headers + body) of the selected emblem, or None."""
    try:
        with open(_data_path(), "rb") as f:
            return f.read()
    except FileNotFoundError:
        return None
