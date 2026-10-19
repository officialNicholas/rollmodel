"""v350: polish for the iOS launch, from a sweep of every screen on an iPhone SE, an iPhone 15, an iPhone 15 Pro Max and an iPad,
upright and sideways.

- The canvas vote's arrows stay clear of the notch and the Dynamic Island when the phone is held sideways (they sat under them).
- The knocked-out screen no longer says the same thing twice ("FELL OFF" over "Fell off", "BAKED" over "Baked!", "DRIED UP" over
  "Dried up!"): with nobody to blame, the small line says "Knocked out" and the big line says how.
- Small buttons are easier to hit, with no change to how they look: Restart Game and Delete account at the foot of Settings, the pencil
  by your name on the Stats card, your name in My Locker, and the Paint Shop's filter chips. Each takes taps a little way around it.
- Pictures can't be picked up and dragged with a long press, as a web page's can.
- The iPhone app has no test unlocks ("Unlock everything", "Unlock all items" and their code) unless it was run from Xcode. TestFlight
  builds go without them too, since App Review installs look just like TestFlight ones and reviewers must not find a secret code. The
  browser preview keeps them. The app says which it is (window.__NATIVE.tester)."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    # the canvas vote's arrows: clear of the notch held sideways
    s = rep(s, ".gnav.prev{left:8px}.gnav.next{right:8px}",
               ".gnav.prev{left:max(8px,calc(env(safe-area-inset-left,0px) + 4px))}.gnav.next{right:max(8px,calc(env(safe-area-inset-right,0px) + 4px))}")
    s = rep(s, ".mworld .gnav.prev{left:10px;padding-right:2px}.mworld .gnav.next{right:10px;padding-left:2px}",
               ".mworld .gnav.prev{left:max(10px,calc(env(safe-area-inset-left,0px) + 4px));padding-right:2px}.mworld .gnav.next{right:max(10px,calc(env(safe-area-inset-right,0px) + 4px));padding-left:2px} /* (v350: clear of the notch held sideways) */")
    # knocked out: the reason said once
    s = rep(s, "$('kofSmall').textContent = by ? 'Splatted by' : reason === 'fall' ? 'Fell off' : reason === 'sun' ? 'Baked' : reason === 'dry' ? 'Dried up' : 'Knocked out';",
               "$('kofSmall').textContent = by ? 'Splatted by' : 'Knocked out'; // (v350: the big line under it says how, so it isn't said twice)")
    # bigger places to tap, the same look: each takes taps a little way around it
    s = rep(s, "#setModal .sfoot .sreset{margin:0;padding:4px 0}",
               "#setModal .sfoot .sreset{margin:0;padding:4px 0}\n"
               "/* (v350) small buttons take taps a little way around them (a tap target near 44 points, as iOS asks), with no change to the look:\n"
               "   Restart Game and Delete account (more below than above, where the buttons are), the Stats card's pencil, your name in My Locker,\n"
               "   and the Paint Shop's filter chips (inside their row's padding, and no further sideways than half the gap between them) */\n"
               "#setModal .sfoot .sreset{position:relative}\n"
               "#setModal .sfoot .sreset::after{content:\"\";position:absolute;inset:-7px -9px -13px}\n"
               "#stRename{position:relative}\n"
               "#stRename::after{content:\"\";position:absolute;inset:-6px}\n"
               "#mLocker.sgp .lkname{position:relative}\n"
               "#mLocker.sgp .lkname::after{content:\"\";position:absolute;inset:-6px -4px}\n"
               "#mLocker.sgp .lkchip::before{content:\"\";position:absolute;inset:-6px -3px -5px}\n"
               "/* (v350) pictures aren't picked up and dragged with a long press, as a web page's are */\n"
               "img,svg{-webkit-user-drag:none}\n"
               "/* (v350) the iPhone app: no test unlocks unless it was run from Xcode (the browser keeps them) */\n"
               "html.appstore .ucode{display:none!important}")
    s = rep(s, "const NATIVE = window.__NATIVE || null;\n",
               "const NATIVE = window.__NATIVE || null;\n"
               "// (v350) the iPhone app: no test unlocks unless it was run from Xcode (the shell's tester). TestFlight goes without, as App Review\n"
               "// installs look just like TestFlight ones. A browser keeps them\n"
               "if (NATIVE && NATIVE.platform === 'ios' && !NATIVE.tester) document.documentElement.classList.add('appstore');\n")
    # Delete account showing or going: Settings fits itself to the screen again
    s = rep(s, "function delPaint() { const b = $('delAcBtn'); if (b) b.hidden = !acctReady(); }",
               "function delPaint() { const b = $('delAcBtn'); if (!b) return; const h = !acctReady(); if (b.hidden !== h) { b.hidden = h; if (!setModal.hidden) setFitSoon(); } } // (v350: and Settings fits itself again)")
    return s
