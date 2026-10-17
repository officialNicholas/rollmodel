# cq02: the Conquest level greybox (the Keep, the Aqueduct Run, the Sunken Plaza)

The first playable piece of the level in docs/conquest-design.md, built from placeholder pieces through the game's own stage pipeline (boxes, ramps, holes, basins), so each piece can be swapped for the real models later. `tools/cq02_level.py` patches the game and puts in `tools/cq02_level.js`. The Season Conquest card opens it.

## What's in
- **The Keep:** the demo's reveal and entrance as before. Then the boss taunts, rises and flies off over the wall behind you. A ring of light appears where it went: roll into it.
- **The Aqueduct Run:** a causeway 2.6 m up, 8 m wide, in an S across a 66 m square, over a canal already slimed purple (slow going, but covering it chips the boss). Gaps of 3 m to jump; three of them have cracked slabs you can pound through into the canal. Ramps back up, one a leg. Basins at the lane's edges and on side ledges a hop off the lane. A collapse (a dark wall and rubble) follows the course behind you at 86% of your speed; caught behind it, the stone gives way and you fall. Two checkpoint buoys and the gate at the end. The boss swims ahead and above: every 7.5 s a slam on the lane ahead (a ring for 1.1 s, then the shock knocks you if you're inside and on the ground), every 13 s it dives and drags slime across the lane for 4 s, every 11 s it drops two jellets in your way.
- **The Sunken Plaza:** a 53 m square with blocks to hop and four plinths at the corners with valve pads on top. Three waves of jellets (4, 6, 8; some armoured from wave 2: a pound cracks the shell, the next hit pops). Then you get the turret: plant it facing a plinth and its lobs land on the pad; a pad 55% painted arms its valve. All four armed, the boss is pinned low in the middle for 12 s: pound its bell 3 times (7% each). It tears loose, flees, and the gate lights. If the time runs out, it shakes the nets off and the pads reset.
- **Jellets:** simplified baby jellies that drift after you, slime the floor and sting (a shove and 10% paint, no life). A pound, a roll, a dash, a giant or a whirlwind pops them; each pop sends a spark into the boss (0.6%).
- **Chip damage:** every purple cell you cover takes 0.006% off the boss. The bar flashes when you've covered a stretch.
- **Lives:** the demo's 3 per checkpoint. A boss hit costs one; at none, you're knocked out and come back at the last checkpoint with 3. A fall costs one too and sends you to the checkpoint (the collapse resets 12 m behind it).
- **The end:** the plaza's gate shows a card with the time, the chip, the pops and the falls, then the menu.

## For iterating
- The boss panel (folded, top left) has a row of section buttons: Keep, Aqueduct, Plaza. Its move buttons still work.
- Tunables live in `window.CQLV` (the browser's console): `chip`, `pop`, `bell`, `bellN`, `frontK`, `frontGrace`, `slamEvery`, `diveEvery`, `jelEvery`, `jelSpd`, `waves`, `valveK`, `stun`.
- A small line at the foot of the screen shows the section, the time, the chip, the pops, the boss's health and how far back the collapse is.
- The probe: `tools/cq/shot.mjs` with `e=cqlvEnter(1)` and `p=x,z,yaw` (a teleport) steps. The checks so far ran the whole plaza loop and the run's checkpoints, falls and chips with no page errors.

## Known gaps (greybox)
- Sections load behind an iris wipe rather than one open world.
- The collapse is a dark wall and rubble; the causeway itself doesn't fall.
- The camera is the normal play camera with no zoom changes yet.
- The turret still sweeps near to far along where you face, so planting takes a little aim; there's no aim help for the pads.
- No new sounds yet; the boss's own sounds and the game's play.
