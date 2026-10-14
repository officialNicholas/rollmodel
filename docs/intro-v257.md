# v257 first-launch intro

A brand-new player's first minute, out in the sun: a sandstone canyon scrapyard at midday. The camera looks up at the deep blue sky over the canyon rim, then comes down on an old oil drum. It rocks left, rocks right, tips over, its lid flies off, and pearly paint pours onto the sand. Two eyes come up out of the puddle and look around, and the camera moves in.

The player then picks, each live on the character:
- the eye colour;
- the eye style;
- the paint colour (puddle, character and buttons all change).

The character hauls itself out, jumps clear and shakes the paint off its body and ears. The player names it and confirms ("All set?": *Not yet* goes back to change things, *Let's roll* goes on). Two strips of tape slap across the screen ("Fresh out of the barrel?" / "Now go paint the town!"). It winks and leaps away, the iris closes, and it opens on the lobby with the character jumping in from the side. The lesson then starts exactly as before (Ol' Bloop: "Hey, rookie! Ready to roll?...").

The look follows the references the player sent:
- a sunlit desert scrapyard, warm sand, hard shadows;
- soft out-of-focus backgrounds in the close-ups;
- black torn-tape headlines in big white letters over a ragged black board;
- the pick marked by a paint splat and a little cursor;
- splat-shaped buttons and slanted send-off banners.

The wording and art are our own.

The music is new and is written on the theme (`music/menu.mp3`). It builds a layer per stage, and a sting hands over to the menu song in time.

## Who sees it

- Only a brand-new player: `!store.introDone && !store.name && !(store.runs > 0) && store.tut.ph === 'match'`.
  - Existing players (a saved name, or any match played, or the lesson done) never see it.
  - Verified: a save with a name and the lesson done boots straight to the lobby.
- To force it for testing, set `window.__introNow = true` before the page loads.
- The orientation chooser (`openOrient`, shown when `!store.orient`) still comes first. It appears at the end of loading, and the intro starts once a choice is made. With the "Tap to start" gate, the intro waits for that tap, so it starts with sound.
- At the end, `store.name`, `store.color`, `store.look.iris`, `store.look.eyes` and `store.introDone = 1` are saved. Quitting halfway means the intro runs again next launch.

## Flow as built (seconds are the intro's own clock)

| Stage | What happens | Music layer |
|---|---|---|
| wait | The scene is ready behind the orientation chooser (if it's needed) | |
| sky 0–2.3 | Looking up at the sky over the canyon rim, then the camera cranes down onto the drum | air (starts as soon as it decodes) |
| barrel 0.5–2.4 | The drum rocks left, right, harder left (a creak and slosh each time) | air |
| barrel 2.5–3.2 | Tips over (thud, camera shake, a puff of sand, the lid flies off and clatters) | air |
| barrel 3.2–6.2 | A rope of glossy pearl paint pours from the mouth into a spreading puddle on the sand | air |
| barrel 6.2–9 | The character's eyes pop up out of the puddle (a bloop and ripples), look left and right, blink; the camera moves in | air |
| iris (card) | "Those eyes need a color." 5 iris colours, live on the face | keys |
| style (card) | "Now give them some style." Round, Squid, Dot | low |
| paint (card) | "Pick your paint." The camera eases back; 6 paints; the puddle, the character, its coat and the game's own colour change live, with a splash | tops |
| form | It rises out of the paint, crouches, jumps clear (drops trailing), lands with a splash, shakes the paint off (the coat bursts into flying drops) | tops |
| name (card) | "What do we call you?" Prefilled with a random name, dice for another | drive (everything) |
| confirm (card) | "All set?" *Not yet* (back to the eye colour, standing now, every pick still live) or *Let's roll* | drive |
| wink | Two tape strips slap in, it winks (a sparkle and a star by its eye), then leaps away into the scrapyard | riser, one bar |
| hand-over | The iris closes as the sting hits and opens on the lobby; it jumps in from the left and lands on its spot | sting; one bar later the menu song comes in at its 8th bar |

Every card after the first has a *Back*.

Only the free eye styles are offered (Round, Squid, Dot). Sly eyes are a 545-dab Paint Shop item, so leaving them out keeps the economy as it was.

## The music

The theme was analysed rather than reused:
- Tempo 110.89 BPM. The menu loop (6.928 to 43.722 s) is exactly 68 beats.
- Key A minor. It runs in a 17-bar cycle with a break at bar 17.
- The main melody enters at bar 9, with its pickup in bar 8. It was pitch-tracked from a demucs separation of the theme, and both statements agree:

```
Dm  A5 F5 D5 F5 | Am  E5. C5 E5 A5 | Bb  F5 D5 Bb4 D5 | E  E5 A4 G#4 B4
Dm  A5 F5. D5 C6 | Am  C6. B5 A5 (C5 E5) | F  A5 C6 B5 G#5 | E  E5 . B4 C5 D5 E5
```

`tools/intro_score.py` composes and renders a new 8-bar piece on those chords, at that tempo, as five stems of one seamless loop. Each stem is rendered three times, sample-identical, and the middle pass is kept, so ringing notes and reverb carry over the loop point (seam error measured at about 1e-15).

| File | Layer | Contents | Size |
|---|---|---|---|
| `music/intro_air.mp3` | 0, barrel and eyes | A dark shimmer (Ludo.ai texture), a low A and E drone, a ticking clock, the melody's first notes on a music box | 218 KB |
| `music/intro_keys.mp3` | 1, eye colour | Warm pads on the chords, the whole melody on celesta | 254 KB |
| `music/intro_low.mp3` | 2, eye style | Bouncing root-and-octave bass, harp arpeggios | 254 KB |
| `music/intro_tops.mp3` | 3, paint colour | Shaker sixteenths, off-beat hats | 218 KB |
| `music/intro_drive.mp3` | 4, naming | Kick, snare, clap, a tom fill, the melody on strings an octave down | 254 KB |
| `music/intro_sting.mp3` | the reveal | A one-bar riser into an E major hit (sub boom, crash, orchestra, celesta run up). E major is the dominant, so the theme's A minor resolves it | 145 KB |
| `sfx/intro_fx.mp3` | effects | Barrel wobble, tip, pour, eyes pop, form, sparkle (Ludo.ai), one sprite | 93 KB |

All loops are 17.31446 s (8 bars), with loop points `a = 0.25`, `b = 17.56444` and a pre-roll before `a`.

The engine is `AU.flm`, inside `makeAudio`:
- It plays through `trkBus`, so the music switch, pause muffle and mute all apply. Effects go through `sfx`.
- Each stem starts on one shared clock as soon as it decodes, so a slow network only delays a layer and never breaks sync.
- Layer changes land on the next beat.
- `AU.flm.sting(lead)` schedules the hit on the first bar line at least `lead` seconds away. The riser starts a bar before it, the stems stop on the hit, and the intro's timeline (wink, jump, iris) is timed from it.
- The menu song is started one bar after the hit at offset 17.605 s (its bar 8, the melody's pickup bar). This skips its intro and lead-in build and carries on in tempo. It is set up as the game's own current track, so the rest of `AU.music` behaves as usual afterwards.
- If sound never started (no tap, muted), the menu song starts the usual way.

Nothing intro-related is fetched for anyone but a first-timer. For them, the fetch starts at the end of loading (the air stem first), so loading time is unchanged for everyone.

A listenable preview of the whole arc is in `docs/intro-v257-music-preview.mp3`. It has each layer every 4 bars, then the riser, the sting at 0:43, and the menu song from its bar 8.

## The scene and what it costs

Everything is built only when the intro runs and disposed at the hand-over (`dispose()`):
- geometries, materials and textures (canvas and image);
- the baked shadow texture;
- the character's own materials (its geometry and face sheets are shared with the game's characters, so they are left alone);
- its entry in `AXOC.S.list`.

While the intro is live it draws instead of the lobby. `frameBody` returns before `step`, `visuals` and `renderFrame`, so the lobby and canvas cost nothing during it. It's one render pass straight to the screen.

- **The sky** is a dome shaded from deep blue overhead to a paler blue low down. Its colours are taken off the painting so the two meet without a seam.
- **The canyon** is a painted panorama (`art/intro_canyon.webp`, Ludo.ai, 2048x972, 106 KB) on a cylinder 26 m out. It shows sandstone mesas, the old train car, wrecked cars, fences with caution tape and a distant radio tower. Its ends are mirrored out to cover wide screens, and its sky fades into the dome.
- **The ground** is one shader on one plane. It holds:
  - the sand (`art/intro_sand.webp`, a seamless 512 px Ludo.ai texture, with large light and dark patches);
  - the hard sun shadows (the drum, its lid and the character as capsules laid along the sun, live; the rocks, agaves, sheet and posts baked once into a 384 px texture);
  - the paint as a metaball field (the pool, the mouth's spill and up to 24 splats from landing drops), with damp sand round its edge. The paint has a sky reflection, sun glint, ripples and the meniscus round the character.
  - Far off, it goes into the canyon's haze, its colour also taken off the painting.
- **The depth of field** is faked without a post pass. Each shot sets a focus amount, and away from what the camera's on:
  - the sand texture, the canyon painting and the props' textures are sampled from smaller mipmaps (a texture bias);
  - the shadow edges soften.

  The close-ups get a soft background like the references.
- **The drum** is a lathe (rims and two ribs, hollow inside) with a 1024x512 canvas texture: the riveted red-paint panels of `art/intro_drum.webp`, darker bands at the rims and ribs, scuffs, a sprayed PAINT stencil and pearl drips. The lid is a separate piece and flies off.
- **The set** is 4 draws:
  - sandstone rocks (faceted, banded);
  - agaves;
  - a sheet of corrugated iron (`art/intro_rust.webp`);
  - caution tape on three posts ("CAUTION WET PAINT").
- **The rest:** the pour is one deformed tube, drops are one instanced mesh (up to 96), and wind-blown sand is one point cloud. The lighting is a sun, a rim light, a warm bounce off the sand and a sky/sand hemisphere.
- **The character** is the game's own `AXOC.make()` axolotl, driven through `AXOC.update` with the game's animator. Eye colour and style, colour, paint coat, `shake()`, `coatBurst()` and the `smirk` wink face are all its own.

The art adds about 160 KB, fetched by first-timers only.

Measured with `tools/perf257_intro.py` (Chromium with SwiftShader, 390x780, averaged per stage, the lobby in the same browser right after).
- *Main-thread ms* is the game's own `lastCpu`: the whole frame's JS and GL calls.
- *Frame ms* is the wall time between frames under SwiftShader. Since rendering there is in software, it mostly measures pixel cost.

| Stage | Main-thread ms | Frame ms (SwiftShader) | Draw calls | Triangles |
|---|---|---|---|---|
| Sky (opening) | 2.0 | 81 | 14 | 22k |
| Drum rocks, tips, pours; eyes pop up | 2.1 | 180 | 17 | 52k |
| Eye colour card (close-up) | 2.5 | 349 | 13 | 51k |
| Eye style card (close-up) | 2.3 | 379 | 13 | 51k |
| Paint card | 2.2 | 318 | 16 | 52k |
| Forming, jumping, shaking | 2.5 | 279 | 16 | 52k |
| Name card | 2.4 | 310 | 16 | 52k |
| All set? | 2.2 | 352 | 13 | 51k |
| Wink, send-off, leap | 2.1 | 271 | 16 | 52k |
| Jump-in (lobby) | 5.6 | 140 | 4 | 44k |
| Lobby | 4.6 | 184 | 4 | 44k |

There is no shadow map, no post pass and no render target.

On the main thread the intro costs about half of what the lobby does. On pixels, the wide shots cost about what the lobby does and the close-ups about 1.7 to 2 times as much under SwiftShader. Timing each layer of the eyes close-up off in turn:

| Layer | Share of the close-up's pixel cost |
|---|---|
| The game's character drawn large | about 60% |
| The ground (sand, paint, shadows) | about 25% |
| The sky, the canyon and the props | about 10% |

The character's share is the same cost the locker's close-up already pays. Baking the still shadows took the ground's share from about 110 ms to 87 ms. The game's own quality ladder (`tunePerf`) keeps running during the intro, so a slow phone drops resolution as it would anywhere else.

## Anchors replaced in `game/index.html` (`tools/v257_intro.py`)

Each anchor must match exactly once:

1. `\n</style>\n\n<div id="stage">`: the stylesheet is appended to the main `<style>`.
2. `    _trk(k) { return k ? !!(TRK[k] && TRK[k].buf) : trk && trk.key; },\n` (in `makeAudio`'s api): `flm` (the intro's music engine) is added after it.
3. `applyOrient(); showMenu();\nawait bootStep(0.82, 0.93, 'Hanging the show');`: the intro module (`var FL = ...`) is inserted before it.
4. `resetRun(); decorate(); renderStages(); AU.music('menu'); menuPose();` (in `showMenu`): the menu song is held while `FL.hush` (from boot until the hand-over).
5. `if (!store.orient) { if (bootHold) {` (the end of loading): `if (FL && FL.due) FL.boot(); else ` is prefixed.
6. `  if ((AXOC.S.ready || SLIME.S.ready) && !VP.slime && booted && state === 'menu' && !lookOpen && !irisBusy) { attachSlimes(); queueWarm(); }\n` (in `frameBody`): followed by the intro's frame, which returns early while it is live.
7. `  visuals(dt, rdt); flushTrail(); pbarTick(rdt); lockerTick(); dipTick(rdt);\n` (in `frameBody`): followed by `FL.after(rdt)`, the jump-in's sideways offset.
8. `  const isc = D === P && lookIntro && state === 'menu' ? V.introSc : 1;\n` (in `visuals`): preceded by the jump-in's hop, squash and rise.
9. `  if (bootHold || !booted || !tutBootEl.classList.contains('gone')` (in `tutMenuTick`): the coach waits while `FL.busy()`.

`FL` is a `var`, so the hooks are safe before it is assigned. For a returning player `FL` is a stub: `due` is false and every hook is a no-op.

If the scene can't be built (for instance neither character pack loaded), the intro stands down: the lobby's song plays and the orientation chooser opens exactly as before. This was tested with both packs pointed at missing files.

## Files

- `tools/v257_intro.py`: the patch module, `apply(s)`. It reads `v257_intro.js`, `v257_intro.css` and `v257_intro_au.js` from beside itself.
- `tools/q257_intro.py`: the quick builder. It writes `game/_intro_test.html`; `--test` adds `window.__T`.
- `tools/c257_intro.py`: makes the screenshot composites from a probe run.
- `tools/r257_intro.py` and `tools/r257_mix.py`: the video (`intro-v257.mp4`). The recorder steps the page at a fixed 30 frames a second of game time (`requestAnimationFrame`, `performance.now` and the CSS animations together) and logs when each stage begins. The mixer lays in the music as the game plays it (the layers on the beat, the sting on a bar line, the menu song from its bar 8) and the intro's effects. The game's own synthesized effects (pops, splats, jumps) aren't in the video's sound.
- `tools/perf257_intro.py`: the cost per stage, against the lobby.
- `tools/p257_intro.py`: the Playwright probe. It plays the whole intro through its cards (portrait, landscape, app insets) and captures every stage. `SAVE=<json>` checks a returning player instead.
- `tools/intro_score.py`: composes and renders the music. `tools/intro_music_build.py`, `tools/intro_audio_an.py` and `tools/intro_music_gen.py` are the analysis and generation helpers. `tools/assets/intro257/` holds the Ludo.ai one-shots the score uses.
- Assets:
  - `game/music/intro_{air,keys,low,tops,drive,sting}.mp3` and `game/sfx/intro_fx.mp3`, reached through the game's own `MUSIC_BASE` and `SFX_BASE`;
  - `game/art/intro_{canyon,sand,drum,rust}.webp`, reached as `art/<name>.webp` like the game's other art.

  The intro's splats are the game's own `art/splat2.webp` and `art/m_splat2.webp`, used as CSS masks filled with your paint.

## Testing

```
python3 tools/q257_intro.py --test            # build game/_intro_test.html (not committed)
python3 -m http.server 8765 --directory game &
PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers python3 tools/p257_intro.py out port inset
PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers python3 tools/p257_intro.py out land inset
SAVE='{"name":"Dusk","runs":9,"orient":"port","tut":{"ph":"done"}}' PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers python3 tools/p257_intro.py out port
```

In the test build, `FL.peek()` reports the phase, draw calls and triangles, `FL.go(phase)` jumps to a phase (`sky`, `barrel`, `iris`, `style`, `paint`, `form`, `name`, `confirm`, `wink`), and `FL._x()` is the scene.

## Not done or worth a look

- **Only tested in SwiftShader.** Worth a run on a real iPhone and a mid-range Android, in particular:
  - the close-up frame time;
  - the one-off shader compile when the character first appears. It's precompiled with `compileAsync` while the camera's still up in the sky, but a phone without parallel compile may still hitch once.
- **The backdrop is a painting.** Its perspective is fixed, so the camera's moves are kept small. Tall or very wide screens see the mirrored ends of it.
- **The fonts in the screenshots are fallbacks.** The sandbox can't load Google Fonts, so the banners show a substitute for Bowlby One; on a device they're Bowlby One like the rest of the game.
- **The music was judged by analysis, not by ear.** The key, the melody re-tracked from the rendered stems, the seams, the levels and the hand-over were all checked numerically. A listen to `docs/intro-v257-music-preview.mp3` and `intro-v257.mp4` should decide:
  - the mix balance;
  - the sting;
  - the menu song's entry point: offset 17.605 s, its bar 8, measured from the kick onsets. If it lands a hair early or late, change `MENU_AT` in `tools/v257_intro_au.js`.
- **The wink is subtle on the Squid and Dot eyes**, since those styles darken the eye. The sparkle and star sell it.
- **No skip button.** The intro is about 40 seconds, with four choices and a check in it. Quitting halfway shows it again next launch.
- **Fallback fonts:** if the web fonts haven't arrived when the barrel's label is drawn, it is drawn again once they have.
