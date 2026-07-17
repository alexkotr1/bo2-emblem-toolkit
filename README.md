# BO2 Emblem Toolkit

Capture another player's Call of Duty: Black Ops II emblem while playing on
PS5, and show your favorite one to whoever you look at — all from a simple
web control panel. No command line required.

> Built for personal use, on your own PS5 and your own home network.

## What it does

Black Ops II fetches emblem data over plain HTTP from Treyarch's old
Demonware servers. This toolkit sits between your PS5 and the internet as a
local network proxy:

- **Capture mode** — saves the emblem of any player whose channel you open.
- **Show mode** — replaces your emblem data with one you've captured (or your
  own), so it displays for other players you look at.
- Everything else (PSN sign-in, matchmaking, friends list, all normal
  traffic) passes through completely untouched — HTTPS traffic is tunneled
  raw and is never decrypted.

## Features

- 🖥️ **One web control panel** — start it, open your browser, click buttons.
  No terminal commands to memorize.
- 📸 **Capture** any player's saved emblems just by viewing their channel.
- 📤 **Show** one selected emblem to everyone you look at, regardless of
  which emblem "slot" their console happens to request (see
  [docs/USAGE.md](docs/USAGE.md) for why this matters).
- ☑️ **Simple, single-selection picker** — a flat list of every emblem you've
  captured, click one to select it. No technical concepts to learn.
- 🎨 **Pixel-accurate rendering** — thumbnails are real composited renders of
  the actual emblem shapes, colors, and layout, not placeholders. The
  renderer was calibrated directly against the live game engine.
- 🏷️ Rename captured emblems with your own labels so they're easy to find
  later.

## Quick start

1. [Install](docs/INSTALL.md) — one-time setup (Python + pointing your PS5 at
   this app).
2. [Usage](docs/USAGE.md) — how to capture and show emblems day to day.

```
pip install -r requirements.txt
python run.py
```

That's it — your browser opens to the control panel automatically.

## Requirements

- Windows, macOS, or Linux with Python 3.9+
- A PS5 and PC on the same local network (same Wi-Fi/router, or the PC's own
  mobile hotspot)
- [Pillow](https://pypi.org/project/Pillow/) (installed via `requirements.txt`)

## How it's built

The project is a small, dependency-light Python package:

```
emblemtool/
  config.py         constants (ports, paths)
  state.py          current mode (off / capture / show)
  storage.py        captured emblems on disk + user-facing labels
  broadcast.py       which single emblem is currently selected to show
  proxy.py          the MITM proxy server itself
  shapes/           calibrated shape-ID data + the emblem renderer
  web/              the control panel: a small JSON API + static frontend
run.py              the only entry point - starts everything
```

See the module docstrings for details on the emblem binary format and how it
was reverse-engineered and validated against the actual game.

## Contributing

Issues and pull requests are welcome. The codebase is intentionally small and
dependency-light — please keep it that way.

## License

[MIT](LICENSE) — do whatever you like with this, including modifying and
redistributing it, as long as you keep the copyright notice and credit
**alexkotr1** as the original author.

## Disclaimer

This tool only touches Black Ops II's own plain-HTTP emblem endpoint; all
other traffic (including PSN authentication) passes through unmodified and
undecrypted. Emblem data is cosmetic, non-sensitive information that's
already visible to anyone you play with or against in-game. Use it on your
own account and network. The author is not affiliated with Activision,
Treyarch, or Sony.
