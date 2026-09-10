"""The MITM proxy the PS5 points its network proxy setting at.

HTTPS (CONNECT) traffic is tunneled raw and never decrypted, so PSN sign-in
and normal console functionality keep working untouched. Plain HTTP emblem-slot
downloads (GET) from Demonware's storage hosts are the only thing inspected:
in CAPTURE mode the real response is saved, in Show mode it's replaced with
whichever emblem is currently selected (see broadcast.py). Uploads - the
emblem editor saving to your account - always pass straight through.

With the debug log on (see debuglog.py), every connection - and everything
unusual about it - is recorded too.
"""
import os
import re
import socket
import threading
import time

from . import config, debuglog
from .state import read_state
from .storage import get_or_create_capture_group, group_dir
from .broadcast import read_selected_data, read_selection

# matches ".../u51b08745d269.slot_504?..." -> userhash, slot number
PATH_RE = re.compile(r"/(u[0-9a-fA-F]+)\.slot_(\d+)")
# 32 layers x 44 bytes - see shapes/render.py for the format
EMBLEM_BYTES = 1408
# An HTTP status line at the start of a reply relayed back to the console
_STATUS_RE = re.compile(rb"HTTP/1\.[01] \d{3}[^\r\n]*")
_MODE_NAMES = {"PASSTHROUGH": "off", "CAPTURE": "capture", "INJECT": "show"}

_noted = set()


def is_emblem_request(host, path):
    """An emblem-slot request on any Demonware host. Matching on what the
    request is, rather than one hardcoded hostname, keeps a regional host or a
    rename in a game update from silently turning the tool into a no-op."""
    return host.lower().endswith(config.EMBLEM_HOST_SUFFIX) and PATH_RE.search(path) is not None


def log(msg, to_debug_log=True):
    """Print to the console window - and, with the debug log on, record it
    there as well (callers with a more detailed debug entry pass False)."""
    print(f"{time.strftime('%H:%M:%S')} {msg}", flush=True)
    if to_debug_log:
        debuglog.info("CONSOLE", msg.strip())


def note_once(key, msg):
    """log() msg the first time `key` comes up, so repeat traffic to the same
    host doesn't flood the console."""
    if key not in _noted:
        _noted.add(key)
        log(msg)


class Traffic:
    """What went through one relayed connection: bytes each way, the first
    HTTP status lines the server sent back (readable for plain HTTP - e.g. the
    reply to a save - while HTTPS tunnels only ever show byte counts), and the
    error that cut it short, if any. on_reply(status_line) fires once, as soon
    as the first final (non-1xx) reply arrives."""

    def __init__(self, on_reply=None):
        self.sent = self.received = 0
        self.statuses = []
        self.error = None
        self.done = False
        self._on_reply = on_reply

    def add(self, from_upstream, data):
        if not from_upstream:
            self.sent += len(data)
            return
        if self.received < 16384 and len(self.statuses) < 3:
            for raw in _STATUS_RE.findall(data):
                line = raw.decode("latin1")
                self.statuses.append(line)
                if self._on_reply and not line.split(" ")[1].startswith("1"):  # skip "100 Continue"
                    self._on_reply(line)
                    self._on_reply = None
        self.received += len(data)


def pipe(src, dst, traffic=None, from_upstream=False):
    try:
        while True:
            data = src.recv(65536)
            if not data:
                break
            if traffic is not None:
                traffic.add(from_upstream, data)
            dst.sendall(data)
    except OSError as e:
        # Once one direction has finished, the shutdown below makes the other
        # one fail too - that's ordinary teardown, not worth reporting.
        if traffic is not None and not traffic.done:
            traffic.error = e
    finally:
        if traffic is not None:
            traffic.done = True
        for s in (src, dst):
            try:
                s.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass


def relay(client, upstream, label, traffic=None):
    """Pump bytes both ways until either side closes. With a Traffic, count
    them and record a one-line summary in the debug log."""
    started = time.perf_counter()
    t1 = threading.Thread(target=pipe, args=(upstream, client, traffic, True), daemon=True)
    t2 = threading.Thread(target=pipe, args=(client, upstream, traffic, False), daemon=True)
    t1.start(); t2.start()
    t1.join(); t2.join()
    if traffic is not None:
        replies = f", replies: {'; '.join(traffic.statuses)}" if traffic.statuses else ""
        cut = f", cut short by: {traffic.error}" if traffic.error else ""
        debuglog.debug("PROXY", f"{label}: closed after {time.perf_counter() - started:.1f}s, "
                                f"sent {traffic.sent} B, received {traffic.received} B{replies}{cut}")
    return traffic


def tunnel(client, host, port, first_bytes, label, traffic=None):
    """Send first_bytes upstream, then relay raw bytes both ways until either
    side closes - a plain pass-through with no HTTP parsing at all."""
    upstream = socket.create_connection((host, port))
    upstream.sendall(first_bytes)
    if traffic is None and debuglog.enabled():
        traffic = Traffic()
    if traffic is not None:
        traffic.sent += len(first_bytes)
    return relay(client, upstream, label, traffic)


def recv_full_response(sock):
    data = b""
    while b"\r\n\r\n" not in data:
        chunk = sock.recv(4096)
        if not chunk:
            break
        data += chunk
    header_end = data.find(b"\r\n\r\n")
    if header_end == -1:
        return data, b""
    header_end += 4
    headers = data[:header_end]
    body = data[header_end:]
    cl = None
    for line in headers.split(b"\r\n"):
        if line.lower().startswith(b"content-length:"):
            cl = int(line.split(b":", 1)[1].strip())
            break
    if cl is not None:
        while len(body) < cl:
            chunk = sock.recv(4096)
            if not chunk:
                break
            body += chunk
    return headers, body


def fetch_real(req, host, port):
    upstream = socket.create_connection((host, port))
    upstream.sendall(req)
    headers, body = recv_full_response(upstream)
    upstream.close()
    return headers, body


def _req_header(req, name):
    """Return the value of an HTTP request header (case-insensitive) or None."""
    needle = (name.lower() + ":").encode()
    for line in req.split(b"\r\n")[1:]:
        if not line:
            break
        if line.lower().startswith(needle):
            return line.split(b":", 1)[1].strip().decode("latin1", "replace")
    return None


def _check_download(what, mode, headers, body, seconds):
    """Record an emblem download's outcome in the debug log, and flag
    everything about it that would leave a capture - or the console's copy -
    wrong or incomplete."""
    if not debuglog.enabled():
        return
    if not headers:
        debuglog.error("EMBLEM", f"GET {what}: the server closed the connection without answering ({seconds:.1f}s)")
        return
    status = headers.split(b"\r\n", 1)[0].decode("latin1", "replace")
    parts = status.split(" ")
    code = parts[1] if len(parts) > 1 else "?"
    length = _req_header(headers, "Content-Length")
    encoding = _req_header(headers, "Content-Encoding")
    chunked = "chunked" in (_req_header(headers, "Transfer-Encoding") or "").lower()
    debuglog.info("EMBLEM", f"GET {what} [{_MODE_NAMES.get(mode, mode)}] -> {status}, "
                            f"{len(body)} bytes in {seconds * 1000:.0f} ms")

    problems = []
    if code != "200":
        problems.append(f"status {code} instead of 200"
                        + (" - saved as a capture anyway, so it will show up blank" if mode == "CAPTURE" else ""))
    if chunked:
        problems.append("chunked transfer encoding, which this proxy doesn't decode - the emblem arrives cut off")
    if encoding:
        problems.append(f"compressed ({encoding}) - a capture of this can't be read")
    incomplete = False
    if code in ("204", "304") and length not in (None, "0"):
        problems.append(f"Content-Length {length} on a reply that never has a body - "
                        f"the proxy waited {seconds:.1f}s for bytes that don't come")
    elif length is not None and length.isdigit() and int(length) != len(body):
        incomplete = True
        problems.append(f"incomplete: got {len(body)} of {length} bytes (the server closed early or went quiet)")
    elif length is None and not chunked and code == "200":
        problems.append("no Content-Length - anything after the first packet may be missing")
    if code == "200" and not chunked and not incomplete and len(body) != EMBLEM_BYTES:
        problems.append(f"{len(body)} bytes instead of the usual {EMBLEM_BYTES} - the emblem format may have changed")
    if seconds > 5:
        problems.append(f"slow: {seconds:.1f}s")
    for p in problems:
        debuglog.warning("EMBLEM", f"GET {what}: {p}")


def _report_save(slot_num, status):
    """Tell the user straight away whether the server took their save."""
    if status.split(" ")[1].startswith("2"):
        log(f"  Save: the server accepted it ({status})")
    else:
        log(f"  Save: the server REJECTED it ({status}) - your emblem was not saved")
        debuglog.error("EMBLEM", f"save for slot_{slot_num} rejected: {status}")


def handle_target_request(client, req, host, port, path):
    mode = read_state()
    m = PATH_RE.search(path)
    slot_num = int(m.group(2)) if m else None
    userhash = m.group(1) if m else None
    method = req.split(b" ", 1)[0].decode("latin1")
    what = f"slot_{slot_num} of {userhash}"  # the debug log shows the ID as player-N

    # Only downloads are ever captured or replaced. Anything else - notably the
    # PUT your emblem editor sends when you save - has to reach the real server
    # intact, body and all; answering it here makes the save look successful
    # while it never actually lands on your account.
    if method != "GET":
        if slot_num is not None:
            log(f"  Save: passed your editor's save for slot_{slot_num} through to the server")
        debuglog.info("EMBLEM", f"{method} {what} [{_MODE_NAMES.get(mode, mode)}] -> forwarding to {host} "
                                f"(Content-Length {_req_header(req, 'Content-Length') or 'missing'})")
        traffic = tunnel(client, host, port, req, f"{method} {what}",
                         Traffic(on_reply=lambda status: _report_save(slot_num, status)))
        if not any(not s.split(" ")[1].startswith("1") for s in traffic.statuses):
            log(f"  Save: no reply from the server for slot_{slot_num} - it may not have been saved", to_debug_log=False)
            debuglog.warning("EMBLEM", f"{method} {what}: the connection closed without an HTTP reply"
                                       + (f" ({traffic.error})" if traffic.error else ""))
        return

    if mode == "INJECT" and slot_num is not None:
        selected = read_selected_data()
        if selected is not None:
            client.sendall(selected)
            sel = read_selection() or {}
            debuglog.info("EMBLEM", f"GET {what} [show] -> answered with selected emblem "
                                    f"{sel.get('group')}:{sel.get('slot')} ({len(selected)} bytes)")
            # A conditional/cache-check request from the console is the main
            # reason Show mode can silently appear to do nothing - your PS5
            # already has a cached copy of one of your slots and may not ask
            # again right away. Nothing to fix here, just worth noting.
            if _req_header(req, "If-None-Match") or _req_header(req, "If-Modified-Since") or _req_header(req, "Range"):
                log(f"  Show: sent selected emblem for slot_{slot_num}, but the console sent a "
                    "cache-check request - it may keep using its cached copy instead")
            else:
                log(f"  Show: sent selected emblem for slot_{slot_num} ({len(selected)} bytes)")
            return
        log(f"  Show mode is on but no emblem is selected - passing real data through")

    started = time.perf_counter()
    headers, body = fetch_real(req, host, port)
    _check_download(what, mode, headers, body, time.perf_counter() - started)

    if mode == "CAPTURE" and slot_num is not None:
        try:
            group = get_or_create_capture_group(userhash)
            with open(os.path.join(group_dir(group), f"slot_{slot_num}.bin"), "wb") as f:
                f.write(headers + body)
            log(f"  Captured: group {group} slot_{slot_num} ({len(body)} bytes)")
        except OSError as e:
            # Still pass the reply on below - a full disk shouldn't break the console.
            log(f"  error: couldn't save the capture of slot_{slot_num}: {e}", to_debug_log=False)
            debuglog.error("STORAGE", f"couldn't save the capture of {what}", exc=True)

    client.sendall(headers + body)


def handle(client):
    try:
        peer = client.getpeername()[0]
    except OSError:
        peer = "?"
    target = "?"
    try:
        req = b""
        while b"\r\n\r\n" not in req:
            chunk = client.recv(4096)
            if not chunk:
                client.close()
                return
            req += chunk
        line = req.split(b"\r\n", 1)[0].decode("latin1")
        parts = line.split()
        if len(parts) < 2:
            debuglog.warning("PROXY", f"{peer}: malformed request line {line[:80]!r}")
            client.close()
            return
        method = parts[0].upper()

        if method == "CONNECT":
            host, _, port = parts[1].partition(":")
            target = f"HTTPS {host}:{port or 443}"
            debuglog.debug("PROXY", f"{peer} {target}")
            if host.lower().endswith(config.EMBLEM_HOST_SUFFIX):
                note_once(("https", host), f"  note: HTTPS traffic to {host} - encrypted, so it's tunneled untouched")
            port = int(port or 443)
            upstream = socket.create_connection((host, port))
            client.sendall(b"HTTP/1.1 200 Connection established\r\n\r\n")
            relay(client, upstream, f"{peer} {target}", Traffic() if debuglog.enabled() else None)
        else:
            url = parts[1]
            rest = url.split("://", 1)[1] if "://" in url else url
            host_port, _, path = rest.partition("/")
            host, _, port = host_port.partition(":")
            port = int(port or 80)
            path = "/" + path
            target = f"{method} {host}{path.split('?', 1)[0]}"
            debuglog.debug("PROXY", f"{peer} {target}")

            rest_of_req = req.split(b"\r\n", 1)[1]
            new_line = f"{method} {path} HTTP/1.1\r\n".encode("latin1")
            req_rewritten = new_line + rest_of_req

            if is_emblem_request(host, path):
                if host.lower() != config.USUAL_EMBLEM_HOST:
                    note_once(("emblem", host), f"  note: emblems are coming from {host} (not the usual "
                              f"{config.USUAL_EMBLEM_HOST}) - handling them anyway")
                handle_target_request(client, req_rewritten, host, port, path)
            else:
                if host.lower().endswith(config.EMBLEM_HOST_SUFFIX):
                    note_once(("http", host), f"  note: HTTP request to {host}{path.split('?', 1)[0]} "
                              "(not an emblem slot) - passed through untouched")
                tunnel(client, host, port, req_rewritten, f"{peer} {target}")
    except socket.gaierror as e:
        log(f"  error: {target}: couldn't look up that address ({e})", to_debug_log=False)
        debuglog.error("PROXY", f"{peer} {target}: DNS lookup failed ({e})")
    except OSError as e:
        log(f"  error: {target}: {e}", to_debug_log=False)
        debuglog.error("PROXY", f"{peer} {target}: network error: {e}")
    except Exception as e:
        log(f"  error: {target}: {e}", to_debug_log=False)
        debuglog.error("PROXY", f"{peer} {target}: unexpected error", exc=True)
    finally:
        client.close()


def serve(host=None, port=None):
    """Run the proxy loop. Blocks forever - call from a dedicated thread."""
    from .state import write_state
    if not os.path.exists(config.STATE_FILE):
        write_state("PASSTHROUGH")
    host = host or config.PROXY_HOST
    port = port or config.PROXY_PORT
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # On Windows, SO_REUSEADDR would let a second copy of the toolkit silently
    # share the port - then nobody knows which copy answers the PS5. Exclusive
    # use turns that into a clear "already in use" error instead.
    if hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
    else:
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        srv.bind((host, port))
    except OSError as e:
        log(f"ERROR: couldn't start the proxy on port {port}: {e}", to_debug_log=False)
        log("       Is another copy of the toolkit (or another program) already using that port?", to_debug_log=False)
        debuglog.error("PROXY", f"couldn't listen on {host}:{port} - the PS5 can't connect", exc=True)
        return
    srv.listen(200)
    log(f"Proxy listening on {host}:{port}  mode={read_state()}")
    while True:
        client, _ = srv.accept()
        threading.Thread(target=handle, args=(client,), daemon=True).start()
