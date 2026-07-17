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

## Copying an emblem onto your own account

1. Click the emblem card you want. A checkmark shows which one is selected. Only one can be selected at a time.
2. Click Show.
3. Open your own emblem editor on the PS5, not another player's profile. The captured emblem loads there instead of your usual saved emblem.
4. Save it from the editor, the same way you'd save anything you built yourself. It's now permanently on your account.

You can change your selection at any point, in any mode. It takes effect as soon as you're in Show mode and reopen the editor.

### Why it sometimes takes a second try

The PS5 caches emblem data locally. If your console already has an emblem cached, it might not ask the server again right away, and Show mode has nothing to intercept until it does. Closing and reopening the editor, or waiting a bit, usually clears this up. The terminal window running the toolkit will print a note when it notices this happening.

## Questions

**Do I need to keep the terminal window open?**
Yes. Closing it stops the proxy and the control panel. You can minimize it.

**Does this affect signing in or matchmaking?**
No. Only the plain-HTTP emblem-storage requests are touched. Everything else, including all HTTPS traffic like PSN sign-in, passes through unmodified and is never decrypted.

**Can I run this for more than one PS5?**
Yes. The proxy setting is per-console, so any number of PS5s on your network can point at the same running toolkit.

**I switched back to Off but I still see the captured emblem somewhere. Why?**
That's the PS5's own local cache still showing what it last loaded, not something the toolkit is still doing. Switching modes only changes what the proxy would serve on the next request, it doesn't force the console to ask again.
