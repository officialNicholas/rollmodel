# v319: the Jellyfish Boss's entrance, finished like a boss fight

![The charge, the stare over your shoulder, the roar with its screen effect, then the health bar](boss-intro-v319.jpg)

Once the boss is out of the pool, it now charges up, looks at you, and roars. The fight starts with the screen shaking, a screen effect, and then its health bar.

## The new end of the entrance

1. **It comes out of the pool**, as before: the pool churns, the gloves burst out and grab the curb, it hauls itself up and shoots up out of the slime.
2. **The charge (about 1.5 s):**
   - It turns a little away and brings its fists together in front of its bell, pressing them and trembling.
   - Sparks of energy stream in to its fists from all round. Its gloves crackle more and more, its eyes glow and its bell tightens and beats fast.
   - The camera comes round in front of it, low, looking up at it, and creeps in.
   - Then the energy breaks in a burst of sparks: a flash, a ring and a moment of the picture splitting.
3. **It looks at you (about 1.5 s):**
   - The camera cuts to over your shoulder, low, looking up into its face, and creeps closer.
   - It turns round to face you, lowers its fists and leans in, eyes narrowed. Its eyes catch the light once.
   - The water goes quiet: one deep heartbeat and a dark swell.
4. **It roars, and the fight starts:**
   - It rears back, then throws itself forward: arms flung wide, bell flared, tentacles whipping, slime and bubbles flying.
   - **The screen shakes** hard and the camera is knocked back.
   - **The screen effect:** a flash, speed lines rushing in toward it, a ring racing out and the edges flushed with its pink. On the hi graphics setting the picture also splits into colour and smears toward it. A shock ring races out over the floor.
5. **Then its health bar:** it drops in, its name stamps in, it fills with the boss's paint with a shine running along it, and it flashes when full. Then the countdown, as before.

It plays the same when the entrance plays again from the panel, and when the boss comes back up after a defeat.

## The fight's feel

- **When it knocks you:** a split-second freeze, a kick of the camera and a jolt of the colour split.
- **When it's hurt:** a split-second freeze.
- **A strike or a mine blowing near you:** a jolt of the colour split.
- **Low on health:** under 30% its bar pulses red.
- **Its defeat:** its last flinch plays in slow motion with a flash and the screen effect, and **Boss defeated!** stamps in over the middle with a win sting.

## Sounds

Made with Ludo and finished by `tools/boss_sfx_build.py`:

| When | Sound |
|---|---|
| The charge | A crackling power-up, swelling into the moment it breaks |
| The stare | One deep heartbeat (felt more than heard on a phone, which suits the hush) |
| The roar | A huge impact boom with a smash and a fizz, under the boss's roar |
| The bar filling | A thick paint gush ending in a sparkle |

## How it's made

- **Effect cost:** the screen effect is drawn only while it plays: one full-screen pass over the frame on both graphics settings. The colour split and the smear are in the hi setting's last pass.
- **Reduced motion:** there's no shake, speed lines, smear or split, just a softer flash.
