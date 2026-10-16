# v314: a smaller knock-out bonus, a closer sideways view, a calmer giant

![The knock-out row filling in under the bar, step by step](tally-camera-v314.jpg)

## 1. The knock-out bonus in the tally

The big "Knock-out bonus" headline is gone. It was as big as the result itself, and the paint result is the story.

- Under the bar, each side gets one small row: "KO" and a star for each of its knock-outs, dim at first.
- In turn, each star fills gold. A little "+2%" rises off it, and that side's paint on the bar and its number go up by 2 at the same moment, with a small splat where it lands.
- The row ends on the side's total (for example "+6%") and stays there, small, under the bar until the winner shows.
- It's quicker: about a third of a second per knock-out (it was 0.62 s), the two sides taking turns.
- Nothing flies across the screen any more, and the number gets no badge.
- A side with no knock-outs shows nothing.

## 2. Sideways, the play view is 10% closer

Playing sideways (landscape), the camera sits 10% closer: its height and its distance behind you are both scaled by 0.9. You see less of the stage, and your character is a little bigger. Upright play is unchanged.

## 3. Turning as a giant is gentler

A giant rolls 1.75 times as fast, and the faster roll also made it turn quicker. At full steer, a giant turned about 60% faster than a normal roll, which made it twitchy.

Your turning while you're a giant is now scaled down. At full steer a giant now turns at about the same rate as a normal roll, a touch slower: 2.5 radians a second where it was 4.4. A normal roll is 2.8. Moving faster at that rate, a giant's turns are wider and heavier.

When the giant wears off, turning is back to normal. The CPUs are unchanged.

## Tested

- **The tally:** a real match end with 3 knock-outs against 1, held at each step, upright and sideways.
  - The rows appear under the bar.
  - The stars fill one at a time, the two sides taking turns.
  - Each star adds 2 to that side's number and its paint on the bar.
  - The totals stay to the end.
- **The camera:** two sideways shots from the very same moment of a match, one at the old distance and one at the new.
- **Turning:** the turn rate at full steer, worked out exactly from the game's own steering, before and after.
  - A normal roll: 2.8 radians a second, the same as before.
  - A giant: 2.5, where it was 4.4.
