# Season Conquest: the Jellyfish Boss level (design, draft 2)

This draft follows the user's notes on draft 1:
- No painting tiles in place to keep them up. Puzzles use the moves and strokes we already have: the turret's shots, the pound, the basins, the fling, and the other strokes.
- Everything is outdoors, in one sunken ruin you keep moving through. No interiors.
- At its heart it stays a game about paint, getting around, and using your strokes to fight.
- The reward is a stroke you can only get here: **Brood**, where you split into copies of yourself. It comes from the boss, which can make baby copies of itself.
- The boss's health goes down a little all the time, the way Cuphead's steady fire chips a boss, but through painting rather than a new shooting mechanic.
- Everyone can finish it: new players struggle, normal players get through with some effort, and players who have mastered the game find shortcuts and finish much faster.

## The core loops

### 1. Chip damage: cover its slime
The boss is a painter too. As it swims low its tentacles drag over the ground and leave **purple slime trails**, and its slime is what it lives on: it feeds on it, and the slime keeps it strong.
- **Covering its slime with your paint drains it.** Every purple cell you roll over or splat turns to your colour and takes a sliver off its health. The jelly flinches, and a thread of its purple is pulled up out of the ground and into you.
- This is the regular game's rule, your colour against a rival's, with the boss as the rival. Nothing new to learn.
- New players cover some slime just by running the course.
- Good players go out of their way to cover the trails and the jellets' purple.
- Experts cover a whole trail in one stroke: a roller stripe along it, a boomerang loop, a rocket splash on a fresh puddle, or a whirlwind straight down it.
- The boss keeps laying slime in every section, runners included, so it always leaves you something to take back, and it dives and comes up elsewhere to lay more.
- Its slime is also a hazard: like a rival's paint it slows you, so uncovered slime makes the runners harder.

### 2. Minions are its babies
- **Jellets:** the boss sheds small simplified copies of itself. They float low, paint the ground purple and sting you on touch.
- **Popping them:** a pound, a ram while giant, a roller, a boomerang, a trap or a whirlwind pops them.
- **Each pop sends a spark back** into the boss and chips it. That puts a second steady source of damage into the fights.

### 3. The big hits come from set pieces
- Each fight has a set piece that knocks off a big piece of health. The set pieces are built from the strokes and moves you already have.
- The health split:
  - **Chip damage** is up to about 35% for a great player, and about 10% for a new one.
  - **The two midway set pieces** are 20% each.
  - **The final fight** takes the rest.
- So the more you chip, the shorter the final fight is. That is where mastery saves the most time.

### 4. Basins under pressure
- On a runner you never roll back over your own colour, so your paint keeps running down.
- Basins along the route refill you, but a dip costs about 1 second, and you take it while the world falls apart around you.
- If you skip a basin you run dry, crawl, and the collapse catches you.
- Experts chain flings and dashes to reach basins that are off the safe line, or carry enough paint to skip one.

### 5. Verticality and shortcuts
- **Cracked slabs:** pound them to drop to the level below. Below are faster channels, shortcuts and hidden basins.
- **Turret pillars:** stone pillars on clam valves. Plant the turret near one, and its paint shots fill the valve and raise the pillar. Each raised pillar is a step up or a bridge.
- **Fling gaps:** a slingshot ring sits at every big gap, and there is a slower way round for anyone who misses.
- **Stroke skips:** a rocket hop over a whole loop, a giant smashing a barricade, a whirlwind dash across a span that is falling.
- Every shortcut is optional. The safe way is always there and is slower.

## Camera, world and checkpoints

- **The camera:** always the normal chase camera behind you, with only the zoom changing (pulled back on runners, pushed in for close moments).
- **The boss in view:** it swims in front of you, above you or to the side, and dives under the course and out of shot. Bubbles, a rumble and fresh slime seeping up through the stones warn you before it comes back up.
- **One open place:** a single sunken city on the edge of a trench, outdoors the whole way. From the start you can already see the Reef Crown, a ruined tower on the horizon, and it gets bigger as you go.
  - The world loads in pieces, but the next piece is always visible before you reach it, so you never cut to a loading screen.
  - The ground keeps rising and the light gets brighter as you near the top.
- **Checkpoints:** a lantern buoy lights up in your colour as you pass. Lives go back to 3 at each one, and the boss keeps the damage you've done.
- **Help for anyone who fails a checkpoint 3 times:** a spare life, and the shortcuts' slow ways get extra glow so they're easier to find.

## The route (about 8:30 a normal run, 5 to 6 minutes for experts)

```
 [0 The Keep pool]  the reveal, it flees toward the camera, you turn and chase
       |
 ==1 Aqueduct Run==  the arches fall in behind you; basins; pound down into the channel
       |
 [2 Sunken Plaza]    jellet waves; turret pillars up to its bell               20%
       |
 ==3 Coral Canyon==  upper ledge or lower floor; boomerang gate; giant smash
       |
 [4 Amphitheatre]    stepped rings; traps under its slam; rocket dive          20%
       |
 [5 The Reef Crown]  the plateau breaks into the trench; it splits into copies   the rest
```

### 0. The Keep pool (about 30 s)
1. The existing entrance plays. The boss looks at you, rises fast and swims off up the far causeway, toward the camera in the top-down sketch.
2. As it goes, it slams the floor once. The shock ring teaches you to jump.
3. Your hero pulls the determined face and turns, and you have control at once.
4. **Checkpoint.**

### 1. The Aqueduct Run (about 75 s)
- **The course:** a ruined aqueduct, the arches falling in **behind** you. That keeps your heart racing without needing any special trick.
- **The boss** swims off to one side and keeps attacking:
  - It slams the arch ahead, and a purple glow on the stone marks the spot 1 second before.
  - It drops jellets in your lane.
  - It dives under the arches and comes up through the far side.
- **Basins** sit on little ledges. Some are on the line you are running, and some are off it, so you have to fling or dash to reach them.
- **Cracked slabs** halfway along: pound one and you drop into the water channel under the arches. That is the faster way, with a current that pushes you on, but the openings are narrow.
- **Checkpoint** at the mid-arch.

### 2. The Sunken Plaza (about 100 s, 20%)
A square, open-air plaza built like a regular stage, with boxes, ramps and pots, ringed by broken columns.
- **Jellet waves:** the boss circles overhead and lets go three waves of jellets. Some in the later waves are armoured, so it takes a pound to crack the shell before the second hit pops them.
- **The turret:** you get it from a pick-up after wave 2.
- **The set piece:**
  1. After wave 3 the boss sinks low over the middle of the plaza to feed on its purple paint.
  2. Four clam valves stand round it. Plant the turret so its shots fill the valves, and each valve raises a pillar. One turret can reach two valves from a good spot, if you know where to plant it.
  3. Climb the raised pillars and jump onto its bell, then pound it 3 times: 20%.
- **The alternative:** the slingshot ring by the fountain launches you straight onto the bell, but only if you aim it well.
- **Checkpoint.**

### 3. Coral Canyon (about 75 s)
- **The course:** a reef canyon with two levels:
  - **The upper ledge** is narrow and fast, and the boss punches at it.
  - **The canyon floor** is reached by pounding a cracked slab. It is wider and safer, and has basins, but it is longer.
- **The boomerang gate:** a coral gate shuts across both levels. Throw a boomerang so its loop hits both switch shells and the gate opens. A boomerang pick-up waits just before the gate. With a good throw you open it without slowing down.
- **The barricade:** a giant orb sits before a rubble barricade. As a giant you smash straight through it. Anyone else has to go round by the side cave.
- **The collapsing span:** a whirlwind dash carries you across before it falls. Without one, you jump the pieces as they drop.
- **Checkpoint.**

### 4. The Amphitheatre (about 100 s, 20%)
An outdoor ruined amphitheatre, with stepped rings around a round stage. You can jump up and down between the rings.
- **The fight:** the boss comes down onto the stage. Its moves are Punch, Slam, Sweep, Slime rain and Shock wave, mixed with jellets.
- **The set piece:**
  1. Paint Traps spawn on the rings. Set one where its Slam is about to land. The slam's ring shows 1 second ahead, so you need to read and move.
  2. The trap goes off under its fist and stuns it.
  3. Climb to the top ring, take the rocket orb and dive onto its bell: 20%.
  4. It happens twice if your chip damage was low, and once if it was high.
- **The freeze orb** shows up in the jellet waves. Flash Freeze stops them, and with a good run you have time to clear them all.
- **Checkpoint.**

### 5. The Reef Crown (about 2 min, the rest)
The ruined tower's plateau on the edge of the trench, open water all round.
- **Phase 1:** every move is back. **Pieces of the plateau break away into the trench** as it goes, and the basins at the edge are at risk. You have to refill and fight at the same time.
- **Phase 2:** below 30% it **splits into many copies of itself**. Only the real one **leaves slime** as it swims; the copies are dry. Follow the fresh trail, cover it to chip it, then pound or fling into the real one.
  - Each hit on the real one breaks up the copies for a few seconds.
  - Hitting a copy only pops it, and pops send a spark of chip damage back to the real one.
- **The finish:** a slow-motion fling into the last of its health.
- The boss shrinks to a jellet, sulks and leaves its power behind. You take it: **Brood unlocked**.
- **Checkpoints** at the start and at the split.

## The reward: Brood (a special stroke)

You split into three for 6 seconds: yourself and two jelly-tinted copies at your sides. They use simplified meshes, the same lighter versions as distant characters.
- **The copies follow your steering in formation,** so you paint three lanes at once.
- **When you pound,** every copy pounds too, each with a smaller splat.
- **A copy that gets hit pops harmlessly,** and you are not knocked out.
- **Getting it:** you earn it the first time you clear the Conquest. From then on you can pick it in Strokes like the other strokes, in every mode.

## Skill and speed

- **New players:** they learn the level through checkpoints, the safe routes and the spare lives.
- **Normal players:** they take the safe line with a few shortcuts. That is about 8 to 9 minutes.
- **Experts:** pound-drops, fling skips and stroke skips, covering trails in one stroke, and chaining pops all save time. That is about 5 to 6 minutes.
- **Results screen:** the time, the chip %, lives lost and the shortcuts found, with a medal for each.
- **A leaderboard for the fastest clear** could reuse the weekly Time Trial board.

## With a friend online

- **Shared and separate:** you share the boss's health, the chip damage and the checkpoints. Each player has their own lives and camera.
- **Down, not out:** a player who is out floats as a bubble for 8 seconds, and the partner rolls through it to bring them back.
- **Splitting the work:**
  - One player plants the turret on the valves while the other pops jellets.
  - Each player can take a different route through the canyon.
- **Fair to both:** the boss picks a target for each move and switches between players.
- **How it runs online:** the boss and the hazards follow a script from the shared seed, so both phones play the same boss. The server referees the section you are in, the damage, the pops and the lives.
  - That needs a new co-op mode on the server, and the lead deploys it.
  - Solo comes first.

## The build plan

| Module | What it adds |
|---|---|
| cq02 | The level frame: the open world loading in pieces, the sections, the checkpoints, the lives, and the chip damage from covering its slime. |
| cq03 | The opening chase and the Aqueduct Run: the collapse behind you, the basins on runners, and pounding through cracked slabs. |
| cq04 | Jellets: the simplified boss mesh, popping, and the spark back to the boss. |
| cq05 | The Sunken Plaza: the waves, and the turret valves and pillars. |
| cq06 | Coral Canyon: two levels, the boomerang gate, the giant barricade and the whirlwind span. |
| cq07 | The Amphitheatre: traps under the slam, the rocket dive. |
| cq08 | The Reef Crown: the breaking plateau and the split, with the real one giving itself away by its trail. |
| cq09 | Brood: the stroke, unlocked on clearing. |
| cq10 | The results, the medals and the tuning. |

**First playable milestone:** the opening, the Aqueduct Run and the Sunken Plaza, with the slime trails and the chip damage working. That is about 3.5 minutes and is enough to judge the feel.
