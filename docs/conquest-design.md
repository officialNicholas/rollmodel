# Season Conquest: the Jellyfish Boss level (design draft)

The aim: one level of about 7 to 9 minutes, played alone or with one online friend. It mixes a little story with runner chases, arena fights against minions, light puzzles and a final fight. You wear the boss down over the whole level, and there is a checkpoint at every section.

## Ground rules from the game as it is

- **The camera stays the normal play camera.** It is the chase cam behind you that turns as you turn. We only change its zoom: pulled back in the runners so you can see further ahead, and pushed in for close moments. No section ever takes the camera away from you. The story moments happen in front of the camera while you keep control. The one exception is the opening reveal, which already exists.
- **You already move forward all the time.** You drag to steer, tap to jump, swipe up to roll or dash, pull back to fling, and press the arrow to pound. A runner section is the normal game in a long corridor, so there are no new controls to learn.
- **The boss lives in the air.** It swims above and around the course, so you see it ahead of you, above you or off to one side. It dives under the stage and out of frame while you deal with something else, then comes back up somewhere new. Its shadow on the floor, bubbles rising through grates and a rumble always warn you before it comes back up.
- **Damage comes from your verbs.** The current demo has no way for the player to hurt the boss. In the level, the boss loses health only when you do something to it: pound it, fling into it, paint it, or land a trap or harpoon on it.
- **Lives:** 3 per checkpoint, and you are back to 3 at each one. A hit from the boss costs one life, as in the demo. Falling into a gap also costs one. When you lose your last life, you go back to the last checkpoint. The boss keeps any damage you have already done.

## The map

The layout follows your sketch: the arena where the boss is revealed at the top, and the runner leading away from it. After the turn-around, "towards the camera" in your top-down sketch becomes "straight ahead" for the player.

```
   [ Keep arena ]  0 Prologue: the reveal, the boss grabs the cage and flees
        |
   ====runner====  1 The Collapse (the floor falls away)
        |
   [  square   ]   2 Minion Yard (minions, then the harpoons)            25%
        |
   ====runner====  3 The Broken Causeway (punches, split lanes, a fling gap)
        |
   [  square   ]   4 Lantern Hall (a dark room, a paint puzzle, the boss under the floor)  25%
        |
   ====ramp======  5 The Rising Tide (climb ahead of the water)
        |
   [ Crown ring ]  6 The Crown (the final fight, two damage cycles)      50%
```

Each `|` is a checkpoint gate: a lantern buoy that lights up in your colour as you pass it.

## Story in four short beats

1. **Reveal** (the existing entrance): the boss rises from the pool, charges up and roars. Then it snatches the hanging cage with your little buddy inside (the Keep already has cages hanging in it). It pounds the floor, which knocks you back, and flies off fast, up and toward the camera.
2. **The turn:** the camera pushes in on your hero. The hero shows the determined face (a new mood for the face system), turns around and starts the chase. It takes 2 seconds, and you have control the moment the hero turns.
3. **Halfway (in Lantern Hall):** the lights go out. The boss's eyes and the swinging cage are the only light in the room, and you hear the buddy calling from somewhere in the dark.
4. **The end:** the boss is beaten, sulks and drops the cage. The buddy pops out and joins your victory pose, and the stamp reads "Boss defeated!"

No text boxes. Everything is shown with action, faces and sound.

## The sections

### 0. Prologue, in the Keep arena (about 30 s)
The existing reveal plays, then the cage grab and the flight. Before you run, you get a 5 second warm-up dodge: the boss slams the floor once on its way out, and the shock ring teaches you to jump. Then comes the turn beat. **Checkpoint 0.**

### 1. The Collapse (runner, about 75 s)
- **The course:** a stone causeway about 10 m wide, about 400 m long, with water far below.
- **Collapsing tiles:** they crack (shaking, and a crack line in the stone) 1.2 s before they drop. **Painted tiles hold twice as long**, so painting ahead of you buys time. This is the first idea that ties painting to survival.
- **Gaps:** jump over them. Later gaps have a ramp that rewards a jump at the right moment.
- **The boss** swims ahead and above. Every 8 to 10 s it turns and does something to you:
  - spits slime blobs that land in your path (the existing Slime rain);
  - punches the causeway from the side, which tilts a section;
  - dives under, then comes up through the floor ahead (its shadow and bubbles warn you). That tears a hole you have to steer around.
- **A mid-gate** about 40 s in. **Checkpoint 1a.**

### 2. Minion Yard (square arena, about 100 s, boss down 25%)
A regular-size square stage (about 26 m half-size), built like the normal stages with boxes, ramps and pots. The boss circles overhead and throws in minions in three waves:
- **Jellets:** small jellyfish that drift after you and paint the floor purple. One pound pops them, and your paint dries them out.
- **Puffers:** they swell when you get close and burst after 2 s, knocking you back. Roll through them before they burst, or fling them into other minions.
- **Shell crabs:** a shell in front protects them from pounds. Roll into them to flip them over, then pound them.

The damage moment comes after wave 3. Four harpoon cannons stand at the corners, and each sits on a round pad. **Paint a pad fully to arm its cannon.** Once all four are armed, they fire chain nets at the boss and pin it to the floor in the middle. Its bell glows: **pound it 3 times** before it breaks free (8 s). That takes off 25%. Then it tears loose and flies on. **Checkpoint 2.**

### 3. The Broken Causeway (runner, about 75 s)
- **Fist slams:** the boss runs alongside and punches the bridge ahead. Each punch sends a shock ring along the bridge, which you jump.
- **Split lanes:** the bridge splits into two or three lanes. One lane is lit and the others crack and fall, so you read and pick.
- **A big gap:** a slingshot pad (a glowing ring) in front of it. Pull back, aim and fling across it. This teaches the fling, which the final fight needs.
- **Under the stage:** the boss swims below, visible through grates and as a moving shadow, then bursts up on one side in a sweep. Its tentacle sweep comes along the floor, and you roll or jump it.
- **A mid-gate. Checkpoint 3a.**

### 4. Lantern Hall (square arena, a puzzle, about 110 s, boss down 25%)
- **Dark:** the boss puts out the lights and hides under the floor, so the room is dark. Your paint glows faintly, and the room lights up only where you have painted.
- **The puzzle:** four lanterns stand on the walls. **Paint an unbroken line from a pot to a lantern** to light it. Paint conducts the light like a wire, so your line has to go round the holes and boxes.
- **Pressure:** eels come out of holes and bite your paint lines apart, so you can repair or block them.
- **The boss** shows only as a shadow under the floor, bumping the floor up under you now and then.
- **Damage:** when all four lanterns are lit, the light reveals the boss under a big grate in the middle. It surfaces, dazed. **Fling into it** (your homing missile, or just the hit), then pound. That takes off 25%. **Checkpoint 4.**

### 5. The Rising Tide (ramp runner, about 60 s)
- **The climb:** a wide spiral ramp up the outside of the keep's tower. The tide rises behind you and the camera pulls back so you can see it chasing.
- **From above:** the boss drops rubble from overhead, and each piece has a red ring on the ground where it will land.
- **Pick-ups:** rocket and giant orbs appear here. Giant smashes through barricades and the rocket skips a whole loop, so the strokes you already know pay off.
- **Checkpoint 5** at the top.

### 6. The Crown (the final fight, about 2 min, the last 50%)
A round arena at the top of the tower, open to the sky. The existing moves all come back, mixed: Punch, Slam, Sweep, Zap, Slime rain, Shock wave, Ripples, Strikes and Sea mines. The damage loop runs twice:
1. After a **Slam**, its fists stick in the floor for 4 s.
2. **Roll circles round a fist** to paint it. Once a fist is fully painted it's stuck, and when both are, the boss is stuck and dizzy.
3. **Fling into its bell** from a slingshot ring, then **pound it.** That takes off 25%.

**Last stand** below 15%: the edge of the arena starts to fall in, closing like the Showdown line, and the boss speeds up. The killing blow is a slow-motion fling. **Checkpoint 6a** after the first cycle.

## Timing

| Section | Clean run | With a few deaths |
|---|---|---|
| 0 Prologue | 0:30 | 0:30 |
| 1 The Collapse | 1:15 | 1:45 |
| 2 Minion Yard | 1:40 | 2:15 |
| 3 The Broken Causeway | 1:15 | 1:45 |
| 4 Lantern Hall | 1:50 | 2:30 |
| 5 The Rising Tide | 1:00 | 1:20 |
| 6 The Crown | 2:00 | 3:00 |
| **Total** | **about 9:30** | **about 13** |

That is a little long. To land at 7 to 9 minutes, the runners can each lose 15 s, or section 5 can be cut, since it is the easiest to drop.

## With an online friend

- **Shared and separate:** both players are on the same course, and each has their own normal camera. You share the boss's health and the checkpoints. Each player has their own lives.
- **Down, not out:** a player who loses their last life floats as a bubble for 8 s, and the partner rolls through the bubble to bring them back. If nobody does, the player comes back at the next gate the partner passes. You go back to the checkpoint only when both are down.
- **Two-player puzzles:**
  - Harpoon pads fill twice as fast with two players painting.
  - In Lantern Hall, two lanterns need lines lit at the same moment.
  - In the Crown, each player can take a fist.
  - Solo play gets longer timers instead.
- **Boss focus:** the boss picks a target for each move and switches between players, so neither gets ignored.
- **How it runs online:** the boss and the hazards follow a fixed script from a shared seed and the section's clock. Both phones play the same boss without streaming it, and the server referees only:
  - which section you are in, and the checkpoints;
  - boss damage;
  - minion KOs;
  - lives.

  This builds on the existing duel server, which already referees KOs, hearts and the clock. It still needs new work on the server: a co-op match mode, minions as server entities, and boss damage events. The lead session has to deploy that. Solo comes first, and co-op follows once solo is fun.

## How I'd build it (modules on top of the current game)

| Module | What it adds |
|---|---|
| cq02 level frame | A sequencer for the sections, checkpoint gates, lives per checkpoint, and the world built as one chain of pieces, with only the nearby pieces drawn. |
| cq03 prologue | The cage grab, the flight away, the determined face and the turn. |
| cq04 runner kit | Collapsing tiles that hold longer when painted, gaps, the boss's runner attacks, and the zoom for runners. |
| cq05 minions | Jellets, puffers and shell crabs. |
| cq06 Minion Yard | The arena, the waves, the harpoon pads, and the pin-and-pound. |
| cq07, cq08 | The Broken Causeway, and Lantern Hall (the paint-circuit puzzle and the dark). |
| cq09 | The Rising Tide, and the Crown fight's damage loop. |
| cq10 | The ending, the reward, and tuning. |
| later | Online co-op, which needs the lead and the server. |

**First playable milestone:** sections 0, 1 and 2 (about 3.5 minutes) in the preview. That is enough to judge whether the runner and the arena feel good before building the rest.
