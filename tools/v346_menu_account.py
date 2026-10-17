"""v346: the account lives in the menu, not in Settings.

- The Account section (Make an account and Log in; or who's signed in, Log out and Delete account, each asking first) moves from
  Settings to the menu that slides in from the right, under Settings and the sound. It works as before; Make an account and Log in
  close the menu and open the account sheet over the lobby. Make an account is green there, like the Friends page's.
- Settings loses the row. The words that pointed to Settings, Account (the Friends board, the Terms and the Privacy Policy) point to
  the menu now.
- Sideways, the menu's buttons are a little shorter so the account fits under them; a longer note scrolls the menu."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    # the row: out of Settings, into the menu under the sound
    s = rep(s, '\n        <div class="sopt wide acrow" id="acRow"><p class="slab" id="acSlab">Account</p><p class="gnote acnote" id="acNote" aria-live="polite"></p><div class="sbtns" id="acBtns"></div></div>', '')
    s = rep(s, '<span id="smSndL">Sound on</span></button></div></aside>',
               '<span id="smSndL">Sound on</span></button><section class="smacct acrow" id="acRow" aria-labelledby="acSlab"><p class="slab" id="acSlab">Account</p><p class="gnote acnote" id="acNote" aria-live="polite"></p><div class="sbtns" id="acBtns"></div></section></div></aside>')
    s = rep(s, ".smenu .sx{position:absolute;top:max(12px,env(safe-area-inset-top));right:max(16px,env(safe-area-inset-right))}",
               ".smenu .sx{position:absolute;top:max(12px,env(safe-area-inset-top));right:max(16px,env(safe-area-inset-right))}\n"
               "/* (v346) the account, in the menu under the sound (it was in Settings): a line above it, its note, its buttons one over the other */\n"
               ".smacct{display:grid;gap:8px;margin-top:2px;padding-top:16px;border-top:2px solid rgba(255,255,255,.09)}\n"
               ".smacct .slab{font-size:15px}\n"
               ".smacct .acnote{min-height:0;font:700 12.5px/1.35 var(--font-ui);color:rgba(255,255,255,.72)}\n"
               ".smacct .sbtns{grid-template-columns:minmax(0,1fr);gap:12px;margin-top:4px}\n"
               ".smacct .sbtn{min-height:46px;font-size:16px}\n"
               ".smacct .sbtn[data-ac=\"new\"]{background:linear-gradient(180deg,#46E07A 0%,#2FCB62 55%,#22B455 100%)}\n"
               ".smacct.soon .sbtn{filter:grayscale(.85) brightness(.7);cursor:default}\n"
               "@media (max-height:520px){.smenu .spanel{gap:12px;padding-bottom:16px}.smenu .sitem{height:50px}.smacct{gap:6px;padding-top:12px}.smacct .sbtns{gap:10px;margin-top:2px}.smacct .sbtn{min-height:40px}}")
    # painted when the menu opens (asking first, if it was, starts over), and while it's open; not with Settings
    s = rep(s, "function openSide() { if (state !== 'menu' || lookOpen || shopOpen || lkOn()) return; paintSide(); sideMenu.hidden = false;",
               "function openSide() { if (state !== 'menu' || lookOpen || shopOpen || lkOn()) return; paintSide(); if (!AC.busy) { AC.del = false; AC.out = false; AC.note = ''; } acSetPaint(); netProbe(); sideMenu.hidden = false;")
    s = rep(s, "paintSettings(); AC.del = false; AC.note = ''; acSetPaint(); if (window.__turnShow)", "paintSettings(); if (window.__turnShow)")
    s = rep(s, "try { if (!setModal.hidden) acSetPaint(); } catch (e) {}", "try { if (!$('sideMenu').hidden) acSetPaint(); } catch (e) {}")
    s = rep(s, "if (!$('setModal').hidden) acSetPaint(); }", "if (!$('sideMenu').hidden) acSetPaint(); }")
    s = rep(s, "if (!$('setModal').hidden) acSetPaint(); if (menuPage === 'events')", "if (!$('sideMenu').hidden) acSetPaint(); if (menuPage === 'events')")
    # Make an account / Log in: the menu closes (it sits over the sheet), the sheet opens; closing it comes back to the menu button
    s = rep(s, "if (a === 'new' || a === 'in') return acctOpen(null, a);", "if (a === 'new' || a === 'in') { closeSide(); return acctOpen(null, a); }")
    # the words that sent players to Settings, Account
    s = rep(s, "Friends come with an account: Settings, Account.", "Friends come with an account: make one in the menu.")
    s = rep(s, "You can delete it any time in Settings.", "You can delete it any time from the menu.")
    s = rep(s, "Settings › Account › Delete account removes", "Menu › Account › Delete account removes")
    s = rep(s, "// the menu: slides in from the right (Settings, the sound; more to come)", "// the menu: slides in from the right (Settings, the sound, your account)")
    s = rep(s, "// ---- Settings: the account (who's signed in, Log out, Delete account with a second tap to be sure), or Make an account / Log in",
               "// ---- the menu (v346: it was in Settings): the account (who's signed in, Log out, Delete account with a second tap to be sure), or Make an account / Log in")
    s = rep(s, "// Log out (Settings): your progress to your account first", "// Log out (the menu's Account): your progress to your account first")
    return s
