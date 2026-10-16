"""v311 (Season Conquest boss): the boss rival, the owner's jellyfish with boxing gloves, rigged and animated, as a factory a fight can
drive. In releases since v315, where the boss demo (tools/v315_boss_demo.py) puts it into the Sunken Keep (v309_conquest_stage.py)
and adds its entrance; tools/boss/build_viewer.py builds a test page with a viewer that runs every move.

The model is the owner's (one mesh, 17,100 triangles, its own texture), rigged offline (tools/boss/fbx_extract.mjs, then
tools/boss/build_pack.py) into game/boss-pack.txt, about 0.76 MB of text, fetched the first time a boss is made. The runtime is
tools/v311_conquest_boss.js, put in after the axolotl's runtime (it borrows its texture decoder). In it:
- the rig: a root and the bell; each arm a chain of six bones along a springy curve down to the glove; each glove a hand bone, a cuff
  and three bones for each finger and the thumb; seven tentacle chains. Four weights a vertex, computed per part (an arm never drags a
  tentacle), smoothed across the joints.
- the hands: the model's own gloves, bent at every joint (no swapped-in hands). Poses open, relax, fist, point and spread blend into
  each other, each finger a moment after the last (index first, pinky last; closing, the thumb comes over last), every joint settling
  on a spring. The fist's thumb was fitted on the rig to wrap round the side and tuck over the curled index, as on the owner's sheet.
- physics, run in fixed small steps (stable at low frame rates): the root on a spring that each pulse beat pushes up (it swims), the
  bell tipping against its own acceleration and wobbling on hits (two ring modes and a squash), the wrists and the arm curves' handles
  on springs (they overshoot and settle; fists stop on the floor), the cuffs jiggling, the tentacles as damped chains in the water (a
  travelling wave of their own, each with its own speed and phase, drag when the boss moves, a slow sink, floor contact).
- the bell's pulse in the vertex shader: the top contracts first and the rim follows (the rim pulls in, the dome rises), then it all
  flows back out, the skirt rippling with it; the same shader motion runs for the outline and the shadow.
- the face: two eye caps and two brows on the bell, drawn in their shader (lids, slant, pupils that follow the player and dart, blinks,
  "> <", spirals, a glow): angry (the default), glare (a sideways look), charging, glow, hurt, dizzy, smug, defeated, surprised,
  neutral, eased into each other.
- purple electricity round the gloves: jagged arcs hugging each glove's outline, re-formed many times a second, with a soft glow;
  stronger when charging and striking, a burst and a ring on the floor where a fist lands; the zap's bolts; bubbles, slime and drips.
- draws: the body, its outline, the face, the lightning and the particles (5, plus the body's shadow).

The interface (all world units; the scale is one number):
  const boss = makeBoss({ scale: 1, hover: 5.6, floorY: 0, poolY: -0.14, poolR: 4, glove: 1.3 });
  scene.add(boss.group); boss.group.position.set(0, floorY, 0)   // its home: the floor under the middle of the bell (the pool's middle)
  boss.ready (a promise) / boss.isReady                          // the pack is in; moves asked for before then are queued
  boss.update(dt, { player, camera })                            // each frame; player: a Vector3 it looks at and turns to; camera: for
                                                                 // the sparks, which face it (else the last drawn camera)
  boss.play(name, opts) -> the move's length in seconds          // plays over the hover; back to the hover when done
  boss.busy, boss.move                                           // a move is on, and which
  boss.lookAt(x, y, z) / boss.lookAt(null)                       // look somewhere else / back at the player
  boss.face(expr, seconds) / boss.face(null)                     // hold an expression over the move's own
  boss.hand('L' | 'R' | 'both', pose) / boss.hand(side, null)    // open, relax, fist, point, spread; null hands back to the move
  boss.onHit(cb), boss.on(event, cb), boss.off(event, cb)
  boss.fist(side, out), boss.fistR                               // a fist's middle and radius, for the fight's collisions
  boss.bellPoint(out), boss.bellR                                // the bell's middle and radius (where it can be hit)
  boss.stats                                                     // { tris, draws, cpuMs }: cpuMs is the last update's cost
  boss.dispose()

Moves (opts.speed runs a move faster, 1 by default, 1.4 for a harder fight; x and z aim it at a floor point, the player by default):
  idle                       the hover: a slow bob, the bell pulsing, tentacles flowing, arms drifting, fists flexing, sparks, blinks
  intro    {}                rises out of the pool, arms spread, shakes off the slime, bumps its fists with a spark burst (5.0 s)
  punch    {hand, x, z}      hand 'L', 'R' or the nearer: a wind-up (the arm draws back, the glove crackles), a fast straight strike
                             to the floor, the impact, recovery (2.0 s; it lands at 0.55 to 0.8)
  slam     {x, z}            both fists up high (the bell stretches, the eyes glow), then down together: a shockwave (2.7 s; lands ~1.0)
  sweep    {hand, dir, x, z} one arm sweeps an arc low across the floor through the target, an open glove, palm first (2.5 s)
  zap      {x, z}            the fists together, a ball of lightning grows between them, then a bolt to the target (2.9 s; fires 1.25)
  hurt     {x, z}            a flinch away from where the hit came from, a flash, a wobble, "> <" (1.15 s)
  stunned  {time}            sinks low, gloves flopped on the floor round it, dizzy spirals (the opening), then shakes it off (time + 2.3 s)
  taunt    {}                wags a finger, beckons with the other glove, a smug chuckle (2.8 s)
  defeat   {}                deflates and sinks into the pool in bubbles, and stays down until the intro plays again (4.2 s)

Events, cb({ move, ... }): start, windup, strike, hit ({ hand, x, y, z, r, ring, power }: the frame a fist lands, the slam's
shockwave, the zap's bolt; also to onHit), sweep (every frame of the sweep's low pass: { hand, x, y, z, r }, one object reused),
zap, recover, done, stunStart, stunEnd, introRise, introShake, introBump, introDone, defeated."""
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)


def apply(s):
    js = open(os.path.join(HERE, 'v311_conquest_boss.js')).read()
    # after the axolotl's runtime (the boss borrows its texture decoder), at module scope, where the game's look (HI, the outline width,
    # the ink colour, the toon ramp) is in place
    a = "// ---------- the axolotl in the game: the slime's stand-in"
    s = rep(s, a, js.rstrip('\n') + '\n' + a)
    return s
