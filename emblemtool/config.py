"""Paths, ports, and other fixed settings used across the toolkit."""
import os

# Project root = the folder this package lives in (one level up from emblemtool/).
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SAVED_DIR = os.path.join(ROOT_DIR, "saved")
SHAPES_DIR = os.path.join(ROOT_DIR, "reference_shapes")
STATE_FILE = os.path.join(ROOT_DIR, "state.txt")
TRAFFIC_LOG = os.path.join(ROOT_DIR, "traffic.jsonl")
TRAFFIC_BODIES_DIR = os.path.join(ROOT_DIR, "traffic_bodies")

ACTIVE_NAME = "_active"  # reserved pseudo-group: the currently armed injection set

PROXY_HOST = "0.0.0.0"
PROXY_PORT = 8080
WEB_HOST = "0.0.0.0"
WEB_PORT = 8090

TARGET_HOST_SUBSTR = "ops2-ps3-cs.prod.demonware.net"
