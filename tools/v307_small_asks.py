"""v307: three asks from playing v306 in the Claude app.

- "You're offline" when you aren't. The web preview inside the Claude app lets a page talk to nothing outside it, so there the account
  form, Friends and online play can never reach Supabase or the game server, and every one of those failures read as being offline.
  The browser says when it turns a connection away for the page's own rules (a securitypolicyviolation event), so the game now knows
  it's in such a page and says what's true: accounts, friends and online play work in the Roll Model app, not in this preview. The
  account form says it as it opens (its button stays off), and so do Settings, Friends and the Online sheet. Opening Settings or the
  account form makes one small request to find out, in case nothing has tried yet. Elsewhere a failed request now says the server
  can't be reached, and "You're offline" is kept for when the phone really is.
- The account's birthday is the birth year only (one picker). The year is sent as its last day, so "13 or older" holds for certain:
  a player born in a year that turns 13 this year counts as 13 from the next 1 January (or from 31 December). The server's check is
  unchanged (it still takes a date); the Privacy Policy and the form say birth year.
- Settings fits on one screen, with nothing to scroll, on any phone and in the Claude app's viewer. The rows are a little tighter,
  How to play sits with the Terms, Privacy and Credits buttons (four in a row), the Turning note is for screen readers only, Restart
  Game and the version share a line, and the Visuals notes are shorter. If a screen is still too short for them, the whole set is
  drawn smaller to fit (setFit: laid out wider by the same factor, so it still fills the width), never scrolled; only a window too
  small to read at 60% scrolls instead.
- Play online opens the Online sheet again. In v306 the card looked for the sheet's opener on window, where nothing put it, so a
  player with an account got "Online matches are coming soon" (the two-phone tests opened the sheet directly, so they never saw it)."""
def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

NET = r"""// ---------- (v307) a page that may not go online. The web preview inside the Claude app lets a page talk to nothing outside it, so
// there the account form, Friends and online play can't work, and each refused connection used to read as "You're offline". The
// browser fires securitypolicyviolation when the page's own rules turn a connection away: from then on the game says these work in
// the Roll Model app. netProbe makes one small request to find out (opening Settings or the account form), in case nothing has
// tried yet ----------
var NET_WALLED = false, NET_PROBED = false;
const NET_APP = 'This preview can’t go online. Accounts, friends and online play work in the Roll Model app.';
const netWhy = () => NET_WALLED ? 'walled' : (typeof navigator !== 'undefined' && navigator.onLine === false) ? 'offline' : 'server';
document.addEventListener('securitypolicyviolation', e => { try { if (/\.supabase\.co|\.fly\.dev/i.test(String(e.blockedURI || ''))) netWall(); } catch (x) {} });
function netWall() {
  if (NET_WALLED) return; NET_WALLED = true;
  try { if (AC.open && !AC.busy) acRender(); } catch (e) {}
  try { if (!setModal.hidden) acSetPaint(); } catch (e) {}
  try { if (FR.open) frRender(); } catch (e) {}
  try { if (ON.v === 'error' || ON.v === 'connecting') { ON.v = 'error'; ON.err = 'Online play works in the Roll Model app, not in this preview.'; onUpd(); } } catch (e) {}
}
function netProbe() { if (NET_WALLED || NET_PROBED || !SB_CFG) return; NET_PROBED = true; try { fetch(SB_CFG.url + '/auth/v1/health', { mode: 'no-cors', cache: 'no-store' }).catch(() => {}); } catch (e) {} }
"""

FIT = r"""
// ---------- (v307) Settings on one screen: if the rows are taller than the room between the title and Done, they're drawn smaller
// to fit (laid out wider by the same factor, so they still fill the width), never scrolled. A window too small to read them at 60%
// scrolls instead ----------
function setFit() {
  const r = $('srows'), f = $('sfit'); if (!r || !f || setModal.hidden) return;
  f.style.transform = ''; f.style.width = ''; r.style.overflowY = '';
  const cs = getComputedStyle(r), room = r.clientHeight - parseFloat(cs.paddingTop) - parseFloat(cs.paddingBottom); let k = 1, h = f.offsetHeight;
  for (let i = 0; i < 4 && h * k > room + 0.5; i++) { k = Math.max(0.6, room / h); f.style.width = (100 / k).toFixed(3) + '%'; f.style.transform = 'scale(' + k.toFixed(4) + ')'; h = f.offsetHeight; }
  if (h * k > room + 1) r.style.overflowY = 'auto';
  f.dataset.k = k.toFixed(3);
}
let setFitQ = 0;
function setFitSoon() { if (setFitQ) return; setFitQ = requestAnimationFrame(() => { setFitQ = 0; setFit(); }); }
addEventListener('resize', () => { if (!setModal.hidden) setFitSoon(); });
try { if (document.fonts) document.fonts.ready.then(() => { if (!setModal.hidden) setFitSoon(); }); } catch (e) {}
"""

CSS = r"""
/* (v307) Settings on one screen: #srows frames the rows and #sfit holds them (the grid, as #srows had it), a little tighter, with
   How to play beside the Terms, Privacy and Credits. A screen still too short for them gets them drawn smaller (setFit) */
#setModal .card>#srows{display:block;overflow:hidden}
#setModal #sfit{display:grid;grid-template-columns:inherit;align-content:start;gap:12px 12px;width:100%;transform-origin:0 0}
#setModal .sopt{gap:5px}
#setModal .slab{font-size:13px}
#setModal .sopt .gnote{min-height:0;font-size:11px;line-height:1.3}
#setModal #turnNote{position:absolute;width:1px;height:1px;margin:0;overflow:hidden;clip:rect(0 0 0 0);clip-path:inset(50%);white-space:nowrap}
#setModal .trn{height:40px}
#setModal .acrow .acnote{min-height:0}
#setModal .sbtn{min-height:46px}
#setModal .sbtns.four{grid-template-columns:repeat(4,minmax(0,1fr));gap:8px}
#setModal .sbtns.four .sbtn{min-height:48px;padding:4px;font-size:11.5px;line-height:1.1}
#setModal .serr{grid-column:1/-1;margin:0;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
#setModal .serr:empty{display:none}
#setModal .sfoot{grid-column:1/-1;display:flex;align-items:center;justify-content:space-between;gap:12px;min-width:0}
#setModal .sfoot .sreset{margin:0;padding:4px 0}
#setModal .sfoot .sver{margin:0;text-align:right}
@media (orientation:landscape){#setModal #sfit{gap:10px 12px}}
/* (v307) the account's birth year: one picker */
.acbd.acyr{grid-template-columns:minmax(0,9em)}
"""

def apply(s):
    # ---- 1) a page that may not go online says so
    a = "// ---------- (v305) Friends, on Supabase: a friend code each, requests both ways, who's online, and a Friends board for the Time\n"
    s = rep(s, a, NET + a)
    s = rep(s, "    : why === 'slow_down' ? 'That’s a lot of changes. Try again later' : why === 'offline' ? 'You’re offline. Try again when you’re online'\n",
               "    : why === 'slow_down' ? 'That’s a lot of changes. Try again later' : why === 'offline' ? 'You’re offline. Try again when you’re online'\n"
               "    : why === 'walled' ? 'Accounts work in the Roll Model app, not in this preview' : why === 'server' ? 'Can’t reach the Roll Model server. Try again in a bit' // (v307)\n")
    s = rep(s, "const acErrText = e => (typeof navigator !== 'undefined' && navigator.onLine === false) ?",
               "const acErrText = e => NET_WALLED ? NET_APP : (typeof navigator !== 'undefined' && navigator.onLine === false) ?")
    s = rep(s, "  } catch (e) { return strict ? { ok: false, why: e && e.out ? 'out' : 'offline' } : { ok: true, name: n, off: true }; }",
               "  } catch (e) { return strict ? { ok: false, why: e && e.out ? 'out' : netWhy() } : { ok: true, name: n, off: true }; } // (v307: offline only when the phone is)")
    s = rep(s, "setTimeout(() => res(strict ? { ok: false, why: 'offline' } : { ok: true, name: n, off: true }), 9000))]);",
               "setTimeout(() => res(strict ? { ok: false, why: netWhy() } : { ok: true, name: n, off: true }), 9000))]);")
    s = rep(s, "if (!r.ok) { AU.nope(); if (r.why !== 'offline' && r.why !== 'slow_down' && r.why !== 'out') {",
               "if (!r.ok) { AU.nope(); if (!/^(offline|walled|server|slow_down|out)$/.test(r.why)) {")
    s = rep(s, "const frErrText = e => (typeof navigator !== 'undefined' && navigator.onLine === false) ?",
               "const frErrText = e => NET_WALLED ? 'Friends work in the Roll Model app, not in this preview.' : (typeof navigator !== 'undefined' && navigator.onLine === false) ?")
    s = rep(s, "  ON.v = e.code === 'old' ? 'old' : 'error'; ON.err = e.code === 'offline' || onOffline() ?",
               "  ON.v = e.code === 'old' ? 'old' : 'error'; ON.err = NET_WALLED ? 'Online play works in the Roll Model app, not in this preview.' : e.code === 'offline' || onOffline() ?")
    s = rep(s, "ON.v = 'error'; ON.err = onOffline() ? 'You’re offline. Online play comes back when you are.' : 'Lost the connection to the game server.'; onUpd(); }",
               "ON.v = 'error'; ON.err = NET_WALLED ? 'Online play works in the Roll Model app, not in this preview.' : onOffline() ? 'You’re offline. Online play comes back when you are.' : 'Lost the connection to the game server.'; onUpd(); }")
    # the account form: said at once, and its button stays off; Settings' account row says it too
    s = rep(s, "'<p class=\"acerr acw\" id=\"acErr\" role=\"alert\">' + frEsc(AC.err) + '</p>'",
               "'<p class=\"acerr acw\" id=\"acErr\" role=\"alert\">' + frEsc(AC.err || (NET_WALLED ? NET_APP : '')) + '</p>'", 2)
    s = rep(s, "  const g = $('acGo'); if (g && !AC.busy) g.disabled = !f.ok;\n}",
               "  const g = $('acGo'); if (g && !AC.busy) g.disabled = !f.ok || NET_WALLED;\n}")
    s = rep(s, ": acOut() ? 'You’re signed out. Log in, or make a new account.' : 'Make an account to add friends and play online.';",
               ": NET_WALLED ? 'Accounts and online play work in the Roll Model app, not in this preview.' : acOut() ? 'You’re signed out. Log in, or make a new account.' : 'Make an account to add friends and play online.';")
    s = rep(s, "  AC.next = typeof next === 'function' ? next : null; AC.tab = tab === 'in' ? 'in' : 'new';",
               "  netProbe(); AC.next = typeof next === 'function' ? next : null; AC.tab = tab === 'in' ? 'in' : 'new';")

    # Play online's card opens the Online sheet (the lobby's onlineOpen is in this same script: no need for window)
    s = rep(s, "function mpGo() { if (typeof window.onlineOpen === 'function') window.onlineOpen(); else",
               "function mpGo() { if (typeof onlineOpen === 'function') onlineOpen(); else")

    # ---- 2) the birthday is the birth year
    s = rep(s, "  let mo = o('', 'Month', f.m || ''), dy = o('', 'Day', f.d || ''), ye = o('', 'Year', f.y || '');\n"
               "  AC_MONTHS.forEach((m, i) => { mo += o(i + 1, m, f.m); }); for (let d = 1; d <= 31; d++) dy += o(d, d, f.d); for (let y = yr; y >= 1900; y--) ye += o(y, y, f.y);\n",
               "  let ye = o('', 'Year', f.y || ''); for (let y = yr; y >= 1900; y--) ye += o(y, y, f.y); // (v307: the birth year only)\n")
    s = rep(s, "'<fieldset class=\"acf\"><legend>Birthday</legend><div class=\"acbd\"><select id=\"acM\" data-k=\"m\" aria-label=\"Birth month\" autocomplete=\"bday-month\">' + mo + '</select><select id=\"acD\" data-k=\"d\" aria-label=\"Birth day\" autocomplete=\"bday-day\">' + dy + '</select><select id=\"acY\"",
               "'<fieldset class=\"acf\"><legend>Birth year</legend><div class=\"acbd acyr\"><select id=\"acY\"")
    s = rep(s, "m = +v('acM'), d = +v('acD'), y = +v('acY'),", "y = +v('acY'),")
    s = rep(s, "  const real = !!(m && d && y) && new Date(y, m - 1, d).getDate() === d, bday = real ? y + '-' + pad(m) + '-' + pad(d) : '';\n",
               "  const real = y >= 1900 && y <= t.getFullYear(), bday = real ? y + '-12-31' : ''; // (v307: the year only, sent as its last day: the youngest a player born then can be, so 13 or older is certain)\n")
    s = rep(s, "bday: !real || bday > today || y < 1900,", "bday: !real,")
    s = rep(s, "all = !!(AC.f.m && AC.f.d && AC.f.y);", "all = !!AC.f.y;")
    s = rep(s, "all && w.bday ? 'That date doesn’t look right' : ''", "all && w.bday ? 'Pick your birth year' : ''")
    s = rep(s, "for (const id of ['acM', 'acD', 'acY']) $(id).classList.toggle('empty', !$(id).value);", "$('acY').classList.toggle('empty', !$('acY').value);")
    s = rep(s, "w === 'birthday' ? 'Check your birthday.'", "w === 'birthday' ? 'Check your birth year.'")
    s = rep(s, "Your name and birthday stay private.", "Your name and birth year stay private.")
    s = rep(s, "your first and last name, your birthday, and when you agreed to these terms. Your name and birthday are private: other players never see them. We ask for your birthday because",
               "your first and last name, your birth year, and when you agreed to these terms. Your name and birth year are private: other players never see them. We ask for your birth year because")

    # ---- 3) Settings on one screen
    s = rep(s, '<div class="srows" id="srows">\n', '<div class="srows" id="srows"><div class="sfit" id="sfit">\n')
    s = rep(s, '        <div class="sopt wide"><p class="slab">Help</p><div class="sbtns"><button class="sbtn" id="howOpen" type="button" aria-haspopup="dialog"><span>How to play</span></button></div><p class="gnote" id="lastErr"></p></div>\n', '')
    s = rep(s, '<div class="sopt full"><div class="sbtns three"><button class="sbtn" id="tosBtn"',
               '<div class="sopt full sdocs"><div class="sbtns four"><button class="sbtn" id="howOpen" type="button" aria-haspopup="dialog"><span>How to play</span></button><button class="sbtn" id="tosBtn"')
    s = rep(s, '        <button class="sreset" id="resetBtn" type="button">Restart Game</button>\n        <p class="sver" id="setVer"></p>\n      </div>\n',
               '        <p class="gnote serr" id="lastErr"></p>\n        <div class="sfoot"><button class="sreset" id="resetBtn" type="button">Restart Game</button><p class="sver" id="setVer"></p></div>\n      </div></div>\n')
    s = rep(s, "GFX_NOTE = { hi: 'Full lighting, reflections, glow and extra detail. Best on newer phones and computers.', perf: 'Simpler lighting and fewer effects, for the smoothest play on any device.' };",
               "GFX_NOTE = { hi: 'Full lighting, reflections and glow. Best on newer devices.', perf: 'Simpler lighting and fewer effects, for the smoothest play.' }; // (v307: one line each)")
    s = rep(s, " $('setDone').textContent = gfxPick === GFX ? 'Done' : 'Restart to apply'; }\nfunction openSettings() {",
               " $('setDone').textContent = gfxPick === GFX ? 'Done' : 'Restart to apply'; setFitSoon(); }\nfunction openSettings() {")
    s = rep(s, "if (window.__turnShow) window.__turnShow(); setModal.hidden = false; setTimeout(() => $('gfxPick')",
               "if (window.__turnShow) window.__turnShow(); setModal.hidden = false; setFit(); netProbe(); setTimeout(() => $('gfxPick')")
    s = rep(s, "if (state === 'menu') { setModal.hidden = false; $('howOpen').focus({ preventScroll: true }); }",
               "if (state === 'menu') { setModal.hidden = false; setFitSoon(); $('howOpen').focus({ preventScroll: true }); }")
    s = rep(s, "if (state === 'menu') { setModal.hidden = false; const b = $({ tos: 'tosBtn', priv: 'privBtn', cred: 'credBtn' }[PB.docFrom]);",
               "if (state === 'menu') { setModal.hidden = false; setFitSoon(); const b = $({ tos: 'tosBtn', priv: 'privBtn', cred: 'credBtn' }[PB.docFrom]);")
    s = rep(s, "  $('acNote').innerHTML = t; $('acBtns').innerHTML = h;\n}", "  $('acNote').innerHTML = t; $('acBtns').innerHTML = h; setFitSoon();\n}")
    a = "function paintSettings() {"
    s = rep(s, a, FIT.lstrip('\n') + a)
    i = s.rfind('</style>'); s = s[:i] + CSS + s[i:]
    return s
