"""v312: your progress goes with your account, "I already have an account" on the first loading screen, and a Log out that hands the
phone to the next player.

- Progress kept with the account: while you're signed in to one, the game keeps a copy of your progress with it (your rank, drops,
  everything bought, crafted and unlocked, the lessons done), about half a minute after it changes and at once when the app is put away.
  What belongs to the phone stays with the phone: sound, music, graphics and screen orientation.
- "I already have an account": on a first launch (a new phone, or after Log out), under the loading bar from the first moment. Log in and
  your progress comes back, past the intro and the lessons, into the lobby ("Welcome back, @you! Your progress is back."). On a first
  launch the loading screen now ends on "Tap to start", so there's time to tap it. An account with no progress saved yet (made before
  this version and not opened since on the phone it was played on) says so, with Try again and Start fresh.
- Log out (Settings, Account) asks first, saves your progress to your account, then starts this phone fresh: back to the loading screen
  with "I already have an account", for someone else to log in or start their own. If the progress can't be saved (offline), nothing
  changes. Restart Game is as before.
- Logging in from Settings brings the account's progress to the phone. A phone with progress of its own that was never signed in says
  so on the Log in form first.
- Two phones on one account: every start checks the account's copy. If the other phone moved on and this one didn't, this one takes the
  account's copy; if both did, the one with more rank wins. The server never lets a copy with less rank replace one with more.
- Needs supabase/migrations/20261016000000_saves.sql run on the project. Until then accounts work as before: logging in brings no
  progress back, and Log out keeps this phone's progress."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

EARLY = r"""
// (v312) a first launch on a phone that isn't signed in to an account: "I already have an account" under the loading bar, from the first
// moment. A tap before the account sheet is ready waits for it (BA.ready, below with the accounts)
var BA = { on: false, want: false, ready: false, me: null };
function baTap(e) { if (e) { e.preventDefault(); e.stopPropagation(); } try { AU.init(); AU.ui(); } catch (x) {} BA.want = true; if (BA.ready) return baOpen(); const b = $('bootAcct'); if (b) { b.classList.add('wait'); b.textContent = 'One moment…'; } }
{ const sb = store.sbs, b = $('bootAcct'), first = !!window.__introNow || (!store.introDone && !store.name && !((store.runs || 0) > 0) && (!store.tut || store.tut.ph === 'match'));
  if (b && first && !(sb && sb.acct && sb.rt && !sb.out)) { BA.on = true; b.hidden = false; b.addEventListener('click', baTap); b.addEventListener('pointerdown', e => e.stopPropagation()); } } // (not "Tap to start")
"""

MAIN = r"""
// ---- (v312) your progress, kept with your account. While you're signed in to one, a copy goes up (rm_save_put) about half a minute after
// it changes, and at once when the app is put away; logging in brings it back (rm_save_get). What belongs to the phone is never sent or
// replaced: the sign-in itself, sound, music, graphics, screen orientation, the readouts.
// Which copy wins: the phone notes the last copy it sent or took (rm.cs: whose, when the account got it, and its fingerprint). If the
// account still has that one, this phone's goes up when it differs. If the account moved on (another phone) and this phone didn't, the
// phone takes the account's, at a start. If both did, more rank wins (the server never lets less replace more; a tie stays with this
// phone). Logging in on a phone that was never this account's brings the account's copy.
var CS = { ok: false, off: false, hold: false, dirty: false, t: 0, busy: null, sync: null, bootP: null, reloading: false, want: false, watch: 0 };
const CS_LOCAL = ['sbs', 'muted', 'sfxOff', 'musicOff', 'gfx', 'orient', 'perfHud', 'acYoung', 'lastErr', 'netTok', 'csHi'], CS_BOOK = 'rm.cs', CS_WAIT = 30000;
const csUid = () => (FR.s && FR.s.uid) || (store.sbs && store.sbs.uid) || '';
const csXp = x => Math.max(0, Math.floor(+x || 0));
const csMissing = e => !!e && (e.status === 404 || /PGRST202|Could not find the function/i.test(String(e.message || ''))); // (the v312 SQL not run yet)
const csBootUp = () => { const b = $('boot'); return !!b && !b.classList.contains('gone'); }; // (still on the loading screen: safe to start again)
// a moment the game can start again without taking anything from the player: the loading screen, or the lobby with nothing open
function csSafe() { try { return csBootUp() || (state === 'menu' && !building && !irisBusy && $('orient').hidden && !document.querySelector('.modal:not([hidden])') && !(FL && FL.busy && FL.busy()) && !menu.classList.contains('tutoring')); } catch (e) { return false; } }
// the account's copy is ahead but the game's busy: look again (afresh) at the next quiet moment in the lobby
function csWatch() { CS.want = true; if (CS.watch) return; CS.watch = setInterval(() => { if (!CS.want || CS.hold) { clearInterval(CS.watch); CS.watch = 0; return; } if (!csSafe()) return; CS.want = false; clearInterval(CS.watch); CS.watch = 0; csSync(); }, 3000); }
function csData() { const o = {}; for (const k of Object.keys(store)) if (!CS_LOCAL.includes(k) && store[k] !== undefined) o[k] = store[k]; return o; }
// the same progress gives the same fingerprint, whatever order its parts were written in
const csCanon = v => v === null || typeof v !== 'object' ? (JSON.stringify(v) || 'null') : Array.isArray(v) ? '[' + v.map(csCanon).join(',') + ']'
  : '{' + Object.keys(v).sort().filter(k => v[k] !== undefined && typeof v[k] !== 'function').map(k => JSON.stringify(k) + ':' + csCanon(v[k])).join(',') + '}';
function csHash(s) { let h = 0x811c9dc5; for (let i = 0; i < s.length; i++) { h ^= s.charCodeAt(i); h = Math.imul(h, 0x01000193); } return (h >>> 0).toString(36) + '.' + s.length; }
function csBook() { try { const b = JSON.parse(localStorage.getItem(CS_BOOK) || 'null'); return b && typeof b === 'object' ? b : null; } catch (e) { return null; } }
function csBookSet(b) { try { if (b) localStorage.setItem(CS_BOOK, JSON.stringify(b)); else localStorage.removeItem(CS_BOOK); } catch (e) {} }
// every save: signed in, a copy goes up in a while (or, before the account's copy has been checked this time, that check)
function csMark() { try { if (!CS || CS.hold || CS.off || baSheet()) return; CS.dirty = true; if (!CS.t && acctReady()) CS.t = setTimeout(() => { CS.t = 0; if (CS.ok) csPush(); else csSync(); }, CS_WAIT); } catch (e) {} } // (never in the way of a save)
function csLater() { if (!CS.t) CS.t = setTimeout(() => { CS.t = 0; if (CS.ok) csPush(); else csSync(); }, 60000); CS.dirty = true; } // (a try that failed: again in a minute)
// what to do with the account's copy g: 'adopt' it, 'push' this phone's, or nothing ('same'). login: just logged in
function csDecide(g, login) {
  if (!g || !g.data) return 'push';
  const b = csBook(), h = csHash(csCanon(csData())), more = csXp(g.xp) > csXp(store.xp);
  if (!b || b.u !== csUid()) return login || more ? 'adopt' : 'push'; // (never this account's on this phone)
  if (+b.at === +g.at) return h === b.h ? 'same' : 'push';            // (the account still has what this phone last sent or took)
  if (h === b.h) return 'adopt';                                       // (another phone moved the account on; this one didn't move)
  return more ? 'adopt' : 'push';                                       // (both moved on)
}
// this phone's copy up to the account. now: put away, logging out, or just checked (an upload under way finishes first)
function csPush(now) {
  if (!CS || CS.off || CS.hold || !CS.ok || !acctReady() || baSheet()) return Promise.resolve('no'); // (the loading screen's sheet open: it decides first)
  clearTimeout(CS.t); CS.t = 0;
  if (CS.busy) return CS.busy.then(() => csPush(now));
  CS.dirty = false;
  const data = csData(), canon = csCanon(data), h = csHash(canon), uid = csUid(), b = csBook();
  if (b && b.u === uid && b.h === h) return Promise.resolve('same');
  return CS.busy = (async () => {
    try {
      const r = await sbRpc('rm_save_put', { p_data: data }, !!now && canon.length < 60000); // (put away: sent so it gets there, if it's small enough)
      if (r && r.ok) { csBookSet({ u: uid, at: r.at, h }); return 'ok'; }
      if (r && r.why === 'behind') { CS.hold = true; return 'behind'; } // (another phone has more: this one takes it at its next start)
      if (r && r.why === 'slow_down') { csLater(); return 'fail'; }
      return 'no';
    } catch (e) { if (csMissing(e)) { CS.off = true; return 'off'; } csLater(); return 'fail'; }
    finally { CS.busy = null; }
  })();
}
// the account's copy against this phone's: at the start of the game, after a failed try, before logging out, on a new account
function csSync() {
  if (!CS || CS.off || CS.hold || !acctReady() || baSheet()) return Promise.resolve('no');
  return CS.sync || (CS.sync = (async () => {
    let g; try { g = await sbRpc('rm_save_get', {}); } catch (e) { if (csMissing(e)) { CS.off = true; return 'off'; } return 'fail'; }
    if (!g || g.ok === false || !acctReady()) return 'fail';
    const d = csDecide(g, false);
    if (d === 'adopt') { if (csSafe()) { csAdopt(g, 'sync'); return 'adopt'; } CS.ok = false; csWatch(); return 'later'; } // (mid-game: at the next quiet moment)
    CS.ok = true; return d === 'push' ? csPush(true) : d;
  })().finally(() => { CS.sync = null; }));
}
// the account's copy in place of this phone's (the phone's own settings and the sign-in kept), and the game starts again with it
function csAdopt(g, why) {
  CS.hold = true; CS.reloading = true; clearTimeout(CS.t); CS.t = 0;
  const keep = {}, data = {}; for (const k of CS_LOCAL) if (store[k] !== undefined) keep[k] = store[k];
  for (const k of Object.keys(g.data)) if (!CS_LOCAL.includes(k)) data[k] = g.data[k];
  for (const k of Object.keys(store)) delete store[k];
  Object.assign(store, { level: 0, sel: 0, best: {}, stars: {}, seen: {}, muted: false, runs: 0 }, data, keep);
  csBookSet({ u: csUid(), at: g.at, h: csHash(csCanon(csData())) });
  store.csHi = { n: acName() || store.name || '', k: why }; save(); saveSend(); // (the app's own copy too, at once)
  if (csBootUp()) { const m = $('bootMsg'); if (m) m.textContent = 'Bringing back your progress'; }
  setTimeout(() => location.reload(), 450);
}
// the loading screen waits a moment for the account's copy (signed in), so a phone that's behind takes it before the lobby is up
function csBootWait() {
  if (CS.reloading) return new Promise(() => {});
  if (!CS.bootP) return Promise.resolve();
  return Promise.race([CS.bootP, new Promise(r => setTimeout(r, 2500))]).then(() => CS.reloading ? new Promise(() => {}) : undefined);
}
// after the game started again with the account's copy: a welcome, once the loading screen has gone
function csHello() {
  const h = store.csHi; if (!h) return; delete store.csHi; save();
  const w = setInterval(() => { if (csBootUp()) return; clearInterval(w);
    setTimeout(() => frToast(h.k === 'sync' ? '<span>Your progress from your other phone is here.</span>' : '<span>Welcome back, <b>' + frEsc(hdOf(h.n || 'you')) + '</b>! Your progress is back.</span>'), 700); }, 250);
}
// just logged in (acLogin): the account's copy comes to this phone. True when that takes over from the login (the game starts again with
// it, or the loading screen's sheet says what's what)
async function csPull(me) {
  if (!CS || CS.hold) return false;
  const ba = baSheet(); acBusy(ba ? 'Finding your progress…' : 'Logging in…');
  let g = null, why = 'net';
  if (CS.off) why = 'off';
  else try { g = await sbRpc('rm_save_get', {}); if (!g || g.ok === false) g = null; } catch (e) { if (csMissing(e)) { CS.off = true; why = 'off'; } }
  if (g && g.data) {
    const d = csDecide(g, true);
    if (d === 'adopt') { csAdopt(g, 'back'); if (ba) baSay(me, '<b>Welcome back, ' + frEsc(hdOf(me.name || acName())) + '!</b><p>Bringing back your progress…</p>'); else acBusy('Bringing back your progress…'); return true; }
    CS.ok = true; if (d === 'push') csPush(true); return false;
  }
  if (g && !ba) { CS.ok = true; csPush(true); } // (nothing kept with the account yet: this phone's progress goes with it from now on. From the loading
  // screen it waits for Start fresh, then goes up with the next save)
  if (ba) { baEmpty(me, g ? 'none' : why); return true; }
  return false;
}
// Log out (Settings): your progress to your account first, then this phone starts fresh for the next player. If it can't be saved,
// nothing changes. Without saves on the server (the v312 SQL not run yet): logged out as before, the progress kept here
async function csLogout() {
  const r = CS.off ? 'off' : CS.hold ? 'behind' : CS.ok ? await csPush(true) : await csSync();
  if (r === 'off') { await acLogout(); return 'You’re logged out. This phone keeps its progress.'; }
  if (!['ok', 'same', 'behind', 'later'].includes(r)) return 'Your progress couldn’t be saved, so you’re still signed in. Try again when you’re online.';
  CS.hold = true; CS.reloading = true; await acLogout(); csFresh(); setTimeout(() => location.reload(), 300); return 'reload';
}
// this phone back to a first launch, as Restart Game does it: sound, music, graphics and orientation kept
function csFresh() {
  const keep = {}; for (const k of ['muted', 'sfxOff', 'musicOff', 'gfx', 'orient']) if (store[k] !== undefined) keep[k] = store[k];
  for (const k of Object.keys(store)) delete store[k];
  Object.assign(store, { level: 0, sel: 0, best: {}, stars: {}, seen: {}, muted: false, runs: 0, tut: { ph: 'match' } }, keep);
  csBookSet(null); save(); saveSend(); try { AU.trim && AU.trim(); } catch (e) {}
}
// the Log in form's word on progress
function csInNote() {
  if (baSheet()) return '<p class="frfine acw">Your rank, drops and everything you’ve unlocked come back to this phone.</p>';
  if (CS.off || csBook() || !((store.xp || 0) > 0 || (store.runs || 0) > 0)) return '';
  return '<p class="frfine acw">Logging in brings your account’s progress to this phone, in place of the progress on it now.</p>';
}
document.addEventListener('visibilitychange', () => { if (document.hidden && CS.dirty) csPush(true); });
window.addEventListener('pagehide', () => { if (CS.dirty) csPush(true); });
try { if (acctReady()) CS.bootP = csSync().catch(() => {}); } catch (e) {} // (signed in: the account's copy, checked while the game loads)

// ---- (v312) "I already have an account" (the loading screen): the account sheet over the loading screen, Log in only. The first launch
// waits while it's open (baAfter); a login with progress starts the game again with it, one without says so (baEmpty)
function baSheet() { return AC.open && $('acModal').classList.contains('boot'); } // (declarations: the saves above ask before this line runs)
function baOn() { return BA.on && (!acctReady() || baSheet() || CS.reloading); } // (the loading screen stays while its sheet is open, or the game's starting again)
function baOpen() {
  BA.want = false; const b = $('bootAcct'); if (b) { b.classList.remove('wait'); b.textContent = 'I already have an account'; }
  if (!SB_CFG || acctReady()) { if (b) b.hidden = true; return; }
  const m = $('acModal'), sm = m.querySelector('.tthd small'); m.classList.add('boot'); if (sm) sm.textContent = 'Already playing?';
  acctOpen(null, 'in');
}
function baClosed() {
  const m = $('acModal'); if (!m.classList.contains('boot')) return; m.classList.remove('boot');
  const sm = m.querySelector('.tthd small'); if (sm) sm.textContent = 'Play with others';
  if (acctReady()) { const b = $('bootAcct'); if (b) b.hidden = true; }
}
function baAfter(fn) { if (!baSheet()) return fn(); const w = setInterval(() => { if (CS.reloading) return clearInterval(w); if (!baSheet()) { clearInterval(w); fn(); } }, 150); }
function baSay(me, html, btns) { BA.me = me; $('acBody').innerHTML = '<div class="frmsg acmsg">' + FR_FACES + html + (btns ? '<div class="acbtns">' + btns + '</div>' : '') + '</div>'; }
function baEmpty(me, kind) {
  AC.busy = false;
  const p = kind === 'net' ? 'Your progress couldn’t be fetched just now. Check your connection, then try again.'
    : kind === 'off' ? 'Bringing back progress isn’t switched on yet, so this phone starts fresh for now.'
    : 'There’s no progress saved with this account yet. Open Roll Model signed in on the phone you played on, and it saves it there. Then try again here.';
  baSay(me, '<b>Signed in as ' + frEsc(hdOf(me.name || acName())) + '</b><p>' + p + '</p>',
    (kind === 'off' ? '' : '<button class="frb go" data-ba="retry" type="button">Try again</button>') + '<button class="frb ghost" data-ba="fresh" type="button">Start fresh</button>');
}
$('acBody').addEventListener('click', async e => {
  const b = e.target.closest('[data-ba]'); if (!b || b.disabled || AC.busy) return; AU.init(); AU.ui();
  if (b.dataset.ba === 'fresh') return acDone('<span>Signed in as <b>' + frEsc(hdOf(acName())) + '</b></span>');
  AC.busy = true; for (const x of $('acBody').querySelectorAll('[data-ba]')) x.disabled = true; const p = $('acBody').querySelector('.acmsg p'); if (p) p.textContent = 'Looking for your progress…';
  let took = false; try { took = await csPull(BA.me || {}); } catch (x) {} AC.busy = false;
  if (!took) acDone('<span>Signed in as <b>' + frEsc(hdOf(acName())) + '</b></span>');
});
BA.ready = true; if (BA.on && !SB_CFG) { BA.on = false; const b = $('bootAcct'); if (b) b.hidden = true; } else if (BA.want) baOpen();
"""

CSS = r"""
/* (v312) "I already have an account": text at the foot of the first loading screen; its sheet over the loading screen, Log in only */
#boot .bootacct{position:absolute;left:50%;bottom:calc(env(safe-area-inset-bottom,0px) + 14px);z-index:2;transform:translateX(-50%);margin:0;padding:12px 18px;border:0;background:none;font:800 14px/1.2 var(--font-ui);color:#2A2437;text-decoration:underline;text-decoration-thickness:2px;text-underline-offset:4px;white-space:nowrap;cursor:pointer;-webkit-tap-highlight-color:transparent;animation:fadein .5s ease-out both}
#boot .bootacct.wait{text-decoration:none;opacity:.7}
#boot.gone .bootacct{pointer-events:none}
#acModal.boot{z-index:45}
#acModal.boot .actabs{display:none}
"""

def apply(s):
    # ---------------- the link, from the first moment of a first launch; every save also marks the account's copy as due
    s = rep(s, '<p class="bootmsg" id="bootMsg">Loading</p>', '<p class="bootmsg" id="bootMsg">Loading</p><button class="bootacct" id="bootAcct" type="button" hidden>I already have an account</button>')
    s = rep(s, "  if (NSAVE && j) { saveJ = j; if (!saveQ) saveQ = setTimeout(saveSend, 400); } };",
               "  if (NSAVE && j) { saveJ = j; if (!saveQ) saveQ = setTimeout(saveSend, 400); } csMark(); }; // (v312: and, signed in, to your account in a while)")
    a = "if (NSAVE) { document.addEventListener('visibilitychange', () => { if (document.hidden) saveSend(); }); window.addEventListener('pagehide', saveSend); }\n"
    s = rep(s, a, a + EARLY)
    # ---------------- the saves and the loading screen's sheet, with the accounts
    a = "\n// ---- Settings: the account (who's signed in, Log out, Delete account with a second tap to be sure), or Make an account / Log in\nfunction acSetPaint() {"
    s = rep(s, a, MAIN.rstrip('\n') + "\n" + a)
    s = rep(s, "    acDone('<span>Welcome back, <b>' + frEsc(hdOf(me.name)) + '</b>!</span>');\n  } catch (e) { acFail(e); }",
               "    if (await csPull(me)) return; // (v312: the account's progress, in place of this phone's: the game starts again with it)\n"
               "    acDone('<span>Welcome back, <b>' + frEsc(hdOf(me.name)) + '</b>!</span>');\n  } catch (e) { acFail(e); }")
    s = rep(s, "    acDone('<span>Welcome, <b>' + frEsc(hdOf(me.name)) + '</b>! Your account is ready.</span>');\n",
               "    acDone('<span>Welcome, <b>' + frEsc(hdOf(me.name)) + '</b>! Your account is ready.</span>'); csSync(); // (v312: this phone's progress, its first copy)\n")
    s = rep(s, "$('acModal').hidden = true;", "$('acModal').hidden = true; baClosed();")
    s = rep(s, "+ (swap ? '<p class=\"frfine acw\">Logging in swaps <b>' + frEsc(swap) + '</b>, the player on this device, for your account.</p>' : '') + '</form>';",
               "+ (swap ? '<p class=\"frfine acw\">Logging in swaps <b>' + frEsc(swap) + '</b>, the player on this device, for your account.</p>' : '') + csInNote() + '</form>';")
    s = rep(s, "async function acDelete() { const r = await sbRpc('rm_delete_me', {}); if (!r || !r.ok) throw new Error('not deleted'); acSignOut(); }",
               "async function acDelete() { const r = await sbRpc('rm_delete_me', {}); if (!r || !r.ok) throw new Error('not deleted'); csBookSet(null); acSignOut(); }")
    # ---------------- Settings: Log out asks, saves, then starts the phone fresh
    s = rep(s, "  else if (AC.del && acctReady()) {",
               "  else if (AC.out && acctReady()) { t = AC.busy ? 'Saving your progress to <b>' + frEsc(hdOf(nm)) + '</b>…' : 'Log out of <b>' + frEsc(hdOf(nm)) + '</b>? Your progress stays with your account, and this phone starts fresh for the next player.'; h = b('outyes', 'Log out') + b('outno', 'Stay'); } // (v312)\n"
               "  else if (AC.del && acctReady()) {")
    s = rep(s, "  if (a === 'del' || a === 'delno') { AC.del = a === 'del'; acSetPaint();",
               "  if (a === 'del' || a === 'delno' || a === 'out' || a === 'outno') { AC.del = a === 'del'; AC.out = a === 'out'; acSetPaint();")
    s = rep(s, "  try { if (a === 'out') { await acLogout(); AC.note = 'You’re logged out.'; } else if (a === 'delyes') {",
               "  try { if (a === 'outyes') { const r = await csLogout(); if (r === 'reload') return; AC.note = r; } else if (a === 'delyes') {")
    s = rep(s, "  AC.busy = false; AC.del = false; acSetPaint();\n});", "  AC.busy = false; AC.del = false; AC.out = false; acSetPaint();\n});")
    # ---------------- the Privacy Policy says so
    s = rep(s, "priv: ['Privacy Policy', '<p>Updated October 15, 2026.</p><h3>On this device</h3><p>Your progress (your dabs, items, ranks and settings) is saved on this device. You don’t need an account to play.</p>",
               "priv: ['Privacy Policy', '<p>Updated October 16, 2026.</p><h3>On this device</h3><p>Your progress (your dabs, items, ranks and settings) is saved on this device. You don’t need an account to play.</p>")
    s = rep(s, "<p>Your password is handled by our sign-in provider, Supabase.",
               "<p>While you’re signed in, we also keep a copy of your game progress (your dabs, items, ranks, unlocks and lessons done) with your account, so you can log in on another phone and pick up where you left off. Log out leaves it with your account and starts this device fresh.</p><p>Your password is handled by our sign-in provider, Supabase.")
    # ---------------- Restart Game: the note of what was last sent goes too (logging in again brings the account's progress)
    s = rep(s, "disarm(); b.disabled = true; const gone = acReset(); // (v306)",
               "disarm(); b.disabled = true; const gone = acReset(); CS.hold = true; csBookSet(null); // (v306; v312)")
    # ---------------- the end of loading: a moment for the account's copy; a first launch waits on "Tap to start" with the link
    s = rep(s, "bootTo(1, 1, 0, 'Ready');", "try { await csBootWait(); } catch (e) {} // (v312: signed in, the account's copy first, so a phone that's behind takes it now)\nbootTo(1, 1, 0, 'Ready');")
    s = rep(s, "const soundOk = window.__tapGate === false || store.muted || await AU.tryStart();",
               "const soundOk = (window.__tapGate === false || store.muted || await AU.tryStart()) && !baOn(); // (v312: a first launch ends on \"Tap to start\", with \"I already have an account\" under it)")
    s = rep(s, "window.addEventListener('keydown', e => { if (bootHold) go(e); }, true);", "window.addEventListener('keydown', e => { if (bootHold && !AC.open) go(e); }, true);")
    s = rep(s, "if (AU.state === 'running') { clearInterval(late); go(); }", "if (AU.state === 'running' && !baOn()) { clearInterval(late); go(); }")
    s = rep(s, "if (FL && FL.due) FL.boot(); else if (!store.orient)", "try { csHello(); } catch (e) {} if (FL && FL.due) baAfter(() => FL.boot()); else if (!store.orient)")
    i = s.rfind('</style>'); s = s[:i] + CSS + s[i:]
    return s
