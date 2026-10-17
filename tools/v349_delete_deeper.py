"""v349: Delete account moves out of the menu, to the foot of Settings, and asks first in a card of its own.

- The menu's Account section, signed in, shows who's signed in and Log out only (Log out still asks first).
- Delete account is a small link at the foot of Settings, beside Restart Game, and only while you're signed in. It opens a card over
  Settings: "Delete account?", who it is and what goes ("Your username, friends and account details all go, and it can't be undone"),
  Keep it to the fore (and the one with focus), Delete for good under it in red on a strip of tape. Keep it, a tap outside the card or Escape closes it.
  Once deleted, the card says so (Account deleted, OK) and the link goes. If it can't be deleted, the card says why and stays.
- The Terms and the Privacy Policy point to Settings for it again (Settings › Delete account)."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    # the menu: Log out only
    s = rep(s, "h = b('out', 'Log out') + b('del', 'Delete account', 'acdel'); }", "h = b('out', 'Log out'); } // (v349: Delete account is at the foot of Settings)")
    s = rep(s, "// ---- the menu (v346: it was in Settings): the account (who's signed in, Log out, Delete account with a second tap to be sure), or Make an account / Log in",
               "// ---- the menu (v346: it was in Settings): the account (who's signed in and Log out, which asks first), or Make an account / Log in.\n"
               "// (v349) Delete account is at the foot of Settings, so it isn't pressed by mistake")
    # Settings: the link, beside Restart Game
    s = rep(s, '<div class="sfoot"><button class="sreset" id="resetBtn" type="button">Restart Game</button><p class="sver" id="setVer"></p></div>',
               '<div class="sfoot"><span class="sfacts"><button class="sreset" id="resetBtn" type="button">Restart Game</button><button class="sreset" id="delAcBtn" type="button" aria-haspopup="dialog" hidden>Delete account</button></span><p class="sver" id="setVer"></p></div>')
    # its card, over Settings
    s = rep(s, '\n\n  <div class="modal" id="pause" hidden>',
               '\n\n  <div class="modal" id="delModal" hidden>\n'
               '    <div class="card" role="alertdialog" aria-modal="true" aria-labelledby="delTitle" aria-describedby="delNote">\n'
               '      <h2 class="ctitle" id="delTitle">Delete account?</h2>\n'
               '      <p class="cnote" id="delNote"></p>\n'
               '      <p class="cnote delerr" id="delErr" role="alert"></p>\n'
               '      <button class="btn play sm" id="delNo" type="button">Keep it</button>\n'
               '      <button class="btn delyes" id="delYes" type="button">Delete for good</button>\n'
               '    </div>\n'
               '  </div>\n\n  <div class="modal" id="pause" hidden>')
    s = rep(s, "#setModal .sfoot .sreset{margin:0;padding:4px 0}",
               "#setModal .sfoot .sreset{margin:0;padding:4px 0}\n"
               "/* (v349) Delete account: a link at the foot of Settings beside Restart Game; it asks first in a card of its own over Settings, Keep it to\n"
               "   the fore and Delete for good under it in red */\n"
               "#setModal .sfoot .sfacts{display:flex;flex-wrap:wrap;align-items:center;gap:4px 18px;min-width:0}\n"
               "#delModal{z-index:13}\n"
               "#delModal .card{width:min(100%,380px)}\n"
               "#delModal .cnote b{font-weight:900;color:inherit}\n"
               "#delModal .delerr{margin:0;color:#C93A4C}\n"
               "#delModal .delerr:empty{display:none}\n"
               "#delModal .btn.delyes{color:#C93A4C} /* (on the card's strip of tape, like its other second buttons) */\n"
               "#delModal .btn.delyes:disabled{opacity:.6}")
    # shown only while signed in: as Settings opens, and when the account changes
    s = rep(s, "function openSettings() { if (state !== 'menu' || lookOpen || shopOpen || lkOn()) return; gfxPick = GFX; paintSettings();",
               "function openSettings() { if (state !== 'menu' || lookOpen || shopOpen || lkOn()) return; gfxPick = GFX; paintSettings(); delPaint();")
    s = rep(s, "function acPaintAll() { try { paintName(); paintPBar(); } catch (e) {} /* (v311: handle or plain name) */",
               "function acPaintAll() { try { paintName(); paintPBar(); } catch (e) {} /* (v311: handle or plain name) */ try { delPaint(); } catch (e) {} /* (v349) */")
    s = rep(s, "  $('setDone').addEventListener('click', disarm); $('setBack').addEventListener('click', disarm); }\n",
               "  $('setDone').addEventListener('click', disarm); $('setBack').addEventListener('click', disarm); }\n"
               "// (v349) Delete account: at the foot of Settings, beside Restart Game, while you're signed in. It asks first in a card of its own: Keep it\n"
               "// to the fore (and focused), Delete for good under it. Once deleted the card says so; if it can't be, the card says why and stays\n"
               "const delModal = $('delModal');\n"
               "function delPaint() { const b = $('delAcBtn'); if (b) b.hidden = !acctReady(); }\n"
               "function delOpen() {\n"
               "  if (!acctReady() || AC.busy) return; const nm = acName() || store.name || '';\n"
               "  $('delTitle').textContent = 'Delete account?'; $('delNote').innerHTML = 'Delete <b>' + frEsc(hdOf(nm)) + '</b> for good? Your username, friends and account details all go, and it can\\u2019t be undone.';\n"
               "  $('delErr').textContent = ''; $('delYes').hidden = false; $('delYes').disabled = $('delNo').disabled = false; $('delYes').textContent = 'Delete for good'; $('delNo').textContent = 'Keep it';\n"
               "  delModal.hidden = false; setTimeout(() => $('delNo').focus({ preventScroll: true }), 30);\n"
               "}\n"
               "function delClose() { if (delModal.hidden || AC.busy) return; delModal.hidden = true; delPaint(); const b = $('delAcBtn'); (b.hidden ? $('setDone') : b).focus({ preventScroll: true }); }\n"
               "$('delAcBtn').addEventListener('click', uiClick(delOpen));\n"
               "$('delNo').addEventListener('click', uiClick(delClose));\n"
               "delModal.addEventListener('click', e => { if (e.target === delModal) delClose(); });\n"
               "document.addEventListener('keydown', e => { if (e.key === 'Escape' && !delModal.hidden) { e.preventDefault(); e.stopPropagation(); delClose(); } }, true);\n"
               "$('delYes').addEventListener('click', async () => {\n"
               "  if (AC.busy || !acctReady()) return; AU.init(); AU.ui(); AC.busy = true; $('delYes').disabled = $('delNo').disabled = true; $('delErr').textContent = ''; $('delYes').textContent = 'Deleting\\u2026';\n"
               "  try { await acDelete(); AC.busy = false; $('delTitle').textContent = 'Account deleted'; $('delNote').textContent = 'Your account is deleted.'; $('delYes').hidden = true; $('delNo').disabled = false; $('delNo').textContent = 'OK'; $('delNo').focus({ preventScroll: true }); }\n"
               "  catch (err) { AC.busy = false; $('delYes').disabled = $('delNo').disabled = false; $('delYes').textContent = 'Delete for good'; $('delErr').textContent = acErrText(err); }\n"
               "  delPaint();\n"
               "});\n")
    # the Terms and the Privacy Policy: in Settings again
    s = rep(s, "You can delete it any time from the menu.", "You can delete it any time in Settings.")
    s = rep(s, "Menu › Account › Delete account removes", "Settings › Delete account removes")
    return s
