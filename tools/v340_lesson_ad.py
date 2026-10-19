"""v340: the lesson's Skip plays an ad too.

- In Ol' Bloop's Strokes lesson, Skip on the Giant's craft was free ("this one's on me"). Now it plays the rewarded ad like any other
  Skip: the play mark on the button, "Watch an ad to finish it now" under it, the "Getting your ad ready" card while it loads, and the
  Giant done once the ad's been watched. Ol' Bloop says so: "Crafting takes 20 minutes. Tap Skip and watch a quick ad".
- The lesson never waits on an ad: if none can come (offline, none to show, or too slow), its craft finishes anyway, with a word from
  Ol' Bloop. Closing the ad early, or Cancel on the card, leaves it on the bench as anywhere else, so Skip can be tapped again.
- An app built without the ads SDK still skips for free."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    s = rep(s, "const adFree = () => ADS.mode === 'none' || !!(store.tut && store.tut.strokes === 'on' && ((store.strokes || {}).craft || {}).id === 'giant');\n",
               "const adFree = () => ADS.mode === 'none'; // (v340: the lesson's Skip plays one too)\n"
               "const adLesson = () => !!(store.tut && store.tut.strokes === 'on' && ((store.strokes || {}).craft || {}).id === 'giant'); // (v340: Ol' Bloop's craft: it never waits on an ad)\n")
    s = rep(s, "  AU.nope && AU.nope(); if (ADS.mode === 'app') adWaitFail(why); else stToast(why === 'offline' ? 'You’re offline: connect to watch the ad' : 'No ad to show right now. Try again soon');\n",
               "  if (adLesson()) { adWaitHide(); craftSkip(); return stToast((why === 'offline' ? 'You’re offline' : 'No ad right now') + ', so this one’s on Ol’ Bloop'); } // (v340: the lesson never gets stuck)\n"
               "  AU.nope && AU.nope(); if (ADS.mode === 'app') adWaitFail(why); else stToast(why === 'offline' ? 'You’re offline: connect to watch the ad' : 'No ad to show right now. Try again soon');\n")
    s = rep(s, "return tutShow('Crafting takes 20 minutes. Tap Skip, this one’s on me',", "return tutShow('Crafting takes 20 minutes. Tap Skip and watch a quick ad',")
    # the notes that said the lesson's was free
    s = rep(s, "the lesson's Skip stays free (it's on Ol' Bloop). The page asks", "(v340: the lesson's too, which finishes anyway if no ad can come). The page asks")
    s = rep(s, "// Skip on the bench: free in the lesson; otherwise the ad, and the craft's done when it's been watched",
               "// Skip on the bench: the ad, and the craft's done when it's been watched (free only in an app without ads)")
    s = rep(s, "// Skip on the bench: a play mark when it plays an ad (spinning while the ad gets ready), plain in the lesson",
               "// Skip on the bench: a play mark when it plays an ad (spinning while the ad gets ready), plain in an app without ads")
    return s
