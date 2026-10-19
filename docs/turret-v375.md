# v375: the turret stays where you point it, and its shots land

![Two moments with a turret, each as v374 then v375, on an iPhone. In v374 the whole view has swung round toward the rival and the shots paint the floor. In v375 the view stays where you steered, the turret's head turns toward the rival, its shots go to them, and the ring sits on them](turret-v375.jpg)

## What was wrong

- **It moved by itself.** A rival anywhere within about 43 degrees of where you faced pulled you round at up to 137 degrees a
  second. It fought your steering, and the camera, which follows where you face, swung with it. In the tests that was 25 to 35
  degrees a second of turning you didn't ask for.
- **It missed.** Its shots only went for a rival within 26 degrees, so between 26 and 43 it pulled you round but still painted the
  floor. Its lead came from the way the rival faced and their top speed, not where they were really going. It also guessed a flight
  time that wasn't the time its lob really took, and that lob was high and slow (about 0.9 s to 9 units), long enough for a rival to
  turn away.

## What it does now

- Only your steering turns you and the camera.
- A rival within 34 degrees of where you face, on your screen, in reach and in sight, gets locked onto: a little buzz, and the ring
  jumps onto them. The turret's head swings round to them, up to 52 degrees either side.
- The lock holds while they stay within 52 degrees, in reach and on screen or just past its edge. A moment off screen or behind a
  wall doesn't break it, so it doesn't flick between rivals.
- Its shots lead the rival by where they're really going (their movement over the last moments, and their fall if they're in the air).
  The lead uses the flight time of the shot it actually fires. That shot is a low, quick arc when nothing's in the way, and the old
  high lob when a wall is.
- With no lock, the shots go straight ahead, near to far and back along a lane, and the ring stays still in the middle of it.
- CPU turrets are unchanged. Items are off online, so this is for offline matches.

## Tested

- Steering at a rival circling you on the Manor, 6 runs: you and the camera turn 0 degrees a second on their own (v374: 25 to 35).
  About 92% of locked-on shots hit (50 or 51 of 55 in 5 of the 6 runs).
- Aiming at a CPU rival that dodges and runs: 34 to 38% of shots hit (v374: about 20%).
- Hands off the stick, it no longer chases a rival round for you, so it hits less that way. That's on purpose.
- CPU turrets against you: v374 339 shots and 255 hits, v375 330 and 299, within the runs' usual spread (the CPU code didn't change).
