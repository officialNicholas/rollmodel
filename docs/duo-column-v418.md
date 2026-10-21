# v418: iPhone Duo's side column, the cover-screen Paint Shop, and opening the phone

![iPhone Duo closed (466 x 678, the 84-point column on the right): the lobby with the bell and menu buttons in the column under the camera, the Paint Shop with no filter chips and more room for the list, the dab store clear of the camera, Settings, Choose Event and a match with the sound button in the column](duo-column-v418.jpg)

## What Apple says about the column

Closed, iPhone Duo keeps its status bar, front camera and Dynamic Island in a column down the right-hand edge of the outer screen
(84 points wide in the iOS 27.1 simulator). From Apple's "Design for iPhone Duo" and "Prepare your app for iPhone Duo" talks:

- Content stays to the left of the column. Line it up with the side safe-area insets, and treat each side on its own: the
  insets are lopsided.
- A full-bleed background may run under the column. Nothing you tap should sit under it.
- The buttons an app has along the top go to the top of the column, and its bottom ones to the bottom, so they sit under the
  right thumb. An immersive screen that doesn't scroll can fill the whole display, as long as no control sits under the column.

The game already kept most screens clear of the column, but it left the column empty, and pop-ups ignored it. The dab store's
close button sat under the camera.

## What it does now

- **Spotting the column.** The game reads the side safe-area insets. A column is one side inset of 30 points or more with no
  inset on the other side. A phone held sideways has the same inset on both sides, so it isn't affected. The game marks the page
  `scol` (column on the right) or `scolL` (on the left), keeps the column's width in `--scw`, and checks again on every resize
  and fold. Phones and iPads see no change.
- **Pop-ups keep clear of the column.** This includes the dab store's close button, which is now left of the camera.
- **The column holds the top buttons.** In the lobby, the bell and menu buttons sit in the column under the camera, one above
  the other. In a match, the sound button sits there too. Everything else in the lobby keeps its place.
  On the Locker, Paint Shop and Strokes pages (v419), the dab counter (with its +) and the turn button sit there too, the
  turn button under the counter.
- **The Paint Shop on the cover screen.** The filter chips (All, Spooky SZN, Skins...) are gone and the shop shows everything.
  The stage is shorter (150 to 210 points instead of about 280). The My Locker and Paint Shop tabs drop their pictures. The list
  grows from about 210 points to about 345. The opened phone keeps the chips.
- **Opening the phone.** On the way from closed to flat, the hinge passes through "partly folded" for about a second. iOS
  reports a fold down the middle while that happens. The lobby moved you into its partly folded layout (the right-hand half,
  smaller) and then back to the middle, which looked like a jump. A new fold now counts only once it has held for 1.2 seconds.
  A fold going away still counts at once.

## Tested

- **The closed size** (466 x 678, insets 0 / 84 / 34 / 0): the lobby, Paint Shop, dab store, Settings, Choose Event and a match.
  Each was screenshotted (above). The every-screen sweep from v367 was run with the column added. Chromium's own safe-area
  override hung in this browser, so the test pages replace the safe-area values with fixed ones.
- **Fold timing:**
  - a fold shown for 0.8 s and then cleared is never applied;
  - a fold held for 1.6 s is applied (you in the right-hand half, as before);
  - a fold clearing applies at once.
- **No column, no change:** an upright iPhone (59 / 0 / 34 / 0) and a sideways one (0 / 59 / 21 / 59) get neither `scol` nor
  `--scw`.
- Apple doesn't publish the column's width. The 84 points is the simulator's figure, and the game uses whatever the phone
  reports.
