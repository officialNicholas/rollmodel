# Roll Model on Supabase

Usernames and accounts (v306), progress kept with an account (v312), friends (codes, requests, who's online, blocks,
party invites, v391) and the Friends leaderboard live in your Supabase project. The game talks to it directly from the phone over Supabase's REST API. The database only answers
through a set of functions (`rm_*`) that check who's asking, so a player can never read or change anything they
shouldn't.

## Switching it on (about 5 minutes, once)

1. **Allow anonymous sign-ins.** Dashboard > Authentication > Sign In / Providers > turn on **Allow anonymous sign-ins**.
   Players get an account without an email the first time they open the game. Linking Sign in with Apple later keeps
   the same account, and so the same friends.
2. **Turn off email confirmation.** Dashboard > Authentication > Sign In / Providers > Email > turn off **Confirm
   email**. A player's account signs in with their username and password; behind the scenes it uses a made-up address
   (`u<account id>@rollmodel.invalid`) that can't receive mail, so a confirmation email could never arrive.
3. **Create the tables and functions.** Dashboard > SQL Editor > New query. Paste the whole of each file below, in this
   order, and press **Run** each time. All are safe to run again later.
   1. `supabase/migrations/20261015000000_friends.sql`
   2. `supabase/migrations/20261015010000_accounts.sql`
   3. `supabase/migrations/20261016000000_saves.sql` (v312: progress kept with the account. Until it's run, logging in
      on a new phone works but brings no progress back, and Log out keeps this phone's progress, as before)
   4. `supabase/migrations/20261018000000_liveops.sql` (v354: play stats, live prices and the admin dashboard's functions.
      Until it's run, the game plays as before with its own prices, and the dashboard says the database isn't ready.
      Making yourself the admin is in `admin/README.md`)
   5. `supabase/migrations/20261019000000_email.sql` (v355: players' emails, the welcome email, Forgot password and the
      reset link, the "password changed" notice. Sending them needs three more things, at the top of that file: pg_net
      turned on, your Resend key in the Vault, and your website and addresses. Until then, emails are saved but not sent)
   6. `supabase/migrations/20261020000000_parties.sql` (v391: invites to a party, the inbox that shows them, and each
      iPhone's token for notifications while the game is closed. Until it's run, the + spots in the lobby say invites
      need a database update, and older games carry on as before. The notifications also need the APNs key on the game
      server: `docs/party-v391.md`)
4. **Send me two values.** Dashboard > Project Settings > API Keys (or Data API):
   - the **Project URL** (`https://<something>.supabase.co`);
   - the **publishable key** (`sb_publishable_...`), or the older **anon public** key if that's what the project shows.

   Both are public by design: they ship inside the app. **Never send the secret or service_role key.**

I put the two values in `tools/online_config.json` and rebuild. Until then the game builds with online play off, and
the Friends screen says friends are on the way.

## What's in the database

| Table | Holds |
|---|---|
| `profiles` | Username, look (paint colour, eyes), rank, the 8-character friend code, and when the player was last online |
| `accounts` | For players who made an account: first and last name, birth year (since v307 the game sends only the year, as its 31 December), and which terms they agreed to and when. Only the player can read it |
| `saves` | For players who made an account: a copy of their progress (rank, drops, everything bought, crafted and unlocked, lessons done), so logging in on another phone brings it back. Only the player can read it. Since v312 |
| `friend_requests` | Pending requests (deleted once accepted, declined or cancelled) |
| `friendships` | One row per pair of friends |
| `blocks` | Who blocked whom |
| `invites` | Invites to a party (its join code from the game server; the v306 to v390 games invited to a duel room), 2 minutes to answer, and whether its notification has gone |
| `push_tokens` | Since v391, one row per iPhone that said yes to notifications: its APNs device token, whether it's an Xcode build, and the account signed in on it now. Nobody reads it but `rm_invite_push` |
| `trial_scores` | Each player's best Time trial run per canvas per week |
| `rate_events` | Recent actions, for the rate limits |
| `rm_installs` | Since v354, one row per install of the game: a random id (no name, no device id), platform and versions, when it was first and last heard from, its rank, dabs and tutorial step now, the tutorial steps and modes it has reached, and running totals. Linked to the player while they're signed in; unlinked when they delete their account |
| `rm_daily` | Since v354, counters per day for the whole game: active installs, sessions, matches per mode and canvas, Paint Shop views and buys per item, dabs earned and spent, rewarded ads, ranks reached |
| `rm_buys` | Since v354, every Paint Shop buy: which install, which item, the price and when |
| `rm_prices` | Since v354, the live prices set in the dashboard (only the items whose price was changed) |
| `rm_admins` | The dashboard's admins. Only you add them, here in the SQL editor |
| `rm_audit` | Every change made in the dashboard: who, when, what (prices, password resets, sign-outs, deleted accounts) |
| `rm_settings` | Switches: the stats (paused, how many new installs a minute and a day) and the emails (paused, the website, the sender and support addresses) |
| `account_emails` | Since v355, each account's email and when it was confirmed. Private: other players never see it, and sign-in stays by username |
| `mail_tokens` | The one-time links in emails (confirm, 24 hours; reset, once in 30 minutes). Only a hash of each is kept |
| `mail_log` | What was sent and when, for checking delivery (no addresses) |
| `mail_templates` | The emails themselves (from `email/`, put here by the migration) |

Row level security is on for every table, with no policies, and the app's roles have no table access. Everything goes
through these functions:

| Function | Does |
|---|---|
| `rm_name_check(name)` | Anyone, even before signing in: is this username allowed, and is it free? |
| `rm_me(name, look, rank)` | Makes your profile the first time (only with a clean, free username), updates the rest after; never renames you; returns your friend code and whether you have an account. Since v308 the game calls it only when the player makes an account (or has one), so a name is held from then on |
| `rm_rename(name)` | A new username (clean and free; 10 tries an hour) |
| `rm_login_email(name)` | The made-up address a username signs in with (nothing for a player without an account) |
| `rm_account_save(first, last, birthday, terms)`, `rm_account()` | The account details (13 or older; the game passes the birth year as its last day, so a player counts as 13 only once that's certain), and reading your own back |
| `rm_save_put(data)`, `rm_save_get()` | Keeps a copy of your progress (accounts only), and reads it back. A copy with less rank than the one kept is refused (`behind`), so a phone left behind can't wipe out progress made on another |
| `rm_delete_me()` | Deletes the player and everything of theirs (saved progress too), and frees the username |
| `rm_inbox2(status)` | Everything the Friends screen and the inbox show, in one call, with party invites; also marks you online (`lobby` / `match` / `offline`) |
| `rm_inbox(status)` | The same for the v306 to v390 games, which only know duel invites (party invites are left out) |
| `rm_add_friend(code)` | Sends a request, or makes you friends at once if they'd already asked you; says who it went to, so the game can nudge their game |
| `rm_answer_request(from, accept)`, `rm_cancel_request(to)`, `rm_remove_friend(other)` | Requests and friends |
| `rm_block(other)`, `rm_unblock(other)` | A block removes the friendship and any requests, and silently drops their requests later |
| `rm_invite(to, code, mode)`, `rm_answer_invite(id, accept)`, `rm_cancel_invite(id)` | Invites to a party (`mode` 'party', the party's 8-character code); friends only, never across a block |
| `rm_push_token(token, env)`, `rm_push_forget(token)` | This iPhone's notification token, for the player signed in (a token belongs to one account at a time; 5 phones each), or taken away (logging out) |
| `rm_invite_push(id)` | The game server, as the player who sent the invite: one open party invite's notification (who it's to, the sender's username, their phones), once per invite |
| `rm_trial(stage, pct)`, `rm_friends_board(stage, week)` | Time trial runs, and the board of you and your friends |
| `rm_track(iid, meta, events)` | Anyone: the game's play stats, in batches (about once a minute). 120 calls an hour per install, 60 events per call, every value checked and clamped. A signed-in player's install is linked to them by their token, never by what the game sends |
| `rm_config()` | Anyone: the live prices |
| `adm_*` | The admin dashboard's functions (`admin/API.md`). Each checks that the caller is listed in `rm_admins` and signed in with an authenticator-app code in the last 12 hours, else refuses |
| `rm_email_get()`, `rm_email_set(email)`, `rm_email_resend()` | Your email: read it, save it (accounts only; 5 changes an hour) and get the welcome email with its confirm button, or get it again |
| `rm_email_verify(token)`, `rm_reset_request(who)`, `rm_reset_password(token, password)` | Anyone (the website's pages): confirm an email; Forgot password (a username or an email; it never says whether the account exists, and sends at most 3 an hour to an account); set a new password from a reset link, which signs the player out everywhere |

Usernames: 3 to 16 letters, digits and underscores with at least one letter, unique however they're capitalised. Bad
words are refused however they're spelt (capitals, digits for letters, underscores between letters), with a short list
of real words that only look bad (Scunthorpe, Cockatoo, Therapist...). Names that pretend to be staff (admin,
moderator, official, the game's own names) are reserved.

Accounts: a player starts anonymous. Making an account (when online play unlocks) sets a password on that same player,
so friends and progress stay; then the details are saved with `rm_account_save`. To sign in on another phone the game
looks up the username's address with `rm_login_email` and signs in with the password.

Progress (v312): while a player is signed in to an account, the game keeps a copy of their progress with it
(`rm_save_put`, at most every 30 seconds while it changes, and when the app is put away). Logging in, on a new phone
or from the first loading screen ("I already have an account"), brings it back (`rm_save_get`). Logging out keeps it
there and starts the phone fresh for the next player. Settings that belong to the phone (sound, graphics, screen
orientation) stay with the phone.

Limits:
- 30 friend-code tries an hour (wrong codes count, so codes can't be guessed);
- 50 pending requests out, 100 in;
- 200 friends;
- 40 invites an hour (an invite lasts 2 minutes);
- 30 notification token updates an hour;
- 120 Time trial runs an hour;
- 240 progress saves an hour, each up to 200 kB;
- 120 batches of play stats an hour per install, and at most 600 new installs a minute for the whole game.

## Testing it without the real project

`supabase/tests/` runs the migrations on a plain local Postgres, with `local_stub.sql` standing in for what Supabase
provides (its roles, `auth.users`, `auth.uid()`). Never run the stub on the real project. Load the stub, then the
migrations in order, into an empty database first (`psql -f`).

```
cd supabase/tests && npm install
PGURL=postgres://postgres@localhost:54329/rmtest npm test
```

The game itself was also tested against a small stand-in for Supabase's sign-in and API, with two browsers adding each
other (see `docs/friends-v305.md`).

## Not on trust yet

- **Play stats:** like any mobile analytics, they come from the phones, and the publishable key that sends them is public.
  The limits above stop a flood, but someone determined could add made-up installs. Read the numbers as trends.
  Real-money purchases, once the game has them, should be counted from the App Store's own reports, not from these.

- **Time trial runs:** the phone reports them, so a Friends board is on the honour system until the game server checks
  runs. That's fine between friends, but not for a Global board with prizes.
- **Rank:** also comes from the phone. It's only shown to friends.
