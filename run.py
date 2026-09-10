#!/usr/bin/env python3
"""Start the BO2 Emblem Toolkit.

This is the only thing you ever need to run. It starts the network proxy
and the web control panel together, then opens the panel in your browser.
See README.md for what this does and docs/INSTALL.md for PS5 setup.

`python run.py --debug` turns the debug log on from the very start (see
emblemtool/debuglog.py) - handy when the problem is that it won't start.
"""
import sys
import threading
import time
import webbrowser

from emblemtool import config, debuglog
from emblemtool.proxy import serve as serve_proxy
from emblemtool.web.server import make_server, log_state_snapshot
from emblemtool.web.netinfo import get_lan_ip


def main():
    if "--debug" in sys.argv or debuglog.remembered():
        try:
            debuglog.set_enabled(True)
        except OSError as e:
            print(f"Couldn't start the debug log: {e}")
    debuglog.install_crash_hooks()

    # Bind the panel first: if it can't start there's no point opening a
    # browser tab to it (or, worse, to whatever else is using the port).
    try:
        server = make_server()
    except OSError as e:
        print(f"ERROR: couldn't start the control panel on port {config.WEB_PORT}: {e}")
        print("       Is the toolkit already running in another window?")
        debuglog.error("PANEL", f"couldn't listen on port {config.WEB_PORT}", exc=True)
        if getattr(sys, "frozen", False):
            input("Press Enter to close this window...")
        return

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
    if debuglog.enabled():
        print(f" Debug log     : {debuglog.log_file()}")
    print("=" * 60)
    print(" Press Ctrl+C to stop.")
    print()
    log_state_snapshot()

    time.sleep(0.3)
    try:
        webbrowser.open(f"http://localhost:{config.WEB_PORT}")
    except Exception:
        pass

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping...")
        debuglog.info("START", "stopped with Ctrl+C")


if __name__ == "__main__":
    main()
