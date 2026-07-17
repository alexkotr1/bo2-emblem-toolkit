# Installing the BO2 Emblem Toolkit

This is a one-time setup. Once it's done, day-to-day use is just
[docs/USAGE.md](USAGE.md).

## Windows: just download the exe

If you're on Windows and don't want to deal with Python at all, grab
`BO2EmblemToolkit.exe` from this project's
[Releases page](https://github.com/alexkotr1/bo2-emblem-toolkit/releases).
It's a single file with everything already inside it. Put it in its own
folder (it saves your captured emblems next to itself), double-click it, and
skip ahead to [Point your PS5 at it](#point-your-ps5-at-it) below.

Windows may warn you that the file is from an unrecognized publisher, since
it isn't signed with a paid code-signing certificate. Click "More info" then
"Run anyway." If you'd rather verify the code yourself first, or you're on
macOS/Linux, use the Python setup instead.

## Running it from source instead (any OS)

### 1. Install Python

You need Python 3.9 or newer.

On Windows, download it from [python.org/downloads](https://www.python.org/downloads/). During installation, check the box that says "Add python.exe to PATH." It's easy to miss, and nothing here will run without it.

On macOS, Python 3 is often already there. If not, get it from python.org or run `brew install python3`.

On Linux, install it through your distro's package manager, for example `sudo apt install python3 python3-pip`.

To check it worked, open a terminal (Command Prompt on Windows) and run:

```
python --version
```

You should see something like `Python 3.11.4`. If you get an error, Python
isn't installed correctly or isn't on your PATH yet.

### 2. Get the toolkit

Download or clone this repository, then open a terminal **in that folder**.

### 3. Install the one dependency

```
pip install -r requirements.txt
```

This installs [Pillow](https://pypi.org/project/Pillow/), used to render
emblem thumbnails. Nothing else is required.

### 4. Run it

**Windows**: double-click `start.bat`.

**Any platform**:

```
python run.py
```

A terminal window will show something like:

```
============================================================
 BO2 Emblem Toolkit
============================================================
 Control panel : http://localhost:8090
 PS5 proxy setting -> 192.168.1.42 : 8080
============================================================
```

Your browser should open to the control panel automatically. If it doesn't,
open `http://localhost:8090` yourself.

Keep this terminal window open while you use the toolkit. Closing it stops everything. To stop on purpose, press `Ctrl+C` in that window, or just close it.

## Point your PS5 at it

Your PS5 and this PC need to be on the same network, either the same Wi-Fi/router, or this PC's own mobile hotspot with the PS5 connected to it.

On the PS5:

1. Settings → Network → Settings → Set Up Internet Connection
2. Choose your connection (Wi-Fi or LAN), then Advanced Settings
3. Set Proxy Server to Use
4. Enter the IP address and port shown in the toolkit's terminal window and at the top of the control panel, for example `192.168.1.42` and `8080`
5. Save, then test the internet connection from the PS5's network settings screen

If the PS5 says it has no internet connection after this, check the troubleshooting section below before assuming something's broken.

## Troubleshooting

**PS5 says "no internet connection" after setting the proxy**

- Double check the PS5 and this PC really are on the same network. If the PS5
  is connected to this PC's mobile hotspot, use the hotspot's IP address (the
  toolkit auto-detects and displays whichever one is right), not your main
  router's IP.
- Windows Firewall may be blocking the connection. Allow inbound TCP traffic
  on port 8080 for Python, or add a rule manually:
  ```
  New-NetFirewallRule -DisplayName "BO2 Emblem Toolkit" -Direction Inbound -Protocol TCP -LocalPort 8080 -Action Allow -Profile Private
  ```
  (run this in an elevated PowerShell window).
- If you use an ad-blocking DNS service, it may be blocking PlayStation's own
  telemetry domains, unrelated to this tool but easy to mistake for it.
  Switching to a normal DNS resolver (e.g. 1.1.1.1) resolves this.

**The control panel doesn't show a LAN IP, or shows the wrong one**

Multiple network adapters (VPNs, virtual adapters, hotspot adapters) can
confuse auto-detection. Find the correct IP yourself:

- Windows: `ipconfig` in a terminal, look for the adapter connected to the
  same network as your PS5.
- macOS/Linux: `ifconfig` or `ip addr`.

**"python is not recognized" / "command not found"**

Python isn't on your PATH. Reinstall Python and make sure to check "Add to
PATH" during setup (Windows), or use `python3` instead of `python`
(macOS/Linux).
