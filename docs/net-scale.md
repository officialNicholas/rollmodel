# Scaling the game server to 1,000 players at once (branch claude/perf-network)

The target: 1,000 people playing online at the same time, on one Fly machine. Three things stood in the way, all fixed
on this branch, and one setting for the deploy.

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

- The whole suite (74 tests before this, 80 now) passes as before, with matches on the main thread.
- The whole suite again with every match going through the worker path inside one thread (`npm run test:inline`):
  the same messages, cloned and a turn of the event loop apart as between threads, so every test of the referee also
  tests the hand-over, and tests can still look inside a match.
- New, on real threads (`test/workers.test.js`): a duel start to finish on one clock with the result and rating saved;
  a dropped and a silent connection picked up again; a rematch and a room; a worker that dies; shutting down.
- New: the journal store (a change is one line, the snapshot is rebuilt and both load back).

## Not done (later, if needed)

- **Matchmaking** compares every queued player with every other four times a second: 10 ms a pass with 1,000 queued at
  once (an extreme case; a few hundred is about 2 ms). Sort by rating and look only at neighbours if queues ever get
  that long.
- **Past about 1,500 players**, the main thread's socket work becomes the limit on any size of machine. Then: more
  machines, or regions (which also cut ping for players far from Chicago).
- **A real database** for players once there are hundreds of thousands: the snapshot is about 100 MB at 200,000.
- **Deploys** restart the one machine, so every match in progress is called off: deploy at a quiet hour.
