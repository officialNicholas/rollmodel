# v376: the character is never see-through over itself

![The start of a Showdown on the Fishing Raft, climbing out of the paint (top) and just after Go (bottom); v375 on the left, v376 on the right. On the left a pale flat copy of the head and body sits over the character and the face shows twice; on the right it's solid](ghost-v376.jpg)

## What was wrong

- Every character carries a see-through copy of itself, in its colour, which shows only where something stands in front of it. That's
  how you can still see where you are behind a wall.
- That copy was drawn after everything solid, so "something in front" included the character's own body.
- The body puffs out where the copy doesn't: the paint coat you climb out of the basin in, and the jelly squash and wobble. So the copy
  sat a little inside the body, counted as hidden behind it, and was laid over it. That gave a pale, flat copy of the head and body on
  top of the real one, with the face showing twice.
- It was worst at the start of a match (coated, squashed, with the camera close), and showed a little whenever the character wobbled.
  It happened to rivals too.

## What it does now

- The see-through copy is drawn before the characters, straight after the stage, so only the stage (walls, crates, the floor) can bring
  it out. Over the character's own body it never shows.
- Behind a wall it shows as before.

## Tested

- The start of a Showdown on the Fishing Raft, real rendering: v375 shows the veil while climbing out of the paint and just after Go;
  v376 is solid in the same moments.
- A crate put between the camera and you: the see-through copy still shows through it on v376, as on v375.
