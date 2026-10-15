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

## Good to know

- The game inside is version 302. Settings shows it as "Version 1.1 (302)".
- A brand-new player first gets the intro: a paint barrel in a desert scrapyard, then picking eye colour, eye style, paint colour and a name, before the lobby and the lesson. Existing players go straight to the lobby. To see it again, delete and reinstall the app.
- Saved names, looks and progress carry over from the earlier builds: the game keeps the same save and the same private address inside the app.
- The app icon is the paint roller. To change it later, drop a new 1024 x 1024 image into **Assets > AppIcon**.
- The whole game is bundled inside the app, fonts included, so it runs fully offline: nothing is ever fetched from the internet. Building the zip checks this and fails if anything in the game points outside the app or names a file the app doesn't have.
- Progress is kept twice: in the game's own storage and in a copy the app keeps in its own files (it goes into phone backups). If iOS clears website data, or the app is closed a moment after a save, the newer copy comes back at the next start.
- If iOS takes the game's graphics away while it's in the background, they come back when you return; if they can't, the game starts again with progress kept. When the phone is short of memory, the game lets go of songs it isn't playing.
- Pinch and double tap never zoom the game, the page settles back after the keyboard closes, and the home bar fades out while you play.
- Players pick upright or wide play when the game first opens, and can change it in Settings. On iPhone the app turns to match. iPad turns freely.
- To test every accessory at once, tap **Unlock all items** at the bottom of Customize and enter **1234**.
- Game sound follows the ring/silent switch and plays alongside your music. In-game buzzes use the Taptic Engine.
- Sound comes back on its own after the app has been in the background, and after a call, Siri or an alarm. If iOS closed the game while it was away, it starts again when you open the app.
- The app tells the game which iPhone it's on, plus Low Power Mode and heat, and the game sets its graphics from that. The screen stays awake during a match.
- The game itself lives in the **Game** folder and doesn't depend on anything iPhone-specific.
- To ship a new version of the game, swap in the updated **Game** folder, raise the **Version** in the General tab and archive again.
- If a newer Xcode shows a yellow "Update to recommended settings" notice, it's safe to accept or ignore.
