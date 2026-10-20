# Network: how online play holds up, and what changed (branch claude/perf-network)

Measured with `server/bench/netprobe.js`: a local server and two headless players (the real SDK plus a body that moves
like the game) play duels over a simulated link. TCP never loses a message, so "loss" is modelled as what TCP turns it
into: the lost segment and everything behind it wait for a retransmission (200 ms plus a round trip).

```
cd server && node bench/netprobe.js lan,rtt60,rtt120,rtt200,jitter,mobile,loss1,loss3,bad 10
node bench/netprobe.js drop
```

## Before (v336)

| Link | Round trip | Rival drawn behind | Rival error p95 / worst | Extrapolated | Rival pops (leap back) |
|---|---|---|---|---|---|
| LAN | 3 ms | 74 ms | 0.6 / 0.9 cm | 0% | 0 |
| 60 ms | 60 ms | 125 ms | 0.7 / 2 cm | 0% | 0 |
| 120 ms ±30 | 128 ms | 189 ms | 1.9 / 6 cm | 6% | 0 |
| 200 ms | 206 ms | 285 ms | 1.5 / 3 cm | 2% | 0 |
| Mobile (spikes) | 126 ms | 203 ms | 1.6 / 72 cm | 4% | some |
| 1% loss | 105 ms | 223 ms | 38 / 130 cm | 23% | 5 per 10 s, up to 1.4 m |
| 3% loss | 158 ms | 235 ms | 83 / 133 cm | 39% | 9 per 10 s, up to 1.2 m |

- Traffic is small: about 37 messages and 1.8 KB a second down, 33 messages and 1.1 KB a second up, per player.
- Honest players are almost never corrected: none on clean links; under 3% loss, about 2 a minute (see below).

### A dropped connection

| | Server notices | Phone notices | Rival told | Back in the match |
|---|---|---|---|---|
| The socket closes (clean) | 11 ms | 28 ms | 33 ms | 0.45 s |
| The link goes silent (tunnel, Wi-Fi to 4G) | never | never | AFK at 5 s | never: forfeit at 15 s |

A link that dies without closing is the common phone case. Neither side noticed: the server kept the player "connected",
the phone kept waiting, and the match was forfeited.

## Fixes

1. **Dead links are noticed.** The SDK drops and reopens a connection that has brought nothing for 3 s (the server
   answers two pings a second and sends 30 snapshots a second in a match). A page that was itself stalled (a long frame,
   a suspended app) gets a fresh 3 s, so a slow phone is never cut off. The server closes a connection that has sent
   nothing for 6 s, so the match marks the player away and holds the place for the usual 20 s.
2. **The rival glides instead of popping.** After a stall, late states pull the sampled position back from where it was
   extrapolated. A leap faster than anyone moves (16 m/s) is now eased out as a fading offset (90 ms), in `remote(id)`.
   Respawns, knock-outs and pots are never smoothed.

Both are in `server/client/rmnet.js`, which the game inlines at build time (tools/v306_lobby.py), so the game picks
them up with no game module; the server part needs a deploy.

## After

| | Before | After |
|---|---|---|
| Silent link: phone notices / server notices / rival told | never / never / never (AFK at 5 s) | 3.2 s / 3.2 s / 3.3 s |
| Silent link: back in the match | never: forfeit at 15 s | 3.7 s |
| Silent link, old client or suspended app: rival sees "lost connection" | never (forfeit at 15 s) | at 6 to 7 s, place held 20 s (test) |
| 1% loss: rival pops (10 s) | 3 to 5, up to 1.4 m | 0 |
| 3% loss: rival pops (10 s) | 9 to 10, up to 1.3 m | 0 to 1 (a respawn-sized move, partly eased) |
| Clean links | unchanged | unchanged (no smoothing kicks in) |

The server suite passes (74 tests, 5 new: the silent link resumed, the server closing a silent connection, the
smoothing, the late-seen hop and the late pot exit).

## Round two: the referee, the simulator, and 60 a second

- **The simulator was reordering messages.** `test/helpers/netsim.js` gave each message its own timer, and timers round
  their delays, so two messages sent within a millisecond could arrive swapped (TCP never does that). That made honest
  players look corrected: a position report overtaking "out of the pot", for instance. It now delivers strictly in order,
  one message a task, as a browser does. With it, the old server corrects honest players about once in 15 minutes of
  3% loss or a poor 4G link (it looked like 2 a minute before), so that finding was mostly the simulator's.
- **Two real edge cases in the referee, fixed anyway** (each with a test that fails without the fix):
  - a hop first seen in the air some time after take-off (the jump message late, or reports missed) was judged from
    the speed at that moment, already slowed by gravity, so an honest hop looked like floating. The take-off speed is
    now worked out from height and time since the ground, up to 450 ms after (a hop lasts about 750 ms), never more
    than the biggest hop, so it allows nothing a cheat couldn't already claim;
  - put out of a pot by the server (it ran dry) while the player's own exit was on its way: the next reports were
    judged from the ejection, so the way already rolled looked like a burst of speed. Their own exit time now counts,
    if it comes within 2 s and nothing has been judged since.
  - After: 0 corrections of honest players in 15 minutes of lossy play.
- **The rival's easing, tuned on the fixed simulator** (30 s runs, leaps the rival makes on screen):

  | Link | Raw | Drawn |
  |---|---|---|
  | 1% loss | 9 | 0 |
  | 3% loss | 19 | 2 (beside a respawn-sized move) |
  | Poor 4G (450 ms, 2% loss, spikes) | 19 | 0 |

  The eased gap is now up to 3 m and shrinks no faster than 12 m/s, so a big gap glides instead of snapping.
- **60 a second: not done.** It would draw the rival about 25 ms fresher, but the server is a Fly `shared-cpu-1x`,
  whose guaranteed share is about 1/16 of a core (with a burst balance; once that's spent it is throttled in 80 ms
  periods). The load test measures about 0.15% of a core per player at 30 a second, so at baseline that's a few dozen
  players before the tick stalls by up to 80 ms; 60 a second would halve that.

## Not done yet, ranked

1. **The server machine.** Move from `shared-cpu-1x` to `performance-1x` (a dedicated core) before online play has
   real numbers of players: otherwise a busy hour throttles the tick and every match stutters at once. A Fly setting,
   for the lead to deploy when the owner agrees (it costs more).
2. **More regions.** One machine in Chicago: a player in Europe or on the West Coast starts 60 to 120 ms behind. The
   plan (docs/online-plan.md) already has regions and ping matchmaking.
3. **60 a second**, once the machine has the headroom (above).
4. **UDP lane** (plan phase 3): the real cure for TCP stalls. Big, native.

# The game on a phone-like setup

`tools/pn_probe.py` (Chromium at 390x844, device scale 3, iPhone user agent, the game's AI driving you). This container
has no graphics chip: everything drawn goes through SwiftShader (software), so the GPU side (frame rate, heat, shader
compile times, canvas blurs) can't be judged here. What can: the main thread's own work per frame, its hitches, draw
calls, triangles and memory. Numbers are for one desktop core at 1x; a recent iPhone is in that range, older ones 2 to 3
times slower.

| Scene | Game's work per frame, mean / p95 | Frames over 16.7 ms | Draw calls | Triangles |
|---|---|---|---|---|
| Lobby | 4.4 / 9.5 ms | 0% | 5 | 43k |
| Locker | 4.3 / 6.9 ms | 0% | 8 | 29k |
| Versus, by stage | 6.9 to 9.3 / 10.6 to 15.0 ms | 0 to 3% | 89 to 108 | 124k to 229k |
| Showdown, four | 12.1 / 18.4 ms | 13% | 128 | 257k |
| Time trial | 6.1 / 9.7 ms | 0% | 97 | 171k |

- No shaders are built mid-match, and memory doesn't creep: six matches in a row keep the same textures, meshes and
  heap after the first (which fills effect pools and shader caches).
- Showdown's spikes are the CPU rivals' planning: one plan costs up to 6 to 8 ms here (they already take turns, one a
  frame). The rest of a Showdown frame is three.js drawing (4.5 ms) and the characters' animation (3.6 ms).
- Launch, in software: three.js reading back each shader's compile log (`renderer.debug.checkShaderErrors`) is 38% of
  the main thread's own time, and the coach's shadow bake (v332, a canvas blur and a PNG encode) about 2 s. Both are
  probably much cheaper on a phone's GPU; worth measuring there before changing.

## pn01: the readout, for measuring on a real phone

`tools/pn01_perf_hud.py` extends the v308 readout (Settings, tap the version five times): launch time, the last match's
start time, an online line (ping, jitter, how far behind the rival is drawn, corrections, traffic) and a tally per screen
(fps, share of frames over 25 ms, worst frame, game work) that can be tapped open in the menu and copied.
Checked with `tools/pn01_shot.py`.
