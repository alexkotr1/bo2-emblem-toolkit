#!/usr/bin/env python3
"""Start the BO2 Emblem Toolkit.

This is the only thing you ever need to run. It starts the network proxy
and the web control panel together, then opens the panel in your browser.
See README.md for what this does and docs/INSTALL.md for PS5 setup.
"""
import threading
import time
import webbrowser

from emblemtool import config
from emblemtool.proxy import serve as serve_proxy
from emblemtool.web.server import make_server
from emblemtool.web.netinfo import get_lan_ip


def main():
    proxy_thread = threading.Thread(target=serve_proxy, daemon=True)
    proxy_thread.start()

    lan_ip = get_lan_ip()
    print("=" * 60)
    print(" BO2 Emblem Toolkit")
    print("=" * 60)
    print(f" Control panel : http://localhost:{config.WEB_PORT}")
    if lan_ip:
        print(f" PS5 proxy setting -> {lan_ip} : {config.PROXY_PORT}")
    else:
        print(f" PS5 proxy setting -> <this PC's LAN IP> : {config.PROXY_PORT}")
        print("   (couldn't auto-detect your LAN IP - see docs/INSTALL.md)")
    print("=" * 60)
    print(" Press Ctrl+C to stop.")
    print()

    time.sleep(0.3)
    try:
        webbrowser.open(f"http://localhost:{config.WEB_PORT}")
    except Exception:
        pass

    server = make_server()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping...")


if __name__ == "__main__":
    main()
