# App Review, second try (game v436)

Apple rejected Roll Model 1.0 (19) for two things:

- **2.1(a), information needed:** a demo account with full access, and content already in it to review (Friends).
- **2.1(b), in-app purchases not submitted:** the app sells dab packs, but the products weren't sent with the build.

## What changed in the game (v436)

- **Report a player** (guideline 1.2, user-generated content). On the Friends page, the ••• menu by a friend, by someone
  asking to be your friend, and by anyone in the new **Played online recently** list (real players from your last online
  matches, never the CPUs) has **Report**. You pick a reason (Offensive name, Cheating, Bullying, Something else), can tick
  **Block them too**, and the report goes to the database (`supabase/migrations/20261023000000_reports.sql`). A name
  reported by three different players is swapped for a neutral one (`player_xxxxxxxx`) straight away, and its owner is asked
  for a new one. The Friends page's fine print now says there's no chat and how to report or block.
- **Nothing reads as unfinished** (guideline 2.1): the Strokes page's "More soon" filler cards are gone, and the few
  messages that said "coming soon" (a party mode switched off, emails when the server has none) now say what's true.

## The demo accounts

`supabase/review/app_review_accounts.sql` makes two accounts, both rank 13 (every mode, Stroke, skill and item open),
25,000 dabs, friends with each other, with Time trial scores on three canvases this week:

- **@rollreview**, the one App Review signs in with;
- **@rollreviewpal**, its friend, so the Friends page has someone on it.

Put two passwords of your own in place of `CHANGE-ME-1` and `CHANGE-ME-2` (in a copy you don't commit), then run it in
Supabase > SQL Editor, **after** the reports migration. Run it again any time to reset both accounts (password,
progress, friendship). It refuses to touch a name that belongs to a real player. The scores are made for the week it's
run, so run it again the day you submit.

## Before you submit

1. Supabase > SQL Editor: run `supabase/migrations/20261023000000_reports.sql`, then your filled copy of the demo SQL.
2. App Store Connect > the app > **In-App Purchases**: for each of the four consumables
   (`studio.primeshots.rollmodel.dabs400`, `dabs2500`, `dabs5500`, `dabs12000`): display name, description, price, and a
   **review screenshot** (the Get Dabs sheet is fine). Each must say **Ready to Submit**.
3. On the version page, under **In-App Purchases and Subscriptions**, add all four, so they go with the build.
4. **App Review Information:** tick **Sign-in required**, username `rollreview` and its password. Paste the notes below.
5. **App Privacy:** the app doesn't ask for tracking permission (no App Tracking Transparency prompt), so the answers must
   not say any data is "used to track you". If they do, change them; otherwise the next review asks for the prompt.
6. Upload the new build (the next build number), pick it for the version, submit.

## Notes for the reviewer (paste into App Review Information > Notes)

Thank you for the review. Here is everything needed to see the whole app.

SIGNING IN
- Demo account: username rollreview (password in the sign-in fields above). No email is needed: accounts sign in with a
  username and password.
- To sign in on a fresh install: on the loading screen, tap "I already have an account" under the loading bar, then enter
  the username and password. (If the intro has already started: Settings > Account > Log in.) The account's progress then
  loads: rank 13, so every mode, Stroke and item is open, with 25,000 dabs to spend.

FRIENDS AND PLAYING ONLINE
- The Friends page (the faces button in the lobby) already shows a friend, @rollreviewpal, a second demo account we made so
  you can see the page with content: their name, look, rank and when they were last online, plus the friend code system
  for adding people.
- That friend is a demo account, so it will usually show as offline and won't accept an invite or join a match during
  your review. Online play works without it: Play > Play online > pick a mode starts matchmaking with real players near the
  same rank. If nobody else is looking at that moment, after 30 seconds the game offers "Play the CPU" instead, so you can
  always play. Every mode (Versus 1v1, 3-way, Showdown, Time trial) can also be played offline against the CPU from Play.
- After a Time trial run, the trophy button shows that canvas's leaderboard for the week, with the demo accounts' scores on
  Palette Island, Blank Canvas and the Fishing Raft.

THERE IS NO CHAT
- Roll Model has no chat of any kind: no text, voice or private messages. Players can't send each other words or
  pictures. The only things one player sees of another are their username, their character's look (paint colour, eyes,
  worn items, all from the game's own set) and their rank. In a match, the only "messages" are a fixed set of emotes
  (pictures from the game), with nothing typed.
- Usernames are checked when they're made: a word filter blocks offensive names, and names must be unique.

REPORT AND BLOCK
- On the Friends page, tap ••• by any player (a friend, someone who sent you a friend request, or anyone in "Played online
  recently") for Report and Block. Report asks for a reason (offensive name, cheating, bullying, something else) and can
  block the player in the same step. Blocking ends a friendship, and a blocked player can't send you friend requests or
  party invites.
- We review every report within 24 hours. A name reported by three different players is replaced with a neutral one
  straight away until we've looked at it, and we can reset names or delete accounts that break our terms.
- Players can delete their account and all its data in the app: Settings > Delete account (at the bottom).

IN-APP PURCHASES
- The four products are consumable packs of dabs, the in-game currency: studio.primeshots.rollmodel.dabs400,
  dabs2500, dabs5500 and dabs12000. They're on the Get Dabs page (the + by the dabs
  counter at the top of the lobby).
- Dabs can also be earned by playing (wins, daily jobs, the free daily spin), so nothing requires a purchase.
- Bonus: any purchase also turns off the occasional between-match ad for that player. It isn't sold on its own, and it
  stays with the player's account (it comes back on a new phone after signing in), since it's part of their saved
  progress.

ADS
- Ads are Google AdMob: an optional rewarded ad the player chooses to watch (to finish a Stroke being crafted, or skip the
  first lesson), and an occasional ad between matches. All are capped at a parental guidance rating, and a player who
  said they're under 13 gets only child-appropriate, non-personalised ads. No tracking permission is requested and none
  is used.

AGE AND PRIVACY
- An account asks for a first name, a birth year and agreement to the terms. Privacy policy and terms are in Settings and
  at playrollmodel.com. Contact: support@playrollmodel.com.

Thank you!
