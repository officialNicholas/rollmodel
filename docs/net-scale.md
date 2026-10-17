# Scaling the game server to 5,000 players at once (branch claude/perf-network)

The target: 5,000 people playing online at the same time. One machine tops out around 1,500 (its main thread's socket
work, on any size of machine), so the server now runs on several machines that act as one: each game machine takes about
1,000 players, one small machine keeps everyone's data, and Fly's proxy puts each player on the right machine. Sections
1 to 3 made one machine good for 1,000; section 4 spreads the load over several.

## 1. One core was the ceiling

The server is one Node.js process, and one Node.js thread runs on one core however big the machine. At 400 players it
already used about 60% of a core; 1,000 needed about 1.5.

Where its time went (a CPU profile of the 400-player load test): about 45% sending and receiving on the sockets, about
36% the matches themselves (checking every move, painting coverage, snapshots), the rest garbage collection and the like.

**Now:** matches run on worker threads (`src/matchworker.js`), one per core but the main thread's (`MATCH_WORKERS=auto`).
The main thread keeps every connection, the lobby and matchmaking; a small stand-in for each match (`src/matchpool.js`)
forwards to its worker and mirrors what the lobby needs back (phase, places, results).

- Messages between threads go in batches: movement reports packed into one buffer a millisecond (handed over without a
  copy), snapshots likewise the other way, and a player's messages in a batch go out in one socket write.
- One clock for every thread, so the times the phones see (pongs from the main thread, snapshots and the start from a
  worker) agree.
- A worker that dies: its players are told the match was called off (`server_error`), they can play again at once,
  and a new worker takes its place.
- Shutting down waits for the workers' last messages, so every player hears the match was called off.
- `MATCH_WORKERS=0` (the default) runs matches on the main thread as before.

## 2. Saving players froze everything

Every sign-in and every finished match rewrote one JSON file with every player ever, half a second later, on the main
thread. Building that file takes about 30 ms at 10,000 players, 180 ms at 50,000 and 575 ms at 200,000, and with 1,000
online something changes all the time, so every match would stutter every half second.

**Now:** a change is one short line appended to a journal beside the file (`store.json.log`). When the journal outgrows
the snapshot (or 64 MB) the snapshot is written again a few hundred players at a time between other work, and the
journal starts over. Loading reads the snapshot and replays the journal. Same file format, so the live data carries over.

| 50,000 players, 20 changes a second | Before | After |
|---|---|---|
| Longest freeze of the main thread | 219 ms | 8 ms |
| Rebuilding the snapshot | (every save) | 227 ms in all, never more than 7 ms at a time |

## 3. The machine

A shared-cpu-1x is guaranteed about 1/16 of a core once its burst balance is spent (Fly then pauses it in 80 ms
periods), and 1,000 players need about 560 MB. `server/fly.toml` now asks for **performance-2x** (two dedicated cores,
4 GB, about $62 a month in Fly's US regions) with `MATCH_WORKERS=auto` (one worker).

## 4. Several machines: 5,000 players

- **Game machines** (Fly process group `game`, performance-2x): each is the whole game server as above, with about
  1,000 players and room for 1,500. Fly sends each new player to a machine under its soft limit (1,000 connections),
  and never more than 1,500 to one. They keep nothing on disk.
- **The store machine** (group `store`, performance-1x, with the volume): keeps every player's account, ratings and
  stats, as the one machine always has, and serves them to the game machines over Fly's private network
  (`src/storeapi.js`; port 8081, never public, and only with `INTERNAL_KEY`, a Fly secret). Any game machine can sign
  in any player and save their results. It also hands out private room codes, so a code is unique across machines.
  Measured: about 1,200 requests a second with 50,000 players on file; 5,000 players need about 100.
- **Getting a player to the right machine:** most connections can go anywhere. Two can't: joining a room (it lives on
  the machine of whoever made it) and picking a match up again after a drop (it runs on one machine). The machine that
  gets such a connection answers with Fly's `fly-replay` header naming the right machine, and Fly's proxy hands the
  connection over before it opens. The SDK asks for a machine by adding `?s=<machine>` to the address:
  - after a drop in a match or a room, it asks for the machine it was on (after a few failures, any machine);
  - `joinRoom(code)` with a room elsewhere: the server answers `room_elsewhere` with the machine, and the SDK moves there
    and joins, without telling the game the connection dropped (the game only sees a new welcome). No game change: the
    game inlines the SDK at build.
- **One clock per machine:** each machine counts time from its own start, so the SDK starts its clock again when it
  lands on another machine (or the same one restarted). Without that, a player moved to a room's machine thought the
  countdown was over and set off early (211 corrections in the load test below; none after).
- **A store machine that can't be reached** makes sign-in fail with "try again" (not fatal: the phone keeps trying), and
  matches already running carry on.
- **Matchmaking** is per machine: with about 1,000 players each, the queues are big enough. Friends play together
  through rooms, which work across machines.
- **Deploys** replace the game machines one at a time, so only the matches on the machine being replaced are called off.

### Measured on this computer (`bench/clusterload.js`)

A store machine and three game machines, each its own process, behind a stand-in for Fly's proxy that also follows
`fly-replay`; 1,200 bots in 300 rooms of 4, made so that most guests start on another machine than their room.

| | Each game machine (about 400 players, 100 matches) |
|---|---|
| Main thread | 24 to 25% of a core |
| Match worker | 13 to 16% |
| Worker tick, 99th percentile | 11 ms |
| Hand-overs to a room's machine | 358 |
| Snapshots a second, per player | 31 (median) |
| Corrections | 14 of 1,200 players (this computer had all four servers, the proxy and 1,200 bots on 4 cores) |

The 1,000-player measurements of one machine are above; machines don't share any work but the store's.

### The setup for 5,000

| | Machines | Each | A month (Fly's US prices) |
|---|---|---|---|
| Game | 6 (about 830 players each; room for one to be down) | performance-2x, 2 cores, 4 GB | 6 x $62 |
| Store | 1, with the 1 GB volume | performance-1x, 1 core, 2 GB | $31 |
| Machines in all | | | about $403 |
| Data out | 4.8 KB a second per player in a match ($0.02/GB) | | about $250 for each 1,000 players online on average |

The data bill follows the average number of people online, not the peak: 5,000 at the busiest hour might be 1,000 to
1,500 on average. Levers if it matters: 20 snapshots a second instead of 30 (`SNAPSHOT_HZ`, a third less), and
smaller snapshots (the TCP and WebSocket headers are about half of each one).

All six game machines are in Chicago to start, as now. Spreading them (say 2 in Chicago, 2 on the US East Coast, 1 on
the West Coast, 1 in Europe) cuts ping for players far from Chicago; Fly sends each player to the nearest machine with
room. Only signing in and saving results go to the store machine.

### Deploying it (the lead, once the owner says so; agents never deploy)

From `server/` on this branch:

1. Back up the data: `fly ssh console -a rollmodel-game -C "cat /data/store.json" > store-backup.json`
2. The shared secret for the private API (generated, never written down anywhere else):
   `fly secrets set INTERNAL_KEY=$(openssl rand -hex 32) -a rollmodel-game`
3. `fly deploy`, then `fly scale count game=6 store=1 --region ord -a rollmodel-game`. The data volume `rm_data` goes
   to the store machine (`[mounts] processes = ["store"]`). Before this branch the app had one machine in the default
   process group with that volume: if `fly deploy` leaves it, destroy it once the store machine is up so the volume
   can move (`fly m list`, `fly m destroy <id>`), and check the store machine's `/data/store.json` against the backup.
4. Check the routing on the live server with the game machines' ids (`fly m list`):
   `node bench/flycheck.js wss://rollmodel-game.fly.dev/ws <id> <id> ...` (each machine reached when asked for, and a
   room made on one machine joined from another). And `/health` on the app: one worker per machine under `workers`.

The store's data format is unchanged, plus its journal (`store.json.log`), which the store machine replays on start.

## Measured

Load test (`npm test` runs it at 400; `RM_LOAD_ROOMS`, `RM_LOAD_MODE=duel`, `RM_LOAD_BOTPROCS`, `MATCH_WORKERS` scale
it). The bots run in their own processes on the same 4-core machine, so they compete with the server for the cores; on
this machine the sockets are loopback, where the kernel also does the receiving side's work during each send, so socket
time here is on the high side of a real network.

| | 400 players, matches on the main thread | 1,000 players, Showdown (250 matches) | 1,000 players, duels (500 matches) |
|---|---|---|---|
| Main thread (sockets, lobby) | 67% of a core (everything) | 56% | 65% |
| Match worker | | 39% | 49% |
| Whole server | 0.67 cores | 1.1 cores | 1.26 cores |
| Worker tick, 99th percentile | | 13 ms | 17 ms (of 33) |
| Snapshots a second, per player | 26 to 30 | 30 (slowest 28) | 29 |
| Corrections of honest players | 0 | 0 | 0 |
| Memory | 219 MB | 424 MB | 563 MB |

On two cores that leaves about 35% of the main thread and half the worker spare at 1,000 players.

## Tested

- The whole suite (74 tests before this, 85 now) passes as before, with matches on the main thread.
- The whole suite again with every match going through the worker path inside one thread (`npm run test:inline`):
  the same messages, cloned and a turn of the event loop apart as between threads, so every test of the referee also
  tests the hand-over, and tests can still look inside a match.
- New, on real threads (`test/workers.test.js`): a duel start to finish on one clock with the result and rating saved;
  a dropped and a silent connection picked up again; a rematch and a room; a worker that dies; shutting down.
- New: the journal store (a change is one line, the snapshot is rebuilt and both load back).
- New, several machines (`test/shards.test.js`, through a stand-in for Fly's proxy): the same account on any machine
  and its result saved once in the shared store; a room joined from another machine without the game hearing of a
  drop; a dropped connection back on the machine running its match; room codes unique across machines; a store that
  can't be reached is not fatal; the private API refuses anyone without the key. And the SDK's clock starting again on
  another machine (`test/unit.test.js`).

## Not done (later, if needed)

- **Matchmaking** compares every queued player with every other four times a second: 10 ms a pass with 1,000 queued at
  once (an extreme case; a few hundred is about 2 ms). Sort by rating and look only at neighbours if queues ever get
  that long.
- **Past about 9,000 players** (six machines at 1,500): more game machines (`fly scale count game=N`), nothing else.
- **The store machine** is the one machine everyone needs to sign in: a database with a standby, or a second store
  machine, if that ever matters.
- **A real database** for players once there are hundreds of thousands: the snapshot is about 100 MB at 200,000.
- **Deploys** restart the one machine, so every match in progress is called off: deploy at a quiet hour.
