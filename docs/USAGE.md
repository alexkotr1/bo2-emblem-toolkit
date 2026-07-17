# Using the BO2 Emblem Toolkit

This assumes you've already finished the one-time [install](INSTALL.md) and
have the control panel open in your browser.

## The three modes

At the top of the control panel are three big buttons:

| Mode | What it does |
|---|---|
| **⏻ Off** | Normal internet. Nothing is captured or changed. Use this when you're not actively capturing or showing an emblem. |
| **📸 Capture** | Saves the emblem of any player whose channel you open on the PS5. |
| **📤 Show** | Displays an emblem you've chosen to every player you look at. |

Only one mode is active at a time.

## Capturing an emblem

1. Click **Capture**.
2. On your PS5, open the player channel / combat record of whoever you want
   to capture (however your game mode normally lets you view another
   player's profile).
3. Their emblem(s) appear automatically under **Your captured emblems**
   within a few seconds — no further action needed.
4. A player can have multiple saved emblems; each one shows up as its own
   card in the list.

Click the name under any card to give it a memorable label (e.g. "Sam's
dragon emblem") instead of the default.

## Showing an emblem

1. Click an emblem card in **Your captured emblems** to select it — a green
   checkmark shows which one is currently selected. Only one can be selected
   at a time; clicking a different one changes your selection.
2. Click **Show**.
3. Look at any player on your PS5 — they'll see your selected emblem instead
   of their real one.

You can change your selection at any time, in any mode — it takes effect
immediately once you're in Show mode.

### Why "Show" sometimes needs a moment

The PS5 caches emblem data locally. If you just captured a player, their
emblem is now cached on your console — looking at them again might not
show anything different right away, since the console may not re-request the
data. Looking at a *different* player (or the same one after a while) works
reliably. This is a PS5-side caching quirk, not a toolkit bug. The terminal
window the toolkit runs in will print a note when it detects this happening.

## FAQ

**Do I need to keep the terminal window open?**
Yes — closing it stops the proxy and the control panel both. You can minimize
it.

**Will this affect my PSN sign-in or matchmaking?**
No. Only Black Ops II's plain-HTTP emblem-storage requests are inspected;
everything else (including all HTTPS traffic, like PSN authentication) is
tunneled through completely unmodified and undecrypted.

**Can I use this on multiple PS5s / accounts?**
Yes — the proxy setting is per-console, so you can point any number of PS5s
on your network at the same running toolkit.

**I switched to Off but I'm still seeing a captured emblem — why?**
Likely PS5-side caching (see above) — the last thing your console fetched is
still what it's displaying locally. Switching modes here only changes what
the proxy *would* serve on the next request; it doesn't force the console to
re-fetch anything.
