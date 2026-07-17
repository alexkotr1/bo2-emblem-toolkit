"""The MITM proxy the PS5 points its network proxy setting at.

HTTPS (CONNECT) traffic is tunneled raw and never decrypted, so PSN sign-in
and normal console functionality keep working untouched. Plain HTTP requests
to the Demonware emblem-storage endpoint are the only thing inspected: in
CAPTURE mode the real response is saved, in Show mode it's replaced with
whichever emblem is currently selected (see broadcast.py).
"""
import os
import re
import socket
import threading
import time

from . import config
from .state import read_state
from .storage import get_or_create_capture_group, group_dir
from .broadcast import read_selected_data

# matches ".../u51b08745d269.slot_504?..." -> userhash, slot number
PATH_RE = re.compile(r"/(u[0-9a-fA-F]+)\.slot_(\d+)")


def log(msg):
    print(f"{time.strftime('%H:%M:%S')} {msg}", flush=True)


def pipe(src, dst):
    try:
        while True:
            data = src.recv(65536)
            if not data:
                break
            dst.sendall(data)
    except OSError:
        pass
    finally:
        for s in (src, dst):
            try:
                s.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass


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


def handle_target_request(client, req, host, port, path):
    mode = read_state()
    m = PATH_RE.search(path)
    slot_num = int(m.group(2)) if m else None
    userhash = m.group(1) if m else None

    if mode == "INJECT" and slot_num is not None:
        selected = read_selected_data()
        if selected is not None:
            client.sendall(selected)
            # A conditional/cache-check request from the console is the main
            # reason "Show" can silently do nothing for a player you just
            # looked at - their console already cached the real response and
            # may not even ask again. Nothing to fix here, just worth noting.
            if _req_header(req, "If-None-Match") or _req_header(req, "If-Modified-Since") or _req_header(req, "Range"):
                log(f"  Show: sent selected emblem for slot_{slot_num}, but the console sent a "
                    "cache-check request - it may keep using its cached copy instead")
            else:
                log(f"  Show: sent selected emblem for slot_{slot_num} ({len(selected)} bytes)")
            return
        log(f"  Show mode is on but no emblem is selected - passing real data through")

    headers, body = fetch_real(req, host, port)

    if mode == "CAPTURE" and slot_num is not None:
        group = get_or_create_capture_group(userhash)
        with open(os.path.join(group_dir(group), f"slot_{slot_num}.bin"), "wb") as f:
            f.write(headers + body)
        log(f"  Captured: group {group} slot_{slot_num} ({len(body)} bytes)")

    client.sendall(headers + body)


def handle(client):
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
            client.close()
            return
        method = parts[0].upper()

        if method == "CONNECT":
            host, _, port = parts[1].partition(":")
            port = int(port or 443)
            upstream = socket.create_connection((host, port))
            client.sendall(b"HTTP/1.1 200 Connection established\r\n\r\n")
            t1 = threading.Thread(target=pipe, args=(upstream, client), daemon=True)
            t2 = threading.Thread(target=pipe, args=(client, upstream), daemon=True)
            t1.start(); t2.start()
            t1.join(); t2.join()
        else:
            url = parts[1]
            rest = url.split("://", 1)[1] if "://" in url else url
            host_port, _, path = rest.partition("/")
            host, _, port = host_port.partition(":")
            port = int(port or 80)
            path = "/" + path

            rest_of_req = req.split(b"\r\n", 1)[1]
            new_line = f"{method} {path} HTTP/1.1\r\n".encode("latin1")
            req_rewritten = new_line + rest_of_req

            if config.TARGET_HOST_SUBSTR in host:
                handle_target_request(client, req_rewritten, host, port, path)
            else:
                upstream = socket.create_connection((host, port))
                upstream.sendall(req_rewritten)
                t1 = threading.Thread(target=pipe, args=(upstream, client), daemon=True)
                t2 = threading.Thread(target=pipe, args=(client, upstream), daemon=True)
                t1.start(); t2.start()
                t1.join(); t2.join()
    except Exception as e:
        log(f"  error: {e}")
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
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((host, port))
    srv.listen(200)
    log(f"Proxy listening on {host}:{port}  mode={read_state()}")
    while True:
        client, _ = srv.accept()
        threading.Thread(target=handle, args=(client,), daemon=True).start()
