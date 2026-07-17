"""Best-effort LAN IP detection, so the web UI can tell the user exactly
what to type into their PS5's proxy settings without opening a terminal.
"""
import socket


def get_lan_ip():
    """Return this machine's LAN IP as seen by outbound traffic, or None."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Doesn't actually send anything (UDP, no handshake) - just asks the
        # OS routing table which local interface/IP would be used to reach
        # an external address.
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except OSError:
        return None
    finally:
        s.close()
