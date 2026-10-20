# v387: Skins (v388: brighter, a new Rainbow)

Five premium looks for the whole body, bought with dabs in the Paint Shop. A skin repaints the character's skin from head to tail
(body, head, gills, legs, tail), and each one moves a little.

| Skin | Price | What it looks like | How it moves |
| --- | --- | --- | --- |
| Galaxy | 2000 | Deep space: dark blue-violet with magenta and blue nebulae and a dusty band across it | Its stars twinkle; the nebulae stay still |
| Lava | 1750 | Near-black basalt broken into uneven plates, the cracks between them molten (yellow-white core, orange to red edges) | Heat flows up through the cracks so each one brightens and dims in turn; the plates breathe; faint veins glow |
| Rainbow | 1500 | Holographic foil: every colour, pearly, with white glints | The colour turns with the angle you see it from and swirls slowly across the body (v388) |
| Matrix | 1750 | A black screen with green code: glyphs of lit pixels in cells | Streams of code rain down the body, each with a bright white-green head and a fading trail; glyphs flicker as it passes |
| Glitter | 1250 | Glitter flakes in your own paint colour, a finer dust of glints between them | Flakes catch the light as you move and turn, and some flash on their own |

## Where they show

- The Paint Shop has a Skins filter (first after the season's), and in All the skins come first after the season's banner. Each card is a
  portrait of you in that skin. Tapping one tries it on in the window above.
- In the locker, Skins is its own section. One skin at a time; Take off goes back to your paint's own skin.
- Putting one on in the locker sweeps it up over you from the ground, with a bright seam where it's arriving, and you spin round once to
  show it off. Everywhere else (lobby, matches, portraits, the Strokes page's demos) it's simply on.
- Friends' pictures and online rivals show your skin (it travels with the rest of what you wear).
- Now and then a CPU rival wears one (one in eight, once the lessons are done). In 2v2 only Glitter, since it keeps the team's colour.

## Readability in a match

- The eyes, the mouth and the paint you come out of a refill in are drawn over a skin as before.
- Your paint is still your colour. The ink line round you and the see-through copy behind walls keep your team's colour, so a skin never
  hides whose side someone is on.
- Glitter is always in your paint colour.

## How it's built

- One shader path in the axolotl's body material (`tools/v387_skins.py`): a uniform `uFx` (which skin, how far it has swept up the body,
  the time). The patterns are drawn from the body's own rest position (`vCp`), so they ride along with every squash and stride.
- The skin sets the surface's colour, roughness and metalness, and adds its own glow (stars, molten cracks, code, glints) after the
  lighting, never through the paint or the drawn face.
- The face is a little calmer on the busy skins (Matrix), so expressions still read.
- Far away, fine detail (stars, glyphs, flakes) fades to its average instead of shimmering.
- The old slime (only used if the axolotl never loads) has no skins.

## v388

- Lava: the red runs hotter and wider: a vivid red edge round every crack and a red glow spilling onto the rock beside it; even the
  coolest cracks stay lit.
- Galaxy: more stars, brighter, and the twinkle never drops one out entirely.
- Glitter: more flakes catch the light, and they and the dust between them flare much brighter.
- Rainbow: the candy stripes are gone. Three designs were tried (holographic foil, tie-dye swirls, a smooth head-to-tail rainbow); the
  foil was kept.
