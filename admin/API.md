# Roll Model admin: the data contract

The dashboard (this folder), the game and the database agree on what's below. The database side is
`supabase/migrations/20261018000000_liveops.sql`; the game side is `tools/v354_stats.py`.

Everything goes through the game's existing Supabase project:
- **Auth:** Supabase Auth (GoTrue), `https://<project>.supabase.co/auth/v1/...`.
- **Data:** PostgREST remote procedure calls, `POST https://<project>.supabase.co/rest/v1/rpc/<function>` with a JSON body of named arguments.

The dashboard holds only two values, both public by design and already inside the game: the **Project URL** and the
**publishable key**. There is no secret or service-role key anywhere: every admin power is a database function that
checks who is calling.

## Who is an admin

A person is an admin only when all of these are true:
1. Their Supabase Auth user id is in the `rm_admins` table. Only the owner can add a row there, by running SQL in the Supabase dashboard; there's no function for it.
2. The request's token is at assurance level **aal2**, meaning they signed in with their password *and* an authenticator-app code (TOTP).
3. That code was entered in the last **12 hours** (the token's `amr` claim says when). After that, even a token that's still being refreshed stops working, and the person signs in again.
4. The token's session is still live (its `session_id` is in `auth.sessions`). Signing out, or the owner ending the session, cuts an admin off at once, though the token itself would last up to an hour.

Every `adm_*` function except `adm_whoami` checks all four, then refuses with
`{"code":"42501","message":"not an admin"}` (HTTP 403 from PostgREST) when any fails.

No admin function works on an admin's own account: resetting the password of, signing out or deleting anyone in `rm_admins` answers `why: "admin"`.

Each admin can only do so much an hour: 30 deleted accounts, 60 password resets, 60 sign-outs and 300 price changes. Past that, the
function answers `why: "slow_down"` and changes nothing.

## Signing in (dashboard to GoTrue)

Every request carries the headers `apikey: <publishable key>` and `Content-Type: application/json`. Once signed in, it also carries `Authorization: Bearer <access_token>`.

1. **Password:** `POST /auth/v1/token?grant_type=password` with `{email, password}`.
   - Returns `{access_token, refresh_token, expires_in, expires_at, user}`.
   - The token's `aal` claim is `aal1`.
2. **The account's second-factor state:** `GET /auth/v1/user` returns `factors: [{id, factor_type:'totp', status:'verified'|'unverified', friendly_name}]`.
3. **No verified TOTP factor yet: enroll one.**
   1. `POST /auth/v1/factors` with `{factor_type:'totp', friendly_name:'Roll Model admin'}`. Returns `{id, type:'totp', totp:{qr_code (an SVG data URI), secret, uri}}`.
      - Show the QR code and the secret. The person adds it to their authenticator app.
      - If an unverified factor already exists, delete it first with `DELETE /auth/v1/factors/<id>`, then enroll again.
   2. Verify it as in step 4.
4. **Verify a code.**
   1. `POST /auth/v1/factors/<factor id>/challenge` returns `{id: <challenge id>, expires_at}`.
   2. `POST /auth/v1/factors/<factor id>/verify` with `{challenge_id, code}` returns a new session `{access_token, refresh_token, expires_in, ..., user}`, now at `aal2`.
5. **Admin or not:** call `adm_whoami()` (below). If `admin` is false, show "This account isn't an admin" and sign out.
6. **Keep the session fresh:** `POST /auth/v1/token?grant_type=refresh_token` with `{refresh_token}`, a minute before `expires_at`. The new token keeps `aal2`.
7. **Sign out:** `POST /auth/v1/logout` (with the Bearer token), then forget the session.

**Session rules in the dashboard:**
- The session lives in `sessionStorage` only, so closing the tab signs out.
- 15 minutes without any input signs out.
- Nothing is shown until `adm_whoami` says `admin: true` at `aal2`.
- The JWT payload is base64url JSON; `aal` is read from it.

## Admin functions

All take named arguments and return JSON. Times are ISO 8601 strings in UTC; days are `YYYY-MM-DD` (UTC).
`p_days` is clamped to 1..180.

### `adm_whoami()`
Anyone signed in can call this. It only tells you about yourself.

```json
{ "id": "uuid", "email": "you@example.com", "aal": "aal2", "listed": true, "admin": true, "why": null, "code_at": "2026-10-18T09:00:00Z" }
```

- `admin` is true only when all four rules above hold.
- `listed` says whether the id is in `rm_admins` at all.
- `why` says what's missing when `admin` is false: `not_listed` (not an admin account), `needs_code` (signed in with the password only: ask for the authenticator code) or `stale` (the code was entered over 12 hours ago, or the session has ended: sign in again).
- `code_at` is when the authenticator code was entered (null before), so the dashboard can say when the session ends.

### `adm_overview(p_days int = 30)`
```json
{
  "now": "2026-10-18T12:00:00Z",
  "online": 37,                 // installs heard from in the last 5 minutes
  "dau": 812, "wau": 2950, "mau": 9100,   // installs heard from in the last 24 hours, 7 days, 30 days
  "installs": 15230,            // every install ever heard from
  "accounts": 2210,             // players with a username and password (not anonymous)
  "new_today": 140, "new_7d": 1012,
  "sessions_today": 1660, "avg_session_secs": 742,
  "retention": { "d1": 0.41, "d7": 0.18, "d30": 0.07,          // share of a cohort back on day N (null when there's no cohort yet)
                 "cohort_d1": 132, "cohort_d7": 951, "cohort_d30": 4020 },   // how many installs each share is out of
  "days": [ { "day": "2026-09-19", "dau": 640, "new": 120, "sessions": 1400, "matches": 3900,
              "ads": 210, "buys": 88, "dabs_spent": 31500, "dabs_earned": 54200, "play_secs": 1040000 } ]   // p_days rows, oldest first, every day present (zeros when nothing)
}
```
- `days[].dau` counts installs heard from on that UTC day; `ads` counts rewarded ads watched to the end.
- Retention: the installs that started 8 to 2 days ago make the day-1 cohort (14 to 8 days ago for day 7, 37 to 31 for day 30), so every cohort day is complete; the share is how many came back exactly N days after their first day.

### `adm_modes(p_days int = 30)`
```json
{
  "modes": [ { "mode": "duel", "plays": 5210, "wins": 2300, "losses": 2800, "draws": 110,
               "players": 3100,              // installs that ever played it
               "avg_secs": 91, "avg_cov": 38.5, // the player's own coverage %, average
               "online": 400 } ],            // of the plays, how many were online
  "days": [ { "day": "2026-09-19", "solo": 120, "duel": 900, "trio": 300, "ffa": 210, "duo": 90, "online": 40 } ],
  "stages": [ { "stage": "island", "plays": 1900 } ],   // plays per canvas, most first
  "diffs": [ { "diff": "easy", "plays": 2100 } ]        // plays per CPU difficulty, most first
}
```
Modes: `solo` (Time trial), `duel` (1v1), `trio` (3-way), `ffa` (Showdown), `duo` (Showdown 2v2). The window is the last `p_days` days, except `players`, which is all time.

### `adm_progress(p_steps text[] = null)`
Pass `p_steps` as the ids of `catalog.json` `tutorial`, in order (null uses the same list built into the database).
```json
{
  "ranks": [ { "rank": 1, "players": 4100, "active": 900 }, { "rank": 2, "players": 2900, "active": 610 } ],   // installs by their latest rank (ranks 1..50; 50 = 50 and up); active: of those, seen in the last 30 days
  "tutorial": [ { "step": "intro", "reached": 15230, "stuck": 0 }, { "step": "match", "reached": 14900, "stuck": 310 } ],
  "active_7d": 2950,
  "median_rank": 4,
  "done_pct": 0.62            // share of installs that reached "done" (basics complete)
}
```
- `tutorial` follows the order of `p_steps`; steps the database has seen that aren't in it come after.
- `median_rank` is over installs seen in the last 30 days.
- `reached` is how many installs ever got to that step.
- `stuck` is how many installs have it as their furthest step, haven't been seen for 3 days or more, and never reached `done`.

### `adm_economy(p_days int = 30)`
```json
{
  "items": [ { "item": "tophat", "views": 3100, "afford_views": 1200, "buys": 140, "dabs": 81200, "buyers_7d": 30,
               "price": 580,               // what the game charges now: the live price, else null (the dashboard then shows catalog.json's default)
               "last_buy": "2026-10-18T09:12:00Z" } ],
  "totals": { "dabs_earned": 1650000, "dabs_spent": 940000, "buys": 3400, "median_balance": 410 },   // median_balance: dabs held by installs active in the last 7 days
  "days": [ { "day": "2026-09-19", "buys": 88, "dabs_spent": 31500, "dabs_earned": 54200 } ],
  "strokes": [ { "stroke": "giant", "crafts": 420, "skips": 130 } ],   // Strokes crafts started, and of those finished early with an ad
  "earn": [ { "src": "match", "dabs": 1400000 } ]                       // where dabs came from: match, comm (Commissions), board (the Friends board's prize), lesson (the lessons' bonus), other
}
```
- `items` lists every item that was looked at, bought or given a live price; the dashboard adds the rest of `catalog.json` with zeros.
- `views`: times the item was looked at in the Paint Shop (tried on), counted once per install per item per day.
- `afford_views`: the views where the player could have bought it right then: it was in stock (sold outright, or already found on its canvas) and they had enough dabs. Items that have to be found first are marked `find: true` in `catalog.json`; their views before they're found don't count as affordable.

### `adm_ads(p_days int = 30)`
```json
{
  "placements": [ { "placement": "craft", "asked": 900, "shown": 820, "rewarded": 790, "failed": 80 } ],
  "days": [ { "day": "2026-09-19", "asked": 40, "shown": 36, "rewarded": 35, "failed": 4 } ]
}
```
Placements: `craft` (Skip a Strokes craft), `lesson` (Skip in the Strokes lesson, Ol' Bloop's own craft). These are rewarded ads only; the game has no other ads.

### `adm_iap(p_days int = 30)`
```json
{ "products": [ { "product": "dabs_500", "buys": 12, "revenue_cents": 5988 } ],
  "days": [ { "day": "2026-09-19", "buys": 1, "revenue_cents": 499 } ] }
```
The game has no real-money purchases yet. This stays empty until it does, and the dashboard says so.

### `adm_prices()`
```json
[ { "item": "tophat", "price": 450, "updated_at": "...", "updated_by": "you@example.com" } ]
```
Only the live overrides. Every other item uses its default from `catalog.json`.

### `adm_set_price(p_item text, p_price int)`
- Sets the live price for one item, or clears the override when `p_price` is null.
- `p_item` must match `^[a-z0-9_]{1,32}$`; `p_price` must be 0..100000.
- Returns `{ "ok": true }` or `{ "ok": false, "why": "item" | "range" | "slow_down" }`.
- Writes an audit row.

### `adm_find(p_q text)`
Searches players with a profile:
- a username, case-insensitive, starting with `p_q`;
- an exact friend code (8 characters; spaces ignored);
- an exact user id (uuid).

```json
[ { "id": "uuid", "name": "Dusk", "code": "ABCD2345", "rank": 7, "account": true, "created_at": "...", "last_seen": "..." } ]
```
At most 25 rows, best matches first. `p_q` must be 2..40 characters (else `[]`).

### `adm_player(p_id uuid)`
```json
{
  "id": "uuid", "name": "Dusk", "code": "ABCD2345", "rank": 7, "look": {},
  "account": true, "anonymous": false,
  "created_at": "...", "last_sign_in_at": "...", "last_seen": "...", "status": "offline",
  "friends": 4, "blocked_by_them": 0,
  "details": { "first_name": "Dana", "last_name": "Lee", "birth_year": 2001, "terms": "2026-10", "agreed_at": "..." },   // null without an account
  "save": { "rank": 7, "xp": 2600, "drops": 900, "items": 6, "at": "..." },      // null when there's no saved copy
  "installs": [ { "iid": "uuid", "platform": "ios", "app_ver": "1.1", "game_ver": 354, "first_at": "...", "last_at": "...",
                  "sessions": 40, "matches": 120, "tut": "done" } ],
  "audit": [ { "at": "...", "admin": "you@example.com", "action": "set_password", "detail": {} } ]
}
```
Returns `null` when there's no such player.
- `details` is what the player typed when making their account. Ask for it before resetting a password, to check it's really them.
- `blocked_by_them` is how many players have blocked this one.

### `adm_set_password(p_id uuid, p_password text)`
- Sets a new password, then signs the player out everywhere.
- The password must be 8..72 characters with at least one letter and one digit.
- Returns `{ "ok": true }` or `{ "ok": false, "why": "weak" | "missing" | "anonymous" | "admin" | "slow_down" }`. `anonymous` means the player has no account to sign in with.
- Signing out ends every session at once; a device that's already in keeps working for up to an hour (until its token expires), then has to log in again.
- Writes an audit row. The password itself is never stored or logged.

### `adm_signout(p_id uuid)`
Signs the player out on every device. Returns `{ "ok": true, "sessions": 2 }`, or `{ "ok": false, "why": "missing" | "admin" | "slow_down" }`. Writes an audit row.

### `adm_delete_player(p_id uuid, p_confirm text)`
- Deletes the player and everything of theirs, exactly as the in-game Delete account does.
- `p_confirm` must equal their username, case-insensitive; it's a typed confirmation. A player with no username yet is confirmed with their user id.
- Their install analytics stay, but are no longer linked to them.
- Returns `{ "ok": true }` or `{ "ok": false, "why": "confirm" | "missing" | "admin" | "slow_down" }`.
- Writes an audit row with their name and id.

### `adm_audit(p_limit int = 100)`
```json
[ { "at": "...", "admin": "you@example.com", "action": "set_price", "target": "tophat", "detail": { "from": null, "to": 450 } } ]
```
Newest first, at most 500. Actions: `set_price`, `set_password`, `signout`, `delete_player`.

## What the game sends

### `rm_track(p_iid uuid, p_meta jsonb, p_ev jsonb)`
- Who can call it: anyone (`anon` and `authenticated`).
- The game batches events and sends them about once a minute, and when the app is put away.
- When the player is signed in, the call carries their token, and the install is linked to their user id (`auth.uid()`). It's never taken from the body.
- Returns `{ "ok": true, "v": 1760780000000 }`, `{ "ok": false, "why": "rate" }` (more than 120 calls an hour from one install, or a flood of new installs), or `{ "ok": false, "why": "bad" }`.
- `v` is the live prices' version, as in `rm_config()`. When it differs from the one the game has, the game asks `rm_config()` again, so a price change reaches players within about a minute.

**`p_iid`:** a random id made once per install, kept in the save.

**`p_meta`:** the install's state now.

```json
{ "plat": "ios", "av": "1.1", "gv": 354, "rank": 7, "xp": 2600, "dabs": 900, "tut": "done", "secs": 63 }
```
- `plat` is `ios` | `web`.
- `secs` is the seconds played since the last call. The server caps it at 3600.

**`p_ev`:** an array of at most 60 events. Unknown kinds and fields are dropped; strings are capped at 32 characters; numbers are clamped.

| `k` | Fields | Counts as |
|---|---|---|
| `open` | (none) | A session starting (launch, or back after 30 minutes away). |
| `tut` | `s`: step id (`catalog.json` `tutorial`) | That step reached, once per install. |
| `match` | `m` (mode), `on` (online, bool), `r` (`win`\|`loss`\|`draw`), `cov` (0..100), `ko` (0..99), `s` (seconds, 0..600), `st` (canvas id), `d` (`easy`\|`hard`\|...) | A match played to its end. |
| `earn` | `src` (`match`\|`comm`\|`board`\|`lesson`\|`other`), `n` (dabs, 0..100000) | Dabs earned. |
| `view` | `i` (item id), `a` (could buy it right then: in stock and enough dabs, bool) | The item looked at in the Paint Shop (the game sends it once per item per session). |
| `buy` | `i` (item id), `p` (dabs paid) | An item bought with dabs. |
| `craft` | `i` (stroke id) | A Strokes craft started. |
| `skip` | `i` (stroke id) | A craft finished early with a rewarded ad. |
| `ad` | `pl` (`craft`\|`lesson`: the Strokes lesson's own craft), `r` (`ask`\|`shown`\|`reward`\|`fail`) | A rewarded ad's progress (in the iPhone app; the web page has no real ads). |
| `rank` | `n` (1..999) | A new rank reached. |
| `iap` | `pr` (product id), `c` (cents) | A real-money purchase (none in the game yet). |

### `rm_config()`
- Who can call it: anyone.
- What it returns: the live overrides, `{ "v": 1760780000000, "prices": { "tophat": 450 } }`, where `v` is when they last changed (ms since 1970, 0 when there are none).
- **When the game asks:** at launch and when it comes back to the foreground, at most every 10 minutes.
- **How it uses them:** it keeps the last answer in the save, so prices hold offline, and applies them in `PRICE()`.
