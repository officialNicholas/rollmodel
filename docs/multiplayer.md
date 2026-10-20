# Roll Model online play: the multiplayer server

This is how Roll Model is played against other people over the internet: a game server (in `server/`, running on
Fly.io) and a small piece of code in the game, the RMNet SDK (`server/client/rmnet.js`), that talks to it. Since v306
the game uses it for online duels (one against one), and since v391 for Showdown with real people (everyone for
themselves, three or four of you, or two teams of two), parties of friends, and matchmaking that looks near you first
(made around v312, brought onto the game in v391); "In the game" below says how, and what is still off online.

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
- **Private rooms** (the v306 to v311 games; v312 plays with friends through parties instead) keep a dropped player's
  place for 60 seconds: the code still works, and the same device comes back into the room when it reconnects.

### The rules of an online Showdown

The same as a Showdown against the CPU, with the server keeping score:

- **Three hearts each** (the server's `hearts` setting; the game's own Showdown has three since v309). A knock-out
  costs a heart; with none left you are out. Paint is fuel, not points.
- **The closing canvas.** The safe square shrinks at 60 and 120 seconds, with a warning 15 seconds before each; out past
  the line your paint burns off, and with none left you are knocked out. The game draws the line on the server's clock.
- **The end.** The last one standing wins (in 2v2, the last pair: a team is out only when both are). If the 3 minutes
  run out first, the most hearts left wins, then the most knock-outs. The places follow: everyone still in, then the
  others in the order they went out.
- **Out of it,** you watch the rest, or leave. Leaving once you are out keeps the place you went out in; leaving while
  still in it counts as last.
- **Free-for-all** is four players, or three when a fourth hasn't turned up after 20 seconds. **2v2** is four: a party
  of two is one team (a party plays a party when there is one); four players on their own are split, the best and the
  worst against the two in the middle.
- **Rated** when matchmaking made it. A party's own match (a party of two in Versus, a party of four in either
  Showdown) is not, and neither is a Showdown of three that turned out to be just one party.
- **After the match** everyone has 30 seconds to ask for a rematch; it needs all of them.

### Parties

A party is up to four friends in one lobby who play together. The game server keeps it.

- **Making one and joining.** Whoever makes a party leads it. A party has an 8-character join code that nobody types:
  it travels inside an invite, and wrong codes are rate limited like room codes. A player joining a party leaves the
  one they were in, and their own place in the queue.
- **Leaving.** Anyone can leave; the lead passes to whoever has been in the party longest, and the last one out closes
  it. The leader can remove someone; a removed player can only come back with a new invite.
- **What each member shows the others:** their username, their look (paint colour, eyes, wearables, rank), whether
  they are ready, their mode vote, and what they are busy with in their own game (the locker, the shop, Strokes,
  Settings, a match against the CPU), or that their connection is away.
- **Ready.** Being busy, or changing your look, un-readies you, and so does a change of mode. When everyone is ready
  the party has 1.5 seconds to back out, then plays: a party of two plays a private duel (unrated); a mode that needs
  more players goes into matchmaking as one ticket. Anyone un-readying (or busy, or dropping) takes the party out of
  the queue.
- **The leader picks the mode** (v392). The modes that fit the party's size: Versus (1v1) for one or two,
  Showdown free-for-all for one to four, 2v2 for one, two or four (a party stays on one team, so not three). The game
  has the others ready up and wait; the leader's Play opens Choose Event with just those modes, and a pick is
  `partyVote` then `partyReady`. The leader's vote is the party's mode, and it doesn't un-ready the others. With no
  pick from the leader (an earlier game in the party), the most votes, then the first that fits. The `partyModes` setting says which modes
  the server offers (all three by default; the game shows any other as coming next, and so does an older server's).
- **Reactions**: eight emotes, sent to the rest of the party, at most four in a row and then one a second.
- **A dropped connection** keeps its place for 60 seconds (`partyGrace`): the app went to the background, or the
  signal went. The same device comes back into the party when it reconnects.

### Invites

Friends live in the game's Supabase project (`supabase/README.md`), so invites are made there: `rm_invite` checks you
are friends and that neither of you has blocked the other, lasts 2 minutes, and counts towards 40 an hour. The game
server only does two things:

- **It passes the word on live.** After making the invite, the game tells the game server who it went to (their
  Supabase id). The server nudges that player's game (a `poke`, which carries nothing but its kind), and the game reads
  its inbox from Supabase at once. So what shows is always what the database allows; a game that claims someone else's
  Supabase id in its hello only receives nudges, never an invite. Friend requests and their answers nudge the same way.
- **It lets the invited player in.** Accepting an invite (`rm_answer_invite`) hands over the party's code, and the game
  joins the party with it. Declining tells the database and the party (who see "can't play right now").

A friend who isn't connected finds the invite in their inbox (it is in the database) if they open the game within the
2 minutes, and since v391 gets a notification on their iPhone (below).

### Notifications while the game is closed (v391)

- **The phone's address.** Once the player has said yes to notifications, the iPhone app registers for them and hands
  the game its device token, which the game keeps with the player's account (`rm_push_token`; only the player writes
  it, one account per phone at a time, five phones each; logging out takes it back with `rm_push_forget`).
- **Sending.** The game's invite to the game server (`partyInvite`) carries the invite's Supabase id and the inviter's
  own Supabase access token. When the friend has no connection to the server, the server asks Supabase, as the
  inviter, for that invite's notification (`rm_invite_push`: only for the invite's sender, only while it's open, only
  between friends with no block, and once per invite) and posts it to each of the friend's phones through Apple's push
  service (`server/src/push.js`: token-based, an ES256 provider token renewed every 40 minutes, HTTP/2, one
  connection per Apple service). It says "@handle invited you to their party. Tap to join!", runs out with the invite,
  and carries the invite's id.
- **Tapping it** opens the game on that invite: its card at the top of the lobby, held there until it's answered.
- **The key** is read from the environment only (`APNS_KEY_ID`, `APNS_TEAM_ID`, `APNS_KEY_P8`, `APNS_BUNDLE_ID`,
  `APNS_PRODUCTION`), set as Fly secrets; with no key the server sends nothing and says so once in its log. How to make
  the key: `docs/party-v391.md`. The sender's own game can read the friend's token through `rm_invite_push` too, once
  per invite; a token is no use without the app's APNs key.

### Matchmaking

There is one queue per mode. A ticket is one player, or a party that plays together. Every 250 ms the server forms
matches, oldest tickets first, from tickets that are in reach of each other. A ticket's reach widens with its wait
(two tickets fit when they are within the reach of the one that has waited longer, so a newcomer is matched at once
with someone who has been waiting):

| Waited | Region | Round trip to the server | Rank (v393) | Rating |
|---|---|---|---|---|
| from 0 s | the same region | within 50 ms of each other | within 2 | within 150 |
| from 4 s | the same or a neighbouring region | within 100 ms | within 5 | within 300 |
| from 8 s | anywhere | within 200 ms | within 10 | within 500 |
| from 12 s | anywhere | any | any | any |

- **The rank** is the player's level, the one the game shows (the `r` of the look the game sends in its hello; a
  party's is its average). Among the tickets in reach, the closest region, then rank, round trip and rating come first
  (one rank apart weighs as much as 25 ms). A game that doesn't send one isn't held back by it.
- **Play online** (v393) offers Versus 1 v 1 (`duel`), Versus 3-way (`trio`: three on one canvas, most paint wins) and
  the Showdown free-for-all (`ffa`). 2v2 (`duo`) is still queued by older games and by parties.

- **The region** comes from the time zone the game reports in its hello (`America/Chicago` is North America, and so
  on: North and South America, Europe, Africa, the Middle East, Asia, Oceania; neighbours are regions whose players
  usually reach each other's servers well under 150 ms apart). Without a time zone name, the offset does it roughly.
  The round trip is the server's own measure of each connection.
- **Parties stay together.** Showdown fills around a party; in 2v2 a party of two is one team (a party plays a party
  when there is one), and four players on their own are split best and worst against the two in the middle. A
  Showdown still a player short after 20 seconds starts with three.
- **The hand-off.** Parties and the matchmaker start every match through one function, `_launch(mode, players)`, with
  each player's team; the match's slots follow the mode's sides.
- **Nobody found after 30 seconds:** the game offers a match against the CPU instead, in the same mode (a Showdown
  against the CPU once the player has it), and keeps looking if the player wants; it never pretends a CPU is a person.
  A party of two still searching is reminded the leader can pick Versus and play each other; a party of three is in a Showdown
  of its own after 20 seconds.
- **More server regions later.** Run one server per region, each with its own matchmaker, and send each player to the
  region with the lowest measured round trip (the game pings each region's `/health` at start). To widen to the whole
  world, a ticket that has waited 8 seconds in a quiet region is also offered to its neighbouring regions' queues
  (either the game holds a second connection and queues in both, cancelling one when the other finds a match, or the
  servers share their waiting tickets through a small common store such as Redis and agree which region hosts the
  match: the one that keeps the worst player's round trip lowest). The stages above stay the same.

### Connections

The game keeps its connection open while the player is signed in to an account in the lobby (so an invite arrives
live), in a party, in a queue or in a match. While it only waits in the lobby it sends a heartbeat every 20 seconds and
the server pings it every 20 seconds (`idlePing`); in a queue, a starting party or a match both ping twice a second
(it keeps a phone's radio awake for the start). A connection that has sent nothing for 75 seconds is closed
(`silentKick`). The game closes its connection when it goes to the background, outside a match.

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
  that floods or sends garbage is disconnected. A late answer to the server's ping (a phone held up for over 30
  seconds) is let go rather than counted as garbage. Private room codes cannot be guessed quickly.

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
| `DATA_FILE` | ./data/store.json | Where players and ratings are saved (`memory` keeps nothing) |
| `LOG_LEVEL` | info | debug, info, warn, error or silent; logs are one JSON object per line |
| `ALLOWED_ORIGINS` | (any) | Web pages allowed to connect, comma separated; the iOS app's page is `rollmodel://localhost` |
| `MAX_CONNECTIONS` | 5000 | Connections at once |
| `MAX_PER_IP` | 64 | Connections from one address |
| `TRUST_PROXY` | 0 | 1 when behind a proxy that sets X-Forwarded-For |
| `SNAPSHOT_HZ` | 30 | Snapshots a second (20 saves about a third of the server's work and bandwidth) |
| `SHUTDOWN_GRACE_MS` | 3000 | How long a shutdown waits for connections to close |
| `RULES` | | JSON to change match rules (for example `{"matchT":60}`), and the lobby's: `partyModes` (`["duel","ffa","duo"]`), `partyGrace` (60), `idlePing` (20), `silentKick` (75); see `server/src/constants.js` |
| `APNS_KEY_ID`, `APNS_TEAM_ID`, `APNS_KEY_P8`, `APNS_BUNDLE_ID` | | Apple's push service, for party invites to a closed game (v391): the key's id, your team id, the .p8 key itself (its whole text) and the app's bundle id. Fly secrets, never in a file. Unset: no notifications |
| `APNS_PRODUCTION` | 0 | 1 sends a token that doesn't say which service it's for to Apple's production service (the app says: Xcode builds are the sandbox, TestFlight and the App Store production) |
| `SUPABASE_URL`, `SUPABASE_KEY` | the game's | The Supabase project and its publishable key, for `rm_invite_push` (only asked when a notification is due) |

Stopping the server (Ctrl+C, or a SIGTERM from the host) is graceful: running matches are called off without rating
changes, everyone is told, and the data file is saved.

## Where it runs: Fly.io

The live server is the Fly.io app `rollmodel-game` (in the personal organization, Nicholas Marcelin):

- **Address:** `https://rollmodel-game.fly.dev` (check it at `/health`); the game connects to
  `wss://rollmodel-game.fly.dev/ws`. The address is baked into the game from `tools/online_config.json`.
- **Machine:** one shared-cpu-1x machine with 512 MB in Chicago (`ord`), always on (no stopping when idle, so the first
  player of the day does not wait for a cold start), with a 1 GB volume `rm_data` mounted at `/data` for the data file.
  One machine handles several hundred players (see the load test above); a second region can come later.
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
const net = new RMNet({ url: 'wss://play.example.com/ws', name: 'Blobby', look: { hat: 'cap' }, token: localStorage.rmToken,
  sb: supabaseUserId,                                           // optional: invites and nudges find the player by it
  zone: 'America/Chicago', beat: 20000 });                      // the time zone (the browser's by default); ms between pings
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
net.setBeat(500);                                               // ping twice a second from now on (a heartbeat in the lobby: 20000)
```

The connection reconnects by itself (backing off from 0.4 s to 8 s) and, within 20 seconds of a drop, picks up the
match where it was (the `resume` event).

Parties (`net.party` holds the latest view; each change comes as a `party` event):

```js
const v = await net.partyCreate();          // { id, code, leader, max, state, startAt?, queuedAt?, mode, modes, members, invites }
await net.partyJoin(v.code);                // rejects with 'not_found', 'full', 'busy' (playing or finding a match) or 'rate'
await net.partyInvite(friendSupabaseId, { name, look }); // after rm_invite: shows in the party, and nudges the friend's game
await net.partyDecline(code);               // (the invited player) no: the party hears it
await net.partyReady(true);                 // everyone ready: 1.5 s, then the match or the search
await net.partyVote('duel');                // 'duel' | 'ffa' | 'duo'
await net.partyLook(look);                  // a new look (un-readies you)
await net.partyBusy('locker');              // 'locker' | 'shop' | 'strokes' | 'settings' | 'cpu' | 'menu' | null (busy un-readies you)
net.partyReact('wave');                     // 'wave' | 'laugh' | 'wow' | 'love' | 'cool' | 'cry' | 'angry' | 'gg'
await net.partyKick(memberId);              // the leader only
await net.partyLeave();
net.poke(friendSupabaseId, 'request');      // nudge a friend's game to read its inbox ('invite' | 'request' | 'answer')
```

A member in the view is `{ id, sb, name, look, ready, vote, busy?, away? }`; `modes` lists each mode that fits the
party's size with how it plays (`plan`: `private` or `queue`) and whether parties may play it on this server (`on`);
`invites` are the invites still waiting (`{ to, name, look, by, left }`, `left` in ms).

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
| `welcome` | `{ id, token, name, nameChanged, ratings, resume, serverTime, proto, modes, caps, partyModes }` (`resume`: the match to pick up, or null; `caps` includes `party` on a server with parties) |
| `queued`, `queueLeft`, `room`, `roomLeft` | lobby updates (`room`: `{ code, mode, host, need, inMatch, players: [{ id, name, look, ready }] }`; `queued` and `queueLeft` say `party: true` for a party's search) |
| `party`, `partyLeft` | your party as it is now (see above); you are out of it (`reason`: left, removed, gone) |
| `react`, `partyNote` | a member's reaction `{ id, e }`; `{ k: 'declined', name, to }`: an invited friend said no (`to`: their Supabase id) |
| `poke` | `{ k }`: something new in your inbox (`invite`, `request`, `answer`); read it from Supabase |
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
`act`, `rematch`, `leaveMatch`, `bye`, `partyCreate`, `partyJoin`, `partyLeave`, `partyKick`, `partyReady`, `partyVote`,
`partyLook`, `partyBusy`, `partyReact`, `partyInvite`, `partyDecline`, `poke` (JSON), and binary STATE (34 bytes, about 30 a second), PING and SPONG
(9 bytes).

From the server: `welcome`, `error`, `kicked`, `queued`, `queueLeft`, `room`, `roomLeft`, `party`, `partyLeft`, `react`,
`partyNote`, `poke`, `name`, `matchFound`,
`matchCancelled`, `start`, `resume`, `ack`, `act`, `correction`, `ko`, `respawn`, `out`, `flat`, `push`, `dodged`, `pot`,
`potEject`, `cov`, `itemSpawn`, `itemTaken`, `itemUsed`, `itemGone`, `itemTrap`, `unGiant`, `playerAway`, `playerBack`,
`playerLeft`, `afk`, `matchEnd`, `rematch`, `matchClosed`, `server` (JSON), and binary SNAP (14 bytes plus 19 per
player, 30 a second), PONG (17 bytes) and SPING (9 bytes). The exact byte layouts are written at the top of
`rmnet.js`.

## In the game (v306, v391)

The online game lives in build modules: `tools/v306_accounts.py` (the username and the account),
`tools/v391_party.py` (the Online sheet's Versus and Showdown, parties, invites, the inbox, notifications and
matchmaking; it took the place of v306's rooms in `tools/v306_lobby.py`, which still brings the SDK),
`tools/v306_match.py` (the match) and `tools/v391_showdown_online.py` (the match for up to four). They were written as
`tools/v312_party.py` and `tools/v312_showdown.py` on the party branch, around v312, and brought onto v390's game as
modules applied last. What a player sees, with pictures, is in `docs/online-v306.md`, `docs/party-v312.md` and
`docs/party-v391.md`. The match works like this:

1. **The canvas.** When the server finds a match, both phones build the stage from the server's seed with the same fixed
   options (normal paint, none of the player's own canvas choices, the seven vote canvases) and send it back; the server
   compares them before the match can start.
2. **The start.** The versus card stays up until the server says when "Go" is, and the 3, 2, 1 lands on it on both
   phones. Each blob drops onto its spot (no basin intro online).
3. **Your blob** moves on your phone at once; every hop, roll, fling, pound, landing, stomp and pot dive goes to the
   server as it happens, and your position about 30 times a second. A move the server refuses is undone (a pot it did
   not let you into pops you out).
4. **The others** are drawn from the server's snapshots a moment in the past, with their trails, hops, rolls, flings
   and pounds, names, colours (changed on your screen if one is too like yours or another's), eyes, wearables and
   ranks. Each is one of the game's own rivals: in 2v2 your teammate is the game's ally and wears your team's colour
   (your two colours mixed, as each team's is), the other pair the other; in a Showdown of three the fourth sits out.
5. **The server decides** knock-outs, flattenings, pushes, dodges, who is in which pot, pots going down and coming back,
   coverage (the bar shows the server's numbers), the clock, the weather (the server's schedule), overtime, the hearts
   a knock-out costs, who is out and in what place, and the result. The game never knocks out, flattens, stuns or rams
   anyone itself online; it shows its own Showdown (the hearts across the top, the banners, the closing line) around
   the server's rulings.
6. **Real time.** The server runs on real time, so online there is no hit-stop, slow motion or kill cam, and a slow
   frame catches up (up to a quarter of a second) instead of playing in slow motion as it does offline. Pause shows the
   menu while the match goes on; Leave match forfeits.
7. **Out of a Showdown:** the camera watches someone still in it, and the Skip button (offline it runs the rest at
   speed) says Leave: online the match runs on real time.
8. **After the match:** the usual tally and winner screen, then Rematch (everyone has to say yes) or Menu, which
   takes a party back to its lobby. A Showdown's last knock-out plays out first (1.7 seconds, as offline).
9. **Called off or taken out before it begins:** a match called off, ended, or that the server took you out of while
   your phone is still on the versus card or the countdown goes back to the lobby with a word on screen ("The match was
   called off", "Away too long"), never into a match you are no longer in.

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
   addresses in logs, and flags suspected cheating; since v391, each iPhone's notification token is kept with the
   player's account (for party invites) until they log out or delete the account. The App Store privacy labels, the privacy policy and the terms need
   to say so, including how long things are kept and how to ask for deletion.
6. **Name moderation.** Names are cleaned and a small list of bad words is refused. Before launch, decide on a bigger
   list (or a moderation service), a report button, and what happens to reported players.
7. **Analytics.** What to measure (round trips by region, match length, abandon rate, cheat flags), where it goes, and
   whether players must agree first.
8. **Notifications while the game is closed.** Built in v391 for party invites (see "Notifications while the game is
   closed" above): the game asks in its own card the first time you invite someone or join a party, the game server
   sends with an APNs key, and tapping one opens the game on the invite. It needs the key set on the server
   (`docs/party-v391.md`). Friend requests could go the same way later.

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
