# v257 first-launch intro

A brand-new player's first minute: a barrel of paint in the dark rocks left, rocks right, tips over and pours. Two eyes come up out of the puddle and look around, the camera moves in, and the player picks the eye colour and style (live on the character). The camera eases back, and the player picks the paint colour (puddle, character and buttons update live). The character hauls itself out, jumps clear and shakes the paint off its body and ears. The player names it. It winks and jumps off screen, the iris closes, and it opens on the lobby with the character jumping in from the side. The lesson then starts exactly as before (Ol' Bloop: "Hey, rookie! Ready to roll?...").

The music is new and is written on the theme (`music/menu.mp3`). It builds a layer per stage, and a sting hands over to the menu song in time.

## Who sees it

- Only a brand-new player: `!store.introDone && !store.name && !(store.runs > 0) && store.tut.ph === 'match'`.
  - Existing players (a saved name, or any match played, or the lesson done) never see it.
  - Verified: a save with a name and the lesson done boots straight to the lobby.
- To force it for testing, set `window.__introNow = true` before the page loads.
- The orientation chooser (`openOrient`, shown when `!store.orient`) still comes first. It appears over the intro's dark scene at the end of loading, and the barrel starts once a choice is made. With the "Tap to start" gate, the intro waits for that tap, so it starts with sound.
- At the end, `store.name`, `store.color`, `store.look.iris`, `store.look.eyes` and `store.introDone = 1` are saved. Quitting halfway means the intro runs again next launch.

## Flow as built (seconds are the intro's own clock)

| Stage | What happens | Music layer |
|---|---|---|
| wait | Barrel in a spotlight in the dark, dust in the beam; orientation chooser if needed | air (starts as soon as it decodes) |
| barrel 0.5–2.4 | Rocks left, right, harder left (a wooden creak and slosh each time) | air |
| barrel 2.5–3.2 | Tips over (thud, camera shake, lid flies off and clatters) | air |
| barrel 3.2–6.2 | A rope of glossy pearl paint pours from the mouth into a spreading puddle | air |
| barrel 6.2–9 | The character's eyes and ears pop up out of the puddle (a bloop and ripples), look left and right, blink; the camera moves in | air |
| eyes (card 1) | Eye colour (5 iris colours) and style (Round, Squid, Dot), live on the character | keys come in on the card; low comes in on the first style pick or on Next |
| paint (card 2) | Camera eases back; 6 paints; the puddle, the character, its coat and the game's own colour (buttons) change live, with a splash | low |
| form | It rises out of the paint, crouches, jumps clear (drops trailing), lands with a splash, shakes the paint off (the coat bursts into flying drops) | tops |
| name (card 3) | "Name your star", prefilled with a random name, dice for another | drive (everything) |
| wink | It winks (a sparkle and a star by its eye), then jumps off screen to the right | riser, one bar |
| hand-over | The iris closes as the sting hits and opens on the lobby; it jumps in from the left and lands on its spot | sting; one bar later the menu song comes in at its 8th bar |

The free stems were judged enough to give away. Sly eyes are a 545-dab Paint Shop item, so they are not offered, which keeps the economy as it was.

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
- geometries, materials and canvas textures;
- the character's own materials (its geometry and face sheets are shared with the game's characters, so they are left alone);
- its entry in `AXOC.S.list`.

While the intro is live it draws instead of the lobby. `frameBody` returns before `step`, `visuals` and `renderFrame`, so the lobby and canvas cost nothing during it.

- The backdrop is one full-screen quad: dark gradient, faint far bokeh, grain.
- The floor is one shader on one plane. It holds the old boards, the spotlight pool, the soft shadows of the barrel and the character, and the puddle as a metaball field: the pool, the mouth's spill, and up to 24 splats from landing drops. It is lit with a glossy rim, a fake reflection and a specular highlight, with ripples and the meniscus around the character. The puddle, splats and shadows add no draw calls.
- The barrel is a lathe with a 512 px canvas texture (staves, hoops and rivets, a taped WET PAINT label, pearl drips) and a 128 px roughness and metalness map. The lid is a separate piece and flies off.
- The pour is one deformed tube, drops are one instanced mesh (up to 96), the beam and dust are one cone and one point cloud, and there are 3 directional lights and a hemisphere light.
- The character is the game's own `AXOC.make()` axolotl, driven through `AXOC.update` with the game's animator. Eye colour and style, colour, paint coat, `shake()`, `coatBurst()` and the `smirk` wink face are all its own.

Measured (Chromium, SwiftShader, 390x780):

| Stage | Draw calls (3D pass) | Triangles |
|---|---|---|
| Barrel alone | 8 | 17.6k |
| Pour | 9 | 18.3k |
| With the character | 10 | 46.8k |

Add 1 draw for the backdrop. There is no shadow map, no post pass and no render target. FRAME_TIME_PLACEHOLDER

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

## Files

- `tools/v257_intro.py`: the patch module, `apply(s)`. It reads `v257_intro.js`, `v257_intro.css` and `v257_intro_au.js` from beside itself.
- `tools/q257_intro.py`: the quick builder. It writes `game/_intro_test.html`; `--test` adds `window.__T`.
- `tools/p257_intro.py`: the Playwright probe. It plays the whole intro through its cards (portrait, landscape, app insets) and captures every stage. `SAVE=<json>` checks a returning player instead.
- `tools/intro_score.py`: composes and renders the music. `tools/intro_music_build.py`, `tools/intro_audio_an.py` and `tools/intro_music_gen.py` are the analysis and generation helpers. `tools/assets/intro257/` holds the Ludo.ai one-shots the score uses.
- Assets: `game/music/intro_{air,keys,low,tops,drive,sting}.mp3` and `game/sfx/intro_fx.mp3`. The page reaches them through the game's own `MUSIC_BASE` and `SFX_BASE`.

## Testing

```
python3 tools/q257_intro.py --test            # build game/_intro_test.html (not committed)
python3 -m http.server 8765 --directory game &
PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers python3 tools/p257_intro.py out port inset
PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers python3 tools/p257_intro.py out land inset
SAVE='{"name":"Dusk","runs":9,"orient":"port","tut":{"ph":"done"}}' PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers python3 tools/p257_intro.py out port
```

In the test build, `FL.peek()` reports the phase, draw calls and triangles, and `FL.go(phase)` jumps to a phase.

## Not done or worth a look

UNFINISHED_PLACEHOLDER
