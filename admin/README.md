# Roll Model admin

The dashboard for running Roll Model before and after launch: live numbers, the Paint Shop's prices, and customer support.
It's a static website with no server code of its own. It signs in with Supabase Auth and asks the game's Supabase project
for everything, through the database functions in `supabase/migrations/20261018000000_liveops.sql` (and, for account
emails, `20261019000000_email.sql`).

## What's in it

| Page | What you see and do |
|---|---|
| Overview | Who's playing: online now, daily, weekly and monthly active, new installs, accounts, sessions, how long they play, and how many come back after 1, 7 and 30 days |
| Players | Ranks, and the tutorial step by step: how many reach each step, and how many stopped there and haven't been back for 3 days |
| Modes | Plays per mode, the favourite, wins and losses, coverage, online share, canvases and CPU difficulty |
| Economy | Every item with its price, looks, buys and buyers; dabs earned and spent; Strokes crafts. Change a price here: players get it within a minute |
| Ads | Rewarded ads asked for, shown, finished and failed, per placement |
| Purchases | Real-money purchases, once the game has any (it has none yet) |
| Insights | Suggestions worked out from the numbers, each with the numbers behind it |
| Support | Find a player by username, friend code, email or id; see their account; email them a reset link, give them a new password, sign them out everywhere, or delete their account |
| Audit log | Every change made from the dashboard: who, when, what |

## How it's kept safe

- **No secret key anywhere.** The site holds only the Project URL and the publishable key, which are public by design and
  already inside the game. Never put the secret or service_role key in it.
- **The database decides who's an admin, on every call.** Someone is an admin only if all of these hold:
  1. their account is in the `rm_admins` table, which only you can change, in the Supabase SQL editor;
  2. they signed in with their password and a code from an authenticator app;
  3. that code was entered in the last 12 hours;
  4. that sign-in hasn't ended (signing out cuts access at once).

  A copy of the website, or a hand-made request, gets nothing without all four.
- **Every change is written to the audit log**, and the dashboard can't edit or delete it.
- **Each admin has an hourly limit:** 30 deleted accounts, 60 password resets (reset links count too), 60 sign-outs and
  300 price changes. Even a stolen admin sign-in can only do so much before you take it off the list.
- **Admin accounts can't be changed from the dashboard:** no password reset, sign-out or delete of anyone in `rm_admins`.
- **The website itself:**
  - It runs no third-party code.
  - A strict Content Security Policy lets only its own scripts run, and lets it talk only to your Supabase project.
  - It can't be put inside another site's frame, and search engines are told not to list it.
  - The sign-in lives only in that browser tab, so closing the tab signs you out.
  - 15 minutes without a click or a key signs you out.

## Setting it up (once, about 10 minutes)

1. **Run the SQL.** Supabase > SQL Editor > New query: paste all of `supabase/migrations/20261018000000_liveops.sql` and
   press Run. Do it after the other files listed in `supabase/README.md`. It's safe to run again. Then do the same with
   `20261019000000_email.sql` for account emails (see Email below).
2. **Check that authenticator apps are on.** Supabase > Authentication > Multi-Factor (or Sign In / Providers): TOTP (app
   authenticator) should be enabled. It is by default.
3. **Make your admin account.** Supabase > Authentication > Users > Add user > Create new user:
   - your real email;
   - a long password you use nowhere else;
   - tick "Auto Confirm User".
4. **Make it an admin.** In the SQL editor, with your email:
   ```sql
   insert into public.rm_admins (id, note) select id, 'owner' from auth.users where email = 'you@example.com';
   ```
5. **Sign in to the dashboard** with that email and password. The first time, it shows a QR code:
   1. scan the code with an authenticator app (1Password, Google Authenticator, Microsoft Authenticator, Authy...);
   2. type in the 6-digit code it shows.

   From then on, every sign-in asks for a code from that app.

If the dashboard says the database isn't set up for admin sign-in, step 1 hasn't been run (or ran into an error: run it
again and read the message at the bottom of the SQL editor).

### Adding or removing an admin
- **Add:** do steps 3 and 4 for their email. They set up their own authenticator app the first time they sign in.
- **Remove:** in the SQL editor:
  ```sql
  delete from public.rm_admins where id = (select id from auth.users where email = 'them@example.com');
  ```
  It takes effect at their next click.

### Lost the phone with the authenticator app?
In the SQL editor, remove the app from the account, then sign in and set it up again:
```sql
delete from auth.mfa_factors where user_id = (select id from auth.users where email = 'you@example.com');
```
Only someone who can sign in to the Supabase dashboard can do this, which is the point.

## Customer support
- **"I forgot my password":**
  - Best: they tap **Forgot password?** on the game's Log in (or on the website's Forgot password page) and get a link
    by email. That works once they've confirmed their email.
  - From the dashboard: find them under Support and press **Send reset link**. It goes to their confirmed email, works
    once for 30 minutes, and nobody else ever sees the new password.
  - No confirmed email? Check it's really them: ask for the first and last name and birth year on the account (shown
    under Account details) and their friend code. Then **Reset password**: the dashboard makes a strong temporary one
    for you to give them. They log in with their username and that password, and are signed out on every other device.
- **"Delete my account":** search for them, then Delete account; type their username to confirm. It's the same as the
  in-game Delete account, and can't be undone.

## Email
The game sends three emails: a welcome that confirms the address, a password-reset link, and a note when a password
changes. They go out through Resend, straight from the database. Until it's switched on, the game still takes emails
(and keeps them for later), Send reset link says nothing went out, and nothing else changes.

To switch it on (after the domain and Resend are set up, see `site/README.md`):
1. **Put the Resend API key in Supabase Vault yourself.** In the SQL editor, with your key:
   ```sql
   select vault.create_secret('re_your_key_here', 'resend_api_key');
   ```
   The key never goes in the website, the game or this repository, and never needs to be sent to anyone.
2. **Turn on pg_net:** Supabase > Database > Extensions > pg_net (the email SQL tries to turn it on itself).
3. **Tell it where things are,** with your domain:
   ```sql
   update public.rm_settings set v = jsonb_build_object('paused', false, 'site', 'https://playrollmodel.com',
     'sender', 'Roll Model <hello@mail.playrollmodel.com>', 'support', 'support@playrollmodel.com') where k = 'mail';
   ```
4. **Try it:** in the game, make an account with your own email. The welcome should arrive within a minute. The
   `public.mail_log` table lists every email sent or refused (no addresses or links in it).

To pause all emails: `update public.rm_settings set v = v || '{"paused": true}' where k = 'mail';`

## Hosting
Recommended: **Cloudflare Pages, behind Cloudflare Access**, at `admin.<your domain>`. Free, and Access puts a second
sign-in (a code emailed to an address you allow) in front of the page itself, before anyone sees even the sign-in form.

1. Build the folder to upload: `sh admin/deploy/build.sh` makes `admin/dist/` with only the files the site needs and its
   security headers (`_headers`). Never upload `admin/` itself: `dev/` and `tests/` hold a mock with fake accounts.
2. Cloudflare > Workers & Pages > Create > Pages > Upload assets: name it `rollmodel-admin` and drop `admin/dist` in.
3. Its Custom domains tab: add `admin.<your domain>`.
4. Cloudflare Zero Trust > Access > Applications > Add > Self-hosted: domain `admin.<your domain>`, and a policy that
   allows only your email (and each admin's). Also protect the `rollmodel-admin.pages.dev` address the same way (or turn
   off its preview URLs), so the page can't be reached around Access.

Each time the dashboard changes, build and upload again.

## Running it on your computer
- With made-up numbers: `node admin/dev/mock.mjs`, then open http://localhost:8791 and sign in as admin@example.com /
  correct-horse-9 (the authenticator code is always 123456). `MOCK=empty` starts from an empty launch.
- Unit tests: `node --test admin/tests/`. In a browser, against the mock: `node admin/tests/e2e.mjs`.
- Against the real database code: start the local Postgres and `supabase/tests/standin.mjs` (see `supabase/README.md`,
  "Testing it without the real project"), then `node admin/tests/live.mjs`. It signs in with a real authenticator code
  and goes through every page, a price change reaching the game, and every support action, with throwaway accounts it
  deletes afterwards.

## What the security rests on in Supabase Auth
The admin check (`public._adm()`) relies on how Supabase Auth issues sign-ins. If Supabase ever changes these, the
dashboard stops letting anyone in (it fails closed), and the SQL needs a look:
- the access token carries `aal` (`aal2` after an authenticator code), `amr` (with a `totp` entry and the time of that
  code, which stays the same when the token is refreshed) and `session_id`;
- ended sign-ins disappear from `auth.sessions`, and the database's owner can read that table.
