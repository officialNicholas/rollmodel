# v373: room around the Locker's eyes, and the lock shows

![The Locker's Eyes section on an iPhone, v372 on the left and v373 on the right: the chosen colour's rings no longer touch the eye style above it or the colours beside it, each colour sits under a style, and the Zombie eyes' lock is a small dark badge again instead of a cream outline on the paper](eyes-v373.jpg)

## What was wrong

- **Spacing.** In the Locker's Eyes section the chosen eye colour is drawn bigger with a white and a black ring, and the chosen eye
  style lifts with its own ring. With 10 points between the rows and between the buttons, the rings collided: the chosen colour's
  ring ran 3 points into the style above it and came within half a point of the next colour (on a phone under 360 points wide it
  overlapped it), and the chosen style's ring came within 2.5 points of the next style.
- **The lock.** On a style you don't have yet (the Zombie eyes), the lock is a small dark badge with a cream padlock. The Locker's rule
  that sizes the eye pictures (36 points) caught the padlock too, so a big cream padlock spilled out of its badge onto the cream paper,
  and only the badge's dark corner showed.

## What it does now

- The five styles and the five colours stand in the same five columns, each colour under a style, 14 points apart (13 on a phone
  under 360 points wide), with 22 points between the two rows. The chosen colour's rings now keep about 9 points from the style above
  and 12 to 15 from the colours beside it; the chosen style's ring keeps 5.5 to 6.5 points from the next style. A little more room under
  the colours before the next heading.
- The padlock keeps its own size, in a slightly bigger dark badge (20 points) with a ring in the paper's colour, so it stands off the
  tile's corner.

## Tested

- The Eyes section at 8 sizes (iPhone, iPhone SE, a 320-point phone, an iPhone on its side, iPhone Duo open both ways, iPad both
  ways): measured with the rings counted, nothing touches anywhere.
- Picking a colour, picking a style, and picking the Dot eyes (which have no coloured middle, so the colours grey out) all work as
  before.
- v371's iPhone Duo fold checks (66 of 66), the v352 checks (25 of 25), v351's two (26 of 26, 7 of 7), v355's (27 of 27) and v354's
  (25 of 25), and the dashboard's end-to-end (38 steps) and live tests (13 steps) pass on this build.
