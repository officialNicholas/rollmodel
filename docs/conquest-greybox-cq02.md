# cq02: the Conquest level greybox (the Keep, the Aqueduct Run, the Sunken Plaza)

The first playable piece of the level in docs/conquest-design.md, built from placeholder pieces through the game's own stage pipeline (boxes, ramps, holes, basins), so each piece can be swapped for the real models later. `tools/cq02_level.py` patches the game and puts in `tools/cq02_level.js`. The Season Conquest card opens it.

## What's in
- **The opening (one world, no countdown, no basin):** the reveal's sweep over the keep, then you crawl in from the edge, looking about. The floor trembles and the pool churns. The boss comes up out of the middle (the demo's entrance, with its camera). You start back with a jolt. It charges and shoots away over your head and over the wall behind you. You turn round, the camera comes round with you, and the run is on: out through a breach in the keep's south wall, onto the causeway.
- **The Aqueduct Run:** one path round the outside of the keep: a stone causeway just above a sea of purple slime, out of the breach, west, north up the west side, east along the north, south down the east side and east to the gate (about 270 m). Off the path is the slime, and the slime is death (a life, and back to the checkpoint, facing along the lane). Gaps of 3 m to jump. Four basins: at the lane's edge or on a ledge a hop off it. A collapse (a dark wall and rubble) follows the course behind you at 86% of your speed; caught behind it, the stone gives way and you fall. Checkpoint buoys at the four corners and the gate at the end. The boss swims 18 m ahead with its bell about 4.5 m up, where the camera sees it; round a corner it keeps in front of you over the slime. Every 6 s it attacks, punch and slam in turn: the punch breaks a square of the causeway (half the lane's width) into the slime, and the hole stays, so you go round by the other side; the slam sends a shock ring running out along the lane at 9 m/s, which you jump (or roll) as it reaches you. Every 13 s it dives and drags slime across the lane for 4 s, every 11 s it drops two jellets in your way.
- **The Sunken Plaza:** a 53 m square with blocks to hop and four plinths at the corners with valve pads on top. Three waves of jellets (4, 6, 8; some armoured from wave 2: a pound cracks the shell, the next hit pops). Then you get the turret: plant it facing a plinth and its lobs land on the pad; a pad 55% painted arms its valve. All four armed, the boss is pinned low in the middle for 12 s: pound its bell 3 times (7% each). It tears loose, flees, and the gate lights. If the time runs out, it shakes the nets off and the pads reset.
- **Jellets:** simplified baby jellies that drift after you, slime the floor and sting (a shove and 10% paint, no life). A pound, a roll, a dash, a giant or a whirlwind pops them; each pop sends a spark into the boss (0.6%).
- **Chip damage:** every purple cell you cover takes 0.006% off the boss. The bar flashes when you've covered a stretch.
- **Lives:** the demo's 3 per checkpoint. A boss hit costs one; at none, you're knocked out and come back at the last checkpoint with 3. A fall costs one too and sends you to the checkpoint (the collapse resets 12 m behind it).
- **The end:** the plaza's gate shows a card with the time, the chip, the pops and the falls, then the menu.

- **No pick-ups:** nothing spawns in the level and the start item is taken away; the plaza hands you the turret itself.

## For iterating
- The boss panel (folded, top left) has a row of section buttons: Keep (restarts the level), Plaza. Its move buttons still work.
- Tunables live in `window.CQLV` (the browser's console): `chip`, `pop`, `bell`, `bellN`, `frontK`, `frontGrace`, `slamEvery`, `diveEvery`, `jelEvery`, `jelSpd`, `waves`, `valveK`, `stun`.
- A small line at the foot of the screen shows the section, the time, the chip, the pops, the boss's health and how far back the collapse is.
- The probe: `tools/cq/shot.mjs` with `e=cqlvEnter(1)` and `p=x,z,yaw` (a teleport) steps. The checks so far ran the whole plaza loop and the run's checkpoints, falls and chips with no page errors.

## Known gaps (greybox)
- The keep and the run are one world (60 m across: the keep's wall has a breach, the ground beyond it is slime). The plaza is still its own world: you go through the gate's light with a flash and come out on it rolling the same way.
- The broken stone stays drawn (the keep's stage is too costly to redraw mid-run): a slab of slime over the gap stands for it until the real piece can fall.
- The two-player reaction (the two look at each other) waits for co-op.
- The collapse is a dark wall and rubble; the causeway itself doesn't fall.
- The camera is the normal play camera with no zoom changes yet.
- The turret still sweeps near to far along where you face, so planting takes a little aim; there's no aim help for the pads.
- No new sounds yet; the boss's own sounds and the game's play.
