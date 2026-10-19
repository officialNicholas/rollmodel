# Roll Model for iPhone and iPad

Everything happens in Xcode and App Store Connect. No Terminal needed.

This is the same app you already have in App Store Connect: bundle ID `studio.primeshots.rollmodel`, the paint roller icon. A build of it goes up as an update to that app, not a new one.

## Send this update to TestFlight

1. Double-click **RollModel.xcodeproj** to open it in Xcode.
2. In the left sidebar, click the blue **RollModel** project, select the **RollModel** target and open **Signing & Capabilities**. Leave "Automatically manage signing" on and pick the same team you used before under **Team**.
3. Open the **General** tab. The version is **1.1** and the build is **2**. If App Store Connect already has a 1.1, raise the version (for example to 1.2).
4. Set the run destination at the top of the window to **Any iOS Device (arm64)**, then choose **Product > Archive**.
5. When the Organizer opens, click **Distribute App**, choose **TestFlight & App Store** (or **TestFlight Internal Only**) and leave **Manage Version and Build Number** checked. Click **Distribute**.
6. After 10 to 30 minutes the build appears under **TestFlight** in your Roll Model app in App Store Connect. Testers get it as an update in the TestFlight app.

## Try it on your iPhone first (optional)

Plug in your iPhone, pick it as the run destination and press **Run**. The first time, the phone asks you to turn on Developer Mode in Settings > Privacy & Security.

## iPhone Duo

- **Build with Xcode 27.1 or newer** (the iOS 27.1 SDK). Built with an older Xcode, the app still runs on iPhone Duo but in a smaller window: in the middle of the open screen, and beside the status bar and camera on the closed one.
- **Open or closed, any way round:** the game takes the shape it's given. On iPhone Duo (or any near-square window) it never asks how you hold it and never asks you to turn the phone; on other iPhones the upright or wide choice works as before. (OrientBridge.swift, GameViewController.swift)
- **Folding or opening mid-match pauses it,** so you can settle your grip; the screen's sharpness is set again for the new size.
- **No more "Hang Risk" warnings:** the sound settings (AVAudioSession) now change off the main thread, so the screen never waits on them. (AppDelegate.swift, SceneDelegate.swift, AdsBridge.swift)
- **The screen's scale and refresh rate come from the game's own window,** not the main screen, since iPhone Duo has two. (DeviceBridge.swift)
- **Try it in the iPhone Duo simulator** (Xcode 27.1): play a match, then close and open the phone, turn it each way, and fold it partway.
- **App Store:** add iPhone Duo screenshots in App Store Connect to get the "optimized for iPhone Duo" badge on the product page: 2007 × 2853 or 2853 × 2007 (open) and 1398 × 2034 or 2034 × 1398 (closed). From April 2027 they're required for any build made with the iOS 27.1 SDK.

## New in this build: more of the iPhone

- **Haptics that feel like iOS's own.** A win, a purchase, a claimed reward and a finished craft give iOS's "success" feel; a purchase that can't go through and an ad that didn't come give the "error" feel; switches, tabs, filters, paint colours and the canvas vote give the light tick of a picker. They follow the phone's own **Settings > Sounds & Haptics > System Haptics**. (HapticsBridge.swift)
- **The App Store rating prompt**, back in the lobby after a win, once a player has 3 wins and 8 matches, and once per game build. iOS decides whether it actually shows (at most three times a year) and never shows it in TestFlight. (DeviceBridge.swift)
- **A nudge when a craft is done.** The first long craft asks in the game's own card, "Get a nudge?"; only a yes brings up iOS's notification prompt. After that each craft schedules a notification for when it's done ("The Giant is ready!"), called off if it's finished in the game first. No setup needed. (NotifyBridge.swift)
- **Game Center**, once you set it up (below): sign-in from the lobby (never mid-match, never in the first lesson), each Time trial's score on that canvas's leaderboard, and a **Game Center** button on the game's Time trial board. Until it's set up, nothing of it shows. (GameCenterBridge.swift)
- **Game Mode:** the app says it's a game (Info.plist), so iOS can turn on Game Mode for it.
- **Opens the way you play:** the app remembers upright or wide, so a wide player's game opens wide instead of turning once it has loaded.
- **Never stuck reloading:** if iOS closes the game's page three times in a minute (a phone very short of memory), the app shows a "Roll Model stopped" card with **Start again** instead of reloading over and over. Progress is kept.
- **Ads:** an ad that finishes loading after the player has left the app no longer pops up when they come back, and a reward still counts if iOS restarted the game under the ad.
- **Small things:** shaking the phone never brings up "Undo Typing"; no long-press menus; the screen may sleep again if the game's page is closed mid-match.

### Game Center (one-time setup)
1. In Xcode, select the **RollModel** target, open **Signing & Capabilities**, click **+ Capability** and add **Game Center**.
2. In App Store Connect, open the app, then **Services > Game Center** (or the **Game Center** section of the version), and turn it on for the version.
3. Add a leaderboard for each canvas (**Leaderboards > +**). Make each one **Recurring**, starting on a Monday at 00:00 UTC, lasting **1 week** and repeating **every week** (that matches the game's own weekly board). Score format **Integer**, sort **High to low**, score range **0 to 100**, and in its localization a suffix of **%**. The **Leaderboard ID** must be exactly:

   | Canvas | Leaderboard ID |
   |---|---|
   | Palette Island | `rm.trial.island` |
   | Blank Canvas | `rm.trial.blank` |
   | Sludge Sewer | `rm.trial.sewer` |
   | Fishing Raft | `rm.trial.raft` |
   | The Crypt | `rm.trial.crypt` |
   | The Cathedral | `rm.trial.cathedral` |
   | The Manor | `rm.trial.manor` |

4. Add the leaderboards to the app version before you submit it.

The game only shows its Game Center button for a canvas once that canvas's leaderboard exists, so you can add them one at a time.

## Rewarded ads

On the Strokes page, **Skip** on a stroke being crafted now plays a rewarded ad (Google AdMob), and the craft finishes once the ad has been watched. Ol' Bloop's Skip in the lesson plays one too; if no ad can come there (offline, or none to show), the lesson's craft finishes anyway, so a new player never gets stuck. The code is in **AdsBridge.swift**.

The app gets an ad ready as soon as the Strokes page opens, and again after each one is watched, so Skip usually plays one at once. If Skip is tapped before it's loaded, the game shows a "Getting your ad ready" card that waits for it (up to about 20 seconds, asking again while it's slow), with Cancel. If none comes, the card says why (offline, too slow, or no ad to show) with Try again. Cancel tells the app to stop waiting (the `cancel` message in AdsBridge.swift), so the ad doesn't pop up afterwards.

### The first time you open the project
Xcode downloads Google's two ad packages, **Google Mobile Ads** and **User Messaging Platform**, by itself. It needs the internet once and takes a minute. If Xcode ever says a package is missing, choose **File > Packages > Resolve Package Versions**. Google's current SDK needs **Xcode 26.2 or newer**; if Xcode is older, update it from the App Store first.

### Your AdMob IDs (already in)
Roll Model's own AdMob IDs are in **Info.plist**:
- **GADApplicationIdentifier** (the app): `ca-app-pub-5968656294161944~1699104716`
- **RollModelRewardedAdUnitID** (the rewarded ad unit, "Craft skip"): `ca-app-pub-5968656294161944/3653605208`

To use a different ad unit later, create it in AdMob (**Apps > RollModel > Ad units > Add ad unit > Rewarded**: leave every **Ad type** box and **Ad pods** on, server-side verification off) and paste its ID over the one above.

**Which ads show where:**
- **Run from Xcode, or installed from TestFlight:** Google's test ads, marked "Test mode". They're safe to watch and tap, and there's always one, so you and your testers can try Skip as much as you like without it counting against your AdMob account.
- **The App Store version:** your real ads, from the "Craft skip" ad unit.

So real ads first show once the update is out on the App Store. Then link the App Store listing in AdMob (**Apps > RollModel > App settings**) so AdMob reviews the app (2 to 3 days); until it's reviewed, AdMob only shows a few ads.

### Longer and playable ads
Since the player chooses to watch, the ad can be longer or interactive:
- **Playable (interactive) ads** are on by default in a rewarded ad unit (the Ad type boxes in step 2).
- **Longer ads:** in AdMob, open the app, then **App settings > High-engagement ads**, and make sure it's **on** (it is by default). Rewarded ads can then run up to 60 seconds before they can be skipped (30 with it off), with up to three steps to close.

### Privacy and consent
- **The EEA, the UK and Switzerland:** in AdMob, open **Privacy & messaging** and create a **European regulations** message for Roll Model. The game shows it the first time a player there asks for an ad, before the ad plays. Where Google says a player needs it, **Settings > Privacy Policy** gets an **Ad privacy choices** button.
- **Children:** a player who said they're under 13 at the account form gets only child-safe ads, none of them personalised (Google's child age treatment), and no consent message. Every ad is capped at the **Parental Guidance** rating. You can block more ad categories in AdMob under **Blocking controls**.
- The app doesn't ask to track players (no tracking prompt), so Google can't use the advertising identifier. So in Privacy & messaging, **don't** add an **IDFA explainer** message: it leads into Apple's tracking prompt, which the app doesn't have (and would need a line in Info.plist to ask for).
- **App Store Connect > App Privacy:** add what Google's ad SDK collects, besides what's already there. Google lists: **Coarse Location** (from the IP address), **Device ID**, **Product Interaction**, **Advertising Data**, **Crash Data**, **Performance Data** and **Other Diagnostic Data**, used for **Third-Party Advertising** and **Analytics**. Google's guide to answering these questions: developers.google.com/admob/ios/privacy/data-disclosure
- The game's Privacy Policy (Settings) now says this too, and no longer says the game has no ads.

## Good to know

- The game inside is version 368. Settings shows it as "Version 1.1 (368)".
- A brand-new player first gets the intro: a paint barrel in a desert scrapyard, then picking eye colour, eye style, paint colour and a name, before the lobby and the lesson. Existing players go straight to the lobby. To see it again, delete and reinstall the app.
- Saved names, looks and progress carry over from the earlier builds: the game keeps the same save and the same private address inside the app.
- The app icon is the paint roller. To change it later, drop a new 1024 x 1024 image into **Assets > AppIcon**.
- The whole game is bundled inside the app, fonts included, so it runs offline: none of it is fetched from the internet. Only online play goes out, to two places: the game server (rollmodel-game.fly.dev) for duels and the game's Supabase project for usernames, accounts and friends. (Ads come from Google's SDK in the app itself, not from the game.) Building the zip checks this and fails if anything else in the game points outside the app or names a file the app doesn't have.
- Online play and accounts are new in this build, so update **App Privacy** for the app in App Store Connect to match the privacy file inside it (PrivacyInfo.xcprivacy): Name, User ID, Gameplay Content and Other Data (the birthday), all linked to the player, none used for tracking, for App Functionality. A player can delete their account in Settings.
- Progress is kept twice: in the game's own storage and in a copy the app keeps in its own files (it goes into phone backups). If iOS clears website data, or the app is closed a moment after a save, the newer copy comes back at the next start.
- If iOS takes the game's graphics away while it's in the background, they come back when you return; if they can't, the game starts again with progress kept. When the phone is short of memory, the game lets go of songs it isn't playing.
- Pinch and double tap never zoom the game, the page settles back after the keyboard closes, and the home bar fades out while you play.
- Players pick upright or wide play when the game first opens, and can change it in Settings. On iPhone the app turns to match. iPad turns freely.
- The test unlocks (**Unlock everything** on the Strokes page, **Unlock all items** in the shop, code **1234**) only show in a build run from Xcode, and in the browser preview. TestFlight and App Store builds don't have them: App Review installs look just like TestFlight ones, and reviewers must not find a secret code. The same goes for the error lines and the hidden performance readout.
- Game sound follows the ring/silent switch and plays alongside your music (the app and the game both ask for iOS's "ambient" sound). In-game buzzes use the Taptic Engine.
- While an ad plays the game's sound is off; it comes back when the ad closes.
- Sound comes back on its own after the app has been in the background, and after a call, Siri or an alarm. If iOS closed the game while it was away, it starts again when you open the app.
- The app tells the game which iPhone it's on, plus Low Power Mode and heat, and the game sets its graphics from that. The screen stays awake during a match.
- The game itself lives in the **Game** folder and doesn't depend on anything iPhone-specific.
- To ship a new version of the game, swap in the updated **Game** folder, raise the **Version** in the General tab and archive again.
- If a newer Xcode shows a yellow "Update to recommended settings" notice, it's safe to accept or ignore.
