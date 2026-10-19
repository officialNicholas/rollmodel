# v384: Paint Storm, Aftershock, and Swim faster in the rain

## What the game is about, and where each stroke sits

A match is two fights at once. One is for the floor: your colour is a fast lane that refills you, theirs slows you, and the result is
coverage. The other is for each other: a knock-out sends a rival back to a basin for a few seconds, which costs them both paint and
ground. Most of the fun is in the moments where the two meet: a pound that lands on a rival and splats a circle of your paint at the same
time, a fling into them, a rocket landing on their patch.

| Stroke | Kind | Mostly for | How it plays |
| --- | --- | --- | --- |
| Rocket | special | both, one big moment | Up, aim the mark, dive: a giant pound's splash where you choose. Skill shot. |
| Giant | special | both | 5 s huge and fast, paint never runs dry, roll into rivals to knock them out. |
| Flash Freeze | special | knock-outs, tempo | Every rival frozen 5 s; a perfect roll or a basin saves them. |
| **Paint Storm** (new) | special | coverage, with real threat | A storm of your paint follows you for 5 s and rains big splats; a drop on a rival knocks it out. |
| Swim faster | skill | movement | More pace on every glide; fast in the rain. |
| Weather Repel | skill | weather | Rain and heat do nothing to you; a fifth slower. |
| Deep Pockets | skill | items | Two transforms at once, and you keep the orb till you use it. |
| **Aftershock** (new) | skill | knock-downs, some coverage | Every pound lands twice: a second ring bursts out twice as wide. |
| Roller, Turret, Paint Trap, Whirlwind, Boomerang | transforms | mixed | Picked up or started with: stripes, shots, mines, a dash, a throw. |

The gaps were a special that **paints a lot while you keep playing** (the rocket and the freeze take you out of normal play, and the
giant changes how you move), and a skill that **changes how you fight** (the three skills are about speed, weather and inventory).

## Paint Storm (special, 600 dabs)

- From the orb, like the other specials. A cloud of your paint gathers over you and for 5 seconds hangs a little ahead of you, further
  ahead the faster you go, so you steer it by where you go.
- About 25 big drops fall in that time. Each lands like a small pound: a splat of your paint (radius 1.7) and a knock-out for any rival
  under it.
- A ring on the floor shows where each will land 0.6 s before it does. A rival can get out of the way, jump it, or roll through it, and
  anyone in a basin or up in a rocket is safe. About a third of the drops go looking for the rival nearest the storm.
- In a test match it added about 5.6% coverage on its own (a rocket's landing is about 2%), and caught a rival kept under it.
- It never blocks your view: from the play camera the cloud sits just above eye height at the top of the screen, and it keeps at least 7
  from the camera, so a sharp turn can't swing the camera into it. Its shadow on the floor shows the storm's area.
- CPUs get it from the orb now and then (as often as the freeze), hold it until someone's near, and on the receiving end sometimes roll
  out from under a drop (30% on easy, 50% medium, 75% hard).
- Offline only, as every special (the orb isn't in online matches).

## Aftershock (skill, 400 dabs)

- 0.3 s after your pound lands, the floor shivers, and a wall of your paint bursts out from the spot to twice the pound's reach (6 for a
  normal pound, capped at 7).
- A rival it catches on the ground is knocked off its feet, stunned for 1.4 s and spills a fifth of its paint. A jump or a roll gets
  you over it, and a giant shrugs it off. It doesn't knock out: the pound still does that.
- It leaves a ring of your paint where it stops.
- What it changes: the usual way out of a pound is a step back out of its circle. With Aftershock that step back is where the second hit
  lands, so the timing game around a pound gets a second beat.
- A giant's pound has its own quake, so no Aftershock there. Offline only, as the other skills.

## Swim faster in the rain

The rain used to double everyone's pace (anyone on Swim faster, and the CPUs). With a turn that only grew to 1.3x at speed, a fast roll
on a wet canvas ran wide and was hard to hold.

- The rain's speed-up is now 1.6x (was 2x).
- At that pace your turn tightens too (up to about 1.8x at full rain pace, was 1.3x), so the turning circle stays close to a dry one.
- The card now says "Much faster in the rain, with a sure grip on the wet".

## Pictures and the Strokes page

- Both pictures drawn flat by Ludo.ai in the same style as the others (solid colours, a thick navy outline, a cream sticker edge):
  `tools/assets/storm_flat_256.webp`, `shock_flat_256.webp`, made with `tools/v384_art.py`.
- The Paint Storm has its own 3D demo on the Strokes page: the cloud over the pad, drops falling onto their rings, one finding the rival.
- A fix that came up on the way: a long name over the demo window (Paint Storm, when it's the equipped one) was cut short on the page's
  first frame, before the name had a width to fit to. It now tries again once it does.
