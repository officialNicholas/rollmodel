# v374: the lesson's tip holds still, and a shorter Strokes lesson

![Left: three frames of your recording on v373, "All yours! Now open your locker" in a different place in each (only the hand, over the tabs, under them). Right: v374, one place, over the character with the hand on My Locker. Below: the Strokes lesson now opens on "Let's learn some more", and the craft step says "Crafting takes 20 minutes. You can skip the wait!"](tip-still-v374.jpg)

## The flicker

After the lesson match, buying the flower and the fangs on the Paint Shop page, "All yours! Now open your locker" went round three
places, every few frames: off the top of the screen with only the hand showing, over the tabs, and under them.

**What caused it.** In a match, Ol' Bloop's line sits docked by his corner, held there by its bottom edge. Every other place the
plate goes clears that as it takes over, but the place over a button (above or below it) only ever set where the plate's top goes,
so after the lesson match that bottom edge stayed on. Held by its top and that old bottom, the plate stretched down to it, so how
tall it measured depended on where it had been put the frame before, and that decided where it went next: round and round. v362's
fix (move only once a new place has held for three frames) slowed it down but couldn't stop it, because the place really did change
every few frames.

**What's different.** The place over a button now drops that old bottom edge, and it measures the plate itself, never the box round
it, so where the plate was put can't change where it goes next. This covers every tip that points at a button, not just this one.

## The Strokes lesson

- No "Look at you, rookie!" card: the lesson opens on "Let's learn some more" (Strokes, Time trial and Showdown are unlocked), with
  the same fanfare.
- The craft step says "Crafting takes 20 minutes. You can skip the wait!" (it said "Tap Skip and watch a quick ad"). Skip still
  plays its ad, and the page's own note under Skip still says so.
- Back is the other way out: leaving the page while the Giant crafts ends the lesson, and the Giant finishes on its own. Ol' Bloop
  used to keep pointing you back at Strokes until the 20 minutes were up.
- Once the Giant is equipped, the lesson ends there: no "Giant it is!" line.

## Tested

- **The real road to the flicker**, played in the test browser on a 420 x 845 screen (your iPhone in the Claude app): the lesson match
  to its end, its finish page, the new items, the Paint Shop, the flower and the fangs bought. v373: the tip moved 39 times in 90
  frames, between the same three places as your recording. v374: it held one place for all 90.
- **The old bottom edge forced onto the tip**: v373 went round three places (24 moves in 60 frames); v374 didn't move.
- **The Strokes lesson**, upright and sideways: the first card is "Let's learn some more"; Skip, then Equip, ends the lesson with no
  closing line; Back at the craft step ends the lesson with the Giant still crafting, and nothing points you back.
- The v352 checks (25 of 25), v351's two (26 of 26, 7 of 7), v355's (27 of 27) and v354's (25 of 25), and the dashboard's end-to-end
  (38 steps) and live tests (13 steps) pass on this build, and v371's iPhone Duo fold checks too.
