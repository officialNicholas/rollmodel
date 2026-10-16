# v320: back to the regular game

The boss fight is out of the game. v320 is the regular game as it was before the boss fight came in (v314), plus the intro's music fix.

## What's gone from the game
- The Jellyfish Boss, the Sunken Keep where it lived, and the boss preview with its test panel.
- Everything built on them:
  - the entrance;
  - the boss's moves and its health bar;
  - the LIFE counter;
  - the boss's sounds;
  - the keep's light, fish and particles.
- The Season Conquest card on the Choose Event screen says **Coming soon** again and does nothing when tapped, as it did up to v314.
- The game is about a third smaller (5.1 MB instead of 7.8 MB), since the boss model and the keep's textures are no longer in it.

## Where the work is kept
- The code is still in the repository, out of the build: tools/v309_conquest_stage.py, tools/v311_conquest_boss.py, tools/v315_boss_demo.py and v316 to v319's boss and keep modules.
- Their docs stay in docs/, and git history has every version.
- To try any of it again, add the modules back to the end of the list in tools/q260.py, in the order the comment there gives.

## Tested
- The release boots with the same 7 known warnings as before.
- A versus match plays, ends and tallies, then returns to the menu, with no page errors and no boss code loaded.
- The Season Conquest card reads "Coming soon".
