# Roll Model online play: the multiplayer server

This is how Roll Model is played against other people over the internet: a game server (in `server/`, running on
Fly.io) and a small piece of code in the game, the RMNet SDK (`server/client/rmnet.js`), that talks to it. Since v306
the game uses it for online duels (one against one); "In the game" below says how, and what is still off online.

## How it works

### Who decides what

Each phone moves its own blob, right away, so steering always feels instant. About 30 times a second the phone tells
the server where its blob is. The server is the referee: it checks every one of those reports and it alone decides
everything that wins or loses a match.

| The phone decides | The server decides |
|---|---|
| How its own blob moves (steering, hops, rolls, flings) | Whether that movement was possible (speed, walls, height, holes) |
| What the screen shows (paint trails, effects, sounds) | Knock-outs, flattenings, dodges, falls |
| | The paint meter, and whether there is enough paint for a pound |
| | Coverage (the score), by painting its own copy of the floor |
| | When pick-ups appear, who gets them, and whether a use is allowed |
| | The match clock, the weather, the Showdown's closing canvas, hearts, results and ratings |

### The rules of an online duel

The same as a versus match against the CPU, with the server keeping score:

- **The score** is the share of the canvas in your colour plus 2 points for each knock-out, as in the game.
- **A tie at the buzzer** plays on for 10 seconds, once; still level after that, it is a draw.
- **Pots stay where they are.** A pot that is drained or burst goes down for 4.6 seconds and comes back in the same
  place (offline, an empty pot moves to a new spot). A burst breaks the pot like a drain does.
- **After the match** both players have 30 seconds to ask for a rematch; when both do, a new match starts on a new
  canvas with the same rival. A player who left takes the rematch with them: the match closes at once.
- **Private rooms** keep a dropped player's place for 60 seconds (a phone that went to another app to send the code):
  the code still works, and the same device comes back into the room when it reconnects.

### How lag is hidden

- **Your own blob never waits for the network.** It moves on your phone at once.
- **Everyone else is drawn a moment in the past**, smoothly in between the positions the server sent. That moment
  (the interpolation delay) adapts to the connection: it covers the measured travel time of positions plus one
  snapshot gap, kept between 60 and 200 ms. If positions arrive late, a player keeps moving the way they were going for
  up to a quarter of a second, then waits; there are no wild jumps.
- **A hit that looked right on your screen counts.** When your pound lands, the server rewinds the other players to the
  moment you were seeing (never more than 200 ms back) and checks the distance there. The other side of fairness: a
  player who dodged in time on their own screen is safe, even if you saw them a moment before their roll.
- **Everyone starts together.** The phones keep a shared clock with the server (they time quick pings and trust the
  fastest ones) and the match starts at an agreed server time, so all players see "Go" within a few milliseconds of
  each other.
- **Small messages, sent at once.** Positions travel as compact binary messages (34 bytes up, 14 bytes plus 19 per
  player down) and the server turns off the network delay that bundles small messages together.

### How cheating is stopped

- **Moving.** Every report is checked against the game's own physics: the fastest you could be going (base speed, rain,
  your own colour, ramps, plus the boosts the server allowed for rolls, flings, pushes and pick-ups), the solid pieces of
  the stage (you cannot stand in or pass through them), and height (you can only be in the air as high and as long as a
  hop, fling or knock could carry you; there is no walking on air over a hole). Small timing wobbles even out; a real
  excess does not. A report that breaks the rules is refused and the player is put back where they last were legal.
  Repeat offenders are kicked and flagged in the database.
- **Actions.** Every pound, roll, fling, hop, pot dive and pick-up use is checked: cooldowns, paint, state, distance.
  The time a phone says something happened is accepted only within that phone's own measured delay, so nobody can
  claim "I rolled half a second ago".
- **Nothing important comes from the phone.** A phone cannot send a knock-out, a score, coverage, or anything on behalf
  of another player; the server ignores any such claim (the player is always the one the connection belongs to).
- **The map.** Every phone builds the stage from the seed the server picks, then sends it back. The server compares
  them all exactly; if anyone's stage differs (a modified game, or a bug), the match is called off and the honest
  players go straight back into the queue.
- **The connection.** Message sizes are capped, each connection has rate limits, every field is checked, and a phone
  that floods or sends garbage is disconnected. Private room codes cannot be guessed quickly.

## Measured in the tests

`npm test` runs all 63 tests on simulated networks and prints these numbers at the end. They come from one run on
a 4-core test machine that was also running all the bots (and other work at the same time), so a dedicated server
machine should do at least as well. They vary a little from run to run.

**Smooth and fair**

| What | Result |
|---|---|
| Network in the main sync test | 120 ms round trip, give or take 30 ms of random extra delay |
| Positions each phone receives | 30 a second |
| How far behind other players are drawn (the interpolation delay, picked by the SDK for the connection) | 155 ms |
| Where another player is drawn, against where they really were at that moment | half the time within 0.4 cm, 95% of the time within 1.6 cm, worst 5.6 cm |
| The same on a mobile-like network (delays now and then jumping to 120 to 250 ms) | 95% of the time within 2.4 cm, worst 46 cm (while a delay spike held positions up) |
| Frames where the SDK had to guess ahead because positions were late | 0.36% (mobile-like network: 4.1%) |
| Four phones starting a match | all within 4.2 ms of each other; the shared clock is within about 5 ms of the server's |
| A pound at 150 ms round trip | the attacker saw the target 2.74 m away (inside the 3.34 m reach) while it was really 3.73 m away: counted as a hit, after rewinding 159 ms |
| A clear miss; a roll 120 ms before the pound lands; a roll 250 ms after | no hit; safe; knocked out |

**Cheating**

| What | Result |
|---|---|
| Honest movement checked against the rules (many stages, every move, uneven frame rates, hitches) | 18,639 reports, none flagged |
| A speed hack of 1.25x, 1.5x, 3x | caught in 1.6 s, 0.8 s, 0.3 s |
| A 1.6x speed hack in a real match | put back every time, then kicked after about 5 seconds and flagged in the database |
| Everything else on the list | refused: teleporting, standing in or passing through solid pieces, flying, a pound during its cooldown or without paint, a pound landing claimed far from where the player was, fake knock-outs, acting as another player, claiming coverage, flooding, oversized or broken messages, an old game version, joining a private room without its code |

**Load on one server process**

| What | Result |
|---|---|
| Players | 400 bots playing at once (100 Showdown matches of 4) |
| Server work for each tick (a tick every 33 ms) | median 4.5 ms, 99% of ticks under 13.5 ms (processor time) |
| The same by the wall clock | median 8.9 ms, slowest 1% up to 25 ms (the bots and other programs were competing for the same processor) |
| Processor use | about 40% of one core |
| Memory | about 190 MB |
| Data from the server to each player | 3.2 KB a second (4.8 KB counting network headers), about 17 MB per hour of play |
| Data from each player to the server | 0.8 KB a second |
| Honest players wrongly put back | none |

Finding a match took 0.2 to 0.5 seconds once everyone was queued, and a phone that lost its connection was back in its
match half a second later (on a 60 ms network). The whole run took about four minutes.

## Running the server on your computer

You need Node.js 22 or newer.

```
cd server
npm install
npm start          # listens on port 8080; the game connects to ws://localhost:8080/ws
npm test           # the whole test suite, then the key numbers (about four minutes)
npm run test:quick # the same with a smaller load test
```

Check it is up: open `http://localhost:8080/health` in a browser.

Settings are environment variables:

| Setting | Default | What it does |
|---|---|---|
| `PORT` | 8080 | Port to listen on |
| `HOST` | 0.0.0.0 | Address to listen on |
| `DATA_FILE` | ./data/store.json | Where players and ratings are saved (`memory` keeps nothing): a snapshot, plus a journal of changes beside it (`.log`) folded in now and then |
| `LOG_LEVEL` | info | debug, info, warn, error or silent; logs are one JSON object per line |
| `ALLOWED_ORIGINS` | (any) | Web pages allowed to connect, comma separated; the iOS app's page is `rollmodel://localhost` |
| `MAX_CONNECTIONS` | 5000 | Connections at once |
| `MAX_PER_IP` | 64 | Connections from one address |
| `TRUST_PROXY` | 0 | 1 when behind a proxy that sets X-Forwarded-For |
| `SNAPSHOT_HZ` | 30 | Snapshots a second (20 saves about a third of the server's work and bandwidth) |
| `SHUTDOWN_GRACE_MS` | 3000 | How long a shutdown waits for connections to close |
| `MATCH_WORKERS` | 0 | Matches on worker threads: `auto` is one per core but the main thread's (which keeps the sockets and the lobby); 0 runs them on the main thread |
| `RULES` | | JSON to change match rules (for example `{"matchT":60}`); see `server/src/constants.js` |

Stopping the server (Ctrl+C, or a SIGTERM from the host) is graceful: running matches are called off without rating
changes, everyone is told, and the data file is saved.

## Where it runs: Fly.io

The live server is the Fly.io app `rollmodel-game` (in the personal organization, Nicholas Marcelin):

- **Address:** `https://rollmodel-game.fly.dev` (check it at `/health`); the game connects to
  `wss://rollmodel-game.fly.dev/ws`. The address is baked into the game from `tools/online_config.json`.
- **Machine:** one machine in Chicago (`ord`), always on (no stopping when idle, so the first player of the day does
  not wait for a cold start), with a 1 GB volume `rm_data` mounted at `/data` for the data file. From the deploy after
  the perf-network branch: performance-2x (two dedicated cores, 4 GB) with `MATCH_WORKERS=auto`, sized for 1,000 players
  at once (docs/net-scale.md); before it, shared-cpu-1x with 512 MB. A second region can come later.
- **Settings** live in `server/fly.toml`: `TRUST_PROXY=1` (the server reads the player's address from Fly's
  `Fly-Client-IP`), `DATA_FILE=/data/store.json`, and `RULES={"items":false}`, which keeps pick-ups off online until the
  game shows the server's pick-ups.
- **Deploying a new version:** `cd server && fly deploy`. Fly builds the image from `server/Dockerfile` and replaces the
  machine; a running match is called off without rating changes (the graceful stop above). From a network that
  inspects TLS (where Fly's remote builder cannot connect), build the image locally and deploy that instead:

  ```
  cd server
  docker build -t registry.fly.io/rollmodel-game:v2 .
  fly auth docker && docker push registry.fly.io/rollmodel-game:v2
  fly deploy --image registry.fly.io/rollmodel-game:v2 --ha=false
  ```
- **Watching it:** `fly logs -a rollmodel-game` (one JSON line per event: matches found, started and ended, violations,
  kicks) and `fly status -a rollmodel-game`.

## For the game: the SDK

`server/client/rmnet.js` is one file with no dependencies. The game uses classic scripts, so paste the whole file into
its own `<script>` before the game's script, leaving out the last line (the `export` line). It then provides
`window.RMNet`. All times are milliseconds on the server's clock (`serverNow()`); distances are metres; `yaw` uses the
game's convention (forward is `sin(yaw), cos(yaw)`).

### Connecting and the lobby

```js
const net = new RMNet({ url: 'wss://play.example.com/ws', name: 'Blobby', look: { hat: 'cap' }, token: localStorage.rmToken });
net.on('welcome', w => { localStorage.rmToken = w.token; });   // keep the device token: it is the player's account
await net.connect();                                            // resolves with the welcome; rejects if the game is too old
await net.queue('duel');                                        // 'duel' | 'trio' | 'ffa' (Showdown) | 'duo' (Showdown 2v2)
await net.cancelQueue();
const code = await net.createRoom('trio');                      // a private room: 5 letters and digits, no look-alikes
await net.joinRoom('K7PQX');                                    // rejects with code 'not_found', 'full', 'busy' or 'rate'
await net.leaveRoom();
net.ready(true);                                                // in a room: the match starts when everyone is ready
net.rematch(true);                                              // after a match: vote for a rematch (false: leave)
await net.setName('New name');                                  // returns the cleaned-up name
net.close();                                                    // leave for good (no reconnect)
```

The connection reconnects by itself (backing off from 0.4 s to 8 s) and, within 20 seconds of a drop, picks up the
match where it was (the `resume` event).

### The match

```js
net.on('matchFound', m => {
  // m: { matchId, mode, seed, opts: { mode, arena, players }, players: [{ slot, id, name, look, side, color, rating }],
  //      you (your slot), rated, room, layoutDeadline }
  // Build the stage from m.seed for m.opts.arena, then send it back:
  net.sendLayout(RMNet.layoutFromStage({ arena: ARENA, boxes: BOXES, ramps: RAMPS, holes: HOLES, pots: POTS,
    powers: POWER_SPOTS, spawns: [START, CSTART, CSTART2, CSTART3].slice(0, m.players.length), puddles: RIVALS }));
});
net.on('start', s => {
  // s: { matchId, startAt, endAt, countdown, layoutHash, spawns: [{ slot, x, y, z, yaw }], weather: [{ ph, at, dur }],
  //      zone: [{ at, warn, size }], rules, pots }
  // Put your blob at s.spawns[you]; it may not move until serverNow() >= startAt.
});
// every frame:
net.sendState({ x, y, z, yaw, spd, vy, air, rolling, charging, slam, hidden, flung, dry, missile, paint, aim });
const r = await net.action('pound');   // { ok, reason } once the server has ruled; undo the effect if ok is false
const p = net.remote(slot);            // another player, smoothed: { x, y, z, yaw, spd, vy, flags, paint, aim, extrapolated }
await net.leaveMatch();                // quit for good (during play it counts as a loss)
net.serverNow();                       // the shared clock
net.stats();                           // { rtt, minRtt, jitter, offset, interpDelay, snapshotsPerSec, corrections, ... }
```

`sendState` can be called every frame; it sends at most 30 a second and stamps each report with a sequence number and
the time. `remote(id)` takes a slot number or a player id, and an optional render time (by default `serverNow()` minus
the interpolation delay). `RMNet.FLAGS` names the bits of `flags`: AIR, ROLL, CHARGE, SLAM, HIDE, FLUNG, DRY, FLAT,
GIANT, WHIRL, MISSILE, KO, IMMUNE, OUT, AWAY, AFK.

### Actions

Call `net.action(type, data)` at the moment it happens. It sends the time and the moment the player was seeing, and
resolves with the server's ruling.

| type | when | data |
|---|---|---|
| `jump` | any hop up from the ground (also out of a pot) | |
| `roll` | a roll on the ground, or the air dash | |
| `fling` | the release of a fling (also the mid-air sling, and out of a pot) | `{ c }` the charge, 0.08 to 1 |
| `pound` | the pound button (bursts out if you are in a pot) | |
| `land` | the pound touches down | `{ x, y, z }` |
| `stomp` | you come down on a rival's head | `{ target }` its slot |
| `enterPot` | you dive into a pot | `{ pot }` its index in the layout |
| `exitPot` | you climb out | |
| `use` | you use what you are holding | |
| `selfKo` | you knocked yourself out | `{ reason }`: `dry`, `fall`, `zone` or `sun` |

### Events

`net.on(name, fn)` returns a function that unsubscribes.

| event | what it carries |
|---|---|
| `welcome` | `{ id, token, name, nameChanged, ratings, resume, serverTime, proto, modes }` (`resume`: the match to pick up, or null) |
| `queued`, `queueLeft`, `room`, `roomLeft` | lobby updates (`room`: `{ code, mode, host, need, inMatch, players: [{ id, name, look, ready }] }`) |
| `matchFound`, `start`, `resume` | see above; `resume` adds `self` (where you are and your state), `others`, `pots`, `cov`, `items` |
| `snapshot` | every snapshot: `{ seq, t, ack, players: [...] }` (`remote()` is usually all you need) |
| `correction` | `{ x, y, z, yaw, reason }`: move your blob there at once |
| `ko` | `{ slot, by, reason, x, y, z, respawnAt, hearts, out }` (reasons: pound, coffin, fall, zone, dry, sun) |
| `respawn` | `{ slot, pot, x, y, z, immuneUntil }`: that player is back, hidden in that pot |
| `flat` | `{ slot, by, x, y, z, until }`: flattened (yours: stop until then) |
| `push` | `{ slot, by, dx, dz, spd, vy, why }`: knocked back (yours: launch your blob that way) |
| `dodged` | `{ slot, by, how }`: roll, dash, immune, pot, air |
| `pot`, `potEject` | `{ i, occ, up, ink }` a pot's state; `{ slot, i, why }` someone thrown out of a pot |
| `coverage` | `{ sides, colors }` coverage percentages, four times a second |
| `act` | another player's action, for effects: `{ slot, a, ts }`; a pound landing is `{ a: 'slam', x, y, z, r }` |
| `itemSpawn`, `itemTaken`, `itemUsed`, `itemGone`, `itemTrap`, `unGiant` | pick-ups |
| `playerAway`, `playerBack`, `playerLeft`, `afk`, `out` | other players' connection and status |
| `matchEnd` | `{ reason, winner, results: [{ slot, id, name, side, coverage, sideCoverage, kos, deaths, place, left, rating }], rematchUntil }` |
| `rematch` | votes so far |
| `matchCancelled`, `matchClosed` | back to the lobby (or the room) |
| `kicked`, `error` | `{ reason }`; `{ code, message }` |
| `latency` | the same as `stats()`, now and then |
| `close`, `reconnecting` | the connection dropped; trying again |
| `open`, `token`, `fatal`, `actionResult`, `name` | the socket opened; the device token; a refusal that stops reconnecting (an old game version, a kick); every ruling on your actions; your cleaned-up name |

### The layout and its hash

The layout the game sends is
`{ arena, boxes: [[x0,x1,z0,z1,y0,y1,shape?]], ramps: [[x0,x1,z0,z1,axis,h0,h1]], holes: [[x0,x1,z0,z1,shape?]],
pots: [[x,y,z]], powers: [[x,y,z,kind?]], spawns: [[x,z,yaw]], puddles?: [[x,y,z]] }`, where shape `'c'` is a round
piece inside that square. `RMNet.layoutFromStage(...)` builds it from the game's own arrays (it moves a round hole's
`'c'` from the game's index 6 to index 4, and drops a box's extra kind). `puddles` (the game's `RIVALS`) is optional:
it lets the server know when a pound in boiling water really refilled you.

The canonical form is `RM1` followed by the JSON of `[arena, boxes, ramps, holes, pots, powers, spawns, puddles]` with
every number written as `Math.round(n * 100)` (so -0 becomes 0), a shape kept only when it is `'c'`, a power kind kept
only when it is a word, and `puddles` written as `[]` when there are none. `RMNet.layoutHash(layout)` hashes that into
16 hex digits. The server runs the very same code, and compares the full canonical text, not just the hash.

A check for any copy of this code: the layout

```js
{ arena: 26.4, boxes: [[-2, 2, -1, 1, 0, 1.5], [5, 7, 5, 7, 0, 2, 'c']], ramps: [[-6, -4, 0, 3, 'z', 0, 1.5]],
  holes: [[8, 10, -10, -8], [-12, -9, 6, 9, 'c']], pots: [[0, 1.5, 0]], powers: [[4, 0, -4, 'roller'], [-4, 0, 4]],
  spawns: [[0, -20, 0], [0, 20, Math.PI]], puddles: [[10, 0, 10]] }
```

has the canonical form
`RM1[2640,[[-200,200,-100,100,0,150],[500,700,500,700,0,200,"c"]],[[-600,-400,0,300,"z",0,150]],[[800,1000,-1000,-800],[-1200,-900,600,900,"c"]],[[0,150,0]],[[400,0,-400,"roller"],[-400,0,400]],[[0,-2000,0],[0,2000,314]],[[1000,0,1000]]]`
and the hash `746f9aef3f617241` (the unit tests check both).

### Messages on the wire

Text messages are JSON objects with a type `t`; frequent ones are binary.

From the game: `hello`, `queue`, `cancelQueue`, `createRoom`, `joinRoom`, `leaveRoom`, `ready`, `setName`, `layout`,
`act`, `rematch`, `leaveMatch`, `bye` (JSON), and binary STATE (34 bytes, about 30 a second), PING and SPONG
(9 bytes).

From the server: `welcome`, `error`, `kicked`, `queued`, `queueLeft`, `room`, `roomLeft`, `name`, `matchFound`,
`matchCancelled`, `start`, `resume`, `ack`, `act`, `correction`, `ko`, `respawn`, `out`, `flat`, `push`, `dodged`, `pot`,
`potEject`, `cov`, `itemSpawn`, `itemTaken`, `itemUsed`, `itemGone`, `itemTrap`, `unGiant`, `playerAway`, `playerBack`,
`playerLeft`, `afk`, `matchEnd`, `rematch`, `matchClosed`, `server` (JSON), and binary SNAP (14 bytes plus 19 per
player, 30 a second), PONG (17 bytes) and SPING (9 bytes). The exact byte layouts are written at the top of
`rmnet.js`.

## In the game (v306)

The online duel lives in three build modules: `tools/v306_accounts.py` (the username and the account),
`tools/v306_lobby.py` (finding a rival: the Matchmaking card, private rooms and friend invites) and
`tools/v306_match.py` (the match itself). What a player sees, with pictures, is in `docs/online-v306.md`. The match works
like this:

1. **The canvas.** When the server finds a match, both phones build the stage from the server's seed with the same fixed
   options (normal paint, none of the player's own canvas choices, the seven vote canvases) and send it back; the server
   compares them before the match can start.
2. **The start.** The versus card stays up until the server says when "Go" is, and the 3, 2, 1 lands on it on both
   phones. Each blob drops onto its spot (no basin intro online).
3. **Your blob** moves on your phone at once; every hop, roll, fling, pound, landing, stomp and pot dive goes to the
   server as it happens, and your position about 30 times a second. A move the server refuses is undone (a pot it did
   not let you into pops you out).
4. **Your rival** is drawn from the server's snapshots a moment in the past, with its trail, hops, rolls, flings and
   pounds, its name, colour (changed on your screen if it is the same as yours), eyes, wearables and rank.
5. **The server decides** knock-outs, flattenings, pushes, dodges, who is in which pot, pots going down and coming back,
   coverage (the bar shows the server's numbers), the clock, the weather (the server's schedule), overtime and the
   result. The game never knocks out, flattens, stuns or rams anyone itself online.
6. **Real time.** The server runs on real time, so online there is no hit-stop, slow motion or kill cam, and a slow
   frame catches up (up to a quarter of a second) instead of playing in slow motion as it does offline. Pause shows the
   menu while the match goes on; Leave match forfeits.
7. **After the match:** the usual tally and winner screen, then Rematch (both have to say yes) or Menu.

Off online for now: pick-ups (the server can hand them out, but the game does not show the server's yet), orbs and the
special strokes that come from them, rare finds and gifts, the Swim faster start boost, the easier paint drain of easy
mode, rams and roll stuns between players, and pots moving to new spots.

## Decisions needed before going live

1. **Pound on a hidden player.** The spec for this work says a player hidden in a pot is safe from a pound, and that is
   how the server is set. The single-player game does the opposite: a pound on an occupied pot knocks the player out
   ("Nailed!"). Pick one; it is one setting (`potShields`).
2. **Hosting and regions.** Decided: Fly.io, one machine in Chicago (see "Where it runs" above), a few dollars a month.
   One server process handles several hundred players on one processor core (see the load test above). When players
   come from far away, add a machine in a second region (for example Europe) and send each player to the closest.
3. **A domain and a TLS certificate.** Done for now: Fly gives `rollmodel-game.fly.dev` with a certificate. A domain of
   your own can point at it later.
4. **Accounts.** Today a player is a device token: lose the phone or reinstall, lose the rating. Before ranked play
   matters, link it to a real account: Sign in with Apple (required by the App Store if any other sign-in is offered)
   and possibly Game Center. That needs an Apple developer setup and server-side token checks.
   Since v305 every player also has a Supabase account for friends (anonymous at first; see `supabase/README.md`), and
   since v306 a username and a real account (username and password) are needed to play online. The next step is for
   the game server to accept that account's token in `hello` in place of its own device token, so ratings, friends and
   invites to private rooms all hang off one identity, and logging in on a new phone brings your rating along.
5. **Privacy policy and terms.** Online play stores a device token, a display name, ratings, match records and IP
   addresses in logs, and flags suspected cheating. The App Store privacy labels, the privacy policy and the terms need
   to say so, including how long things are kept and how to ask for deletion.
6. **Name moderation.** Names are cleaned and a small list of bad words is refused. Before launch, decide on a bigger
   list (or a moderation service), a report button, and what happens to reported players.
7. **Analytics.** What to measure (round trips by region, match length, abandon rate, cheat flags), where it goes, and
   whether players must agree first.

## Next steps

- **A faster lane than WebSocket.** WebSocket runs over TCP, so one lost packet holds up everything behind it for a
  round trip (the tests model this as delay spikes). Positions should move to an unreliable channel: WebRTC data
  channels or WebTransport on the web, or the native UDP plan in `docs/online-plan.md`, keeping WebSocket for the rest.
- **Full server-side simulation.** Today the server checks movement against the game's physics; it does not run them.
  Running the same simulation on the server (with input replay on the phone) would close the last gaps, such as small
  speed-ups within the tolerance, and would let the server move blobs for knock-backs itself.
- **Server bots to fill matches** when the queue is quiet, using the same rules as the game's CPU rivals.
- **Porting the level generator** to the server, so the server builds the stage itself instead of comparing what the
  phones send (one less message, and a faster start).
- **The other bumps between players.** Pounds, stomps and pot bursts are refereed. The game's rams, roll stuns and
  shoves still need the same treatment (the player who hits sends a claim, the server checks it with the same
  rewind), as do turret shots and the whirlwind's splats. Turret shots carry a rule since v304: three hits in a row from one
  turret stun for 1.5 s, so the referee has to count the run of hits per target (a miss or half a second without a hit breaks it).
- **Puddles that come and go, and moving pots**, if the online game keeps them, need their timings from the server.
- **The rocket pick-up.** Online, the server hands out the roller, whirlwind, turret, trap, free slam and giant. The
  rocket (straight up over the canvas, steer, then dive) is not handed out yet: the referee needs to know its flight
  first, or it would look like flying.
