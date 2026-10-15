"""v305: Friends, on Supabase.

- Each player gets an 8-character friend code (no 0/O or 1/I/L to mix up). Add a friend by typing theirs; they accept, or if they'd
  already added you, you're friends at once. Requests can be declined or cancelled, friends removed, and players blocked (a block
  isn't announced: their requests just never arrive).
- The Friends screen (the lobby's Friends button) shows your code with Copy (and Share, in the iOS app), the add box, requests,
  your friends with who's online ("In the lobby", "In a match", or when they were last on), what you're waiting on, and who
  you've blocked. A red count on the lobby button shows new requests; a new one pops a note in the lobby.
- The Time trial board's Friends tab is live: this week's bests of you and your friends on each canvas. Runs go up as you finish
  them (queued if you're offline). When the week turns, the top three of a board of three or more win 100/60/30 dabs.
- How it talks to Supabase: its REST API straight from the page (no library, so nothing new to bundle). The first time, an
  anonymous account is made (no email); its refresh token is kept with the save. Everything else goes through the database's
  rm_* functions (supabase/migrations), which only ever hand out what a player may see.
- Online is off until the project's address and publishable key are in tools/online_config.json (they're public by design). Off,
  or with no network (the claude.ai preview can't reach the internet), the Friends screen says so and nothing else changes.
- While the Friends screen is open, the lobby's 3D view holds still behind it, as under Commissions.
- iOS: the device bridge can now open the share sheet, for the friend code."""
import json, os

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

HERE = os.path.dirname(os.path.abspath(__file__))

def cfg():
    p = os.path.join(HERE, 'online_config.json')
    try: c = json.load(open(p))
    except FileNotFoundError: c = {}
    url, key = (c.get('supabase_url') or '').strip().rstrip('/'), (c.get('supabase_key') or '').strip()
    assert not url or url.startswith('https://'), url
    assert '"' not in url + key and "'" not in url + key and '\\' not in url + key
    return url, key

HTML = r"""  <div class="modal ttm" id="friendsModal" hidden><div class="ttcard frcard" role="dialog" aria-modal="true" aria-labelledby="friendsTitle">
    <button class="ttx" id="frX" type="button" aria-label="Close"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6.5 6.5l11 11M17.5 6.5l-11 11" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"/></svg></button>
    <div class="tthd"><small>Play together</small><h3 id="friendsTitle">Friends</h3></div>
    <div class="frbody" id="frBody"></div>
  </div></div>
"""

CSS = r"""
/* (v305) Friends: the same taped notebook sheet as the leaderboard */
.frcard{width:min(100%,400px)}
.frbody{display:grid;grid-template-columns:minmax(0,1fr);align-content:start;gap:14px;min-height:min(300px,48vh);overflow:auto;margin-right:-6px;padding:2px 6px 2px 0;-webkit-overflow-scrolling:touch}
.frbody>*{min-width:0}
.frbody h4,.frme small,.fradd label{display:flex;align-items:center;gap:6px;margin:0;font:800 11px/1 var(--font-ui);letter-spacing:.12em;text-transform:uppercase;color:#6E6680}
.frbody h4 i{font-style:normal;padding:2px 6px;border-radius:999px;background:rgba(23,19,32,.08);color:var(--black);letter-spacing:.04em}
.frbody h4 em{font-style:normal;letter-spacing:.04em;color:#2C7A3F}
.frcode{display:flex;align-items:center;gap:8px;margin-top:7px}
.frcode b{flex:1;min-width:0;padding:9px 8px 7px;border-radius:2px;background:#FFE896;box-shadow:0 10px 10px -8px rgba(0,0,0,.5);font:400 25px/1 var(--font-display);letter-spacing:.14em;text-align:center;white-space:nowrap;rotate:-1deg;user-select:all;-webkit-user-select:all}
.frb{display:inline-flex;align-items:center;justify-content:center;gap:5px;min-height:36px;padding:0 13px;border:0;border-radius:999px;background:var(--black);color:#FFF8EA;font:800 12px/1 var(--font-ui);letter-spacing:.06em;text-transform:uppercase;white-space:nowrap;cursor:pointer;box-shadow:2px 3px 0 rgba(0,0,0,.25);transition:transform .12s ease}
.frb:active{transform:scale(.94)}.frb:disabled{opacity:.45;pointer-events:none}
.frb.go{background:#2E9E48;color:#fff}.frb.bad{background:#D33A4C;color:#fff}
.frb.ghost{background:rgba(23,19,32,.07);color:var(--black);box-shadow:none}
.frb.ic{width:36px;padding:0}.frb svg{width:16px;height:16px}
.fradd div{display:flex;gap:8px;margin-top:7px}
.fradd input{flex:1;min-width:0;height:42px;box-sizing:border-box;padding:0 12px;border:2px solid var(--black);border-radius:6px;background:#fff;color:var(--black);font:400 21px/1 var(--font-display);letter-spacing:.14em;text-transform:uppercase}
.fradd input::placeholder{color:#A9A3B5;letter-spacing:.04em;text-transform:none;font:600 15px/1 var(--font-ui)}
.fradd input:focus{outline:none;box-shadow:0 0 0 3px rgba(242,181,58,.6)}
.frnote{min-height:1.3em;margin:5px 0 0;font:700 12.5px/1.3 var(--font-ui);color:#2C7A3F}.frnote.bad{color:#C2283C}
.frlist{list-style:none;margin:4px 0 0;padding:0;display:grid}
.frrow{display:grid;grid-template-columns:40px minmax(0,1fr) auto;align-items:center;gap:10px;min-height:54px;border-bottom:1px dashed rgba(84,140,205,.35)}
.frrow.sm{min-height:46px}
.frface{display:block;width:40px;height:40px}
.frwho{display:grid;gap:3px;min-width:0}
.frwho b{font:700 15px/1.15 var(--font-ui);color:var(--black);white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.frwho small{display:flex;align-items:center;gap:5px;min-width:0;font:600 12px/1.2 var(--font-ui);color:#5E566E;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.frst{flex:none;width:8px;height:8px;border-radius:50%;background:#B9B3C4}.frst.lobby{background:#2E9E48;box-shadow:0 0 0 3px rgba(46,158,72,.22)}.frst.match{background:#F2A33A;box-shadow:0 0 0 3px rgba(242,163,58,.25)}
.frbtns{display:flex;align-items:center;gap:6px}
.frmenu{grid-column:1/-1;display:flex;align-items:center;flex-wrap:wrap;gap:8px;padding:0 0 10px 50px;font:700 13px/1.3 var(--font-ui)}
.frempty{margin:4px 0 0;font:600 13.5px/1.45 var(--font-ui);color:#5E566E}
.frfine{margin:0;font:600 11.5px/1.4 var(--font-ui);font-style:italic;color:#6E6680}
.frwarn{margin:0;font:700 12.5px/1.35 var(--font-ui);color:#C2283C}
.frblk summary{cursor:pointer;font:800 11px/1 var(--font-ui);letter-spacing:.12em;text-transform:uppercase;color:#6E6680;padding:4px 0}
.frmsg{display:grid;justify-items:center;align-content:center;gap:9px;min-height:220px;text-align:center}
.frmsg b{font:400 19px/1.1 var(--font-display);text-transform:uppercase}
.frmsg p{margin:0;max-width:30ch;font:600 13.5px/1.45 var(--font-ui);color:#5E566E}
.frmsg .ffaces{position:relative;display:block;width:120px;height:56px}.frmsg .ffaces svg{position:absolute;top:0;left:12px;width:52px;height:52px}.frmsg .ffaces svg:nth-child(2){left:56px}
.frspin{width:30px;height:30px;box-sizing:border-box;border:3px solid rgba(23,19,32,.14);border-top-color:var(--black);border-radius:50%;animation:frspin .9s linear infinite}
@keyframes frspin{to{transform:rotate(360deg)}}
#friendsBtn .frdot{position:absolute;top:-7px;right:-7px;z-index:2;min-width:22px;height:22px;box-sizing:border-box;padding:0 6px;border-radius:999px;background:#E3122F;color:#fff;font:800 12.5px/22px var(--font-ui);text-align:center;box-shadow:0 0 0 2.5px #171320;animation:frpop .35s cubic-bezier(.3,1.6,.5,1)}
@keyframes frpop{0%{scale:.3}}
.frtoast{position:fixed;left:50%;top:calc(env(safe-area-inset-top,0px) + 78px);z-index:70;display:flex;align-items:center;gap:8px;max-width:min(88vw,360px);box-sizing:border-box;padding:9px 16px 9px 10px;border-radius:999px;background:#171320;color:#FFF8EA;font:700 13.5px/1.25 var(--font-ui);box-shadow:0 6px 18px rgba(0,0,0,.35);transform:translateX(-50%);animation:frin .35s cubic-bezier(.2,1.3,.4,1) both;pointer-events:none}
.frtoast .frface{width:28px;height:28px;flex:none}
.frtoast.out{opacity:0;translate:0 -12px;transition:opacity .35s ease,translate .35s ease}
@keyframes frin{0%{opacity:0;translate:0 -14px}}
.ttrow .ttwho .frface{width:26px;height:26px;flex:none}
#ttModal.frlive .tttabs [data-tt="friends"] svg{display:none}
@media (prefers-reduced-motion:reduce){.frspin{animation-duration:2.5s}.frtoast,#friendsBtn .frdot{animation:none}}
"""

JS = r"""
// ---------- (v305) Friends, on Supabase: a friend code each, requests both ways, who's online, and a Friends board for the Time
// trial. The page talks to Supabase's REST API itself (no library): an anonymous account the first time (its refresh token kept
// with the save), then the database's rm_* functions for everything else (supabase/migrations: they only hand out what a player
// may see). No project set, or no network (the claude.ai preview), and the Friends screen says so; nothing else changes ----------
const SB_CFG = (() => { let c = { url: '__SB_URL__', key: '__SB_KEY__' };
  try { const o = window.__sb || JSON.parse(localStorage.getItem('rm.sb') || 'null'); if (o && o.url && o.key) c = o; } catch (e) {} // (a test project, for development)
  return c.url && c.key && /^(https:\/\/|http:\/\/(localhost|127\.0\.0\.1)[:/])/.test(c.url) ? { url: String(c.url).replace(/\/+$/, ''), key: String(c.key) } : null; })();
const NATIVE_SHARE = !!(window.__NATIVE && window.__NATIVE.share);
const FR = { s: null, sp: null, me: null, box: null, busy: false, polling: false, err: '', at: 0, retryAt: 0, open: false, note: '', noteOk: true, typed: '', menu: '', confirm: '', seen: null, skew: 0, board: {}, boardBusy: '', sync: '', sig: '', flushing: false, paid: false };
const frEsc = s => String(s == null ? '' : s).replace(/[&<>"']/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[c]);
const frCode = c => c ? c.slice(0, 4) + ' ' + c.slice(4) : '';
const frErrText = e => (typeof navigator !== 'undefined' && navigator.onLine === false) ? 'You’re offline. Friends come back when you’re online.' : e && e.status === 429 ? 'Busy right now. Try again in a minute.' : 'Can’t reach the Roll Model server right now.';
async function sbFetch(path, body, auth, keep) {
  const h = { apikey: SB_CFG.key, 'Content-Type': 'application/json' };
  if (auth && FR.s) h.Authorization = 'Bearer ' + FR.s.access_token; else if (/^eyJ/.test(SB_CFG.key)) h.Authorization = 'Bearer ' + SB_CFG.key; // (a legacy anon key is a token itself)
  const ctl = typeof AbortController === 'function' ? new AbortController() : null, to = setTimeout(() => { if (ctl) ctl.abort(); }, 10000);
  try {
    const r = await fetch(SB_CFG.url + path, { method: 'POST', headers: h, body: JSON.stringify(body || {}), signal: ctl ? ctl.signal : undefined, keepalive: !!keep });
    const t = await r.text(); let j = null; try { j = t ? JSON.parse(t) : null; } catch (e) {}
    if (!r.ok) { const e = new Error((j && (j.message || j.msg || j.error_description || j.error)) || 'HTTP ' + r.status); e.status = r.status; throw e; }
    return j;
  } finally { clearTimeout(to); }
}
function sbKeep(j) {
  if (!j || !j.access_token || !j.refresh_token) throw new Error('no session');
  FR.s = { access_token: j.access_token, refresh_token: j.refresh_token, expires_at: j.expires_at || Math.floor(Date.now() / 1000) + (j.expires_in || 3600), uid: j.user && j.user.id };
  store.sbs = Object.assign({}, store.sbs, { rt: FR.s.refresh_token, uid: FR.s.uid || (store.sbs && store.sbs.uid) || null }); save(); return FR.s;
}
// a live session: the one in hand, else refreshed from the saved token, else (the first time, or that token's gone) a new account.
// One at a time: refresh tokens are single use
function sbSession() {
  if (FR.s && FR.s.expires_at - 60 > Date.now() / 1000) return Promise.resolve(FR.s);
  return FR.sp || (FR.sp = (async () => {
    const rt = (FR.s && FR.s.refresh_token) || (store.sbs && store.sbs.rt);
    if (rt) { try { return sbKeep(await sbFetch('/auth/v1/token?grant_type=refresh_token', { refresh_token: rt })); }
      catch (e) { if (!(e.status >= 400 && e.status < 500) || e.status === 429) throw e; store.sbs = Object.assign({}, store.sbs, { rt: null, lost: (store.sbs && store.sbs.uid) || true }); } }
    return sbKeep(await sbFetch('/auth/v1/signup', { data: {} }));
  })().finally(() => { FR.sp = null; }));
}
async function sbRpc(fn, args, keep) {
  await sbSession();
  try { return await sbFetch('/rest/v1/rpc/' + fn, args || {}, true, keep); }
  catch (e) { if (e.status !== 401) throw e; FR.s.expires_at = 0; await sbSession(); return sbFetch('/rest/v1/rpc/' + fn, args || {}, true, keep); }
}
const frName = () => String(store.name || 'Rookie').slice(0, 16);
const frLook = () => ({ c: colorId, e: myLook.eyes });
const frRank = () => repOf(store.xp || 0).lv;
const frSig = () => frName() + '|' + colorId + '|' + myLook.eyes + '|' + frRank();
const frStatus = () => state === 'menu' ? 'lobby' : 'match';
async function frStart() {
  if (!SB_CFG || FR.busy || FR.me) return; FR.busy = true; FR.err = ''; if (FR.open) frRender();
  try { FR.me = await sbRpc('rm_me', { p_name: frName(), p_look: frLook(), p_rank: frRank() }); FR.sync = frSig(); FR.busy = false; await frPoll(); }
  catch (e) { FR.err = frErrText(e); FR.retryAt = Date.now() + 30000; }
  finally { FR.busy = false; if (FR.open) frRender(); if (!$('ttModal').hidden && ttTab === 'friends') ttRender(); }
}
async function frPoll() {
  if (!FR.me || FR.polling) return; FR.polling = true;
  try { const b = await sbRpc('rm_inbox', { p_status: frStatus() }); FR.box = b; FR.err = ''; FR.at = Date.now(); FR.skew = (Date.parse(b.now) || Date.now()) - Date.now(); frSeen(b); frBadge(); if (FR.open) frRender(true); frFlushTrials(); frPayout(); }
  catch (e) { FR.at = Date.now(); FR.err = frErrText(e); if (FR.open) frRender(true); }
  finally { FR.polling = false; }
}
// every second: start once there's a name and the onboarding's done (or the screen is opened); then keep the inbox fresh, quicker
// while the screen is open, slower in a match (that's also what keeps you showing as online to your friends)
function frTick() {
  if (!SB_CFG || document.hidden) return;
  if (!FR.me) { if (!FR.busy && Date.now() > FR.retryAt && store.name && (tutPh() === 'done' || FR.open)) frStart(); return; }
  if (FR.sync !== frSig() && state === 'menu') { FR.sync = frSig(); sbRpc('rm_me', { p_name: frName(), p_look: frLook(), p_rank: frRank() }).catch(() => { FR.sync = ''; }); }
  if (Date.now() - FR.at > (FR.open ? 6000 : state === 'menu' ? 20000 : 60000)) frPoll();
}
setInterval(frTick, 1000);
document.addEventListener('visibilitychange', () => { if (!FR.me) return; if (document.hidden) sbRpc('rm_inbox', { p_status: 'offline' }, true).catch(() => {}); else { FR.at = 0; frTick(); } });
// a new request while you're about the lobby: a note at the top, once
function frSeen(b) {
  const fresh = FR.seen ? b.incoming.filter(r => !FR.seen.has(r.id)) : []; FR.seen = new Set(b.incoming.map(r => r.id));
  if (fresh.length && !FR.open && state === 'menu') frToast(fresh.length === 1 ? frFace(fresh[0].look) + '<span><b>' + frEsc(fresh[0].name) + '</b> wants to be friends</span>' : '<span>' + fresh.length + ' new friend requests</span>');
}
function frBadge() {
  const n = FR.box ? FR.box.incoming.length : 0, btn = $('friendsBtn'); let d = btn.querySelector('.frdot');
  if (!n) { if (d) d.remove(); return; } if (!d) { d = document.createElement('b'); d.className = 'frdot'; btn.appendChild(d); } const t = n > 9 ? '9+' : String(n); if (d.textContent !== t) d.textContent = t;
  btn.setAttribute('aria-label', 'Friends, ' + n + (n === 1 ? ' request' : ' requests'));
}
function frToast(html) { const t = document.createElement('div'); t.className = 'frtoast'; t.setAttribute('role', 'status'); t.innerHTML = html; document.body.appendChild(t); AU.pop(); setTimeout(() => t.classList.add('out'), 3200); setTimeout(() => t.remove(), 3700); }
// a friend's face: the axolotl head in their paint
function frFace(look) {
  const p = PALETTE.find(q => q.id === (look && look.c)) || PALETTE[0], g = '#' + p.hex.toString(16).padStart(6, '0'), gills = 'M9.5 17 4.5 12.5M8.5 21.5 2.5 20.5M9.5 26 4.5 28.5M30.5 17l5-4.5M31.5 21.5l6-1M30.5 26l5 2.5';
  return '<svg class="frface" viewBox="0 0 40 40" aria-hidden="true"><g fill="none" stroke-linecap="round"><path d="' + gills + '" stroke="#171320" stroke-width="5.4"/><path d="' + gills + '" stroke="' + g + '" stroke-width="3"/></g><ellipse cx="20" cy="23.5" rx="13" ry="11.2" fill="' + p.hi + '" stroke="#171320" stroke-width="2.3"/><ellipse cx="15" cy="17.6" rx="4.6" ry="2.2" fill="#fff" opacity=".42"/><ellipse cx="15.2" cy="22.6" rx="1.9" ry="2.4" fill="#171320"/><ellipse cx="24.8" cy="22.6" rx="1.9" ry="2.4" fill="#171320"/><circle cx="14.6" cy="21.8" r=".7" fill="#fff"/><circle cx="24.2" cy="21.8" r=".7" fill="#fff"/><path d="M16.6 27.2q3.4 4.4 6.8 0z" fill="#5A0C1E" stroke="#171320" stroke-width="1.3" stroke-linejoin="round"/></svg>';
}
function frWhen(f) {
  if (f.online) return f.status === 'match' ? 'In a match' : 'In the lobby';
  const s = Math.max(0, (Date.now() + FR.skew - Date.parse(f.last_seen)) / 1000);
  return s < 3600 ? 'Online ' + Math.max(1, Math.round(s / 60)) + 'm ago' : s < 86400 ? 'Online ' + Math.round(s / 3600) + 'h ago' : s < 7 * 86400 ? 'Online ' + Math.round(s / 86400) + 'd ago' : 'Online a while ago';
}
const FR_X = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 7l10 10M17 7 7 17" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"/></svg>';
const FR_MORE = '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="5.5" cy="12" r="2.2" fill="currentColor"/><circle cx="12" cy="12" r="2.2" fill="currentColor"/><circle cx="18.5" cy="12" r="2.2" fill="currentColor"/></svg>';
function frRow(f) {
  const open = FR.menu === f.id, conf = open && FR.confirm;
  return '<li class="frrow' + (open ? ' open' : '') + '">' + frFace(f.look) + '<span class="frwho"><b>' + frEsc(f.name) + '</b><small><i class="frst ' + (f.online ? f.status : 'off') + '"></i>' + frWhen(f) + ' · Rank ' + (f.rank | 0) + '</small></span>'
    + '<span class="frbtns"><button class="frb ghost ic" data-act="more" data-id="' + f.id + '" type="button" aria-expanded="' + open + '" aria-label="More for ' + frEsc(f.name) + '">' + FR_MORE + '</button></span>'
    + (!open ? '' : '<div class="frmenu">' + (conf ? '<span>' + (conf === 'remove' ? 'Remove ' : 'Block ') + frEsc(f.name) + '?</span><button class="frb bad" data-act="' + conf + '" data-id="' + f.id + '" type="button">' + (conf === 'remove' ? 'Remove' : 'Block') + '</button><button class="frb ghost" data-act="nvm" type="button">Keep</button>'
      : '<button class="frb ghost" data-act="askremove" data-id="' + f.id + '" type="button">Remove friend</button><button class="frb ghost" data-act="askblock" data-id="' + f.id + '" type="button">Block</button>') + '</div>') + '</li>';
}
const FR_FACES = '<span class="ffaces" aria-hidden="true">' + ['green', 'purple'].map(c => frFace({ c })).join('') + '</span>';
// the screen. A poll redraws it only when something it shows has changed, and keeps what you're typing
function frRender(fromPoll) {
  const el = $('frBody'); if (!el) return; let h = '';
  if (!SB_CFG) h = '<div class="frmsg">' + FR_FACES + '<b>Friends are on the way</b><p>They play online, and online play isn’t switched on in this version yet.</p></div>';
  else if (!FR.me) h = FR.err && !FR.busy ? '<div class="frmsg">' + FR_FACES + '<b>Can’t connect</b><p>' + frEsc(FR.err) + '</p><button class="frb go" data-act="retry" type="button">Try again</button></div>' : '<div class="frmsg"><span class="frspin" aria-hidden="true"></span><p>Getting your friend code…</p></div>';
  else {
    const b = FR.box || { friends: [], incoming: [], outgoing: [], blocked: [] }, on = b.friends.filter(f => f.online).length;
    h += '<section class="frme"><small>Your friend code</small><div class="frcode"><b>' + frCode(FR.me.code) + '</b><button class="frb" data-act="copy" type="button">Copy</button>' + (NATIVE_SHARE ? '<button class="frb" data-act="share" type="button">Share</button>' : '') + '</div></section>';
    h += '<form class="fradd" id="frAdd" autocomplete="off" novalidate><label for="frIn">Add a friend</label><div><input id="frIn" type="text" inputmode="text" autocapitalize="characters" autocorrect="off" spellcheck="false" maxlength="9" placeholder="Their friend code" value="' + frEsc(FR.typed) + '"><button class="frb go" type="submit">Add</button></div><p class="frnote' + (FR.noteOk ? '' : ' bad') + '" aria-live="polite">' + frEsc(FR.note) + '</p></form>';
    if (b.incoming.length) h += '<section><h4>Want to be friends <i>' + b.incoming.length + '</i></h4><ul class="frlist">' + b.incoming.map(r => '<li class="frrow">' + frFace(r.look) + '<span class="frwho"><b>' + frEsc(r.name) + '</b><small>Rank ' + (r.rank | 0) + '</small></span><span class="frbtns"><button class="frb go" data-act="acc" data-id="' + r.id + '" type="button">Accept</button><button class="frb ghost ic" data-act="dec" data-id="' + r.id + '" type="button" aria-label="Decline ' + frEsc(r.name) + '">' + FR_X + '</button></span></li>').join('') + '</ul></section>';
    h += '<section><h4>Friends <i>' + b.friends.length + '</i>' + (on ? '<em>· ' + on + ' online</em>' : '') + '</h4>' + (b.friends.length ? '<ul class="frlist">' + b.friends.map(frRow).join('') + '</ul>' : '<p class="frempty">No friends yet. Send them your code, or add theirs above.</p>') + '</section>';
    if (b.outgoing.length) h += '<section><h4>Waiting on</h4><ul class="frlist">' + b.outgoing.map(r => '<li class="frrow sm">' + frFace(r.look) + '<span class="frwho"><b>' + frEsc(r.name) + '</b><small>Request sent</small></span><span class="frbtns"><button class="frb ghost" data-act="cancel" data-id="' + r.id + '" type="button">Cancel</button></span></li>').join('') + '</ul></section>';
    if (b.blocked.length) h += '<details class="frblk"' + (FR.blkOpen ? ' open' : '') + '><summary>Blocked (' + b.blocked.length + ')</summary><ul class="frlist">' + b.blocked.map(r => '<li class="frrow sm"><span></span><span class="frwho"><b>' + frEsc(r.name) + '</b></span><span class="frbtns"><button class="frb ghost" data-act="unblock" data-id="' + r.id + '" type="button">Unblock</button></span></li>').join('') + '</ul></details>';
    if (FR.err) h += '<p class="frwarn">' + frEsc(FR.err) + '</p>';
    h += '<p class="frfine">Friends see your name, your paint colour and your rank, and when you’re online.</p>';
  }
  if (fromPoll && h === FR.sig) return; FR.sig = h;
  const a = document.activeElement, typing = a && a.id === 'frIn', p0 = typing ? a.selectionStart : 0, p1 = typing ? a.selectionEnd : 0, top = el.scrollTop;
  el.innerHTML = h; el.scrollTop = top;
  if (typing) { const i = $('frIn'); if (i) { i.focus({ preventScroll: true }); try { i.setSelectionRange(p0, p1); } catch (e) {} } }
}
async function frCopy() {
  const t = FR.me.code; let ok = false;
  try { if (navigator.clipboard && window.isSecureContext) { await navigator.clipboard.writeText(t); ok = true; } } catch (e) {}
  if (!ok) { const ta = document.createElement('textarea'); ta.value = t; ta.setAttribute('readonly', ''); ta.style.cssText = 'position:fixed;left:0;top:0;opacity:0'; document.body.appendChild(ta); ta.select(); try { ta.setSelectionRange(0, 99); ok = document.execCommand('copy'); } catch (e) {} ta.remove(); }
  FR.note = ok ? 'Your code is copied. Send it to a friend!' : 'Couldn’t copy it. Your code is ' + frCode(t) + '.'; FR.noteOk = ok; frRender();
}
const FR_ADD = { sent: n => 'Request sent to ' + n + '.', friends_now: n => 'You and ' + n + ' are friends now!', already_friends: n => 'You’re already friends with ' + n + '.', already_sent: n => 'Already sent. Waiting on ' + n + '.',
  not_found: () => 'No player has that code. Check it and try again.', self: () => 'That’s your own code!', limit: () => 'You’ve reached the friend limit.', slow_down: () => 'That’s a lot of tries. Wait a bit, then try again.' };
const frBody = $('frBody');
frBody.addEventListener('submit', async e => {
  e.preventDefault(); const i = $('frIn'), code = (i.value || '').toUpperCase().replace(/[^A-Z0-9]/g, ''); AU.ui();
  if (code.length !== 8) { FR.note = 'A friend code is 8 letters and numbers.'; FR.noteOk = false; return frRender(); }
  const btn = e.target.querySelector('button[type="submit"]'); btn.disabled = true;
  try { const r = await sbRpc('rm_add_friend', { p_code: code }); const k = r.ok ? r.state : r.why; FR.note = (FR_ADD[k] || FR_ADD.not_found)(r.name || ''); FR.noteOk = !!r.ok;
    if (r.ok) { FR.typed = ''; i.value = ''; if (r.state === 'friends_now') { AU.power(); buzz([12, 40, 12]); } } await frPoll(); }
  catch (err) { FR.note = frErrText(err); FR.noteOk = false; }
  frRender();
});
frBody.addEventListener('input', e => { if (e.target.id !== 'frIn') return; const v = e.target.value.toUpperCase().replace(/[^A-Z0-9]/g, '').slice(0, 8), f = v.length > 4 ? v.slice(0, 4) + ' ' + v.slice(4) : v; if (e.target.value !== f) e.target.value = f; FR.typed = f; if (FR.note) { FR.note = ''; const n = frBody.querySelector('.frnote'); if (n) n.textContent = ''; } });
frBody.addEventListener('toggle', e => { if (e.target.classList && e.target.classList.contains('frblk')) FR.blkOpen = e.target.open; }, true);
frBody.addEventListener('click', async e => {
  const b = e.target.closest('[data-act]'); if (!b) return; const a = b.dataset.act, id = b.dataset.id; AU.init(); AU.ui();
  if (a === 'retry') { FR.retryAt = 0; FR.err = ''; frRender(); return frStart(); }
  if (a === 'copy') return frCopy();
  if (a === 'share') { nativeSay('device', { share: 'Add me on Roll Model! My friend code is ' + frCode(FR.me.code) }); return; }
  if (a === 'more') { FR.menu = FR.menu === id ? '' : id; FR.confirm = ''; return frRender(); }
  if (a === 'askremove' || a === 'askblock') { FR.confirm = a.slice(3); return frRender(); }
  if (a === 'nvm') { FR.menu = ''; FR.confirm = ''; return frRender(); }
  const call = { acc: ['rm_answer_request', { p_from: id, p_accept: true }], dec: ['rm_answer_request', { p_from: id, p_accept: false }], cancel: ['rm_cancel_request', { p_to: id }],
    remove: ['rm_remove_friend', { p_other: id }], block: ['rm_block', { p_other: id }], unblock: ['rm_unblock', { p_other: id }] }[a];
  if (!call) return; b.disabled = true;
  try { const r = await sbRpc(call[0], call[1]); if (a === 'acc' && r && r.ok) { AU.power(); buzz([12, 40, 12]); } FR.menu = ''; FR.confirm = ''; FR.err = ''; await frPoll(); }
  catch (err) { FR.err = frErrText(err); }
  frRender();
});
// ---- the Time trial's Friends board: your runs go up as you finish them (kept if you're offline), and when the week turns the top
// three of a board with three or more on it win dabs (worked out on the phone, like the rest of the game's rewards for now)
function frTrial(sid, p) { if (!SB_CFG) return; store.ttq = (store.ttq || []).concat([{ s: sid, p: Math.round(p), w: ttWeek() }]).slice(-30); save(); delete FR.board[sid]; frFlushTrials(); }
async function frFlushTrials() {
  if (!FR.me || FR.flushing || !(store.ttq && store.ttq.length)) return; FR.flushing = true;
  try { while (store.ttq && store.ttq.length) { const q = store.ttq[0]; if (q.w === ttWeek()) { const r = await sbRpc('rm_trial', { p_stage: q.s, p_pct: q.p }); if (r && r.why === 'slow_down') break; delete FR.board[q.s]; } store.ttq.shift(); save(); } }
  catch (e) {} finally { FR.flushing = false; }
}
async function frPayout() {
  const o = store.tt; if (FR.paid || !o || !o.prev || !o.prev.best || store.ttFrPaid === o.prev.wk) return; FR.paid = true;
  const wk = new Date(o.prev.wk).toISOString().slice(0, 10); let won = 0, line = '';
  try { for (const sid of Object.keys(o.prev.best)) { const r = await sbRpc('rm_friends_board', { p_stage: sid, p_week: wk }), rows = r.rows || [], i = rows.findIndex(x => x.me);
      if (rows.length >= TT_FRIENDS_MIN && i >= 0 && i < 3) { won += TT_PRIZE.friends[i]; line = ttOrd(i + 1) + ' on ' + ttName(sid); } }
    store.ttFrPaid = o.prev.wk; if (won) { store.drops = (store.drops || 0) + won; renderLobbyUI(); frToast('<span>Friends board: <b>' + frEsc(line) + '</b>! +' + won + ' dabs</span>'); AU.power(); } save(); }
  catch (e) { FR.paid = false; }
}
function frBoardHtml(sid) {
  if (!FR.me) { if (!FR.busy && Date.now() > FR.retryAt) frStart(); return FR.err && !FR.busy ? '<p class="ttnone"><b>Can’t load your friends’ times.</b>' + frEsc(FR.err) + '</p>' : '<p class="ttnone"><b>Loading your friends’ times…</b></p>'; }
  const c = FR.board[sid]; if (!c || Date.now() - c.at > 30000) frBoardLoad(sid);
  if (!c) return '<p class="ttnone"><b>Loading your friends’ times…</b></p>';
  let h = c.err && !c.rows.length ? '<p class="ttnone"><b>Can’t load your friends’ times.</b>' + frEsc(c.err) + '</p>' : !c.rows.length ? '<p class="ttnone"><b>No runs from you or your friends here this week.</b>Play a Time trial on this canvas to set the first.</p>'
    : '<ol class="ttlist">' + c.rows.slice(0, 20).map((r, i) => '<li class="ttrow' + (i < 3 ? ' r' + (i + 1) : '') + (r.me ? ' me' : '') + '"><b class="ttrk" aria-label="' + ttOrd(i + 1) + '">' + (i + 1) + '</b><span class="ttwho">' + frFace(r.look) + frEsc(r.name) + (r.me ? '<em>You</em>' : '') + '</span><b class="ttpc">' + (r.best | 0) + '<small>%</small></b></li>').join('') + '</ol>';
  const P3 = TT_PRIZE.friends; h += '<p class="tttease">When the week turns, the top three win ' + P3[0] + ', ' + P3[1] + ' and ' + P3[2] + ' dabs' + (c.rows.length < TT_FRIENDS_MIN ? ', once ' + TT_FRIENDS_MIN + ' or more of you are on the board.' : '.') + '</p>';
  if (!(FR.box && FR.box.friends.length)) h += '<p class="tttease">Add friends from the lobby’s Friends button to race them here.</p>';
  return h;
}
async function frBoardLoad(sid) {
  if (FR.boardBusy === sid) return; FR.boardBusy = sid; await frFlushTrials();
  try { const r = await sbRpc('rm_friends_board', { p_stage: sid, p_week: null }); FR.board[sid] = { at: Date.now(), rows: r.rows || [] }; }
  catch (e) { const old = FR.board[sid]; FR.board[sid] = { at: Date.now() - 20000, rows: old ? old.rows : [], err: frErrText(e) }; }
  finally { FR.boardBusy = ''; }
  if (!$('ttModal').hidden && ttTab === 'friends' && ttSel === sid) ttRender();
}
if (SB_CFG) $('ttModal').classList.add('frlive');
"""

def apply(s):
    url, key = cfg()
    # the Friends screen: the notebook sheet in place of the "coming soon" card
    i = s.index('  <div class="modal" id="friendsModal" hidden>\n'); j = s.index('  <div class="modal" id="docModal" hidden>\n', i)
    s = s[:i] + HTML + s[j:]
    a = "@media (prefers-reduced-motion:reduce){.ttcard{animation:none}.tttabs button{transition:none}}\n"
    s = rep(s, a, a + CSS.lstrip('\n'))
    s = rep(s, "function openFriends() { if (state !== 'menu') return; PB.ret = document.activeElement; $('friendsModal').hidden = false; setTimeout(() => $('friendsClose').focus({ preventScroll: true }), 30); }\n"
               "function closeFriends() { if ($('friendsModal').hidden) return; $('friendsModal').hidden = true; if (PB.ret && PB.ret.focus) PB.ret.focus({ preventScroll: true }); }\n",
               "function openFriends() { if (state !== 'menu') return; PB.ret = document.activeElement; FR.open = true; FR.note = ''; FR.menu = ''; FR.confirm = ''; frRender(); $('friendsModal').hidden = false; if (SB_CFG) { if (!FR.me) frStart(); else { FR.at = 0; frPoll(); } } setTimeout(() => $('frX').focus({ preventScroll: true }), 30); }\n"
               "function closeFriends() { if ($('friendsModal').hidden) return; FR.open = false; FR.menu = ''; FR.confirm = ''; $('friendsModal').hidden = true; if (PB.ret && PB.ret.focus) PB.ret.focus({ preventScroll: true }); }\n")
    s = rep(s, "$('friendsClose').addEventListener('click', uiClick(closeFriends));\n", "$('frX').addEventListener('click', uiClick(closeFriends));\n")
    # the client itself, after the Time trial board it feeds (it uses ttWeek, TT_PRIZE and friends)
    a = "document.addEventListener('keydown', e => { if (e.key === 'Escape' && !$('ttModal').hidden) { e.preventDefault(); e.stopPropagation(); closeTT(); } }, true);\n"
    s = rep(s, a, a + JS.replace('__SB_URL__', url).replace('__SB_KEY__', key).lstrip('\n'))
    # the board's Friends tab
    s = rep(s, "  } else {\n    const P3 = TT_PRIZE[ttTab]; h = '<div class=\"ttlock\"><span class=\"ttlk\">'",
               "  } else if (ttTab === 'friends' && SB_CFG) h = frBoardHtml(sid); // (v305: live)\n  else {\n    const P3 = TT_PRIZE[ttTab]; h = '<div class=\"ttlock\"><span class=\"ttlk\">'")
    s = rep(s, "    h += '<p class=\"tttease\">Soon: the top three on <b>Friends</b> and <b>Global</b> win dabs every week.</p>';",
               "    h += SB_CFG ? '<p class=\"tttease\">The top three on <b>Friends</b> win dabs every week. <b>Global</b> comes with online play.</p>' : '<p class=\"tttease\">Soon: the top three on <b>Friends</b> and <b>Global</b> win dabs every week.</p>';")
    # a finished Time trial run goes up to the Friends board
    s = rep(s, "  if (mode === 'solo') { endInfo.sid = TH.id; endInfo.tt = ttAdd(TH.id, ry); }",
               "  if (mode === 'solo') { endInfo.sid = TH.id; endInfo.tt = ttAdd(TH.id, ry); frTrial(TH.id, ry); }")
    # the lobby holds still behind the Friends screen too
    s = rep(s, "|| !commModalEl.hidden))) renderFrame();", "|| !commModalEl.hidden || !friendsModalEl.hidden))) renderFrame();")
    s = rep(s, "const commModalEl = $('commModal');\n", "const commModalEl = $('commModal'), friendsModalEl = $('friendsModal');\n")
    return s
