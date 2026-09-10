# Using the BO2 Emblem Toolkit

This assumes you've already finished the one-time [install](INSTALL.md) and have the control panel open in your browser.

## The three modes

| Mode | What it does |
|---|---|
| Off | Normal internet. Nothing is captured or changed. |
| Capture | Saves the emblem of any player whose profile or channel you open. |
| Show | Loads your selected emblem into your own emblem editor. |

Only one mode runs at a time.

## Capturing an emblem

1. Click Capture.
2. On your PS5, open the profile or channel of the player you want to copy from.
3. Their emblem shows up under "Your captured emblems" within a few seconds. Nothing else to do.
4. A player can have more than one saved emblem. If so, each one shows up as its own card.

Click the text under a card to rename it to something you'll recognize later, like "Sam's dragon emblem," instead of the default.

## Deleting emblems

Hover over a card and click the × in its corner to delete that emblem, or click **Delete all** next to Refresh to clear the whole list. Either way it asks first, and deleted emblems can't be recovered. If you delete the emblem that's selected for Show, it gets unselected too.

## Copying an emblem onto your own account

1. Click the emblem card you want. A checkmark shows which one is selected. Only one can be selected at a time.
2. Click Show.
3. Open your own emblem editor on the PS5, not another player's profile. The captured emblem loads there instead of your usual saved emblem.
4. Save it from the editor, the same way you'd save anything you built yourself. It's now permanently on your account.

You can change your selection at any point, in any mode. It takes effect as soon as you're in Show mode and reopen the editor.

## Two things to know before you start

**The editor only checks the server once per game session.** The first time you open your emblem editor, Black Ops II caches whatever it loads and won't ask again after that, even if you pick a different emblem in the control panel. If you need to load a second or third emblem, you have to clear that cache first: either fully restart the game, or switch to Zombies and back to Multiplayer, then open the editor again. Just backing out of the editor and going back in isn't enough.

**It won't work if the emblem uses a shape you haven't unlocked.** Emblems are built from shapes, ranks, and weapon-qualification icons that Black Ops II normally only lets you use once you've earned them. If a captured emblem includes something your own account hasn't unlocked, the game may fail to load it, show it incorrectly, or refuse to save it. There's no way around this from the toolkit's side, since the game itself is enforcing it, not the proxy.

## Sending a debug log

If something isn't working, a debug log usually shows the developer why:

1. In the control panel, under **Troubleshooting**, switch **Debug log** on.
2. Do whatever isn't working again (capturing, Show, saving, ...).
3. Click **Open logs folder** and send the newest `debug-....log` file, for example by attaching it to a GitHub issue.

The log records what the toolkit did, every error it hit, and which servers your PS5 contacted. It never includes your emblems, login details, or other players' IDs (those are replaced with player-1, player-2, ...). Debug logging stays on, even after a restart, until you switch it off. If the toolkit won't start at all, start it once with `--debug` (`python run.py --debug`, or `BO2EmblemToolkit.exe --debug` from a terminal) and the log will show why.

## Questions

**Do I need to keep the terminal window open?**
Yes. Closing it stops the proxy and the control panel. You can minimize it.

**Does this affect signing in or matchmaking?**
No. Only the plain-HTTP emblem-storage requests are touched. Everything else, including all HTTPS traffic like PSN sign-in, passes through unmodified and is never decrypted.

**Can I run this for more than one PS5?**
Yes. The proxy setting is per-console, so any number of PS5s on your network can point at the same running toolkit.

**I switched back to Off but I still see the captured emblem somewhere. Why?**
That's the PS5's own local cache still showing what it last loaded, not something the toolkit is still doing. Switching modes only changes what the proxy would serve on the next request, it doesn't force the console to ask again.
