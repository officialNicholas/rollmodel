# Roll Model online play: plan, with latency first

Written after v259 (fully offline iOS app). Two questions: does the way the app runs the game (a bundled web page in a web view, served from the app's own private address) get in the way of online play, and how do we make ping as low as it can be.

## 1. The offline web view and online play

### Not affected

- **Network traffic takes the normal path.** The app's file server only answers for the game's own files (`rollmodel://localhost/...`). Connections to a game server (`wss://`) or to Supabase (`https://`) go straight out through the web view's own network stack. Nothing passes through our code, so the offline setup adds no latency.
- **Secure connections from the page work.** A page that isn't a secure context may still open `wss://` sockets and make `https://` requests. Servers must accept the page's origin, `rollmodel://localhost`. Supabase's REST API answers any origin for key-based requests, and our own game server can allow it.
- **The sound, graphics and memory fixes (v258, v259)** don't touch the network.

### Needs a decision before we build

1. **The page is not a secure context.** WebKit treats custom app schemes as not secure and has no public way to change that ([WebKit bug 204558](https://bugs.webkit.org/show_bug.cgi?id=204558), [Apple developer forums](https://developer.apple.com/forums/thread/725916)). Inside the page, that rules out:
   - Web Crypto, which Supabase's browser sign-in (PKCE) uses.
   - WebTransport, the browser's low-latency UDP-style channel.
   - Possibly WebRTC data channels too.

   **Decision:** sign-in and the fast network lane live in the app (Swift), not in the page. That also fits the plan to move more of the game native. Alternative, not recommended now: serve the game from a tiny server inside the app on `http://localhost`, which does count as secure. It means an origin change (the v259 save copy would carry saves across) and a server to babysit.
2. **Sign-in can't use web redirects.** The app sends any `https://` page navigation to Safari, so a web OAuth redirect would leave the game. Sign-in uses Apple's own flows instead: Sign in with Apple (required by the App Store whenever other social logins are offered) and `ASWebAuthenticationSession` for any other provider. The Supabase session is handed to the game through the bridge.
3. **Single-player lifecycle behavior must branch for online matches:**
   - **Losing focus pauses the game.** Online, nothing pauses: the match goes on on the server. Show "Reconnecting" and keep sending neutral input.
   - **Going to the background.** iOS suspends the app within seconds and the socket drops. The server holds the player's slot for a grace period (about 20 to 30 s, with the axolotl idle or CPU-driven). The app rejoins with a reconnection token and resyncs from a full snapshot.
   - **v259 graphics-loss restart and the reload after iOS closes the page.** During an online match, the restart must rejoin the match with the stored reconnection token, not drop to the menu.
   - **v259 save copy.** It stays an offline cache. Online progress, currency and items are owned by the server (Supabase), and the "newer copy wins" rule never overrides server data.
4. **The page's main thread also draws the game.** A slow frame or garbage collection delays network messages. In the app, networking runs on a native thread that timestamps packets on arrival. The page reads the newest state each frame.
5. **Frame rate is not tick rate.** Low Power Mode and heat cap drawing at 30 fps. Network sends and the simulation run on a fixed clock that doesn't depend on drawing.
6. **The claude.ai preview can't go online.** Its sandbox blocks network connections, so online play is app-only (and later a real website, if we want one).

## 2. Where ping comes from, and what we do about each part

The table assumes a player on 4G or Wi-Fi, playing on a server in their region.

| Part | Typical | Lever |
|---|---|---|
| Distance to the server | about 1 ms of round trip per 100 km of fiber | Servers in several regions, matched by measured ping |
| Last mile (radio) | Wi-Fi 2 to 10 ms, 5G 10 to 30, 4G 30 to 60, plus up to 100+ ms when the radio wakes | Keep the radio awake before the match starts |
| Waiting for the server's next tick | half a tick (17 ms at 30 Hz) | 30 Hz tick, send on change |
| Waiting to send input | half a send interval | Send input the moment it changes, plus a fixed 30 Hz stream |
| Lost packets on TCP (head-of-line blocking) | a lost packet stalls everything behind it for a round trip or more | Unreliable UDP lane for moving state |
| Buffer to smooth other players | 1 snapshot plus jitter, 50 to 80 ms | Adaptive buffer sized from measured jitter |
| Main-thread hitches | 0 to 30 ms of jitter | Native network thread; preallocated buffers |

Your own axolotl feels instant whatever the ping (prediction, below). What ping changes is how fresh other players look, and how fair hits feel.

### 2.1 Feel: hide ping where it can be hidden

- **Client prediction for your own axolotl.** Input moves you and paints immediately. Each server snapshot is checked, unacknowledged inputs are replayed on top, and any correction is eased in over about 100 ms. This needs the simulation split from drawing, with a fixed step and a seeded random generator (Phase 0).
- **Interpolation for others.** Rivals are drawn a little in the past, between two snapshots. The buffer adapts to measured jitter. When a packet is late, motion extrapolates for up to 100 ms rather than freezing.
- **Server-side lag compensation for hits.** For pound, missile, turret and trap, the server rewinds rivals to where the attacker saw them (capped at about 150 ms) before deciding a hit. Hits that looked clean count.
- **Predicted effects.** Splats, slams and projectiles start on your screen at once; the server confirms or quietly cancels them.
- **Paint.** Paint is predicted locally. The server's coverage is the truth for the score, and paint is sent as compact strokes (position, radius, team), not grid cells.

### 2.2 Cut real ping

- **Regions.** Start with US East, US West and Europe; add Asia-Pacific and South America when the telemetry says so. One server process per match, in the region that keeps the worst player's ping lowest.
- **Matchmaking by measured ping.** At app start (and again before matchmaking) the app pings each region about 5 times and keeps the median. Players are grouped in their best region. After a short wait, the search widens to a second region only if its ping is under a cap (about 90 ms).
- **Pre-connect.** Open the connection to the match region during the stage vote and fight card, so the encryption handshake and the radio wake-up happen before the countdown. Keep a light heartbeat (2 to 4 per second) while matchmaking, so a phone's radio isn't asleep at "Go".
- **Small, binary packets.**
  - Positions quantized to 16 bits; snapshots delta-compressed against the last one the client acknowledged.
  - Each input packet also carries the previous 3 or 4 inputs, so one loss costs nothing.
  - No JSON on the fast lane.
- **Two lanes.**
  - **Fast lane (unreliable, unordered UDP):** inputs up, snapshots down.
    - In the iOS app: native UDP via Apple's Network framework, each packet encrypted with a session key from the sign-in handshake (CryptoKit on the phone, libsodium on the server).
    - On a website later: WebTransport datagrams. Safari ships it on by default from 26.4 ([Safari 26.4 report](https://www.apfelpatient.de/news/apple-safari-26-4-44-features-und-191-bugs-behoben), [overview](https://www.videosdk.live/developer-hub/webtransport/safari-webtransport)). Test real devices first, since engines still differ on the handshake.
  - **Reliable lane (WebSocket):** join, match events, chat, results, and the whole game if UDP is blocked (some Wi-Fi networks block it).
- **Tick rates.**
  - Server simulation: 30 Hz.
  - Snapshots: 30 Hz, dropping to 20 Hz for a player whose connection struggles.
  - Input: sent immediately on change, plus a steady 30 Hz stream.
- **No Nagle delay.** TCP_NODELAY on every server socket.

### 2.3 Measure

- A small ping and connection indicator in matches. Warn before joining when the best region is over about 150 ms.
- Telemetry to Supabase per match: round trip, jitter, loss, region, network type. It tells us where to add regions and how big the buffers should be.
- A test mode that adds fake latency, jitter and loss on the client, so the game's feel can be tuned at 50, 100 and 200 ms before real servers exist.

## 3. Cheating

The server owns the simulation, coverage, hits, the clock, results and rewards; the client only sends input. Prediction is cosmetic: the server never trusts a position the client reports. Supabase writes for results, currency and items come only from the server, using its own service key, with row-level security so a client can read its profile but not write rewards.

## 4. Order of work

| Phase | What | Ping work in it |
|---|---|---|
| 0 | In the current game, no server yet: split the simulation from drawing, fixed 30 Hz step, seeded random generator, inputs as commands, snapshot save and restore, binary encoding. A fake-latency test harness. | Prediction and interpolation built and tuned against fake lag |
| 1 | Authoritative server (Node, sharing the game's simulation code), WebSocket, one region, private matches by invite code, rejoin after background | Pre-connect, heartbeat, delta snapshots, rejoin |
| 2 | Native sign-in (Sign in with Apple, Supabase session through the bridge), profiles, server-written results; regions and ping matchmaking | Region choice by measured ping |
| 3 | Native UDP fast lane in the app, WebSocket fallback | No head-of-line stalls on lossy mobile networks |
| 4 | Lag compensation polish, ranked queues, telemetry-driven regions, ping indicator | Fair hits; regions where players are |

Phase 0 is the biggest single piece, and everything else depends on it. It changes no gameplay and can ship to players while it's being done.
