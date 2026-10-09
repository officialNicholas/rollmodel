# Roll Model for iOS

A thin native shell around the game: a full-screen web view that loads the bundled copy of `game/`, with two bridges the page already speaks.

- `orient`: the page posts `port`, `land` or `` when the player picks an orientation at launch or in Settings. `OrientBridge` locks the app to it.
- `device`: `{ keepAwake: true }` during a match keeps the screen on.
- `window.__NATIVE = { ios: true, tier: 3 }` is injected at document start so the game picks its high graphics tier.

## Build

1. `python3 tools/ios_pack.py` from the repository root. It copies `game/` into `ios/RollModel/RollModel/www` and writes `RollModel-iOS.zip`.
2. Open `ios/RollModel/RollModel.xcodeproj` in Xcode 15 or newer.
3. Set your team under Signing, change the bundle identifier if you like, and run on a device. iOS 15 and up, iPhone and iPad.

Audio plays without a tap because the web view allows inline media without a user gesture; the game still waits for the first touch to start its audio context, as on the web.
