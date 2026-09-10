# Changelog

## 1.1.0 - 2026-09-10

### Fixed

- **Saving a copied emblem now actually saves it to your account.** In Show mode the toolkit used to answer your emblem editor's save itself, so the game said it was saved but the server never received it and your account kept its old emblem. Saves now always go through to the server, and the console tells you whether the server accepted them.
- **Keeps working if the emblem server changes.** Emblem requests are now recognized on any Demonware server instead of one hard-coded address, so a game update or a different region using another server doesn't silently break the tool. If a different server shows up, the console says which one.
- **"Delete all" no longer fails on Windows** when a file is briefly in use (by antivirus, search indexing, or the control panel itself). It retries for a moment, and shows an error instead of silently doing nothing if it still can't.
- **Running the toolkit twice at once is now caught.** On Windows a second copy used to start without complaint and share the same ports, so the PS5 would talk to one copy or the other at random. The second copy now says the port is already in use.
- Other plain-HTTP requests to Demonware servers now pass through untouched.
- The browser only opens once the control panel has actually started, and a capture that fails to save (for example on a full disk) no longer breaks the PS5's request.

### Added

- **Delete emblems.** Hover over a card and click the × in its corner to delete it, or use **Delete all** next to Refresh. Both ask first.
- **Debug log** for bug reports, in the new **Troubleshooting** section of the control panel. When it's on, everything the toolkit does and every error is written to a file in the `logs` folder; **Open logs folder** takes you straight to it. It never contains your emblems, login details, or other players' IDs. You can also start with `--debug` to log a toolkit that won't start. See [docs/USAGE.md](docs/USAGE.md#sending-a-debug-log).

### Security

- The control panel now only accepts requests from its own page, so other websites you visit can't change the mode or delete your emblems in the background.

## 1.0.0 - 2026-07-17

- First release: capture another player's emblem from your PS5 and load it into your own emblem editor.
