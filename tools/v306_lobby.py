"""v306 (online lobby): the RMNet SDK in the page, the game server address, the connection, and the Online sheet
(find a match, private rooms, duel invites to friends).

Owned by the lobby agent. Applied after v306_accounts and before v306_match.

- The SDK: server/client/rmnet.js, read at build time (so it always matches the server) and inlined less its export line, as a
  classic script before the game's own; it sets window.RMNet.
- The game server's address comes from tools/online_config.json (game_server_url, wss:// only). Empty, and online play is off.
  For tests: window.__net or localStorage 'rm.net' (wss://, or ws:// to localhost or 127.0.0.1).
- onlineOpen() opens the Online sheet (the accounts module's Matchmaking card calls it): Find a match (1v1 matchmaking), Make a
  room (its 5-character code to Copy, or Share in the iOS app), Join with a code. It connects as it opens (8 s, then "Can't
  connect" with Try again; an old game gets "Update the game to play online"). Closing it lets the connection go, unless you're
  queued, in a room or in a match; then a chip at the top of the lobby says so and opens it again.
- Friends (v305): a Duel button on a friend in the lobby makes a room and sends them an invite (Supabase rm_invite); you wait 2
  minutes at most, or until they say not now. An invite to you shows as a card in the lobby and at the top of Friends: Play
  joins their room, Not now says no. The inbox is checked every 3 s while you wait on an invite, 8 s in the lobby with a friend
  online, 20 s otherwise.
- A match found: the sheet closes and window.netMatchFound(m, net) (the match module) takes over. Until that exists, the sheet says
  "Match found!", and 2 s later leaves the match and goes back to the start. Called off before the match screen took over: back
  to the queue or the room, with a word. The match module calls onlineAfterMatch() when a match is over.
- While the sheet is open, the lobby's 3D view holds still behind it, as under Friends."""
import json, os

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

HERE = os.path.dirname(os.path.abspath(__file__))

def net_url():
    p = os.path.join(HERE, 'online_config.json')
    try: c = json.load(open(p))
    except FileNotFoundError: c = {}
    u = (c.get('game_server_url') or '').strip()
    assert not u or u.startswith('wss://'), u
    assert not any(ch in u for ch in '"\'\\<> '), u
    return u

def sdk():
    # the SDK as the server has it, less the export line (a classic script can't have one): it defines RMNetSDK and sets window.RMNet
    lines = open(os.path.join(os.path.dirname(HERE), 'server', 'client', 'rmnet.js')).read().rstrip('\n').split('\n')
    assert lines[-1].startswith('export '), lines[-1][:80]
    js = '\n'.join(lines[:-1]).rstrip('\n') + '\n'
    assert '</script' not in js.lower() and '<!--' not in js and 'window.RMNet = RMNet' in js
    return js

HTML = r"""  <div class="modal ttm" id="onModal" hidden><div class="ttcard oncard" role="dialog" aria-modal="true" aria-labelledby="onTitle">
    <button class="ttx" id="onX" type="button" aria-label="Close"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6.5 6.5l11 11M17.5 6.5l-11 11" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"/></svg></button>
    <div class="tthd"><small>1v1 &middot; Most paint wins</small><h3 id="onTitle">Online</h3></div>
    <div class="frbody onbody" id="onBody"></div>
  </div></div>
  <p class="onsr" id="onLive" role="status" aria-live="polite"></p>
"""

CSS = r"""
/* (v306) Online: the Friends sheet's notebook page, for finding a match and private rooms */
.oncard{width:min(100%,400px)}
.onsr{position:absolute;width:1px;height:1px;margin:-1px;padding:0;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap;border:0}
.onhome{display:grid;grid-template-columns:minmax(0,1fr);align-content:start;gap:16px}
.onfind{display:grid;grid-template-columns:auto minmax(0,1fr);align-items:center;gap:12px;width:100%;min-height:82px;box-sizing:border-box;margin:4px 0 2px;padding:12px 16px 12px 10px;border:0;border-radius:2px;cursor:pointer;text-align:left;color:#FFF8EA;
  background:url(art/m_cpaper_g.webp) center/180px,#E3122F;background-blend-mode:multiply;box-shadow:inset 0 0 0 1px rgba(0,0,0,.08),4px 5px 0 rgba(0,0,0,.42);rotate:-.8deg;transition:transform .12s ease}
.onfind:active{transform:scale(.97)}
.onfind b{display:block;font:400 25px/1 var(--font-display);text-transform:uppercase;letter-spacing:.01em;text-shadow:0 2px 0 rgba(0,0,0,.22)}
.onfind small{display:block;margin-top:5px;font:700 12.5px/1.3 var(--font-ui);opacity:.94}
.onvs{display:flex;align-items:center;justify-content:center;gap:2px}
.onvs .frface{width:46px;height:46px}
.onvs i{margin:0 3px;font:400 14px/1 var(--font-display);font-style:normal;text-transform:uppercase;opacity:.75}
.onmys{display:grid;place-items:center;flex:none;width:40px;height:40px;box-sizing:border-box;border:2.4px dashed currentColor;border-radius:50%;font:400 19px/1 var(--font-display);opacity:.7}
.onfind .onvs .frface{width:40px;height:40px}.onfind .onmys{width:34px;height:34px;font-size:16px;margin-left:-6px}
.onbody{overflow-x:hidden}
.onfr{display:grid;grid-template-columns:minmax(0,1fr);gap:10px;align-content:start}
.onmk{width:100%;box-sizing:border-box;min-height:42px}
.onjoin input{letter-spacing:.24em}
.onnote{margin:0;padding:9px 11px 8px;border-radius:2px;background:#FFE896;box-shadow:0 9px 9px -8px rgba(0,0,0,.5);font:700 13.5px/1.35 var(--font-ui);color:var(--black);rotate:-.6deg}
.onwait{min-height:250px}
.onwait .onvs{color:#6E6680}
.frmsg p.ontime{margin:0;max-width:none;font:400 30px/1 var(--font-display);letter-spacing:.04em;font-variant-numeric:tabular-nums;color:var(--black)}
.onroomw{display:grid;grid-template-columns:minmax(0,1fr);gap:14px}
.onroom{display:grid;gap:2px}
.onroom>small{font:800 11px/1 var(--font-ui);letter-spacing:.12em;text-transform:uppercase;color:#6E6680}
.oncode{flex-wrap:wrap}.oncode b{flex:1 0 auto;padding:10px 8px 7px;font-size:34px;letter-spacing:.22em}
.onyou{display:inline-block;margin-left:5px;padding:3px 7px 2px;border-radius:999px;background:#E8364F;color:#fff;font:800 10px/1 var(--font-ui);font-style:normal;letter-spacing:.06em;text-transform:uppercase;vertical-align:2px;rotate:-3deg}
.onslot .frwho b{color:#8A8398}.onslot .onmys{width:40px;height:40px;color:#8A8398}
.onok{color:#2C7A3F}
.onstat{display:flex;align-items:center;justify-content:center;gap:9px;margin:0;font:700 13.5px/1.35 var(--font-ui);color:#5E566E;text-align:center}
.onstat .frspin{flex:none;width:18px;height:18px;border-width:2.5px}
.onbtns{display:flex;flex-wrap:wrap;justify-content:center;gap:8px}
.onbtns .frb{min-width:110px;min-height:40px}
.frrow .frbtns .frb.go.onwt{background:rgba(23,19,32,.07);color:var(--black);box-shadow:none}
/* an invite to you, over the lobby; and while you're queued or in a room with the sheet shut, a chip that says so */
.oninv{position:absolute;left:50%;top:calc(env(safe-area-inset-top,0px) + 78px);z-index:11;display:grid;grid-template-columns:auto minmax(0,1fr);align-items:center;gap:8px 10px;width:max-content;max-width:min(calc(100% - 32px),340px);box-sizing:border-box;padding:10px 12px 11px 10px;border-radius:18px;background:#171320;color:#FFF8EA;box-shadow:0 8px 22px rgba(0,0,0,.4);transform:translateX(-50%);animation:frin .35s cubic-bezier(.2,1.3,.4,1) both}
.oninv .frface{width:38px;height:38px}
.oninvt{min-width:0;font:700 14.5px/1.25 var(--font-ui)}.oninvt b{font-weight:800}
.oninvb{grid-column:1/-1;display:flex;justify-content:flex-end;gap:8px}
.oninv .frb{min-height:36px}.oninv .frb.ghost{background:rgba(255,248,234,.14);color:#FFF8EA}
.onchip{position:absolute;left:50%;top:calc(env(safe-area-inset-top,0px) + 78px);z-index:11;display:flex;align-items:center;gap:8px;max-width:calc(100% - 32px);min-height:38px;box-sizing:border-box;padding:0 15px 0 13px;border:0;border-radius:999px;background:#171320;color:#FFF8EA;font:700 13.5px/1 var(--font-ui);white-space:nowrap;box-shadow:0 6px 18px rgba(0,0,0,.35);transform:translateX(-50%);cursor:pointer;animation:frin .35s cubic-bezier(.2,1.3,.4,1) both}
.onchip span{overflow:hidden;text-overflow:ellipsis}
.onchip b{font:400 14px/1 var(--font-display);letter-spacing:.04em;font-variant-numeric:tabular-nums}
.onchip svg{width:14px;height:14px;flex:none;opacity:.7}
@media (min-aspect-ratio:1/1) and (max-height:600px){.oncard{width:min(100%,620px)}.onhome{grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:20px}.onfind{min-height:96px}.onwait{min-height:180px;gap:7px}.frmsg p.ontime{font-size:24px}
  .onroomw{grid-template-columns:minmax(0,1fr) minmax(0,1fr);grid-template-areas:"code who" "stat who" "btns who";align-items:start;gap:10px 20px}.onroom{grid-area:code}.onwho{grid-area:who}.onroomw>.onstat{grid-area:stat}.onroomw>.onbtns{grid-area:btns}.oncode b{font-size:28px}}
@media (prefers-reduced-motion:reduce){.oninv,.onchip{animation:none}}
"""

JS = r"""
// ---------- (v306) Online: matchmaking, private rooms and duel invites, on the game server (server/, the referee; its SDK RMNet is inlined
// above the game's script). The Online sheet finds a match (1v1), or makes a room whose code a friend types in; a friend in the lobby gets a
// Duel button in Friends, which makes a room and invites them to it through Supabase (v305). When a match is found the sheet closes and the
// match module (v306_match) takes over: window.netMatchFound(m, net). When the match is over, it calls onlineAfterMatch().
// What the match module reads, in ON (these names stay):
//   ON.net      the RMNet connection, or null. After a drop it reconnects by itself (net.connected: up right now)
//   ON.me       this connection's welcome from the server ({ id, name, ratings, ... }), or null
//   ON.queued   null, or { mode, at } while matchmaking (at: when the wait began, Date.now())
//   ON.room     null, or the server's room view { code, mode, host, need, inMatch, players: [{ id, name, look, ready }] }
//   ON.match    null, or the matchFound message, from then until onlineAfterMatch()
//   ON.inv      null, or the invite you sent and are waiting on { id, to, name, look, at, st: 'sending' | 'open' | 'accepted' }
//   ON.invites  the open invites to you (rm_inbox's, newest first), less the ones you've answered
//   ON.open     the Online sheet is up
//   ON.gate     null, or a function: online play only opens when it returns true (for the accounts module to ask for an account first)
// and onLook() / onName(): your look and name as the server has them ----------
const NET_URL = (() => { let u = '__NET_URL__'; try { const o = window.__net || localStorage.getItem('rm.net'); if (o) u = String(o); } catch (e) {} // (a test server, for development)
  return /^(wss:\/\/|ws:\/\/(localhost|127\.0\.0\.1)[:/])[^\s"'<>\\]*$/.test(u) ? u : ''; })();
const ON = { net: null, me: null, queued: null, room: null, match: null, inv: null, invites: [], open: false, gate: null,
  v: '', err: '', note: '', typed: '', jnote: '', cnote: '', join: '', want: false, again: false, lost: 0, cp: null, cpEnd: null, ret: null, foundT: 0, unq: 0, qAt: 0, off: false, after: false, nope: new Set(), seen: new Set(), sig: '' };
// your look as the other player sees it: paint, eyes, rank, and what you're wearing (only the slots in use; well under the server's 512 bytes)
function onLook() { const w = {}; for (const k of ['head', 'back', 'mouth', 'eye', 'side', 'neck', 'lash', 'arms']) if (myLook[k]) w[k] = myLook[k]; w.iris = myLook.iris; return { c: colorId, e: myLook.eyes, r: frRank(), w }; }
const onName = () => frName();
const onE = (code, src) => Object.assign(new Error(code), { code, why: src && (src.message || src.reason) });
const onOffline = () => typeof navigator !== 'undefined' && navigator.onLine === false;
const onClock = ms => { const s = Math.max(0, Math.round(ms / 1000)); return Math.floor(s / 60) + ':' + String(s % 60).padStart(2, '0'); };
const ON_MYS = '<span class="onmys" aria-hidden="true">?</span>';
const onVs = (a, b) => '<span class="onvs" aria-hidden="true">' + a + '<i>vs</i>' + b + '</span>';
function onSay(t) { const el = $('onLive'); if (!el) return; el.textContent = ''; setTimeout(() => { el.textContent = t; }, 60); } // (for screen readers: what just happened)
// ---- the connection
// one that's up: the one in hand, or the one coming back (given 8 s), or a new one. The SDK never gives up on a plain network failure (it
// keeps trying), so the 8 s are ours; a refusal (an old game) ends it at once
function onlineConnect() {
  if (!NET_URL || typeof RMNet !== 'function') return Promise.reject(onE('off'));
  if (ON.net && ON.net.connected && ON.me) return Promise.resolve(ON.net);
  if (ON.cp) return ON.cp;
  const fresh = !ON.net, net = ON.net || onNew(); let done = false;
  const p = new Promise((res, rej) => {
    const end = e => { if (done) return; done = true; clearTimeout(to); offW(); offF(); if (ON.cp === p) { ON.cp = null; ON.cpEnd = null; } if (!e) return res(net); if (ON.net === net) onlineDrop(); rej(e); };
    const to = setTimeout(() => end(onE(onOffline() ? 'offline' : 'timeout')), 8000), offW = net.on('welcome', () => end()), offF = net.on('fatal', e => end(onE(e && e.code === 'version' ? 'old' : 'fatal', e)));
    ON.cpEnd = end;
  });
  ON.cp = p; if (fresh) net.connect().catch(() => {}); // (a refusal comes through 'fatal' too)
  return p;
}
function onNew() {
  const net = new RMNet({ url: NET_URL, name: onName(), look: onLook(), token: store.netTok || null, client: 'rm-306' });
  const on = (ev, fn) => net.on(ev, d => { if (ON.net === net) fn(d || {}); }); // (a connection let go says nothing more)
  ON.net = net; ON.me = null;
  on('token', t => { if (t.token && t.token !== store.netTok) { store.netTok = t.token; save(); } }); // (who you are on the server, so your rating stays yours)
  on('welcome', w => { ON.me = w; onBack(); });
  on('close', e => { ON.me = null; net.name = onName(); net.look = onLook(); if (e.willReconnect) onLost(); }); // (the next hello says who you are now)
  on('queued', m => { ON.queued = { mode: m.mode || 'duel', at: ON.queued ? ON.queued.at : (m.requeued && ON.qAt) || Date.now() }; onUpd(); });
  on('queueLeft', () => { ON.queued = null; onUpd(); });
  on('room', onRoom);
  on('roomLeft', () => { ON.room = null; onUpd(); });
  on('matchFound', onFound);
  on('resume', onResume);
  on('matchCancelled', onCalledOff);
  on('fatal', onFatal);
  on('error', e => { if (e.code === 'handler') console.error('online: ' + e.message); }); // (the SDK catches what a handler throws)
  return net;
}
// let go of the connection (and with it the queue or the room, which the server lets go of too)
function onlineDrop() {
  const n = ON.net, end = ON.cpEnd; ON.net = null; ON.me = null; ON.cp = null; ON.cpEnd = null; ON.queued = null; ON.room = null; ON.lost = 0; ON.want = false; ON.again = false;
  if (ON.inv) onInvEnd('');
  if (end) end(onE('closed')); if (n) n.close();
}
// the connection dropped and the SDK is getting it back; the server has let go of your place in the queue or the room meanwhile
function onLost() { if (!ON.match && (ON.queued || ON.room || ON.inv)) { ON.lost = ON.lost || Date.now(); onUpd(); } }
// back (or the first time): the queue or the room taken up again. A room left empty is gone by then: a new one (and the invite sent again)
async function onBack() {
  const lost = ON.lost, net = ON.net; ON.lost = 0;
  if (!lost || ON.match) return onUpd();
  try { if (ON.room) { ON.want = true; await net.joinRoom(ON.room.code); } else if (ON.queued) await net.queue(ON.queued.mode); }
  catch (e) {
    if (ON.net !== net) return; const had = !!ON.room; ON.room = null; ON.queued = null;
    try { if (!had) throw e; ON.want = true; await net.createRoom('duel');
      if (!ON.inv) ON.note = 'The connection dropped, so your room has a new code.';
      else { const r = await sbRpc('rm_invite', { p_to: ON.inv.to, p_room: ON.room.code, p_mode: 'duel' }); if (!r || !r.ok || !ON.inv) throw e; Object.assign(ON.inv, { id: r.id, at: Date.now(), st: 'open' }); } }
    catch (e2) { ON.want = false; if (ON.inv) await onInvEnd(''); else if (ON.room) await onLeave(); ON.note = 'The connection dropped. Try again.'; if (!ON.open && state === 'menu') frToast('<span>' + ON.note + '</span>'); }
  }
  onUpd(); if (FR.open) frRender();
}
// refused for good (an old game, or another screen took over): no more tries
function onFatal(e) {
  if (ON.match) return; // (the match module's)
  const old = e.code === 'version'; ON.v = old ? 'old' : 'error';
  ON.err = e.code === 'kicked' && e.message === 'replaced' ? 'You’re playing online on another screen.' : e.code === 'banned' ? 'This device can’t play online.' : 'The game server turned the connection down.';
  onlineDrop(); onUpd(); if (!ON.open && !old && state === 'menu') frToast('<span>' + frEsc(ON.err) + '</span>');
}
// the connection for an action, with "Connecting…" while it comes up; null (and the error showing) if it doesn't
async function onNet() {
  if (!(ON.net && ON.net.connected && ON.me) && !ON.v) { ON.v = 'connecting'; onRender(); }
  try { const n = await onlineConnect(); if (ON.v === 'connecting') { ON.v = ''; onUpd(); } return n; } catch (e) { onFail(e); return null; }
}
function onFail(e) {
  if (!e || e.code === 'closed' || e.code === 'off') return;
  ON.v = e.code === 'old' ? 'old' : 'error'; ON.err = e.code === 'offline' || onOffline() ? 'You’re offline. Online play comes back when you are.' : 'Can’t reach the game server right now.'; onUpd();
}
const ON_JOIN = { not_found: 'No room has that code. Check it and try again.', full: 'That room’s full already.', busy: 'They’re in a match right now. Try again in a minute.', rate: 'That’s a lot of tries. Wait a little, then try again.' };
const onReqText = e => e && e.code === 'timeout' ? 'The game server didn’t answer. Try again.' : e && e.code === 'disconnected' ? 'Lost the connection. Try again.' : e && e.status ? frErrText(e) : 'Something went wrong. Try again.';
// ---- the lobby: the queue, rooms
async function onFind() {
  ON.note = ''; const net = await onNet(); if (!net) return;
  try { if (ON.room) await onLeave(); ON.unq = 0; ON.queued = { mode: 'duel', at: Date.now() }; onUpd(); await net.queue('duel'); onSay('Finding a rival'); }
  catch (e) { ON.queued = null; ON.note = onReqText(e); onUpd(); }
}
async function onUnq() { const net = ON.net; ON.unq = Date.now(); ON.queued = null; onUpd(); try { if (net) await net.cancelQueue(); } catch (e) {} }
async function onMake() {
  ON.note = ''; ON.cnote = ''; const net = await onNet(); if (!net) return;
  try { if (ON.queued) await onUnq(); ON.want = true; ON.again = false; if (!ON.room) await net.createRoom('duel'); AU.pop(); onSay('Your room’s code is ' + ON.room.code.split('').join(' ')); }
  catch (e) { ON.want = false; ON.note = onReqText(e); }
  onUpd();
}
// a code as typed or pasted: capitals, letters and numbers only (pasted with words around it, the last 5-character word)
function onCodeOf(v) { v = String(v || '').toUpperCase(); let c = v.replace(/[^A-Z0-9]/g, ''); if (c.length > 5) { const w = v.match(/\b[A-Z0-9]{5}\b/g); c = w ? w[w.length - 1] : c.slice(0, 5); } return c; }
async function onJoin(raw) {
  const code = onCodeOf(raw); ON.typed = code;
  if (code.length !== 5) { ON.jnote = 'A room code is 5 letters and numbers.'; AU.nope(); return onRender(); }
  ON.note = ''; ON.jnote = ''; ON.cnote = ''; const net = await onNet(); if (!net) return;
  try { if (ON.queued) await onUnq(); if (ON.room) await onLeave(); ON.want = true; ON.again = false; await net.joinRoom(code); ON.typed = ''; AU.pop(); onSay('You’re in the room'); }
  catch (e) { ON.want = false; ON.jnote = ON_JOIN[e.code] || onReqText(e); AU.nope(); }
  onUpd();
}
async function onLeave() { const net = ON.net; ON.want = false; ON.again = false; ON.cnote = ''; if (ON.inv) return onInvEnd(''); try { if (net && ON.room) await net.leaveRoom(); } catch (e) {} ON.room = null; onUpd(); }
function onRoom(m) {
  const was = ON.room, my = ON.me && ON.me.id, r = { code: m.code, mode: m.mode, host: m.host, need: m.need, inMatch: !!m.inMatch, players: Array.isArray(m.players) ? m.players : [] };
  ON.room = r; if (ON.match) return; // (the match module has the screen)
  if (was && was.code === r.code) for (const p of r.players) if (p.id !== my && !was.players.some(q => q.id === p.id)) { AU.pop(); onSay(p.name + ' is in the room'); }
  // ready while someone's still to come (so the match starts the moment they're in), and once you've said so; everyone back after a match: Play again
  const me = r.players.find(p => p.id === my);
  if (me && !me.ready && !r.inMatch && (ON.want || r.players.length < r.need)) { ON.want = true; ON.net.ready(true); }
  onUpd();
}
async function onCopy() {
  const c = ON.room && ON.room.code; if (!c) return; let ok = false;
  try { if (navigator.clipboard && window.isSecureContext) { await navigator.clipboard.writeText(c); ok = true; } } catch (e) {}
  if (!ok) { const ta = document.createElement('textarea'); ta.value = c; ta.setAttribute('readonly', ''); ta.style.cssText = 'position:fixed;left:0;top:0;opacity:0'; document.body.appendChild(ta); ta.select(); try { ta.setSelectionRange(0, 99); ok = document.execCommand('copy'); } catch (e) {} ta.remove(); }
  ON.cnote = ok ? 'Copied! Send it to your friend.' : 'Couldn’t copy it. The code is ' + c + '.'; onRender();
}
// ---- a match: the match module takes it from here (or, until it's in, a word and back to the start)
function onFound(m) {
  const net = ON.net;
  // found just as you cancelled, or once you'd gone into a game against the CPU: let it go (the other player goes back in the queue)
  if ((state !== 'menu' && !ON.match) || (!m.room && ON.unq && Date.now() - ON.unq < 3000)) { net.leaveMatch().catch(() => {}); return; }
  clearTimeout(ON.foundT); ON.foundT = 0; if (ON.queued) ON.qAt = ON.queued.at;
  ON.match = m; ON.queued = null; ON.want = false; ON.inv = null; ON.lost = 0; ON.note = ''; ON.off = false; ON.after = false;
  if (FR.open) closeFriends();
  if (typeof window.netMatchFound === 'function') { ON.v = ''; onlineClose(); onCard(); try { window.netMatchFound(m, net); } catch (e) { frameErr(e); } return; }
  ON.v = 'found'; if (!onlineOpen()) onRender(); AU.ready(); buzz([10, 30, 10]); onSay('Match found!');
  ON.foundT = setTimeout(onFoundEnd, 2000);
}
// (a stand-in until the match module is in) out of the match, the room and the queue, and back to the start
async function onFoundEnd() {
  const net = ON.net; ON.foundT = 0; if (ON.v !== 'found') return; ON.match = null; ON.want = false;
  try { if (net && net.match) await net.leaveMatch(); } catch (e) {}
  try { if (net && ON.room) await net.leaveRoom(); } catch (e) {}
  try { if (net && ON.queued) await net.cancelQueue(); } catch (e) {}
  ON.room = null; ON.queued = null; if (ON.v === 'found') ON.v = ''; if (!ON.open) onlineDrop(); onUpd();
}
// called off before it began (someone left, the stages didn't match, a phone never answered): back where you were, with a word. Once the
// match screen has taken over it's the match module's, and onlineAfterMatch() brings you back
function onCalledOff(m) {
  const was = ON.match; if (!was || (m.matchId && was.matchId !== m.matchId)) return;
  if (state !== 'menu') { ON.off = true; return; }
  clearTimeout(ON.foundT); ON.foundT = 0; ON.match = null; ON.v = ''; ON.note = 'The match was called off'; AU.nope(); onSay(ON.note);
  setTimeout(() => { if (!ON.match && !onlineOpen()) onUpd(); }, 150); // (from the queue, the server puts you back in it: that word comes next)
}
// a match to pick up (the app was closed in the middle of one): the match module's if it takes it, otherwise let go (it counts as a loss)
function onResume(m) {
  if (ON.match && ON.match.matchId === m.matchId) return; // (a reconnect during the match the match module is playing: it's listening)
  if (typeof window.netMatchResume === 'function') { ON.match = m; onlineClose(); window.netMatchResume(m, ON.net); return; }
  ON.net.leaveMatch().catch(() => {});
}
// the match module, when a match is over: the room again if you're still in one (or the queue, after a match that was called off put you back
// in line); otherwise the connection is let go. It waits for the menu
function onlineAfterMatch() { ON.after = true; if (state === 'menu') onAfter(); }
function onAfter() {
  const off = ON.off; ON.after = false; ON.off = false; clearTimeout(ON.foundT); ON.foundT = 0; ON.match = null; ON.v = ''; ON.want = false; ON.cnote = '';
  if (ON.net && (ON.room || ON.queued)) { ON.again = !!ON.room && !off; ON.note = off ? 'The match was called off' : ''; onlineOpen(); return; }
  onlineDrop(); onUpd();
}
// ---- duel invites to friends (Supabase, v305: rm_invite, rm_answer_invite, rm_cancel_invite; rm_inbox's invites and sent)
const ON_INV = { not_friends: n => 'You and ' + n + ' aren’t friends any more.', slow_down: () => 'That’s a lot of invites. Wait a bit, then try again.', bad_room: () => 'Couldn’t send the invite. Try again.' };
async function onlineInvite(f) {
  if (!NET_URL || !f || !f.id || !FR.me || state !== 'menu' || (ON.gate && !ON.gate())) return;
  if (FR.open) closeFriends();
  if (ON.inv && ON.inv.to === f.id) { onlineOpen(); return; } // (already asked: back to waiting)
  if (ON.inv) await onInvEnd('');
  const inv = ON.inv = { id: null, to: f.id, name: String(f.name || 'Your friend'), look: f.look, at: Date.now(), st: 'sending' };
  ON.note = ''; ON.cnote = ''; ON.v = ''; onlineOpen();
  const net = await onNet(); if (!net) { if (ON.inv === inv) ON.inv = null; return; }
  try {
    if (ON.queued) await onUnq();
    ON.want = true; ON.again = false; if (!ON.room) await net.createRoom('duel');
    const r = await sbRpc('rm_invite', { p_to: f.id, p_room: ON.room.code, p_mode: 'duel' });
    if (ON.inv !== inv) return; // (called off meanwhile)
    if (!r || !r.ok) return onInvEnd((ON_INV[r && r.why] || ON_INV.bad_room)(inv.name));
    Object.assign(inv, { id: r.id, at: Date.now(), st: 'open' }); AU.pop(); onSay('Invite sent. Waiting for ' + inv.name);
  } catch (e) { if (ON.inv === inv) return onInvEnd(e && e.status ? frErrText(e) : onReqText(e)); }
  onUpd(); if (FR.open) frRender();
}
// the invite you sent is over (not now, no answer, or you cancelled it): it's taken back, and so is the room
async function onInvEnd(note) {
  const i = ON.inv; if (!i) return; ON.inv = null; ON.want = false;
  if (i.id && i.st !== 'accepted') sbRpc('rm_cancel_invite', { p_id: i.id }).catch(() => {});
  const net = ON.net; if (net && ON.room) { try { await net.leaveRoom(); } catch (e) {} } ON.room = null;
  ON.note = note || ''; if (note) AU.nope();
  if (note && !ON.open && state === 'menu') frToast(frFace(i.look) + '<span>' + frEsc(note) + '</span>');
  if (!ON.open && !ON.queued && !ON.match && ON.net) onlineDrop();
  onUpd(); if (FR.open) frRender();
}
// after every inbox (frPoll): invites to you (a sound for a new one), and how the one you sent is doing
function onInbox(b) {
  try {
    const now = Date.now() + FR.skew, list = (b.invites || []).filter(i => i && i.id && i.from && !ON.nope.has(i.id) && Date.parse(i.expires) > now), fresh = list.filter(i => !ON.seen.has(i.id));
    for (const i of list) ON.seen.add(i.id); ON.invites = NET_URL ? list : [];
    if (NET_URL && fresh.length && state === 'menu') { AU.pop(); buzz([12, 40, 12]); onSay(fresh[0].from.name + ' wants to duel'); }
    const i = ON.inv, s = i && i.id && (b.sent || []).find(x => x.id === i.id);
    if (s && (s.status === 'declined' || s.status === 'cancelled')) onInvEnd(i.name + ' can’t play right now');
    else if (s && s.status === 'accepted' && i.st !== 'accepted') { i.st = 'accepted'; i.acc = Date.now(); onSay(i.name + ' said yes'); }
    onUpd();
  } catch (e) {}
}
// Play (yes: into their room) or Not now
async function onAnswer(id, yes) {
  const i = ON.invites.find(x => x.id === id); ON.nope.add(id); ON.invites = ON.invites.filter(x => x.id !== id); onUpd(); if (FR.open) frRender();
  if (!yes) { sbRpc('rm_answer_invite', { p_id: id, p_accept: false }).catch(() => {}); return; }
  if (!i || state !== 'menu' || (ON.gate && !ON.gate())) return;
  if (FR.open) closeFriends();
  const who = String(i.from.name || 'your friend'); ON.join = who; ON.v = 'joining'; ON.note = ''; ON.cnote = ''; onlineOpen();
  let r = null; try { r = await sbRpc('rm_answer_invite', { p_id: id, p_accept: true }); } catch (e) { if (ON.v === 'joining') { ON.v = ''; ON.note = frErrText(e); onUpd(); } return; }
  if (ON.v !== 'joining') return; // (the sheet was shut meanwhile: not joining after all)
  if (!r || !r.ok || !r.room) { ON.v = ''; ON.note = 'That invite has run out.'; AU.nope(); return onUpd(); }
  let net = null; try { net = await onlineConnect(); } catch (e) { if (ON.v === 'joining') { ON.v = ''; onFail(e); } return; }
  if (ON.v !== 'joining') return;
  try { if (ON.queued) await onUnq(); if (ON.inv) await onInvEnd(''); else if (ON.room) await onLeave(); ON.want = true; ON.again = false; ON.v = 'joining'; await net.joinRoom(r.room); if (ON.v === 'joining') ON.v = ''; AU.pop(); }
  catch (e) { ON.want = false; if (ON.v === 'joining') ON.v = ''; ON.note = e.code === 'not_found' ? who + '’s room has closed.' : ON_JOIN[e.code] || onReqText(e); AU.nope(); }
  onUpd();
}
// (Friends) a Duel button on a friend who's in the lobby
function onDuelBtn(f) {
  if (!NET_URL || !f.online || f.status !== 'lobby') return ''; const w = ON.inv && ON.inv.to === f.id, n = frEsc(f.name);
  return '<button class="frb go' + (w ? ' onwt' : '') + '" data-on="duel" data-id="' + frEsc(f.id) + '" type="button" aria-label="' + (w ? 'Waiting for ' : 'Duel ') + n + '">' + (w ? 'Waiting' : 'Duel') + '</button>';
}
function onInvRow(i) {
  const n = frEsc(i.from.name), id = frEsc(i.id);
  return '<li class="frrow">' + frFace(i.from.look) + '<span class="frwho"><b>' + n + '</b><small>Wants to duel!</small></span><span class="frbtns"><button class="frb go" data-on="iplay" data-id="' + id + '" type="button" aria-label="Play ' + n + '">Play</button><button class="frb ghost" data-on="inope" data-id="' + id + '" type="button" aria-label="Not now, ' + n + '">Not now</button></span></li>';
}
const onInvList = () => ON.invites.length ? '<section aria-label="Duel invites"><h4>Invites <i>' + ON.invites.length + '</i></h4><ul class="frlist">' + ON.invites.slice(0, 3).map(onInvRow).join('') + '</ul></section>' : '';
// how often the inbox is checked (frTick): every 3 s while you wait on an invite you sent, 6 s on the Friends screen, 8 s in the lobby with a
// friend online (so their invite gets here quickly), 20 s otherwise, and a minute in a match
function onPollGap() { return ON.inv && ON.inv.id ? 3000 : FR.open ? 6000 : state === 'menu' ? (FR.box && FR.box.friends.some(f => f.online) ? 8000 : 20000) : 60000; }
// ---- the sheet
function onlineOpen() {
  if (state !== 'menu' || (ON.gate && !ON.gate())) return false;
  if (!ON.open) { ON.ret = document.activeElement; ON.open = true; $('onModal').hidden = false; setTimeout(() => { if (ON.open) $('onX').focus({ preventScroll: true }); }, 30); }
  if (ON.v === 'error' || ON.v === 'old') ON.v = '';
  onRender(); onCard();
  if (NET_URL && !ON.v && !(ON.net && (ON.net.connected || ON.lost))) onNet(); // (connected while they choose)
  return true;
}
function onlineClose() {
  if (!ON.open) return; ON.open = false; $('onModal').hidden = true; ON.jnote = ''; ON.cnote = ''; if (ON.v !== 'found') ON.note = '';
  if (ON.v === 'connecting' || ON.v === 'error' || ON.v === 'old' || ON.v === 'joining') ON.v = '';
  if (ON.ret && ON.ret.focus && document.contains(ON.ret)) ON.ret.focus({ preventScroll: true });
  if (ON.v !== 'found' && !ON.queued && !ON.room && !ON.match && !ON.inv && ON.net) onlineDrop(); // (nothing going on: no connection kept)
  onCard();
}
const onUpd = () => { if (ON.open) onRender(true); onCard(); };
function onView() { return !NET_URL ? 'off' : ON.v || (ON.inv ? 'inv' : ON.room ? 'room' : ON.queued ? 'queue' : 'home'); }
function onRender(soft) {
  const el = $('onBody'); if (!el) return; const v = onView(), me = frFace(onLook()), note = ON.note ? '<p class="onnote">' + frEsc(ON.note) + '</p>' : ''; let h = '';
  if (v === 'off') h = '<div class="frmsg">' + FR_FACES + '<b>Online play is on the way</b><p>It isn’t switched on in this version yet.</p></div>';
  else if (v === 'connecting') h = '<div class="frmsg"><span class="frspin" aria-hidden="true"></span><p>Connecting…</p></div>';
  else if (v === 'error') h = '<div class="frmsg">' + FR_FACES + '<b>Can’t connect</b><p>' + frEsc(ON.err || 'Can’t reach the game server right now.') + '</p><button class="frb go" data-on="retry" data-f type="button">Try again</button></div>';
  else if (v === 'old') h = '<div class="frmsg">' + FR_FACES + '<b>Update the game to play online</b><p>This version of Roll Model is too old for online play. Update it, then come back.</p></div>';
  else if (v === 'joining') h = '<div class="frmsg"><span class="frspin" aria-hidden="true"></span><p>Joining ' + frEsc(ON.join) + '…</p></div>';
  else if (v === 'found') { const m = ON.match, o = m && (m.players || []).find(p => p.slot !== m.you); h = '<div class="frmsg onwait">' + onVs(me, o ? frFace(o.look) : ON_MYS) + '<b>Match found!</b><p>' + (o ? 'You vs ' + frEsc(o.name) : 'Get ready') + '</p></div>'; }
  else if (v === 'queue') h = note + '<div class="frmsg onwait">' + onVs(me, ON_MYS) + '<b>' + (ON.lost ? 'Reconnecting…' : 'Finding a rival…') + '</b><p class="ontime" id="onTime" role="timer" aria-label="Time looking"></p><p>1v1 against someone at your level.</p><button class="frb ghost" data-on="unq" data-f type="button">Cancel</button></div>' + onInvList();
  else if (v === 'inv') { const i = ON.inv, n = frEsc(i.name), st = ON.lost ? 'Reconnecting…' : i.st === 'sending' ? 'Inviting ' + n + '…' : i.st === 'accepted' ? n + ' is on the way…' : 'Waiting for ' + n + '…';
    h = note + '<div class="frmsg onwait">' + onVs(me, frFace(i.look)) + '<b>' + st + '</b>' + (i.st === 'open' && !ON.lost ? '<p class="ontime" id="onTime" role="timer" aria-label="Time left to answer"></p><p>They’ve got 2 minutes to say yes.</p>' : '<span class="frspin" aria-hidden="true"></span>') + '<button class="frb ghost" data-on="uninv" data-f type="button">Cancel</button></div>' + onInvList(); }
  else if (v === 'room') h = onRoomHtml(note) + onInvList();
  else h = onInvList() + note + '<div class="onhome"><button class="onfind" data-on="find" data-f type="button"><span class="onvs" aria-hidden="true">' + me + ON_MYS + '</span><span><b>Find a match</b><small>1v1 against someone at your level</small></span></button>'
    + '<section class="onfr"><h4>Play a friend</h4><button class="frb onmk" data-on="make" type="button">Make a room</button>'
    + '<form class="fradd onjoin" id="onJoinF" autocomplete="off" novalidate><label for="onCode">Join with a code</label><div><input id="onCode" type="text" inputmode="text" autocapitalize="characters" autocorrect="off" spellcheck="false" enterkeyhint="go" placeholder="Their room code" value="' + frEsc(ON.typed) + '" aria-describedby="onJoinNote"><button class="frb go" type="submit">Join</button></div><p class="frnote bad" id="onJoinNote" aria-live="polite">' + frEsc(ON.jnote) + '</p></form></section></div>';
  if (soft && h === ON.sig) return onClocks(); ON.sig = h;
  const a = document.activeElement, inside = a && el.contains(a), typing = inside && a.id === 'onCode', p0 = typing ? a.selectionStart : 0, p1 = typing ? a.selectionEnd : 0, top = el.scrollTop;
  const key = inside && a.dataset && a.dataset.on ? '[data-on="' + a.dataset.on + '"]' + (a.dataset.id ? '[data-id="' + a.dataset.id + '"]' : '') : '';
  el.innerHTML = h; el.scrollTop = top; onClocks();
  const i = typing && $('onCode');
  if (i) { i.focus({ preventScroll: true }); try { i.setSelectionRange(p0, p1); } catch (e) {} }
  else if (inside && ON.open) { const f = (key && el.querySelector(key)) || el.querySelector('[data-f]') || $('onX'); f.focus({ preventScroll: true }); } // (the same button if it's still there, else what comes next)
}
function onRoomHtml(note) {
  const r = ON.room, my = ON.me && ON.me.id, full = r.players.length >= r.need, me = r.players.find(p => p.id === my), o = r.players.find(p => p.id !== my), c = frEsc(r.code);
  let h = note + '<div class="onroomw"><section class="onroom"><small id="onCodeL">Room code</small><div class="frcode oncode"><b aria-hidden="true">' + c + '</b><span class="onsr">' + c.split('').join(' ') + '</span><button class="frb" data-on="copy" data-f type="button" aria-describedby="onCodeL">Copy</button>'
    + (NATIVE_SHARE ? '<button class="frb" data-on="share" type="button">Share</button>' : '') + '</div><p class="frnote" aria-live="polite">' + frEsc(ON.cnote) + '</p></section>';
  h += '<section class="onwho"><h4>In the room <i>' + r.players.length + '/' + r.need + '</i></h4><ul class="frlist">' + r.players.map(p => '<li class="frrow sm">' + frFace(p.look) + '<span class="frwho"><b>' + frEsc(p.name) + (p.id === my ? '<em class="onyou">You</em>' : '') + '</b><small' + (p.ready ? ' class="onok">Ready' : '>Not ready yet') + '</small></span></li>').join('')
    + (full ? '' : '<li class="frrow sm onslot">' + ON_MYS + '<span class="frwho"><b>Your friend</b><small>Not here yet</small></span></li>') + '</ul></section>';
  const st = ON.lost ? 'Reconnecting…' : !full ? 'Waiting for your friend to join…' : me && !me.ready ? '' : 'Waiting for ' + (o ? o.name : 'your friend') + ' to be ready…';
  return h + (st ? '<p class="onstat"><span class="frspin" aria-hidden="true"></span>' + frEsc(st) + '</p>' : '') + '<div class="onbtns">' + (full && me && !me.ready ? '<button class="frb go" data-on="ready" type="button">' + (ON.again ? 'Play again' : 'Ready') + '</button>' : '') + '<button class="frb ghost" data-on="leave" type="button">Leave</button></div></div>';
}
// the clocks: how long you've been looking, how long your friend has left to answer
function onClocks() {
  const t = ON.queued && !ON.inv ? onClock(Date.now() - ON.queued.at) : ON.inv && ON.inv.st === 'open' ? onClock(120000 - (Date.now() - ON.inv.at)) : '';
  const a = $('onTime'); if (a && a.textContent !== t) a.textContent = t; const b = $('onChipT'); if (b && b.textContent !== t) b.textContent = t;
}
// the lobby with nothing over it: the only place an invite or the chip shows
const onCalm = () => state === 'menu' && !lookOpen && !shopOpen && !irisBusy && $('sideMenu').hidden && !document.querySelector('#stage > .modal:not([hidden])');
const ON_ARR = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 5.5 15.5 12 9 18.5" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>';
function onCard() {
  const st = $('stage'), calm = onCalm(), i = ON.invites[0], show = !!(i && calm && !ON.match); let c = $('onInvCard');
  if (!show) { if (c) c.remove(); }
  else { if (!c) { c = document.createElement('div'); c.className = 'oninv'; c.id = 'onInvCard'; c.setAttribute('role', 'group'); c.setAttribute('aria-label', 'Duel invite'); st.appendChild(c); }
    if (c.dataset.id !== i.id) { const n = frEsc(i.from.name), id = frEsc(i.id); c.dataset.id = i.id; c.innerHTML = frFace(i.from.look) + '<span class="oninvt"><b>' + n + '</b> wants to duel!</span><span class="oninvb"><button class="frb go" data-on="iplay" data-id="' + id + '" type="button" aria-label="Play ' + n + '">Play</button><button class="frb ghost" data-on="inope" data-id="' + id + '" type="button" aria-label="Not now, ' + n + '">Not now</button></span>'; } }
  // while you're queued, in a room or waiting on an invite with the sheet shut: what's going on, and the way back to it
  const busy = !show && calm && !ON.match && ON.net && (ON.queued || ON.room || ON.inv); let ch = $('onChip');
  if (!busy) { if (ch) ch.remove(); return; }
  if (!ch) { ch = document.createElement('button'); ch.type = 'button'; ch.className = 'onchip'; ch.id = 'onChip'; ch.dataset.on = 'open'; st.appendChild(ch); }
  const t = ON.lost ? 'Reconnecting…' : ON.inv ? 'Waiting for ' + ON.inv.name : ON.queued ? 'Finding a rival' : ON.room.players.length < ON.room.need ? 'Room ' + ON.room.code + ' · waiting for your friend' : 'Room ' + ON.room.code;
  const h = '<i class="frst lobby" aria-hidden="true"></i><span>' + frEsc(t) + '</span><b id="onChipT"></b>' + ON_ARR;
  if (ch._h !== h) { ch._h = h; ch.innerHTML = h; ch.setAttribute('aria-label', t + '. Open Online'); onClocks(); }
}
function onAct(a, id) {
  if (a === 'find') onFind(); else if (a === 'unq') { onUnq(); onSay('Stopped looking'); } else if (a === 'make') onMake(); else if (a === 'leave') onLeave(); else if (a === 'copy') onCopy();
  else if (a === 'share') { if (ON.room) nativeSay('device', { share: 'Play me in Roll Model! Join my room with the code ' + ON.room.code }); }
  else if (a === 'ready') { ON.want = true; if (ON.net) ON.net.ready(true); } else if (a === 'retry') { ON.v = ''; onlineOpen(); } else if (a === 'uninv') onInvEnd('');
  else if (a === 'iplay' || a === 'inope') onAnswer(id, a === 'iplay'); else if (a === 'open') onlineOpen();
  else if (a === 'duel') { const f = FR.box && FR.box.friends.find(x => x.id === id); if (f) onlineInvite(f); }
}
// one listener for the sheet, the invite card, the chip and the Duel and invite buttons in Friends
$('stage').addEventListener('click', e => { const b = e.target.closest('[data-on]'); if (!b || b.disabled) return; AU.init(); AU.ui(); onAct(b.dataset.on, b.dataset.id); });
$('onBody').addEventListener('submit', e => { e.preventDefault(); AU.init(); AU.ui(); const i = $('onCode'); if (i) onJoin(i.value); });
$('onBody').addEventListener('input', e => { if (e.target.id !== 'onCode') return; const v = onCodeOf(e.target.value); if (e.target.value !== v) e.target.value = v; ON.typed = v; if (ON.jnote) { ON.jnote = ''; const n = $('onJoinNote'); if (n) n.textContent = ''; } });
$('onX').addEventListener('click', () => { AU.init(); AU.ui(); onlineClose(); }); // (uiClick is defined further down the script)
$('onModal').addEventListener('click', e => { if (e.target === $('onModal')) onlineClose(); });
document.addEventListener('keydown', e => { if (!ON.open) return; if (e.key === 'Escape') { e.preventDefault(); onlineClose(); } e.stopPropagation(); }, true); // (the lobby's keys wait while it's up)
// once a second: the clocks; your invite's 2 minutes; invites to you running out; a connection away 20 s given up on; and the queue or the room let
// go once you're off into a game against the CPU
function onTick() {
  const i = ON.inv, now = Date.now();
  if (i && i.st === 'open' && now - i.at > 124000) onInvEnd('No answer from ' + i.name); // (a yes at the last second still gets here: the next check is up to 3 s off)
  else if (i && i.st === 'accepted' && now - i.acc > 30000) onInvEnd(i.name + ' couldn’t get in. Try again?');
  if (ON.lost && now - ON.lost > 20000 && !ON.match) { onlineDrop(); ON.v = 'error'; ON.err = onOffline() ? 'You’re offline. Online play comes back when you are.' : 'Lost the connection to the game server.'; onUpd(); }
  if (ON.after && state === 'menu') onAfter();
  if (state !== 'menu' && !ON.match && ON.net && (ON.queued || ON.room || ON.inv)) onlineDrop();
  if (ON.invites.length) { const t = now + FR.skew, l = ON.invites.filter(x => Date.parse(x.expires) > t); if (l.length !== ON.invites.length) { ON.invites = l; onUpd(); if (FR.open) frRender(); } }
  onCard(); onClocks();
}
setInterval(onTick, 1000);
const onModalEl = $('onModal');
"""

def apply(s):
    url = net_url()
    # the SDK, before the game's script
    a = '<script src="three.r186.min.js"></script>\n'
    s = rep(s, a, a + "<script>\n// (v306) RMNet, the game server's SDK: server/client/rmnet.js as it is, less its export line. It sets window.RMNet\n" + sdk() + '</script>\n')
    # the Online sheet, after Friends
    a = '  <div class="modal" id="docModal" hidden>\n'
    s = rep(s, a, HTML + a)
    a = "@media (prefers-reduced-motion:reduce){.frspin{animation-duration:2.5s}.frtoast,#friendsBtn .frdot{animation:none}}\n"
    s = rep(s, a, a + CSS.lstrip('\n'))
    # the lobby's side of it, after the Friends client it builds on (sbRpc, FR, frFace...)
    a = "if (SB_CFG) $('ttModal').classList.add('frlive');\n"
    s = rep(s, a, a + JS.replace('__NET_URL__', url).lstrip('\n'))
    # Friends: a Duel button on a friend in the lobby, invites at the top of what's waiting for you, the inbox read for them, and its pace
    s = rep(s, """    + '<span class="frbtns"><button class="frb ghost ic" data-act="more" data-id="' + f.id + '\"""",
               """    + '<span class="frbtns">' + onDuelBtn(f) + '<button class="frb ghost ic" data-act="more" data-id="' + f.id + '\"""")
    s = rep(s, "    if (b.incoming.length) h += '<section><h4>Want to be friends <i>'",
               "    if (NET_URL) h += onInvList(); // (v306: duel invites)\n    if (b.incoming.length) h += '<section><h4>Want to be friends <i>'")
    s = rep(s, 'frSeen(b); frBadge(); ', 'frSeen(b); onInbox(b); frBadge(); ')
    s = rep(s, "  if (Date.now() - FR.at > (FR.open ? 6000 : state === 'menu' ? 20000 : 60000)) frPoll();",
               "  if (Date.now() - FR.at > onPollGap()) frPoll(); // (v306: quicker with a friend online, and while an invite waits)")
    # the lobby holds still behind the Online sheet too
    s = rep(s, "|| !friendsModalEl.hidden))) renderFrame();", "|| !friendsModalEl.hidden || !onModalEl.hidden))) renderFrame();")
    return s
