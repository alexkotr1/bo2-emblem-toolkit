"""The web control panel: a small JSON API (below) plus static files served
from web/static/. This is the only interface end users touch - there is no
command-line mode for day-to-day use.
"""
import http.server
import json
import mimetypes
import os
import socket
import time
import urllib.parse

from .. import config, debuglog
from ..state import read_state, write_state
from ..storage import list_emblems, group_dir, set_emblem_label, delete_emblem, delete_all_emblems
from ..broadcast import select_emblem, clear_selection, read_selection
from ..shapes import render as emblem_render
from .netinfo import get_lan_ip

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

_MODE_TO_INTERNAL = {"off": "PASSTHROUGH", "capture": "CAPTURE", "inject": "INJECT"}
_MODE_TO_PUBLIC = {v: k for k, v in _MODE_TO_INTERNAL.items()}


def log_state_snapshot():
    """One line of context near the top of a debug log."""
    emblems = list_emblems()
    debuglog.info("STATE", f"mode={_MODE_TO_PUBLIC.get(read_state(), 'off')}, selected={read_selection()}, "
                           f"{len(emblems)} captured emblems in {len({e['group'] for e in emblems})} groups, "
                           f"LAN IP shown to the user: {get_lan_ip() or 'not detected'}")


def _debug_status():
    return {"enabled": debuglog.enabled(), "log_file": debuglog.log_file(), "log_dir": config.LOG_DIR}


def _logged(handler):
    """Wrap do_GET/do_POST: an unexpected exception becomes a logged 500 the
    panel can show, instead of a silently dropped connection. With the debug
    log on, every action - and any request that fails or is slow - is
    recorded; routine polling isn't, to keep the log readable."""
    def wrapper(self):
        self._status = None
        self._summary = ""
        started = time.perf_counter()
        route = self.path.split("?", 1)[0]
        try:
            handler(self)
        except ConnectionError:
            debuglog.debug("PANEL", f"{self.command} {route}: the browser went away mid-reply")
        except Exception:
            debuglog.error("PANEL", f"{self.command} {route} crashed", exc=True)
            if self._status is None:
                try:
                    self._json({"ok": False, "error": "unexpected error - turn on the debug log and try again"}, 500)
                except OSError:
                    pass
        ms = (time.perf_counter() - started) * 1000
        if self.command == "POST" or (self._status or 500) >= 400 or ms > 1000:
            debuglog.info("PANEL", f"{self.command} {route}{self._summary} -> {self._status} ({ms:.0f} ms)")
    return wrapper


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass  # keep the terminal quiet - proxy.py already logs what matters

    def log_error(self, fmt, *args):
        debuglog.warning("PANEL", f"http error from {self.client_address[0]}: {fmt % args}")

    # ---------- helpers ----------

    def _json(self, obj, code=200):
        body = json.dumps(obj).encode()
        self._status = code
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _bytes(self, data, content_type, code=200):
        self._status = code
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _read_json_body(self):
        length = int(self.headers.get("Content-Length", 0) or 0)
        if not length:
            return {}
        raw = self.rfile.read(length)
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {}

    def _serve_static(self, rel_path):
        if rel_path == "":
            rel_path = "index.html"
        full = os.path.normpath(os.path.join(STATIC_DIR, rel_path))
        if not full.startswith(STATIC_DIR) or not os.path.isfile(full):
            self._json({"error": "not found"}, 404)
            return
        ctype = mimetypes.guess_type(full)[0] or "application/octet-stream"
        with open(full, "rb") as f:
            self._bytes(f.read(), ctype)

    # ---------- GET ----------

    @_logged
    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path

        if path == "/api/debug":
            self._json(_debug_status())

        elif path == "/api/status":
            self._json({
                "mode": _MODE_TO_PUBLIC.get(read_state(), "off"),
                "selected": read_selection(),
            })

        elif path == "/api/emblems":
            self._json(list_emblems())

        elif path == "/api/network-info":
            self._json({
                "lan_ip": get_lan_ip(),
                "proxy_port": config.PROXY_PORT,
                "web_port": config.WEB_PORT,
            })

        elif path == "/LICENSE":
            license_path = os.path.join(config.RESOURCE_DIR, "LICENSE")
            if os.path.isfile(license_path):
                with open(license_path, "rb") as f:
                    self._bytes(f.read(), "text/plain; charset=utf-8")
            else:
                self._json({"error": "not found"}, 404)

        elif path.startswith("/api/render/"):
            bits = path.split("/")
            if len(bits) == 5:
                group = urllib.parse.unquote(bits[3])
                slot = bits[4].removesuffix(".png")
                slot_path = os.path.join(group_dir(group), f"slot_{slot}.bin")
                if os.path.exists(slot_path):
                    try:
                        body = emblem_render.render_file_png_bytes(slot_path, size=220)
                        self._bytes(body, "image/png")
                    except Exception as e:
                        debuglog.error("RENDER", f"couldn't draw the thumbnail for {group}:{slot}", exc=True)
                        svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="220" height="220">'
                               f'<rect width="100%" height="100%" fill="#1a1a1a"/>'
                               f'<text x="10" y="30" fill="#e55" font-size="12">render error</text>'
                               f'<text x="10" y="50" fill="#999" font-size="10">{e}</text></svg>')
                        self._bytes(svg.encode(), "image/svg+xml")
                    return
            self._json({"error": "not found"}, 404)

        elif path.startswith("/api/"):
            self._json({"error": "not found"}, 404)

        else:
            self._serve_static(path.lstrip("/"))

    # ---------- POST ----------

    @_logged
    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path
        # The panel only ever sends JSON. Requiring it stops a page on some
        # other website from changing modes or deleting emblems behind your
        # back: browsers won't send a cross-site JSON POST without a CORS
        # check that this server never approves.
        if self.headers.get_content_type() != "application/json":
            self._json({"ok": False, "error": "expected application/json"}, 415)
            return
        body = self._read_json_body()
        # What the debug log shows of the request - never label text.
        self._summary = " " + json.dumps({k: (f"<{len(str(v))} chars>" if k in ("label", "message", "detail") else v)
                                          for k, v in body.items()}) if body else ""

        if path == "/api/debug":
            try:
                debuglog.set_enabled(bool(body.get("enabled")))
            except OSError as e:
                self._json({"ok": False, "error": f"couldn't create the log file: {e}"}, 500)
                return
            if debuglog.enabled():
                log_state_snapshot()
            self._json({"ok": True, **_debug_status()})

        elif path == "/api/debug/open-folder":
            try:
                debuglog.open_log_folder()
            except OSError as e:
                self._json({"ok": False, "error": f"couldn't open the logs folder: {e}"}, 500)
                return
            self._json({"ok": True})

        elif path == "/api/debug/client-error":
            # A script error or failed request in the panel page itself.
            debuglog.warning("UI", f"panel page error: {str(body.get('message'))[:500]}"
                                   f"\n    {str(body.get('detail'))[:2000]}")
            self._json({"ok": True})

        elif path == "/api/mode":
            public_mode = body.get("mode")
            internal = _MODE_TO_INTERNAL.get(public_mode)
            if not internal:
                self._json({"ok": False, "error": "invalid mode"}, 400)
                return
            write_state(internal)
            self._json({"ok": True})

        elif path == "/api/select":
            group, slot = body.get("group"), body.get("slot")
            slot_path = os.path.join(group_dir(group or ""), f"slot_{slot}.bin")
            if not group or slot is None or not os.path.exists(slot_path):
                self._json({"ok": False, "error": "not found"}, 404)
                return
            select_emblem(group, int(slot))
            self._json({"ok": True})

        elif path == "/api/deselect":
            clear_selection()
            self._json({"ok": True})

        elif path == "/api/delete":
            group, slot = body.get("group"), body.get("slot")
            try:
                deleted = isinstance(slot, int) and delete_emblem(group, slot)
                # Show mode serves a copy, so a deleted selection would
                # otherwise keep loading into the editor.
                if deleted and read_selection() == {"group": group, "slot": slot}:
                    clear_selection()
            except OSError as e:
                self._json({"ok": False, "error": f"couldn't delete it: {e}"}, 500)
                return
            if not deleted:
                self._json({"ok": False, "error": "not found"}, 404)
                return
            self._json({"ok": True})

        elif path == "/api/delete-all":
            self._summary += f" ({len(list_emblems())} emblems)"
            try:
                clear_selection()
                delete_all_emblems()
            except OSError as e:
                self._json({"ok": False, "error": f"couldn't delete everything: {e}"}, 500)
                return
            self._json({"ok": True})

        elif path.startswith("/api/emblems/") and path.endswith("/label"):
            bits = path.split("/")
            # /api/emblems/<group>/<slot>/label
            if len(bits) == 6:
                group = urllib.parse.unquote(bits[3])
                slot = bits[4]
                set_emblem_label(group, int(slot), (body.get("label") or "").strip())
                self._json({"ok": True})
                return
            self._json({"ok": False, "error": "bad request"}, 400)

        else:
            self._json({"error": "not found"}, 404)


class _PanelServer(http.server.ThreadingHTTPServer):
    # Same reason as proxy.serve: on Windows a second copy of the toolkit must
    # fail to start, not silently share the port with the first one.
    allow_reuse_address = not hasattr(socket, "SO_EXCLUSIVEADDRUSE")

    def server_bind(self):
        if hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        super().server_bind()


def make_server(host=None, port=None):
    host = host or config.WEB_HOST
    port = port or config.WEB_PORT
    return _PanelServer((host, port), Handler)
