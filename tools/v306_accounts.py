"""v306 (accounts): usernames in the intro, the account form when online play unlocks, logging in, and the account in Settings.

- A player's name is their username now: 3 to 16 letters, numbers or _ (the game keeps them to 12, as it always has for names), at
  least one letter, one of a kind, nothing rude and no reserved names. Wherever one is typed (the first launch's name card, Rename in
  the lobby, the Friends screen, the account form) a line under it says what's wrong at once (unWhy: the same rules as the server's
  _uname_why), then, online, whether it's free ("Checking...", "It's yours", "Taken. Try another"). Next or Save only go on with one that
  can be had; it's kept on the server as they do (rm_me makes the profile with it, rm_rename changes it). Offline, the first launch
  goes on anyway and the friends client checks it later. The dice only rolls usernames (no spaces, two digits on the end).
- Friends and online play need an account: a username and password, first and last name, birthday (13 or older) and the Terms of
  Service and Privacy Policy agreed to. It's made from the player you already are (the anonymous one v305 made: the same user, so the
  username, friend code and friends carry over). Supabase signs in with an email, so each account gets a made-up one from its id
  (players never see it); you log in with your username. Logging in on a device that had an anonymous player deletes that player
  (with its own token), so its username is free again.
- The account sheet (the Friends sheet's taped notebook page): New account and Log in. Opened from the Friends screen (which says
  friends need an account), from Play online, and from Settings, where the Account row shows who's signed in, with Log out and
  Delete account (the App Store asks for deleting in the app).
- Play online (Choose event's old Matchmaking card) unlocks once the Strokes page has been opened (players who did the Strokes lesson
  already have). Tapped: no account, the sheet first; then window.onlineOpen() (the lobby's).
- The Privacy Policy and Terms say what accounts keep. Restart Game also lets go of the player online (an anonymous one is deleted, an
  account is logged out on this device).
- v305's client, changed: frStart makes a profile only with a username that can be had (else the Friends screen asks for one), and
  keeps store.name in step with the server's. A device that logged out, or a real account whose session is gone, is signed out
  (store.sbs.out): never quietly given a new anonymous player. A session refresh and an anonymous sign-up wait up to 30 s, and a refresh
  that doesn't come back is asked again at once (a lost answer used the refresh token up, and the player with it).
- For the other modules: acctReady() (signed in with a real account) and acctOpen(next, tab) (the sheet; next() after a sign-up or
  log-in), also on window."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

HTML = r"""  <div class="modal ttm" id="acModal" hidden><div class="ttcard accard" role="dialog" aria-modal="true" aria-labelledby="acTitle">
    <button class="ttx" id="acX" type="button" aria-label="Close"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6.5 6.5l11 11M17.5 6.5l-11 11" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"/></svg></button>
    <div class="tthd"><small>Play with others</small><h3 id="acTitle">Make an account</h3></div>
    <div class="actabs" role="tablist" aria-label="Account"><button type="button" role="tab" data-tab="new" aria-selected="true" aria-controls="acBody">New account</button><button type="button" role="tab" data-tab="in" aria-selected="false" aria-controls="acBody">Log in</button></div>
    <div class="acbody" id="acBody" role="tabpanel"></div>
  </div></div>
"""

CSS = r"""
/* (v306) usernames: the line under a name field (what's wrong at once, then whether it's free) */
.flun{min-height:1.3em;margin:9px 2px -4px;font:700 13px/1.3 var(--font-ui);color:#B9B2C6}
.flun[data-s="ok"]{color:#7FE09A}.flun[data-s="bad"]{color:#FF8D9B}
.unst{min-height:1.3em;margin:0;font:700 12.5px/1.3 var(--font-ui);color:#6E6680}
.unst[data-s="ok"]{color:#2C7A3F}.unst[data-s="bad"]{color:#C2283C}
#nameModal .unst{margin:-4px 0 0;text-align:center;font-size:13.5px}
.unshake{animation:unshake .38s ease}
@keyframes unshake{20%{translate:-6px 0}40%{translate:5px 0}60%{translate:-3px 0}80%{translate:2px 0}}
.unpick{display:grid;gap:6px;width:100%;max-width:310px;margin-top:2px}
.unpick>div{display:flex;gap:8px}
.unpick input{flex:1;min-width:0;height:44px;box-sizing:border-box;padding:0 12px;border:2px solid var(--black);border-radius:6px;background:#fff;color:var(--black);font:600 17px/1 var(--font-ui)}
.unpick input:focus{outline:none;box-shadow:0 0 0 3px rgba(242,181,58,.6)}
.unpick .unst{text-align:left}
/* (v306) the account sheet: the Friends sheet's taped notebook page, with the form written on its lines */
#docModal.acup{z-index:31}
.accard{width:min(100%,400px)}
.actabs{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:6px;margin-left:-10px}
.actabs button{--skp:#E3A12C;--skt:#2A1A04;display:flex;align-items:center;justify-content:center;min-height:38px;padding:6px 4px;border:0;border-radius:2px;cursor:pointer;
  background:url(art/m_cpaper_g.webp) center/180px,var(--skp);background-blend-mode:multiply;color:var(--skt);font:400 13px/1 var(--font-display);text-transform:uppercase;letter-spacing:.02em;
  box-shadow:inset 0 0 0 1px rgba(0,0,0,.08),3px 4px 0 rgba(0,0,0,.4);filter:brightness(.82) saturate(.9);scale:.95;transition:scale .18s ease,filter .18s ease,translate .18s ease}
.actabs button[data-tab="in"]{--skp:#3A84D4;--skt:#FFF8EA}
.actabs button[aria-selected="true"]{filter:none;scale:1;translate:0 -2px;box-shadow:inset 0 0 0 1px rgba(0,0,0,.08),5px 6px 0 rgba(0,0,0,.45)}
.acbody{display:grid;grid-template-columns:minmax(0,1fr);align-content:start;min-height:min(250px,40vh);overflow:auto;margin-right:-6px;padding:4px 6px 4px 0;-webkit-overflow-scrolling:touch;overscroll-behavior:contain}
.acform{display:grid;grid-template-columns:minmax(0,1fr);gap:10px;min-width:0}
.acform.busy{pointer-events:none}
.acf{display:grid;gap:5px;min-width:0;margin:0;padding:0;border:0}
.acf label,.acf legend{display:block;margin:0;padding:0;font:800 11px/1 var(--font-ui);letter-spacing:.12em;text-transform:uppercase;color:#6E6680}
.acf legend{margin-bottom:5px}
.acform input[type=text],.acform input[type=password],.acform select{display:block;width:100%;min-width:0;height:44px;box-sizing:border-box;margin:0;padding:0 11px;border:2px solid var(--black);border-radius:6px;background-color:#fff;color:var(--black);font:600 16px/1 var(--font-ui);-webkit-appearance:none;appearance:none}
.acform input:focus,.acform select:focus{outline:none;box-shadow:0 0 0 3px rgba(242,181,58,.6)}
.acform input[aria-invalid="true"]{border-color:#C2283C}
.acform select{padding:0 24px 0 9px;background:#fff url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 12 8'%3E%3Cpath d='M1 1.5l5 5 5-5' fill='none' stroke='%23171320' stroke-width='2.2' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E") right 8px center/11px 8px no-repeat}
.acform select.empty{color:#8E879C}
.acpair{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:8px}
.acpair>div{display:grid;gap:5px;min-width:0}
.acbd{display:grid;grid-template-columns:minmax(0,1.5fr) minmax(0,.9fr) minmax(0,1.15fr);gap:6px}
.acpw{display:flex;gap:6px}.acpw input{flex:1}
.acshow{flex:none;min-width:64px;min-height:44px}
.acagree{display:flex;flex-wrap:wrap;align-items:center;gap:2px 5px;font:600 13.5px/1.4 var(--font-ui);color:var(--black)}
.acagree input{flex:none;width:26px;height:26px;margin:0 3px 0 0;box-sizing:border-box;border:2px solid var(--black);border-radius:5px;background:#fff;-webkit-appearance:none;appearance:none;cursor:pointer}
.acagree input:checked{border-color:#1F6F33;background:#2E9E48 url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath d='M5 12.5l4.5 4.5L19 7.5' fill='none' stroke='%23fff' stroke-width='3.4' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E") center/18px no-repeat}
.acagree input:focus-visible{outline:none;box-shadow:0 0 0 3px rgba(242,181,58,.6)}
.acagree label{cursor:pointer}
.aclink{padding:0;border:0;background:none;color:#1F5FB0;font:800 13.5px/1.4 var(--font-ui);text-decoration:underline;text-underline-offset:2px;cursor:pointer}
.acerr{margin:0;font:700 13px/1.35 var(--font-ui);color:#C2283C}.acerr:empty{display:none}
.acgo{min-height:46px;font-size:13.5px}
.acbody .frfine{margin:0}
.acmsg p b{font:inherit;font-weight:800;text-transform:none;color:var(--black)}
.acmsg .acbtns{display:flex;flex-wrap:wrap;justify-content:center;gap:8px;margin-top:2px}
@media (min-aspect-ratio:1/1) and (max-height:600px){.accard{width:min(100%,640px)}.accard .tthd small{display:none}.acform{grid-template-columns:minmax(0,1fr) minmax(0,1fr);column-gap:16px;row-gap:8px}.acform>.acw{grid-column:1/-1}.acform>.acagree,.acform>.acgo{grid-column:auto}.acform>.acerr,.acform>.frfine{order:1}.acform input[type=text],.acform input[type=password],.acform select,.acshow{height:40px;min-height:40px}.acbody{min-height:0}.acform.acin{grid-template-columns:minmax(0,1fr);max-width:420px}} /* (wide: two columns, the box and the button side by side) */
/* (v306) Settings: the account */
.acrow .acnote{text-align:left}.acrow .acnote b{color:#fff}
.sbtn.acdel{background:linear-gradient(180deg,#E25466 0%,#C93A4C 55%,#AE2D3E 100%)}
"""

# the username rules, next to the names they're for (randomName rolls only usernames now)
RULES = r"""// ---------- (v306) usernames: 3 to 16 letters, numbers or _ (at least one letter), one of a kind, nothing rude and no reserved names.
// The same rules as the server's (_uname_why and _uname_bad in supabase/migrations/*_accounts.sql: change one, change the other), so the
// player hears at once what's wrong; the server's answer is the one that counts ----------
// bad anywhere in the name (once capitals are split into words, leetspeak is undone and the ordinary words below are taken out)
const UN_SUB = ['fuck', 'fcuk', 'phuk', 'phuck', 'shit', 'cunt', 'nigg', 'fagg', 'bitch', 'whore', 'slut', 'twat', 'pussy', 'asshole',
  'hitler', 'porn', 'penis', 'vagina', 'dildo', 'boob', 'jizz', 'nazi', 'kkk', 'retard', 'wank', 'cock', 'dick', 'sex', 'rape', 'rapist',
  'piss', 'bastard', 'douche', 'bollock', 'tranny', 'molest', 'pedo', 'orgasm', 'horny', 'boner', 'blowjob', 'handjob', 'nipple', 'testic',
  'scrot', 'anal', 'cumshot', 'milf', 'hentai', 'xxx', 'killyou', 'suicide'];
// ordinary words that contain one of those
const UN_OK = ['scunthorpe', 'niggle', 'niggling', 'swank', 'peacock', 'cockatoo', 'cockatiel', 'cockpit', 'cockroach', 'woodcock',
  'hancock', 'hitchcock', 'shuttlecock', 'cockle', 'gamecock', 'babcock', 'cocker', 'cockney', 'dickens', 'dickinson', 'benedick', 'dickson',
  'sussex', 'essex', 'sextant', 'sexton', 'grape', 'drape', 'scrape', 'trapez', 'rapeseed', 'parapet', 'therape', 'therapist', 'serape', 'crape',
  'torpedo', 'pedometer', 'analy', 'analog', 'canal', 'kanal', 'banal', 'thorny', 'trombone'];
// bad as a word of its own (they hide inside ordinary words: class, cucumber, title, raccoon, hello...)
const UN_WHOLE = ['ass', 'arse', 'cum', 'fag', 'fuk', 'spic', 'kike', 'chink', 'coon', 'tit', 'tits', 'anus', 'homo', 'damn', 'hell',
  'crap', 'prick', 'slag', 'twit', 'turd', 'nude', 'naked', 'kys'];
const UN_RESERVED = /^(admin|administrator|mod|mods|moderator|staff|support|help|helpdesk|official|system|server|root|null|undefined|guest|you|cpu|bot|rollmodel|roll_model|bloop|olbloop|ol_bloop|marcelin|anthropic|claude|player[0-9_]*)$/;
function unBad(p) {
  const raw = String(p == null ? '' : p).replace(/([a-z])([A-Z])/g, '$1 $2').toLowerCase(); // (as written: digits and _ split words, "Dick99")
  let sk = raw.replace(/[0-9@$!|+]/g, c => 'oizeasgtbgasiit'['0123456789@$!|+'.indexOf(c)]); // (leetspeak undone: "d1ck", "4ss")
  for (const w of UN_OK) sk = sk.split(w).join(' ');
  const letters = sk.replace(/[^a-z]/g, ''), words = raw.split(/[^a-z]+/);
  if (UN_SUB.some(w => letters.includes(w))) return true;
  if (words.concat(sk.split(/[^a-z]+/)).some(w => UN_WHOLE.includes(w))) return true;
  let runs = '', run = ''; // (letters spelled out one at a time, "d_i_c_k", count as a word too)
  for (const w of words) { if (w.length === 1) run += w; else { if (run.length > 1) runs += ' ' + run; run = ''; } }
  if (run.length > 1) runs += ' ' + run;
  return runs.trim().split(' ').some(w => UN_WHOLE.includes(w) || UN_SUB.some(s => w.includes(s)));
}
// why a username can't be used (null when it can): short, long, chars, reserved or bad (taken is the server's to say)
function unWhy(p) {
  const n = String(p == null ? '' : p), l = n.toLowerCase(), len = Array.from(n).length;
  if (len < 3) return 'short';
  if (len > 16) return 'long';
  if (!/^[A-Za-z0-9_]+$/.test(n) || !/[A-Za-z]/.test(n)) return 'chars';
  if (UN_RESERVED.test(l) || /^_*(admin|moderator|official)/.test(l) || /(admin|moderator|official)_*[0-9]*$/.test(l)) return 'reserved';
  if (unBad(n)) return 'bad';
  return null;
}
const unNorm = v => String(v == null ? '' : v).trim().replace(/\s+/g, '_'); // (usernames have no spaces: _ in their place)
function unSay(why, n) {
  return why === 'empty' ? 'Pick a username' : why === 'short' ? 'At least 3 letters or numbers' : why === 'long' ? 'That’s too long'
    : why === 'chars' ? (/\s/.test(n) ? 'No spaces. Try _ instead' : /^[0-9_]*$/.test(n) ? 'Add a letter or two' : 'Just letters, numbers and _')
    : why === 'reserved' ? 'That one’s reserved. Try another' : why === 'bad' ? 'Let’s keep it friendly. Try another' : why === 'taken' ? 'Taken. Try another'
    : why === 'slow_down' ? 'That’s a lot of changes. Try again later' : why === 'offline' ? 'You’re offline. Try again when you’re online'
    : why === 'out' ? 'You’re signed out. Log in first' : 'Try another';
}
"""

JS = r"""
// ---------- (v306) usernames and accounts. A player's name is their username: one of a kind, checked as it's typed and kept on the
// server when it's picked. An account (username and password, first and last name, birthday, the terms agreed to) is what friends and
// online play need; it's made from the player you already are, so the same user keeps its username, friend code and friends.
// Supabase signs in with an email, so each account gets a made-up one from its id (players never see it); you log in with your
// username. store.sbs (v305's: the refresh token and user id) also says perm (a real account, not anonymous), acct (its details
// saved), name (the username on the server) and out (signed out: no player here until you log in or make an account) ----------
const ACC_TERMS = 'tos-2026-10-15'; // (which Terms of Service and Privacy Policy were agreed to: kept with the account)
const AC = { open: false, tab: 'new', next: null, busy: false, f: {}, show: false, ret: null, del: false, note: '', err: '' };
function acOut() { return !!(store.sbs && store.sbs.out); } // (these three are declarations, so code placed before this block can call them)
function acHas() { return !!(SB_CFG && store.sbs && store.sbs.rt && !acOut()); } // (a player on the server: a new name goes there first)
function acctReady() { return !!(SB_CFG && store.sbs && store.sbs.rt && store.sbs.perm && store.sbs.acct && !acOut()); } // (signed in, with a real account)
const acName = () => (FR.me && !FR.me.needs_name && FR.me.name) || (store.sbs && store.sbs.name) || '';
const acErrText = e => (typeof navigator !== 'undefined' && navigator.onLine === false) ? 'You’re offline. Try again when you’re online.' : e && e.status === 429 ? 'Too many tries. Wait a minute, then try again.' : 'Can’t reach the Roll Model server. Try again in a bit.';
const acJwt = t => { try { return JSON.parse(atob(String(t).split('.')[1].replace(/-/g, '+').replace(/_/g, '/'))) || {}; } catch (e) { return {}; } };
const acStop = (why, at) => Object.assign(new Error(why || 'bad'), { why: why || 'bad', at });
// Supabase's API as sbFetch does it, with the method and token given (a PUT to change the user; another player's token, to delete it)
async function acFetch(method, path, body, tok, wait) {
  const h = { apikey: SB_CFG.key, 'Content-Type': 'application/json' }; if (tok) h.Authorization = 'Bearer ' + tok;
  const ctl = typeof AbortController === 'function' ? new AbortController() : null, to = setTimeout(() => { if (ctl) ctl.abort(); }, wait || 12000);
  try {
    const r = await fetch(SB_CFG.url + path, { method, headers: h, body: body ? JSON.stringify(body) : undefined, signal: ctl ? ctl.signal : undefined });
    const t = await r.text(); let j = null; try { j = t ? JSON.parse(t) : null; } catch (e) {}
    if (!r.ok) { const e = new Error((j && (j.msg || j.message || j.error_description || j.error)) || 'HTTP ' + r.status); e.status = r.status; e.code = j && (j.error_code || j.code); throw e; }
    return j;
  } finally { clearTimeout(to); }
}
// a new session from the refresh token: given longer than other calls, and asked again at once if it doesn't come back. The server may
// have used the token up anyway (it takes the same one again for a few seconds only), and a lost one logs a real account out
async function acRefresh(rt) {
  const go = () => acFetch('POST', '/auth/v1/token?grant_type=refresh_token', { refresh_token: rt }, null, 30000);
  try { return await go(); } catch (e) { if (e.status) throw e; await new Promise(r => setTimeout(r, 600)); return go(); }
}
// what the server says of this player: a real account or not, and its username (the name everywhere in the game)
function acSync(r) {
  if (!r || r.ok === false || !r.id || !store.sbs) return;
  store.sbs = Object.assign({}, store.sbs, { perm: r.anon === false ? 1 : 0, acct: r.account ? 1 : 0 });
  if (!r.needs_name && r.name) { store.sbs.name = r.name; if (store.name !== r.name) { store.name = r.name; paintName(); } }
  save();
}
function acPaintAll() { if (!$('setModal').hidden) acSetPaint(); if (menuPage === 'events') acMatchPaint(); if (FR.open) { FR.sig = ''; frRender(); } }

// ---- the line under a username field: what's wrong at once; then (online, after a pause) whether it's free
const UN_W = {}, UN_FREE = new Map(); // (each field's check, by its id; the server's answers, a minute each)
const unMine = n => { const m = acHas() && acName(); return !!m && m.toLowerCase() === String(n).toLowerCase(); };
function unWatch(id, stId, onState) {
  let t = 0, seq = 0;
  const show = (s, txt) => { const i = $(id), st = $(stId); if (!i) return; i.dataset.un = s; i.setAttribute('aria-invalid', String(s === 'bad')); if (st) { st.dataset.s = s; st.textContent = txt; } if (onState) onState(s); };
  return UN_W[id] = () => {
    const i = $(id); if (!i) return; clearTimeout(t); const n = unNorm(i.value), why = n ? unWhy(n) : 'empty', my = ++seq;
    if (why) return show('bad', unSay(why, n));
    if (unMine(n)) return show('ok', 'It’s yours');
    if (!SB_CFG || navigator.onLine === false) return show('off', 'Looks good');
    const c = UN_FREE.get(n.toLowerCase()); if (c && Date.now() - c.at < 60000) return show(c.ok ? 'ok' : 'bad', c.ok ? 'It’s yours' : unSay(c.why, n));
    show('wait', 'Checking…');
    t = setTimeout(async () => { let r = null; try { r = await sbFetch('/rest/v1/rpc/rm_name_check', { p_name: n }); if (r) UN_FREE.set(n.toLowerCase(), { at: Date.now(), ok: !!r.ok, why: r.why }); } catch (e) {}
      if (my !== seq) return; if (!r) show('off', 'Looks good'); else show(r.ok ? 'ok' : 'bad', r.ok ? 'It’s yours' : unSay(r.why, n)); }, 350);
  };
}
// typing in one: a space becomes _ (usernames have none), and its line checks again
document.addEventListener('input', e => { const i = e.target, w = i && UN_W[i.id]; if (!w) return; const v = i.value, f = v.replace(/\s/g, '_');
  if (f !== v) { const p = i.selectionStart; i.value = f; try { i.setSelectionRange(p, p); } catch (x) {} } if (i.id === 'frUnIn') FR.unTyped = i.value; w(); }, true);
// keep this username: the player's profile made with it, or renamed to it. Offline it goes on anyway (strict: not for a player already
// on the server, whose name there would differ)
async function unClaim(n, strict) {
  if (!SB_CFG || acOut()) return { ok: true, name: n, off: true };
  try {
    let r = await sbRpc('rm_me', { p_name: n, p_look: frLook(), p_rank: frRank() });
    if (r && r.ok !== false && r.name !== n) { const q = await sbRpc('rm_rename', { p_name: n }); r = q && q.ok ? Object.assign(r, { name: q.name, needs_name: false }) : q; }
    if (!r || r.ok === false) return { ok: false, why: (r && r.why) || 'bad' };
    FR.need = ''; if (FR.me) Object.assign(FR.me, { name: r.name, needs_name: false }); else FR.retryAt = 0;
    acSync(r); return Object.assign({}, r, { ok: true });
  } catch (e) { return strict ? { ok: false, why: e && e.out ? 'out' : 'offline' } : { ok: true, name: n, off: true }; }
}
// Next (or Save) under a username: kept on the server before it goes on; a problem stays on the card, said on the line
async function unSubmit(id, stId, btnId, done, strict) {
  const i = $(id), st = $(stId), b = $(btnId); if (!i || !b || b.dataset.busy) return; const n = unNorm(i.value), why = n ? unWhy(n) : 'empty';
  if (why || i.dataset.un === 'bad') { AU.nope(); if (UN_W[id]) UN_W[id](); if (st) kick(st, 'unshake'); return; }
  b.dataset.busy = '1'; b.disabled = true; if (st) { st.dataset.s = 'wait'; st.textContent = 'Checking…'; }
  const r = await Promise.race([unClaim(n, strict), new Promise(res => setTimeout(() => res(strict ? { ok: false, why: 'offline' } : { ok: true, name: n, off: true }), 9000))]);
  delete b.dataset.busy; b.disabled = false;
  if (!r.ok) { AU.nope(); if (r.why !== 'offline' && r.why !== 'slow_down' && r.why !== 'out') { UN_FREE.set(n.toLowerCase(), { at: Date.now(), ok: false, why: r.why }); if (UN_W[id]) UN_W[id](); } // (its line, and its button, as for any name that can't be had)
    if (st) { st.dataset.s = 'bad'; st.textContent = unSay(r.why, n); kick(st, 'unshake'); } return; }
  done(r.name || n);
}
unWatch('acUser', 'acUserSt', () => acValid()); // (the account form's)
// the first launch's name card (its form is built when the intro starts)
function unIntro() { unWatch('flNameIn', 'flNameSt', s => { const b = $('flNameGo'); if (b && !b.dataset.busy) b.disabled = s === 'bad'; }); $('flDice').addEventListener('click', () => { if (UN_W.flNameIn) UN_W.flNameIn(); }); }
// Rename in the lobby: the same line under it (its Save says what's wrong when it's tapped), and a long name a size smaller, to fit
unWatch('nameInput', 'nameSt', () => { const i = $('nameInput'), n = i.value.length; i.style.fontSize = n > 10 ? '21px' : n > 8 ? '25px' : ''; });
$('nameDice').addEventListener('click', () => UN_W.nameInput());

// ---- the Friends screen before the friends themselves: signed out, a username to pick, or no account yet
function acAskHtml() {
  const out = acOut(), lost = out && store.sbs.lost, nm = !out && acName();
  return '<div class="frmsg acmsg">' + FR_FACES + '<b>' + (lost ? 'You’ve been signed out' : out ? 'You’re signed out' : 'Make an account') + '</b><p>'
    + (lost ? 'Log in again to see your friends.' : out ? 'Log in to see your friends, or make a new account.' : 'Friends are for players with an account. Your username' + (nm ? ' <b>' + frEsc(nm) + '</b>' : '') + ' and friend code come with you.')
    + '</p><div class="acbtns"><button class="frb go" data-ac="new" type="button">Make an account</button><button class="frb" data-ac="in" type="button">Log in</button></div></div>';
}
function unPickHtml() {
  const why = FR.need || 'needs', nm = frName(), base = unNorm(nm);
  if (FR.unTyped == null) FR.unTyped = unWhy(base) ? randomName() : why === 'taken' ? base.slice(0, 10) + (10 + ((Math.random() * 90) | 0)) : base;
  queueMicrotask(() => { if (UN_W.frUnIn) UN_W.frUnIn(); }); // (its line, once it's on the page)
  return '<div class="frmsg acmsg">' + FR_FACES + '<b>Pick your username</b><p>' + (why === 'taken' ? 'Someone already has <b>' + frEsc(nm) + '</b>. Pick one that’s just yours.' : 'Your username is your name in the game, and it’s one of a kind. Pick yours to play online.') + '</p>'
    + '<form class="unpick" id="frUn" autocomplete="off" novalidate><div><input id="frUnIn" type="text" maxlength="12" autocomplete="off" autocapitalize="off" autocorrect="off" spellcheck="false" enterkeyhint="done" aria-label="Your username" aria-describedby="frUnSt" value="' + frEsc(FR.unTyped) + '"><button class="frb go" id="frUnGo" type="submit">Save</button></div><p class="unst" id="frUnSt" aria-live="polite"></p></form></div>';
}
unWatch('frUnIn', 'frUnSt', s => { const b = $('frUnGo'); if (b && !b.dataset.busy) b.disabled = s === 'bad'; });
frBody.addEventListener('submit', e => { if (e.target.id !== 'frUn') return; e.preventDefault(); e.stopImmediatePropagation(); AU.init(); // (before the add-a-friend form's handler)
  unSubmit('frUnIn', 'frUnSt', 'frUnGo', nm => { AU.power(); store.name = nm; save(); paintName(); FR.unTyped = null; FR.need = ''; FR.sig = ''; if (FR.me) frRender(); else { FR.retryAt = 0; frStart(); } }, true); }, true);
frBody.addEventListener('click', e => { const b = e.target.closest('[data-ac]'); if (!b) return; AU.init(); AU.ui(); acctOpen(null, b.dataset.ac === 'in' ? 'in' : 'new'); });

// ---- the account sheet: New account (from the player you are) and Log in
const AC_MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
const acYoung = () => !!store.acYoung && Date.now() - store.acYoung < 864e5; // (under 13: no account from this device for a day, so it isn't just tried again with another year)
const acSuggest = () => { const n = unNorm(acName() || store.name); return unWhy(n) ? randomName() : FR.need === 'taken' && !acName() ? n.slice(0, 10) + (10 + ((Math.random() * 90) | 0)) : n; }; // (their name, as a username)
const AC_YOUNG = '<div class="frmsg acmsg">' + FR_FACES + '<b>Sorry, not yet!</b><p>You need to be 13 or older to play online. Everything else in Roll Model is yours to play.</p><div class="acbtns"><button class="frb" data-ac="close" type="button">OK</button></div></div>';
const acPw = (id, k, ac) => '<div class="acpw"><input id="' + id + '" data-k="' + k + '" type="' + (AC.show ? 'text' : 'password') + '" maxlength="72" autocomplete="' + ac + '" autocapitalize="off" autocorrect="off" spellcheck="false" value="' + frEsc(AC.f[k] || '') + '"><button class="frb ghost acshow" data-ac="show" type="button" aria-pressed="' + AC.show + '">' + (AC.show ? 'Hide' : 'Show') + '</button></div>';
function acNewHtml() {
  const f = AC.f, yr = new Date().getFullYear(), o = (v, t, s) => '<option value="' + v + '"' + (String(s) === String(v) ? ' selected' : '') + '>' + t + '</option>';
  let mo = o('', 'Month', f.m || ''), dy = o('', 'Day', f.d || ''), ye = o('', 'Year', f.y || '');
  AC_MONTHS.forEach((m, i) => { mo += o(i + 1, m, f.m); }); for (let d = 1; d <= 31; d++) dy += o(d, d, f.d); for (let y = yr; y >= 1900; y--) ye += o(y, y, f.y);
  const tx = (id, k, lab, ac, cap) => '<div><label for="' + id + '">' + lab + '</label><input id="' + id + '" data-k="' + k + '" type="text" maxlength="40" autocomplete="' + ac + '" autocapitalize="' + cap + '" autocorrect="off" spellcheck="false" value="' + frEsc(f[k] || '') + '"></div>';
  return '<form class="acform" id="acNew" novalidate autocomplete="on">'
    + '<div class="acf"><label for="acUser">Username</label><input id="acUser" data-k="user" type="text" maxlength="12" autocomplete="username" autocapitalize="off" autocorrect="off" spellcheck="false" aria-describedby="acUserSt" value="' + frEsc(f.user || '') + '"><p class="unst" id="acUserSt" aria-live="polite"></p></div>'
    + '<div class="acf"><div class="acpair">' + tx('acFirst', 'first', 'First name', 'given-name', 'words') + tx('acLast', 'last', 'Last name', 'family-name', 'words') + '</div><p class="unst" id="acNameSt" aria-live="polite"></p></div>'
    + '<fieldset class="acf"><legend>Birthday</legend><div class="acbd"><select id="acM" data-k="m" aria-label="Birth month" autocomplete="bday-month">' + mo + '</select><select id="acD" data-k="d" aria-label="Birth day" autocomplete="bday-day">' + dy + '</select><select id="acY" data-k="y" aria-label="Birth year" autocomplete="bday-year">' + ye + '</select></div><p class="unst" id="acBdSt" aria-live="polite"></p></fieldset>'
    + '<div class="acf"><label for="acPass">Password</label>' + acPw('acPass', 'pass', 'new-password') + '<p class="unst" id="acPassSt" aria-live="polite"></p></div>'
    + '<div class="acagree acw"><input type="checkbox" id="acAgree" data-k="agree"' + (f.agree ? ' checked' : '') + ' aria-label="I agree to the Terms of Service and Privacy Policy"><label for="acAgree">I agree to the</label><button class="aclink" type="button" data-doc="tos">Terms of Service</button><span>and</span><button class="aclink" type="button" data-doc="priv">Privacy Policy</button></div>'
    + '<p class="acerr acw" id="acErr" role="alert">' + frEsc(AC.err) + '</p>'
    + '<button class="frb go acgo acw" id="acGo" type="submit" disabled>Make my account</button>'
    + '<p class="frfine acw">Friends see your username, paint colour and rank. Your name and birthday stay private.</p></form>';
}
function acInHtml() {
  const swap = acHas() && !(store.sbs && store.sbs.perm) && acName();
  return '<form class="acform acin" id="acIn" novalidate autocomplete="on">'
    + '<div class="acf acw"><label for="acInUser">Username</label><input id="acInUser" data-k="inUser" type="text" maxlength="16" autocomplete="username" autocapitalize="off" autocorrect="off" spellcheck="false" value="' + frEsc(AC.f.inUser || '') + '"></div>'
    + '<div class="acf acw"><label for="acInPass">Password</label>' + acPw('acInPass', 'inPass', 'current-password') + '</div>'
    + '<p class="acerr acw" id="acErr" role="alert">' + frEsc(AC.err) + '</p>'
    + '<button class="frb go acgo acw" id="acGo" type="submit">Log in</button>'
    + (swap ? '<p class="frfine acw">Logging in swaps <b>' + frEsc(swap) + '</b>, the player on this device, for your account.</p>' : '') + '</form>';
}
function acRender() {
  const body = $('acBody'); if (!body) return; const nu = AC.tab === 'new', young = nu && acYoung();
  for (const b of $('acModal').querySelectorAll('.actabs button')) b.setAttribute('aria-selected', String(b.dataset.tab === AC.tab));
  $('acTitle').textContent = nu ? 'Make an account' : 'Welcome back';
  body.innerHTML = young ? AC_YOUNG : nu ? acNewHtml() : acInHtml(); body.scrollTop = 0;
  if (nu && !young && UN_W.acUser) UN_W.acUser(); acValid();
}
// the form as typed: each part checked as the server will (names: letters, spaces and . ' -; a real birthday; the password's rules)
function acForm() {
  const v = id => { const e = $(id); return e ? e.value : ''; }, pad = x => String(x).padStart(2, '0');
  const clean = s => s.normalize('NFC').replace(/[’‘`´]/g, "'").replace(/\s+/g, ' ').trim(); // (iOS types ’ for ')
  const user = unNorm(v('acUser')), first = clean(v('acFirst')), last = clean(v('acLast')), m = +v('acM'), d = +v('acD'), y = +v('acY'), pass = v('acPass'), agree = !!($('acAgree') && $('acAgree').checked);
  const nameOk = s => /^\p{L}[\p{L} .'-]{0,39}$/u.test(s), t = new Date(), today = t.getFullYear() + '-' + pad(t.getMonth() + 1) + '-' + pad(t.getDate());
  const real = !!(m && d && y) && new Date(y, m - 1, d).getDate() === d, bday = real ? y + '-' + pad(m) + '-' + pad(d) : '';
  const cy = t.getFullYear() - 13, cut = cy + '-' + pad(t.getMonth() + 1) + '-' + pad(Math.min(t.getDate(), new Date(cy, t.getMonth() + 1, 0).getDate())); // (13 years ago today, as the server counts it)
  const why = { user: !!unWhy(user) || !!($('acUser') && $('acUser').dataset.un === 'bad'), first: !nameOk(first), last: !nameOk(last), bday: !real || bday > today || y < 1900,
    pass: !(pass.length >= 8 && /\p{L}/u.test(pass) && /[0-9]/.test(pass)), agree: !agree };
  return { ok: !Object.values(why).some(Boolean), why, user, first, last, bday, pass, young: real && bday > cut };
}
function acValid() {
  if (AC.tab !== 'new' || !$('acNew')) return; const f = acForm(), w = f.why, set = (id, s, t) => { const e = $(id); if (e) { e.dataset.s = s; e.textContent = t; } };
  const nb = !!(AC.f.first && w.first) || !!(AC.f.last && w.last), all = !!(AC.f.m && AC.f.d && AC.f.y);
  set('acNameSt', nb ? 'bad' : '', nb ? 'Letters only, please' : ''); $('acFirst').setAttribute('aria-invalid', String(!!(AC.f.first && w.first))); $('acLast').setAttribute('aria-invalid', String(!!(AC.f.last && w.last)));
  set('acBdSt', all && w.bday ? 'bad' : '', all && w.bday ? 'That date doesn’t look right' : '');
  for (const id of ['acM', 'acD', 'acY']) $(id).classList.toggle('empty', !$(id).value);
  set('acPassSt', w.pass ? '' : 'ok', w.pass ? '8 or more, with a letter and a number' : 'Good password');
  const g = $('acGo'); if (g && !AC.busy) g.disabled = !f.ok;
}
function acBusy(t) { const g = $('acGo'), f = $('acBody').querySelector('.acform'); if (f) f.classList.toggle('busy', !!t); if (!g) return; if (t) { g.dataset.t = g.dataset.t || g.textContent; g.textContent = t; g.disabled = true; } else { if (g.dataset.t) g.textContent = g.dataset.t; g.disabled = false; acValid(); } }
function acFail(e) {
  AC.busy = false; const w = e && e.why;
  if (w === 'age') { store.acYoung = Date.now(); save(); return acRender(); }
  AC.err = e && e.at === 'user' ? unSay(w, unNorm(AC.f.user)) + '.' : w === 'nouser' ? 'No account has that username.' : w === 'pass' ? 'Wrong password. Try again.'
    : w === 'first' ? 'Check your first name: letters only.' : w === 'last' ? 'Check your last name: letters only.' : w === 'birthday' ? 'Check your birthday.'
    : e && e.code === 'weak_password' ? 'Pick a harder password.' : e && e.out ? 'You’re signed out. Log in again.' : e && e.at === 'save' ? 'Something went wrong. Try again.' : acErrText(e);
  if (e && e.at === 'user') { const i = $('acUser'), st = $('acUserSt'); if (i) i.dataset.un = 'bad'; if (st) { st.dataset.s = 'bad'; st.textContent = unSay(w, unNorm(AC.f.user)); } }
  const x = $('acErr'); if (x) x.textContent = AC.err; AU.nope(); acBusy(null); if (x) kick(x, 'unshake');
}
function acDone(html) { AC.busy = false; const next = AC.next; AC.next = null; AC.f = {}; AC.show = false; // (nothing typed kept)
  acClose(true); frToast(html); AU.power(); acPaintAll(); if (next) setTimeout(next, 250); }
// a new account: the username kept (made or renamed), the made-up email and the password set on this very player, a fresh token
// (no longer anonymous), then the details. Each step is safe to run again, so a try that broke off part way just goes on
async function acCreate() {
  const f = acForm(); if (AC.busy) return; if (!f.ok) return acValid();
  if (f.young) { store.acYoung = Date.now(); save(); AU.nope(); return acRender(); } // (under 13: a kind word, and nothing's made)
  AC.busy = true; AC.err = ''; acBusy('Making your account…');
  try {
    if (acOut()) store.sbs = Object.assign({}, store.sbs, { out: 0, lost: 0 }); // (signed out before: a new player for the new account)
    const me = await unClaim(f.user, true); if (!me.ok) throw acStop(me.why, 'user');
    const s = await sbSession(), uid = s.uid || acJwt(s.access_token).sub;
    if (me.anon !== false) await acFetch('PUT', '/auth/v1/user', { email: 'u' + String(uid).replace(/-/g, '') + '@rollmodel.invalid' }, s.access_token);
    try { await acFetch('PUT', '/auth/v1/user', { password: f.pass }, FR.s.access_token); } catch (e) { if (e.code !== 'same_password') throw e; }
    FR.s.expires_at = 0; await sbSession();
    const r = await sbRpc('rm_account_save', { p_first: f.first, p_last: f.last, p_birthday: f.bday, p_terms: ACC_TERMS });
    if (!r || !r.ok) throw acStop(r && r.why, 'save');
    store.sbs = Object.assign({}, store.sbs, { perm: 1, acct: 1, out: 0, lost: 0, name: me.name }); store.name = me.name; save(); paintName();
    if (FR.me) { Object.assign(FR.me, { name: me.name, needs_name: false, account: true, anon: false }); FR.at = 0; } else { FR.retryAt = 0; frStart(); } // (the friends, at once)
    acDone('<span>Welcome, <b>' + frEsc(me.name) + '</b>! Your account is ready.</span>');
  } catch (e) { acFail(e); }
}
// logging in: the username's sign-in email, then its password. The anonymous player this device had goes (deleted with its own token,
// so its username is free again), the account's session takes its place, and the friends client starts over with it
async function acLogin() {
  if (AC.busy) return; const n = unNorm($('acInUser') ? $('acInUser').value : ''), pw = $('acInPass') ? $('acInPass').value : '';
  if (!n || !pw) { AC.err = !n ? 'Type your username.' : 'Type your password.'; const x = $('acErr'); if (x) { x.textContent = AC.err; kick(x, 'unshake'); } AU.nope(); return; }
  AC.busy = true; AC.err = ''; acBusy('Logging in…');
  try {
    const em = await sbFetch('/rest/v1/rpc/rm_login_email', { p_name: n }); if (!em) throw acStop('nouser');
    let j; try { j = await acFetch('POST', '/auth/v1/token?grant_type=password', { email: em, password: pw }); }
    catch (e) { if (e.status === 400 || e.code === 'invalid_credentials') throw acStop('pass'); throw e; }
    try { await FR.sp; } catch (e) {} await acDropAnon(j.user && j.user.id); // (a refresh on its way finishes first: it mustn't land after the switch)
    FR.gen = (FR.gen || 0) + 1; FR.busy = false; FR.me = null; FR.box = null; FR.seen = null; FR.board = {}; FR.paid = false; FR.need = ''; FR.err = ''; FR.sig = ''; FR.unTyped = null;
    store.sbs = { perm: 1, out: 0 }; sbKeep(j); frBadge();
    const me = await sbRpc('rm_me', { p_name: frName(), p_look: frLook(), p_rank: frRank() }); // (its profile, with this device's look and rank)
    if (!me || me.ok === false) { FR.need = (me && me.why) || 'bad'; throw acStop('nouser'); }
    FR.me = me; acSync(me); FR.sync = frSig(); FR.at = 0; frPoll(); AC.f.inPass = '';
    if (!me.account) { AC.busy = false; AC.tab = 'new'; AC.f.user = me.name; AC.err = 'Almost there: add your details to finish your account.'; acRender(); return; } // (made but never finished)
    acDone('<span>Welcome back, <b>' + frEsc(me.name) + '</b>!</span>');
  } catch (e) { acFail(e); }
}
async function acDropAnon(uid) {
  const s = FR.s, rt = (s && s.refresh_token) || (store.sbs && store.sbs.rt); if (!rt || (store.sbs && store.sbs.perm) || acOut()) return;
  if (uid && ((s && s.uid === uid) || (store.sbs && store.sbs.uid === uid))) return; // (logging in to the player it already is)
  try { let t = s && s.expires_at - 30 > Date.now() / 1000 ? s.access_token : null;
    if (!t) t = (await acRefresh(rt)).access_token;
    if (acJwt(t).is_anonymous === true) await acFetch('POST', '/rest/v1/rpc/rm_delete_me', {}, t); } // (only ever an anonymous player)
  catch (e) {}
}
// signed out (logged out, deleted, or a real account's session gone): nothing online until you log in or make an account, and never a
// new anonymous player in its place
function acSignOut(lost) {
  FR.gen = (FR.gen || 0) + 1; FR.s = null; FR.me = null; FR.box = null; FR.seen = null; FR.board = {}; FR.need = ''; FR.err = ''; FR.sig = ''; FR.busy = false; FR.unTyped = null; AC.f = {};
  store.sbs = { out: 1, lost: lost ? 1 : 0 }; save(); frBadge(); acPaintAll();
}
function acLost() { acSignOut(!!(store.sbs && store.sbs.perm)); }
async function acLogout() { // (this device only: the account stays, to log in to again)
  try { const s = await Promise.race([sbSession(), new Promise((_, no) => setTimeout(() => no(new Error('slow')), 6000))]); await acFetch('POST', '/auth/v1/logout?scope=local', null, s.access_token); } catch (e) {}
  acSignOut();
}
async function acDelete() { const r = await sbRpc('rm_delete_me', {}); if (!r || !r.ok) throw new Error('not deleted'); acSignOut(); } // (the user and everything that hangs off it)
// Restart Game: this device lets go of its player online too. An anonymous one is deleted (its username's free again); a real account is
// only logged out here, to log in to again
function acReset() {
  const s = FR.s, rt = (s && s.refresh_token) || (store.sbs && store.sbs.rt), perm = !!(store.sbs && store.sbs.perm);
  if (!SB_CFG || !rt || acOut()) return Promise.resolve();
  return (async () => { let t = s && s.expires_at - 30 > Date.now() / 1000 ? s.access_token : null;
    if (!t) t = (await acRefresh(rt)).access_token;
    if (perm || acJwt(t).is_anonymous !== true) await acFetch('POST', '/auth/v1/logout?scope=local', null, t); else await acFetch('POST', '/rest/v1/rpc/rm_delete_me', {}, t); })().catch(() => {});
}
// the sheet. next(): after a sign-up or log-in (Play online goes on to the match). Signed in already: straight to next()
function acctOpen(next, tab) {
  if (acctReady()) { if (typeof next === 'function') next(); return; }
  if (!SB_CFG) { frToast('<span>Online play is coming soon</span>'); return; }
  AC.next = typeof next === 'function' ? next : null; AC.tab = tab === 'in' ? 'in' : 'new'; AC.err = ''; AC.busy = false; if (!AC.f.userTyped) AC.f.user = acSuggest(); // (their name now, unless they've typed one here)
  if (!AC.open) AC.ret = document.activeElement; AC.open = true; $('acModal').hidden = false; acRender();
  const c = $('acModal').querySelector('.ttcard'); c.style.animation = 'none'; void c.offsetWidth; c.style.animation = '';
  setTimeout(() => { const i = !touchy() && $(AC.tab === 'in' ? 'acInUser' : 'acUser'); (i || $('acX')).focus({ preventScroll: true }); }, 40);
}
function acClose(keep) {
  if (!AC.open) return; AC.open = false; AC.busy = false; if (!keep) AC.next = null; $('acModal').hidden = true; setTimeout(() => window.scrollTo(0, 0), 60);
  if (AC.ret && AC.ret.focus && document.body.contains(AC.ret) && !AC.ret.closest('[hidden]')) AC.ret.focus({ preventScroll: true });
}
const acBody = $('acBody'), acSet = (e, v) => { const k = e.target.dataset.k; if (!k) return false; AC.f[k] = e.target.type === 'checkbox' ? e.target.checked : e.target.value; if (k === 'user') AC.f.userTyped = true; return true; };
acBody.addEventListener('input', e => { if (!acSet(e)) return; if (AC.err) { AC.err = ''; const x = $('acErr'); if (x) x.textContent = ''; } acValid(); });
acBody.addEventListener('change', e => { if (acSet(e)) acValid(); });
acBody.addEventListener('submit', e => { e.preventDefault(); AU.init(); try { document.activeElement.blur(); } catch (x) {} if (e.target.id === 'acNew') acCreate(); else if (e.target.id === 'acIn') acLogin(); });
acBody.addEventListener('click', e => {
  const d = e.target.closest('[data-doc]'); if (d) { AU.init(); AU.ui(); return openDoc(d.dataset.doc, () => { const x = $('acAgree'); if (x) x.focus({ preventScroll: true }); }); } // (read them if you like: nothing makes you)
  const b = e.target.closest('[data-ac]'); if (!b) return; AU.init(); AU.ui();
  if (b.dataset.ac === 'close') return acClose();
  if (b.dataset.ac === 'show') { AC.show = !AC.show; for (const id of ['acPass', 'acInPass']) { const i = $(id); if (i) i.type = AC.show ? 'text' : 'password'; }
    for (const x of acBody.querySelectorAll('[data-ac="show"]')) { x.textContent = AC.show ? 'Hide' : 'Show'; x.setAttribute('aria-pressed', String(AC.show)); } }
});
// Enter: the next field until it's all filled in, then the button
acBody.addEventListener('keydown', e => {
  if (e.key !== 'Enter' || e.target.tagName !== 'INPUT' || e.target.type === 'checkbox') return; const f = e.target.form; if (!f) return;
  if (f.id === 'acIn' && e.target.id === 'acInUser') { e.preventDefault(); $('acInPass').focus(); return; }
  if (f.id !== 'acNew' || acForm().ok) return; e.preventDefault(); const els = [...f.querySelectorAll('input:not([type=checkbox]),select')], k = els.indexOf(e.target), nx = els.slice(k + 1).find(x => !x.value) || els[k + 1];
  if (nx) nx.focus(); else try { e.target.blur(); } catch (x) {}
});
$('acModal').querySelector('.actabs').addEventListener('click', e => { const b = e.target.closest('[data-tab]'); if (!b || AC.busy || b.dataset.tab === AC.tab) return; AU.init(); AU.ui(); AC.tab = b.dataset.tab; AC.err = ''; acRender(); });
$('acX').addEventListener('click', () => { AU.init(); AU.ui(); acClose(); });
$('acModal').addEventListener('click', e => { if (e.target === $('acModal') && !AC.busy) acClose(); });
$('acModal').addEventListener('keydown', e => e.stopPropagation()); // (keys are for the form, not the game behind it)
document.addEventListener('keydown', e => { if (AC.open && e.key === 'Escape' && $('docModal').hidden) { e.preventDefault(); e.stopPropagation(); if (!AC.busy) acClose(); } }, true);
window.acctReady = acctReady; window.acctOpen = acctOpen;

// ---- Settings: the account (who's signed in, Log out, Delete account with a second tap to be sure), or Make an account / Log in
function acSetPaint() {
  const row = $('acRow'); if (!row) return; const on = !!SB_CFG, nm = acName() || store.name || '';
  const b = (a, t, cls) => '<button class="sbtn' + (cls ? ' ' + cls : '') + '" type="button" data-ac="' + a + '"' + (AC.busy || !on ? ' disabled' : '') + '><span>' + t + '</span></button>';
  row.classList.toggle('soon', !on); $('acSlab').innerHTML = 'Account' + (on ? '' : ' <i class="soontag">Coming soon</i>');
  let t, h;
  if (!on) { t = 'Accounts come with online play.'; h = b('new', 'Make an account') + b('in', 'Log in'); }
  else if (AC.del && acctReady()) { t = 'Delete <b>' + frEsc(nm) + '</b> for good? Your username, friends and account details all go, and it can’t be undone.'; h = b('delyes', 'Delete for good', 'acdel') + b('delno', 'Keep it'); }
  else if (acctReady()) { t = (AC.note ? frEsc(AC.note) + ' ' : '') + 'Signed in as <b>' + frEsc(nm) + '</b>'; h = b('out', 'Log out') + b('del', 'Delete account', 'acdel'); }
  else { t = AC.note ? frEsc(AC.note) : acOut() ? 'You’re signed out. Log in, or make a new account.' : 'Make an account to add friends and play online.'; h = b('new', 'Make an account') + b('in', 'Log in'); }
  $('acNote').innerHTML = t; $('acBtns').innerHTML = h;
}
$('acBtns').addEventListener('click', async e => {
  const b = e.target.closest('[data-ac]'); if (!b || b.disabled || AC.busy) return; const a = b.dataset.ac; AU.init(); AU.ui(); AC.note = '';
  if (a === 'new' || a === 'in') return acctOpen(null, a);
  if (a === 'del' || a === 'delno') { AC.del = a === 'del'; acSetPaint(); return $('acBtns').querySelector('button').focus({ preventScroll: true }); }
  AC.busy = true; acSetPaint();
  try { if (a === 'out') { await acLogout(); AC.note = 'You’re logged out.'; } else if (a === 'delyes') { await acDelete(); AC.note = 'Your account is deleted.'; } }
  catch (err) { AC.note = acErrText(err); }
  AC.busy = false; AC.del = false; acSetPaint();
});

// ---- Play online (Choose event): open once the Strokes page has been seen (a player who did the Strokes lesson has seen it). Then:
// an account first, if there's none; then the lobby's online screen
const mpOpen = () => !!(store.abilSeen || (store.tut && store.tut.strokes));
function acMatchPaint() {
  const b = $('evMatch'), c = b && b.closest('.evcard'); if (!c) return; const on = mpOpen(), lv = repOf(store.xp || 0).lv;
  c.classList.toggle('lock', !on); c.classList.toggle('fresh', on && !store.mpTried);
  $('evMatchLock').innerHTML = ABIL_LOCK + (lv < ABIL_RANK ? 'Rank ' + ABIL_RANK : 'Open Strokes');
  if (on) b.removeAttribute('aria-disabled'); else b.setAttribute('aria-disabled', 'true');
  b.setAttribute('aria-label', on ? 'Play online: 1v1 against real people' : 'Play online, locked: open Strokes in the lobby to unlock it');
}
function evToast(c, t) { const old = c.querySelector('.evtoast'); if (old) old.remove(); const s = document.createElement('span'); s.className = 'evtoast'; s.setAttribute('role', 'status'); s.textContent = t; c.appendChild(s); setTimeout(() => s.remove(), 1700); }
function mpGo() { if (typeof window.onlineOpen === 'function') window.onlineOpen(); else evToast($('evMatch').closest('.evcard'), 'Online matches are coming soon'); }
function mpTap() {
  const c = $('evMatch').closest('.evcard');
  if (!mpOpen()) { AU.nope(); buzz(8); return evToast(c, repOf(store.xp || 0).lv < ABIL_RANK ? 'Reach rank ' + ABIL_RANK + ', then open Strokes' : 'Open Strokes in the lobby to unlock it'); }
  AU.ui(); if (!store.mpTried) { store.mpTried = 1; save(); acMatchPaint(); }
  if (!SB_CFG) return evToast(c, 'Online matches are coming soon');
  acctOpen(mpGo);
}
"""

DOC_TOS = ("<p>Updated October 15, 2026. Roll Model is still being made, and these terms will grow with it.</p>"
           "<h3>Play fair</h3><p>No cheating, hacking, or using bugs to win.</p>"
           "<h3>Be kind</h3><p>Pick a username that’s friendly to everyone: no swearing, nothing hateful, and no pretending to be someone else. We can change or remove a username that breaks these rules, and close an account that keeps breaking them.</p>"
           "<h3>Your account</h3><p>You need to be 13 or older to make an account and play online. Keep your password to yourself: you’re responsible for what happens on your account. You can delete it any time in Settings.</p>"
           "<h3>Changes</h3><p>We may update these terms as the game grows. The date at the top says when they last changed.</p>")
DOC_PRIV = ("<p>Updated October 15, 2026.</p>"
            "<h3>On this device</h3><p>Your progress (your dabs, items, ranks and settings) is saved on this device. You don’t need an account to play.</p>"
            "<h3>Your username</h3><p>Your username is kept on our server so no one else can take it. Other players can see it, with your paint colour and rank.</p>"
            "<h3>Your account</h3><p>If you make an account, we keep your username, your first and last name, your birthday, and when you agreed to these terms. Your name and birthday are private: other players never see them. We ask for your birthday because online play is for players 13 and older.</p>"
            "<p>Your password is handled by our sign-in provider, Supabase. It’s stored scrambled (hashed), never in a form anyone can read, not even us.</p>"
            "<h3>Playing online</h3><p>To run friends and online matches we keep your friend code, your friends, friend requests and blocks, invites to play, your Time trial scores for the friends board, records of your online matches, and when you were last online.</p>"
            "<h3>Who has it</h3><p>We don’t sell your information or show you ads. Supabase stores it for us, and online matches run on our game server.</p>"
            "<h3>Deleting it</h3><p>Settings › Account › Delete account removes your account and everything above from our server for good. Restart Game in Settings clears this device.</p>")

def apply(s):
    assert "'" not in DOC_TOS + DOC_PRIV and '\\' not in DOC_TOS + DOC_PRIV # (they go inside a '...' string)
    # ---- the username rules, next to the names, and the dice rolling only usernames
    a = "const randomName = () => { let n; do { n = NAME_IDEAS[(Math.random() * NAME_IDEAS.length) | 0]; } while (n === store.name && NAME_IDEAS.length > 1); return n; };\n"
    s = rep(s, a, "const randomName = () => { let n; do { n = NAME_IDEAS[(Math.random() * NAME_IDEAS.length) | 0].replace(/ /g, '_') + (10 + ((Math.random() * 90) | 0)); } while (n === store.name || unWhy(n) || /(69|88)$/.test(n)); return n; }; // (v306: a username: no spaces, two digits so it's likely free)\n" + RULES)
    # ---- the account sheet, its look, and the client (after v305's friends client, which it builds on)
    s = rep(s, '  <div class="modal" id="docModal" hidden>\n', HTML + '  <div class="modal" id="docModal" hidden>\n')
    a = "@media (prefers-reduced-motion:reduce){.frspin{animation-duration:2.5s}.frtoast,#friendsBtn .frdot{animation:none}}\n"
    s = rep(s, a, a + CSS.lstrip('\n'))
    a = "if (SB_CFG) $('ttModal').classList.add('frlive');\n"
    s = rep(s, a, a + JS.lstrip('\n'))
    # ---- v305's client: a profile only with a username that can be had; a real account's session never quietly replaced
    s = rep(s, """async function frStart() {
  if (!SB_CFG || FR.busy || FR.me) return; FR.busy = true; FR.err = ''; if (FR.open) frRender();
  try { FR.me = await sbRpc('rm_me', { p_name: frName(), p_look: frLook(), p_rank: frRank() }); FR.sync = frSig(); FR.busy = false; await frPoll(); }
  catch (e) { FR.err = frErrText(e); FR.retryAt = Date.now() + 30000; }
  finally { FR.busy = false; if (FR.open) frRender(); if (!$('ttModal').hidden && ttTab === 'friends') ttRender(); }
}
""", """async function frStart() {
  if (!SB_CFG || FR.busy || FR.me || acOut()) return; FR.busy = true; FR.err = ''; const g = FR.gen = (FR.gen || 0) + 1; if (FR.open) frRender(); // (v306: signed out, nothing till you log in)
  try {
    const r = await sbRpc('rm_me', { p_name: frName(), p_look: frLook(), p_rank: frRank() }); if (g !== FR.gen) return; // (logged in or out meanwhile: that answer's old)
    if (r && r.ok === false) { FR.need = r.why || 'bad'; FR.retryAt = Date.now() + 600000; } // (v306: no profile yet: that name's taken or can't be a username. The Friends screen asks for one)
    else { FR.need = ''; FR.me = r; acSync(r); FR.sync = frSig(); FR.busy = false; await frPoll(); }
  }
  catch (e) { if (g === FR.gen) { FR.err = frErrText(e); FR.retryAt = Date.now() + 30000; } }
  finally { if (g === FR.gen) FR.busy = false; if (FR.open) frRender(); if (!$('ttModal').hidden && ttTab === 'friends') ttRender(); if (!$('setModal').hidden) acSetPaint(); }
}
""")
    s = rep(s, "    if (rt) { try { return sbKeep(await sbFetch('/auth/v1/token?grant_type=refresh_token', { refresh_token: rt })); }\n",
               "    if (rt) { try { return sbKeep(await acRefresh(rt)); } // (v306: more patient, and asked again: see acRefresh)\n")
    s = rep(s, "    return sbKeep(await sbFetch('/auth/v1/signup', { data: {} }));\n",
               "    if (store.sbs && (store.sbs.perm || store.sbs.out)) { acLost(); throw Object.assign(new Error('signed out'), { status: 401, out: true }); } // (v306: a real account's session gone, or signed out: log in again, never a new player in its place)\n"
               "    return sbKeep(await acFetch('POST', '/auth/v1/signup', { data: {} }, null, 30000)); // (v306: patient too: an answer lost here leaves a player no one can reach)\n")
    # the Friends screen before the friends: signed out, a username to pick, or no account yet (the friends themselves need one)
    s = rep(s, """  const el = $('frBody'); if (!el) return; let h = '';
  if (!SB_CFG) h = '<div class="frmsg">' + FR_FACES + '<b>Friends are on the way</b><p>They play online, and online play isn’t switched on in this version yet.</p></div>';
  else if (!FR.me) h = FR.err && !FR.busy ? '<div class="frmsg">' + FR_FACES + '<b>Can’t connect</b><p>' + frEsc(FR.err) + '</p><button class="frb go" data-act="retry" type="button">Try again</button></div>' : '<div class="frmsg"><span class="frspin" aria-hidden="true"></span><p>Getting your friend code…</p></div>';
""", """  const el = $('frBody'); if (!el) return; let h = '';
  if (fromPoll && document.activeElement && document.activeElement.id === 'frUnIn') return; // (v306: not while a username's being typed)
  if (!SB_CFG) h = '<div class="frmsg">' + FR_FACES + '<b>Friends are on the way</b><p>They play online, and online play isn’t switched on in this version yet.</p></div>';
  else if (acOut()) h = acAskHtml();
  else if (!FR.me && FR.need) h = unPickHtml();
  else if (!FR.me) h = FR.err && !FR.busy ? '<div class="frmsg">' + FR_FACES + '<b>Can’t connect</b><p>' + frEsc(FR.err) + '</p><button class="frb go" data-act="retry" type="button">Try again</button></div>' : '<div class="frmsg"><span class="frspin" aria-hidden="true"></span><p>Getting your friend code…</p></div>';
  else if (FR.me.needs_name) h = unPickHtml();
  else if (!acctReady()) h = acAskHtml();
""")
    s = rep(s, "  if (!FR.me) { if (!FR.busy && Date.now() > FR.retryAt) frStart(); return FR.err && !FR.busy ?",
               "  if (!FR.me) { if (acOut() || FR.need) return '<p class=\"ttnone\"><b>' + (FR.need ? 'Pick your username' : 'Log in') + ' to race your friends here.</b>Your friends are on the lobby’s Friends button.</p>'; if (!FR.busy && Date.now() > FR.retryAt) frStart(); return FR.err && !FR.busy ?")
    # ---- the first launch's name card: a username, its line under it, kept on the server at Next (offline it goes on: checked later)
    s = rep(s, '<p class="flnote">It goes up in lights when you win.</p>', '<p class="flnote">Pick a username. It goes up in lights when you win.</p>')
    s = rep(s, """aria-label="Your name"><button class="fldice" id="flDice" type="button" aria-label="Pick a random name">' + DICE + '</button></div></div>'""",
               """aria-label="Your username" aria-describedby="flNameSt"><button class="fldice" id="flDice" type="button" aria-label="Pick a random username">' + DICE + '</button></div><p class="flun" id="flNameSt" aria-live="polite"></p></div>'""")
    a = "    $('flDice').addEventListener('click', () => { AU.init(); AU.pop(); $('flNameIn').value = randomName(); kick($('flDice'), 'bump'); if (X) move('ears'); });\n"
    s = rep(s, a, a + "    unIntro(); // (v306: the line under it, and Next only for a name that can be had)\n")
    s = rep(s, "    $('flName').addEventListener('submit', e => { e.preventDefault(); AU.init(); AU.ui(); try { $('flNameIn').blur(); } catch (x) {} setTimeout(() => window.scrollTo(0, 0), 60); store.name = cleanName($('flNameIn').value) || randomName(); go('confirm'); });\n",
               "    $('flName').addEventListener('submit', e => { e.preventDefault(); AU.init(); unSubmit('flNameIn', 'flNameSt', 'flNameGo', nm => { if (!X || X.ph !== 'name') return; AU.ui(); try { $('flNameIn').blur(); } catch (x) {} setTimeout(() => window.scrollTo(0, 0), 60); store.name = nm; go('confirm'); }); }); // (v306: kept on the server first, when it can be)\n")
    s = rep(s, "if (!i.value) i.value = cleanName(store.name) || randomName(); AU.flm.layer(4); }", "if (!i.value) i.value = cleanName(store.name) || randomName(); i.dispatchEvent(new Event('input')); AU.flm.layer(4); }")
    # ---- Rename in the lobby: a username too (with a player on the server, it changes there first)
    s = rep(s, """</svg></button></div>\n      <button class="btn play sm" id="nameOk" type="submit">Let's go</button>""",
               """</svg></button></div>\n      <p class="unst" id="nameSt" aria-live="polite"></p>\n      <button class="btn play sm" id="nameOk" type="submit">Let's go</button>""")
    s = rep(s, """$('nameTitle').textContent = first ? "What's your name?" : 'Your name';""", """$('nameTitle').textContent = first ? "What's your name?" : 'Your username';""")
    s = rep(s, "inp.value = cleanName(store.name) || randomName(); nameModal.hidden = false;", "inp.value = cleanName(store.name) || randomName(); nameModal.hidden = false; inp.dispatchEvent(new Event('input'));")
    s = rep(s, """$('nameForm').addEventListener('submit', e => {
  e.preventDefault(); AU.init(); AU.ui();
  store.name = cleanName($('nameInput').value) || randomName(); save(); paintName();
  const go = nameFirst; closeName(); if (go) start();
});""", """$('nameForm').addEventListener('submit', e => {
  e.preventDefault(); AU.init();
  unSubmit('nameInput', 'nameSt', 'nameOk', nm => { AU.ui(); store.name = nm; save(); paintName(); const go = nameFirst; closeName(); if (go) start(); }, acHas()); // (v306: a username, kept on the server first)
});""")
    # ---- Play online: the Matchmaking card, for real now, locked until the Strokes page has been opened
    s = rep(s, "stSkillSel = null; stCat = 'special'; menuPage = 'strokes';", "if (!store.abilSeen) { store.abilSeen = 1; save(); } /* (v306: having seen it opens Play online) */ stSkillSel = null; stCat = 'special'; menuPage = 'strokes';")
    s = rep(s, '<div class="evcard soon" data-ev="match" style="--ec:#19B7A5"><button class="evmain" id="evMatch" type="button" aria-disabled="true"><span class="evbar"><i>Coming soon</i></span>',
               '<div class="evcard" data-ev="match" style="--ec:#19B7A5"><button class="evmain" id="evMatch" type="button"><span class="evbar"><i>Live online</i></span>')
    s = rep(s, '<span class="evtx"><b>Matchmaking</b><small>Play people online</small></span>', '<span class="evtx"><b>Play online</b><small>1v1 against real people</small></span>')
    s = rep(s, '<img id="evMatchArt" alt=""></span></button><i class="evsoon">Coming soon</i></div>', '<img id="evMatchArt" alt=""></span></button><i class="evlock" id="evMatchLock" aria-hidden="true"></i><i class="evnew" aria-hidden="true">New!</i></div>')
    s = rep(s, "$('evMatch').addEventListener('click', () => { AU.init(); AU.nope(); const c = $('evMatch').closest('.evcard'), old = c.querySelector('.evtoast'); if (old) old.remove(); const t = document.createElement('span'); t.className = 'evtoast'; t.textContent = 'Matchmaking is coming soon'; c.appendChild(t); setTimeout(() => t.remove(), 1700); });\n",
               "$('evMatch').addEventListener('click', () => { AU.init(); mpTap(); }); // (v306: Play online)\n")
    s = rep(s, "evArt(); evFold(); evLockPaint();", "evArt(); evFold(); evLockPaint(); acMatchPaint();")
    # ---- Settings: the Account row in place of "Play with friends: coming soon"
    s = rep(s, '        <div class="sopt wide soon"><p class="slab">Play with friends <i class="soontag">Coming soon</i></p><div class="sbtns"><button class="sbtn" type="button" disabled><span>Invite friends</span></button><button class="sbtn" type="button" disabled><span>Link account</span></button></div></div>\n',
               '        <div class="sopt wide acrow" id="acRow"><p class="slab" id="acSlab">Account</p><p class="gnote acnote" id="acNote" aria-live="polite"></p><div class="sbtns" id="acBtns"></div></div>\n')
    s = rep(s, "gfxPick = GFX; paintSettings();", "gfxPick = GFX; paintSettings(); AC.del = false; AC.note = ''; acSetPaint();")
    # ---- the Terms and Privacy Policy: opened over the account sheet too (and back to it after); what accounts keep
    s = rep(s, "function openDoc(k) { const d = DOCS[k]; if (!d) return; PB.docFrom = k; $('docTitle').textContent = d[0]; $('docBody').innerHTML = d[1]; $('docBody').scrollTop = 0; setModal.hidden = true; $('docModal').hidden = false;",
               "function openDoc(k, back) { const d = DOCS[k]; if (!d) return; PB.docFrom = k; PB.docBack = typeof back === 'function' ? back : null; $('docModal').classList.toggle('acup', !!PB.docBack); $('docTitle').textContent = d[0]; $('docBody').innerHTML = d[1]; $('docBody').scrollTop = 0; if (!PB.docBack) setModal.hidden = true; $('docModal').hidden = false;")
    s = rep(s, "function closeDoc() { if ($('docModal').hidden) return; $('docModal').hidden = true; if (state === 'menu') {",
               "function closeDoc() { if ($('docModal').hidden) return; $('docModal').hidden = true; if (PB.docBack) { const f = PB.docBack; PB.docBack = null; return f(); } if (state === 'menu') {")
    s = rep(s, "  tos: ['Terms of Service', '<p>Roll Model is still in development. The full terms of service will be published here before the game launches.</p><p>Until then, play fair and have fun.</p>'],\n",
               "  tos: ['Terms of Service', '" + DOC_TOS + "'],\n")
    s = rep(s, "  priv: ['Privacy Policy', '<p>Roll Model saves your progress (your name, dabs, items, ranks and settings) in this browser, on this device. You don’t need an account to play.</p><p>Clearing this browser’s site data resets your progress.</p><p>The full privacy policy will be published here before the game launches.</p>'],\n",
               "  priv: ['Privacy Policy', '" + DOC_PRIV + "'],\n")
    # ---- Restart Game: the player online goes too (an anonymous one deleted, an account logged out here), before the reload
    s = rep(s, "    disarm(); b.disabled = true;\n", "    disarm(); b.disabled = true; const gone = acReset(); // (v306)\n")
    s = rep(s, "    save(); saveSend(); try { AU.trim && AU.trim(); } catch (e) {}\n    setTimeout(() => location.reload(), 150);\n",
               "    save(); saveSend(); try { AU.trim && AU.trim(); } catch (e) {}\n    Promise.race([gone, new Promise(r => setTimeout(r, 3000))]).then(() => setTimeout(() => location.reload(), 150));\n")
    return s
