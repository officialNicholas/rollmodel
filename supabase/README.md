# Roll Model on Supabase

Friends (codes, requests, who's online, blocks, invites) and the Friends leaderboard live in your Supabase project. The game
talks to it directly from the phone over Supabase's REST API. The database only answers through a set of functions
(`rm_*`) that check who's asking, so a player can never read or change anything they shouldn't.

## Switching it on (about 5 minutes, once)

1. **Allow anonymous sign-ins.** Dashboard > Authentication > Sign In / Providers > turn on **Allow anonymous sign-ins**.
   Players get an account without an email the first time they open the game. Linking Sign in with Apple later keeps
   the same account, and so the same friends.
2. **Create the tables and functions.** Dashboard > SQL Editor > New query. Paste the whole of
   `supabase/migrations/20261015000000_friends.sql` and press **Run**. It's safe to run again later.
3. **Send me two values.** Dashboard > Project Settings > API Keys (or Data API):
   - the **Project URL** (`https://<something>.supabase.co`);
   - the **publishable key** (`sb_publishable_...`), or the older **anon public** key if that's what the project shows.

   Both are public by design: they ship inside the app. **Never send the secret or service_role key.**

I put the two values in `tools/online_config.json` and rebuild. Until then the game builds with online play off, and
the Friends screen says friends are on the way.

## What's in the database

| Table | Holds |
|---|---|
| `profiles` | Name, look (paint colour, eyes), rank, the 8-character friend code, and when the player was last online |
| `friend_requests` | Pending requests (deleted once accepted, declined or cancelled) |
| `friendships` | One row per pair of friends |
| `blocks` | Who blocked whom |
| `invites` | Invites to a private duel (room code from the game server, 2 minutes to answer) |
| `trial_scores` | Each player's best Time trial run per canvas per week |
| `rate_events` | Recent actions, for the rate limits |

Row level security is on for every table, with no policies, and the app's roles have no table access. Everything goes
through these functions:

| Function | Does |
|---|---|
| `rm_me(name, look, rank)` | Makes your profile the first time, updates it after; returns your friend code |
| `rm_inbox(status)` | Everything the Friends screen shows, in one call; also marks you online (`lobby` / `match` / `offline`) |
| `rm_add_friend(code)` | Sends a request, or makes you friends at once if they'd already asked you |
| `rm_answer_request(from, accept)`, `rm_cancel_request(to)`, `rm_remove_friend(other)` | Requests and friends |
| `rm_block(other)`, `rm_unblock(other)` | A block removes the friendship and any requests, and silently drops their requests later |
| `rm_invite(to, room, mode)`, `rm_answer_invite(id, accept)`, `rm_cancel_invite(id)` | Invites to a private duel |
| `rm_trial(stage, pct)`, `rm_friends_board(stage, week)` | Time trial runs, and the board of you and your friends |

Limits:
- 30 friend-code tries an hour (wrong codes count, so codes can't be guessed);
- 50 pending requests out, 100 in;
- 200 friends;
- 40 invites an hour;
- 120 Time trial runs an hour.

## Testing it without the real project

`supabase/tests/` runs the migration on a plain local Postgres, with `local_stub.sql` standing in for what Supabase
provides (its roles, `auth.users`, `auth.uid()`). Never run the stub on the real project.

```
cd supabase/tests && npm install
PGURL=postgres://postgres@localhost:54329/rmtest npm test
```

The game itself was also tested against a small stand-in for Supabase's sign-in and API, with two browsers adding each
other (see `docs/friends-v305.md`).

## Not on trust yet

- **Time trial runs:** the phone reports them, so a Friends board is on the honour system until the game server checks
  runs. That's fine between friends, but not for a Global board with prizes.
- **Rank:** also comes from the phone. It's only shown to friends.
