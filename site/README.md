# playrollmodel.com

The game's website: a home page, Support, Privacy Policy and Terms of Service, plus `app-ads.txt` for AdMob.
Plain HTML and one stylesheet, no build step. Hosted on Cloudflare Pages.

- `index.html` home; `support/`, `privacy/`, `terms/` the other pages (each an `index.html`, so the addresses are /support/ and so on)
- `style.css` the look (colours from the app icon); `icon.png`, `apple-touch-icon.png`, `favicon.png` from the app icon
- `app-ads.txt` tells ad networks which AdMob account may sell this app's ads (needs the App Store listing's
  marketing/developer URL set to https://playrollmodel.com)

The Privacy Policy and Terms text is the game's own (Settings › Privacy / Terms). When those change in the game, change them here too.

Preview locally: `python3 -m http.server 8000` in this folder, then http://localhost:8000.
