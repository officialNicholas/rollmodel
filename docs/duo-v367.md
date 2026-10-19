# v367: no frozen "New canvas" before a match, and ready for iPhone Duo

![Top: on iPhone Duo open, Settings without the Screen row, the season's canvases in one row, and the results with all three buttons. Bottom: the bar under "New canvas", the pause card after folding mid-match, and the match controls and vote page kept clear of a camera along one side](duo-v367.jpg)

## What was wrong

- **"New canvas" looked hung.** Before a match the game builds the canvas, then prepares every shader the match can
  need. The first match after opening the game prepared them all at once, some 115 of them, and the screen couldn't draw
  while it did. A new player's first match is always the lesson, so it was the first thing a new player saw (here on the
  iPhone Duo simulator). Same canvas, a canvas vote and online matches did a smaller version of the same.
- **Xcode's "AVAudioSession Hang Risk" warnings.** The app turned its sound settings on from the main thread, which can
  hold up the screen while the phone's audio system is busy.
- **iPhone Duo.** Apple's guidance ("Preparing your app for iPhone Duo" and the "Prepare" page) asks apps to size from
  their own window, re-read the size whenever it changes, not decide layout by device type or orientation, and keep
  controls inside a safe area that is often lopsided on iPhone Duo. The app read the screen's scale and refresh rate
  from the main screen, decided turning by "is it an iPad", and the game asked a near-square screen which way it was
  held. The sweep of every screen at the Duo's four sizes also found two layout bugs that hit other screens too.

## What it does now

### "New canvas"
- The canvas is built, then the shaders are prepared a piece at a time, each piece finished before the next, with a
  slim bar under "New canvas" filling as they go (a sheen runs along it). Where the browser can, the shader work is
  handed off to run in the background. The screen keeps drawing between pieces, so it never looks frozen.
- While the wipe is shut, the scene behind it isn't drawn as well (nothing of it shows).
- Once everything is prepared, a new canvas needs only a few pieces, and a canvas rebuilt in the menu is prepared
  between frames instead of in one go.

### Sound settings (iOS)
- Every change to the sound settings now happens off the main thread, one after another; whatever must follow (the game
  restarting its sound, picking up after an ad) runs once it's done.

### iPhone Duo
- **Any way round.** A near-square screen (long side under 1.6 times the short one: iPhone Duo open or closed, an iPad, a
  square window) turns freely. The game never asks how it's held or asks for a turn there, and Settings has no Screen
  row. Phones keep the upright or wide choice as before. The app decides this from its own window and asks again
  whenever the window changes size.
- **Folding or opening mid-match pauses the match** (as does turning the phone or a big window resize), so the player
  can settle their grip.
- **A pixel budget for matches on phones:** about 1.2 million pixels a frame. iPhone Duo's open screen (669 x 951
  points) holds half as much again as the biggest iPhone's, with a phone's chip, so it draws at 1.37x its points instead
  of 1.6x rather than running hotter. Every iPhone today is under the line and unchanged; iPads are left as they were.
  The budget is worked out again when the size changes.
- **Lopsided safe area.** iPhone Duo keeps its camera and status bar along one side of the screen, held upright too. The
  game kept clear of side insets only on a phone held sideways; now the match's controls, the canvas vote page,
  Settings' Done and the lobby's friend spots keep clear of them in every layout. A phone held upright has no side
  insets, so nothing moves there.
- **The app's own window, not the main screen,** gives the screen's scale and refresh rate; iPhone Duo has two screens.
  Upside-down portrait is allowed in the app's list, so a near-square screen can turn all four ways (phones still never
  turn upside down).

### Layout fixes found on the way (all screens, not only iPhone Duo)
- **Results:** on a wide screen under about 850 points high (iPhone Duo open, a small tablet, many laptops), the results
  beside the painting showed Rematch cut off and no Same canvas or Menu. The panel was held to the lower half of the
  screen; it now takes the height it needs.
- **Season canvases (Spooky SZN):** on a landscape screen between a phone's height and a big tablet's, the 2 x 2 grid
  pushed Play off the bottom. They now sit in one row there.

## Tested

- **"New canvas" before the first lesson,** timed in the test browser, which draws in software and is far slower than any
  phone's graphics chip (so the comparison is what counts, not the seconds):

  | | v366 | v367 |
  | --- | --- | --- |
  | Longest time the screen couldn't draw | 25.7 s | 6.4 s |
  | Tap to the match starting | 35.8 s | 37.3 s |
  | What shows meanwhile | "New canvas", frozen | "New canvas" and the bar filling, piece by piece |

  The same shaders get made either way (about 115), so the whole wait is about the same; what changes is that the screen
  stays alive and shows progress. On a phone each piece takes a fraction of a second.

- **iPhone Duo behaviour** (19 checks, all pass): a phone still gets the chooser and the Screen row; iPhone Duo open
  (951 x 669) gets neither, saves no choice and shows no turn card; the match draws at 1.37x; folding to 466 x 678
  mid-match pauses it and the match goes back to 1.6x; a small size change (a bar showing) doesn't pause; opening it
  again pauses and goes back to 1.37x; no page errors.
- **Every screen at the Duo's four sizes** (open and folded, upright and sideways): the lobby, menu, settings, stats,
  friends, locker, shop, strokes, events, vote and season pages, commissions, time trial board, online, account, login,
  terms, privacy, credits, Ol' Bloop's cards, the pop-ups, Showdown and Time trial matches, and the end screens (the
  duel's versus card, match and pause card are in the safe-area check below). The sweep found the results and season bugs above. The results now show all three buttons at 890 x 626, 951 x 669,
  1024 x 600, 1133 x 744 and 1366 x 768 (each was cut off before), and still do at 1180 x 820, 1440 x 900 and on phones.
  The season page fits at 890 x 626, 951 x 669, 960 x 640 and 1024 x 600 (Play was cut off before), and still does at
  1133 x 744, 1180 x 820 and the Duo's other sizes.
- **Lopsided safe area:** with a 44-point inset on the right (upright) or on top (sideways), at both Duo sizes, no
  control in the lobby, Settings, the vote and season pages, the versus card, the match or the pause card sits under it
  (bar a 2 to 3 point overhang of the menu button's shadow and Settings' slanted buttons).
- **Swift:** reviewed by hand; there's no Swift compiler here, so build it in Xcode. Apple doesn't publish iPhone Duo's
  inset sizes, so the 44 points above is a stand-in: the game uses whatever the phone reports.
- **The earlier tests** pass on this build: the v352 checks (25 of 25), v351's two (26 of 26, 7 of 7), v355's (27 of 27)
  and v354's (24 of 24), and the dashboard's end-to-end (38 steps) and live tests (13 steps).
