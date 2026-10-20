"""v391: parties. The + spots beside you in the lobby invite friends; up to three join you, for a party of four.

Built on the party work made around v312 (docs/party-v312.md), brought onto today's lobby and Friends page. Applied last. It takes
the place of v306's online layer (from its "(v306) Online: matchmaking, private rooms and duel invites" comment to just before
onModalEl), keeping the names the match module uses (ON, onlineOpen, onlineAfterMatch, onUpd, onLook, onInbox...).

- The + spots. Tapping a + beside you opens the invite picker: your friends, online ones first, each with Invite. Once both spots
  beside you hold someone (or an invite on its way) a third + appears, so three friends can come: a party of four. Until Play
  online opens (rank 2, Strokes seen, as v359 has it) a + says when it opens.
- An invite. Made in Supabase (rm_invite: friends only, blocks honoured, 2 minutes), passed on live by the game server. The friend's
  game rings: a card at the top of the lobby (Join, Not now), a count on the inbox bell beside the menu button, and a two-note chime.
  Their spot in your lobby shows their face and the time left. With the game closed, their iPhone gets a notification (the game
  server sends it, with the APNs key it has); tapping it opens the game on the invite.
- In a party. Each friend stands in a + spot as their own character (paint, eyes, wearables), with a name plate under them: a crown
  for the leader, a tick when ready, and where they are (In the locker, In the shop...). The foot of the lobby is the party's: Leave
  (the door), the mode vote (the modes that fit the party; most votes win, the leader breaks a tie), reactions, and the big button
  is Ready. Everyone ready: a moment to back out, then the match (two play a Versus of their own) or the search. Opening the locker,
  the shop, Strokes or Settings un-readies you, and so does a new look. The leader taps a plate to remove someone.
- Friends: Invite takes the place of Duel on each friend (In party, Invited). Party invites sit at the top of the sheet. Duel and the
  room codes are gone.
- Notifications: the first time you invite someone or join a party, a card offers a nudge when a friend invites you with the game
  closed; only a yes brings up iOS's own question. The app's token is kept with your account (rm_push_token), and let go of when
  you log out.
- The connection is kept while you're signed in to an account in the lobby, so invites arrive at once: a heartbeat every 20 s while
  it only waits, two pings a second in a queue or a match; closed when the app goes to the background (the party keeps your place a
  minute)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

BELL = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3.2c-3.3 0-5.6 2.5-5.6 5.8v3.4L4.6 15.6c-.4.7.1 1.5.9 1.5h13c.8 0 1.3-.8.9-1.5l-1.8-3.2V9c0-3.3-2.3-5.8-5.6-5.8Z" fill="#fff" stroke="#171320" stroke-width="1.6" stroke-linejoin="round"/><path d="M9.6 18.6a2.5 2.5 0 0 0 4.8 0" fill="none" stroke="#fff" stroke-width="2.2" stroke-linecap="round"/></svg>'
PLUS = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 5v14M5 12h14" stroke="#171320" stroke-width="6.6" stroke-linecap="round"/><path d="M12 5v14M5 12h14" stroke="#fff" stroke-width="3.8" stroke-linecap="round"/></svg>'
DOOR = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M13 4H6.5v16H13" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linejoin="round"/><path d="M11 12h9m-3.2-3.4L20.2 12l-3.4 3.4" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></svg>'
SMILE = '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="8.6" fill="none" stroke="currentColor" stroke-width="2.4"/><circle cx="9" cy="10.2" r="1.4" fill="currentColor"/><circle cx="15" cy="10.2" r="1.4" fill="currentColor"/><path d="M8.4 14.2q3.6 3.6 7.2 0" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/></svg>'
XSVG = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6.5 6.5l11 11M17.5 6.5l-11 11" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round"/></svg>'

# the invite picker and the inbox: the Friends page's graph-paper sheet (v326), rising over the lobby
SHEETS = r"""  <div class="modal ttm pyshm" id="pkModal" hidden><div class="pysh" role="dialog" aria-modal="true" aria-labelledby="pkTitle">
    <div class="frshd"><h2 class="frsht" id="pkTitle">Invite friends</h2><i class="frcnt" id="pkSub">1/4</i><button class="pyx" id="pkX" type="button" aria-label="Close">__X__</button></div>
    <div class="frbody frscroll" id="pkBody"></div>
  </div></div>
  <div class="modal ttm pyshm" id="ibModal" hidden><div class="pysh" role="dialog" aria-modal="true" aria-labelledby="ibTitle">
    <div class="frshd"><h2 class="frsht" id="ibTitle">Inbox</h2><button class="pyx" id="ibX" type="button" aria-label="Close">__X__</button></div>
    <div class="frbody frscroll" id="ibBody"></div>
  </div></div>
""".replace('__X__', XSVG)

DOCK = r"""          <div class="pydock" id="pyDock" hidden>
            <button class="pyround" id="pyLeave" data-py="leave" type="button" aria-label="Leave the party">__DOOR__</button>
            <div class="pymodes" id="pyModes" role="radiogroup" aria-label="Vote for a mode"></div>
            <button class="pyround" id="pyReactBtn" data-py="emo" type="button" aria-label="Reactions" aria-haspopup="menu" aria-expanded="false">__SMILE__</button>
            <div class="pyemo" id="pyEmo" role="menu" aria-label="Reactions" hidden></div>
          </div>
""".replace('__DOOR__', DOOR).replace('__SMILE__', SMILE)

CSS = r"""
/* (v391) parties: the inbox bell by the menu button, the party's name plates and reactions in the lobby, its dock (Leave, the mode
   vote, reactions) beside the Ready button, the + spots, and the invite picker and the inbox as the Friends page's sheet */
.mbtn.ibbell svg{width:23px;height:23px;filter:drop-shadow(0 1.5px 0 rgba(23,19,32,.45))}
.mbtn.ibbell.ring svg{animation:ibring .9s cubic-bezier(.3,1.4,.5,1)}
@keyframes ibring{15%{rotate:16deg}30%{rotate:-14deg}45%{rotate:10deg}60%{rotate:-6deg}75%{rotate:3deg}}
.ibdot{position:absolute;top:-8px;right:-8px;z-index:2;min-width:21px;height:21px;box-sizing:border-box;padding:0 5px;border-radius:999px;background:#E3122F;color:#fff;font:800 12px/21px var(--font-ui);text-align:center;box-shadow:0 0 0 2.5px #171320;animation:frpop .35s cubic-bezier(.3,1.6,.5,1)}
.ibdot[hidden]{display:none}
.pylayer{position:absolute;inset:0;z-index:3;pointer-events:none;overflow:hidden}
.pylayer[hidden]{display:none}
.pyplate{position:absolute;left:0;top:0;display:flex;align-items:center;gap:4px;max-width:118px;box-sizing:border-box;padding:4px 9px 4px 5px;border:0;border-radius:999px;background:#171320;color:#FFF8EA;font:800 12px/1.05 var(--font-ui);white-space:nowrap;box-shadow:0 3px 0 rgba(23,19,32,.22);pointer-events:auto;cursor:default;will-change:transform;-webkit-tap-highlight-color:transparent}
.pyplate[hidden]{display:none}
.pyplate .pyn{display:grid;min-width:0;gap:1px}
.pyplate b{overflow:hidden;text-overflow:ellipsis;font-weight:800}
.pyplate .pyst{flex:none;display:grid;place-items:center;width:16px;height:16px;border-radius:50%;background:rgba(255,248,234,.2);font:900 10px/1 var(--font-ui);font-style:normal}
.pyplate.ready{background:#2E9E48}.pyplate.ready .pyst{background:#fff;color:#2E9E48}
.pyplate.busy{background:#B86A14}.pyplate.away{background:#6E6680}
.pyplate small{font:700 9.5px/1 var(--font-ui);opacity:.9;text-transform:uppercase;letter-spacing:.04em;white-space:nowrap}
.pyplate.busy,.pyplate.away{border-radius:12px}
.pyplate .pycrown{flex:none;width:15px;height:15px;margin-right:-1px}
.pyplate.me{z-index:1;box-shadow:0 0 0 2px var(--ink,#E3122F),0 3px 0 rgba(23,19,32,.22)}
.pyplate.tap{cursor:pointer}
.pymenu{position:absolute;left:0;top:0;z-index:4;display:grid;gap:6px;min-width:150px;padding:10px;border-radius:14px;background:#171320;color:#FFF8EA;box-shadow:0 8px 22px rgba(0,0,0,.4);pointer-events:auto;font:700 13px/1.25 var(--font-ui);text-align:center;animation:frin .25s cubic-bezier(.2,1.3,.4,1) both}
.pymenu .frb{min-height:36px}.pymenu .frb.ghost{background:rgba(255,248,234,.14);color:#FFF8EA}
.pybub{position:absolute;left:0;top:0;display:grid;place-items:center;min-width:44px;height:44px;box-sizing:border-box;padding:0 8px;border-radius:16px;background:#fff;box-shadow:0 0 0 2.5px #171320,0 5px 0 rgba(23,19,32,.25);font:400 27px/1 var(--font-ui);will-change:transform;pointer-events:none}
.pybub::after{content:"";position:absolute;left:50%;bottom:-8px;width:13px;height:13px;margin-left:-7px;background:#fff;box-shadow:2.5px 2.5px 0 #171320;transform:rotate(45deg) skew(8deg,8deg)}
.pybub b{font:400 20px/1 var(--font-display);color:#171320;letter-spacing:.02em}
.pybub{animation:pybubo 2.1s linear both}
.pybub i{display:block;font-style:normal;animation:pybub 2.1s cubic-bezier(.2,1.4,.4,1) both}
@keyframes pybubo{0%{opacity:0}10%{opacity:1}84%{opacity:1}100%{opacity:0}}
@keyframes pybub{0%{transform:scale(.2) translateY(14px)}14%{transform:scale(1.12)}24%{transform:scale(1)}82%{transform:scale(1)}100%{transform:scale(.8) translateY(-8px)}}
.slot.inv{background:rgba(255,255,255,.75)}
.slot.inv .frface{width:34px;height:34px;transform:skewX(8deg)}
.slot.inv b{position:absolute;left:50%;bottom:-17px;transform:translateX(-50%) skewX(8deg);padding:2px 6px;border-radius:999px;background:#171320;color:#FFF8EA;font:800 10.5px/1.1 var(--font-ui);font-variant-numeric:tabular-nums;white-space:nowrap}
.slot.lk svg{opacity:.45}
.pydock{position:relative;display:grid;grid-template-columns:auto minmax(0,1fr) auto;align-items:center;gap:8px;padding:0 4px}
.pydock[hidden]{display:none}
.pyround{appearance:none;display:grid;place-items:center;width:46px;height:46px;margin:0;padding:0;border:0;border-radius:50%;background:linear-gradient(180deg,#4F4A69 0%,#38334E 58%,#2B273D 100%);color:#fff;box-shadow:0 0 0 2.5px #171320,inset 0 2px 0 rgba(255,255,255,.2),inset 0 -3px 0 rgba(0,0,0,.25),0 4px 0 #171320;cursor:pointer;-webkit-tap-highlight-color:transparent}
.pyround svg{width:24px;height:24px}.pyround:active{transform:translateY(3px)}
.pyround:focus-visible,.pymode:focus-visible{outline:3px solid var(--gold);outline-offset:3px}
.pymodes{display:grid;grid-template-columns:repeat(var(--n,3),minmax(0,1fr));gap:7px}
.pymode{appearance:none;position:relative;display:grid;justify-items:center;align-content:center;gap:3px;min-width:0;min-height:56px;margin:0;padding:6px 3px 5px;border:0;border-radius:3px;cursor:pointer;color:#171320;
  background:url(art/m_cpaper_g.webp) center/180px,#F4EEE3;background-blend-mode:multiply;box-shadow:inset 0 0 0 1px rgba(0,0,0,.08),3px 4px 0 rgba(0,0,0,.35);rotate:-.6deg;transition:transform .12s ease}
.pymode:nth-child(2){rotate:.5deg}.pymode:active{transform:scale(.95)}
.pymode b{font:400 13px/1 var(--font-display);text-transform:uppercase;letter-spacing:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:100%}
.pymode small{font:800 9.5px/1 var(--font-ui);letter-spacing:.06em;text-transform:uppercase;opacity:.62;white-space:nowrap}
.pymode[aria-checked="true"]{box-shadow:inset 0 0 0 2.5px #171320,3px 4px 0 rgba(0,0,0,.35)}
.pymode.win{background:url(art/m_cpaper_g.webp) center/180px,#FFD24A;background-blend-mode:multiply}
.pymode.win::before{content:"";position:absolute;top:-6px;left:50%;width:12px;height:12px;margin-left:-6px;border-radius:50%;background:#2E9E48;box-shadow:0 0 0 2px #171320}
.pymode:disabled{cursor:default;opacity:.62;filter:saturate(.4)}
.pymode .pysoon{position:absolute;right:-5px;top:-7px;padding:2px 5px 2px;background:#171320;color:#FFF8EA;font:800 8.5px/1 var(--font-ui);letter-spacing:.06em;text-transform:uppercase;rotate:4deg}
.pyvotes{display:flex;justify-content:center;gap:2px;height:11px}
.pyvotes i{width:11px;height:11px;border-radius:50%;background:var(--c,#999);box-shadow:0 0 0 1.5px #171320}
.pyemo{position:absolute;right:0;bottom:calc(100% + 12px);z-index:5;display:grid;grid-template-columns:repeat(4,46px);gap:6px;padding:8px;border-radius:16px;background:#171320;box-shadow:0 8px 22px rgba(0,0,0,.4);animation:frin .25s cubic-bezier(.2,1.3,.4,1) both}
.pyemo[hidden]{display:none}
.pyemo button{appearance:none;display:grid;place-items:center;width:46px;height:46px;margin:0;padding:0;border:0;border-radius:12px;background:rgba(255,248,234,.1);font:400 26px/1 var(--font-ui);cursor:pointer}
.pyemo button b{font:400 17px/1 var(--font-display);color:#FFF8EA}
.pyemo button:active{transform:scale(.9)}
.mhome.lobby.inparty .playbtn{flex-direction:column;gap:3px}
.mhome.lobby.inparty .playbtn .pbl{white-space:nowrap}
.playbtn .pysub{display:block;font:800 11px/1 var(--font-ui);letter-spacing:.06em;text-transform:uppercase;opacity:.92;white-space:nowrap}
.playbtn .pysub:empty{display:none}
.playbtn.pyready{filter:saturate(.25) brightness(1.08)}
.playbtn.pygo{filter:hue-rotate(95deg) saturate(.9)}
.onhome.onpick{grid-template-columns:minmax(0,1fr);gap:14px}
.ongrid{display:grid;grid-template-columns:minmax(0,1fr);gap:20px;padding:12px 6px 4px 4px}
.onev .evbar{background:#171320}
.onev div.evmain{cursor:default}.onev div.evmain:hover,.onev div.evmain:active{transform:skewX(-5deg)}
.onev.soon div.evmain{cursor:pointer}
.onev .evmain:disabled{cursor:default}.onev .evdrop button:disabled{opacity:.45;cursor:default}
.onhint.onnear{margin-top:-4px}
.onev .evdrop b{font-size:17px;white-space:nowrap}
@media (max-aspect-ratio:1/1){.pymodes.n3 .pymode{padding-left:2px;padding-right:2px}.pymodes.n3 .pymode b{font-size:clamp(9px,calc((100vw - 170px) / 20.5),13px);letter-spacing:-.02em}.pymodes.n3 .pymode small{font-size:8.5px;letter-spacing:.03em}}
.onwait .onmd{font:800 11px/1 var(--font-ui);letter-spacing:.08em;text-transform:uppercase;color:#6E6680}
.onvs .onmys+.onmys{margin-left:-8px}
@media (min-aspect-ratio:1/1) and (max-height:600px){.onhome.onpick{grid-template-columns:minmax(0,1fr);gap:8px}.ongrid{grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:14px 20px;padding-top:10px}
  .onhome.onpick .onfr{grid-template-columns:auto auto minmax(0,1fr);align-items:center;gap:12px}.onhome.onpick .onfr h4{margin:0}.onhome.onpick .onfr .onhint{text-align:left}}
.onhint{margin:0;font:700 12.5px/1.35 var(--font-ui);color:#6E6680;text-align:center}
.frb.pkon{background:rgba(23,19,32,.07);color:var(--black);box-shadow:none}
.pysh .frrow.pkcan{cursor:pointer;-webkit-tap-highlight-color:transparent}.pysh .frrow.pkcan:active{transform:translateY(2px)}
.ibtime{font-variant-numeric:tabular-nums}
/* the sheet: the Friends page's graph paper, taped at the top, over the lobby (from the bottom upright, down the right sideways) */
.modal.pyshm{place-items:end center;padding:0}
.pysh{--ink0:#111014;--gx:max(16px,env(safe-area-inset-left));--gr:max(16px,env(safe-area-inset-right));--gb:env(safe-area-inset-bottom,0px);position:relative;display:flex;flex-direction:column;box-sizing:border-box;width:100%;max-width:560px;height:min(76%,620px);padding:24px var(--gr) 0 var(--gx);border-radius:26px 26px 0 0;
  background:#F6F1E8 url(art/m_paperbg.webp) center/420px;box-shadow:0 -10px 30px rgba(23,19,32,.22);color:var(--black);text-align:left;animation:pyshin .3s cubic-bezier(.2,1.1,.4,1) both}
@keyframes pyshin{from{transform:translateY(40%);opacity:0}}
.pysh::before{content:"";position:absolute;left:50%;top:-15px;width:120px;height:32px;margin-left:-60px;background:url(art/m_tape3.webp) center/100% 100% no-repeat;transform:rotate(2deg);filter:drop-shadow(0 1px 0 rgba(23,19,32,.15))}
.pysh .frshd{flex:none;display:flex;align-items:center;gap:10px;min-width:0;padding:0 2px 12px}
.pysh .frsht{margin:0;font:900 26px/.95 var(--font-head);text-transform:uppercase;letter-spacing:0;color:var(--black);white-space:nowrap;transform:skewX(-6deg);text-shadow:.04em .04em 0 #FFF8EA,.08em .08em 0 var(--black)}
.pysh .frcnt{flex:none;font-style:normal;padding:4px 9px 3px;border-radius:999px;background:var(--ink0);color:#fff;font:400 14px/1 var(--font-display)}
.pysh .pyx{appearance:none;flex:none;display:grid;place-items:center;width:40px;height:40px;margin:-4px 0 0 auto;padding:0;border:0;border-radius:50%;background:var(--ink0);color:#fff;box-shadow:0 3px 0 rgba(0,0,0,.3);cursor:pointer}
.pysh .pyx svg{width:18px;height:18px}.pysh .pyx:active{transform:translateY(2px)}
.pysh .frscroll{flex:1 1 auto;min-height:0;margin:0;overflow-x:hidden;overflow-y:auto;overscroll-behavior:contain;display:grid;grid-template-columns:minmax(0,1fr);align-content:start;gap:16px;padding:2px 2px calc(var(--gb) + 24px);-webkit-overflow-scrolling:touch}
.pysh .frscroll>*{min-width:0}
.pysh .frlist{gap:10px;margin-top:8px}
.pysh .frrow{min-height:58px;padding:7px 10px;border:0;border-radius:12px;background:#FFFDF7;box-shadow:inset 0 0 0 1.5px rgba(23,19,32,.1),3px 4px 0 rgba(23,19,32,.13)}
.pysh .frmsg{min-height:180px}
.pysh .frfine{padding:0 2px}
.pysh .onnote{margin:0 2px}
@media (min-aspect-ratio:1/1){.modal.pyshm{place-items:stretch end}.pysh{width:min(58vw,470px);max-width:none;height:auto;margin-top:max(8px,env(safe-area-inset-top));padding-top:20px;border-radius:26px 0 0 0;animation-name:pyshins}}
@keyframes pyshins{from{transform:translateX(40%);opacity:0}}
@media (min-aspect-ratio:1/1) and (max-height:600px){.pymode{min-height:48px}.pyround{width:42px;height:42px}.pydock{gap:7px}}
@media (prefers-reduced-motion:reduce){.pybub,.pybub i,.mbtn.ibbell.ring svg,.ibdot,.pysh{animation:none}}
"""

JS = r"""
// ---------- (v391) Online: parties of up to four friends, invites (made in Supabase, passed on live by the game server, and as a
// notification on a friend's iPhone when their game is closed) and the inbox, and matchmaking that looks near first (the server's).
// It takes the place of v306's rooms and duel invites. What the match module reads, in ON (these names stay): ON.net (the
// connection, or null), ON.me (its welcome), ON.queued (null, or { mode, at, party } while matchmaking), ON.match (the matchFound
// message, from then until onlineAfterMatch()), ON.open (the Online sheet is up), ON.v / ON.err (the sheet's state); and onLook(),
// onName(), onUpd(), onlineOpen(), onlineClose(), onlineAfterMatch(). ON.party: the game server's view of your party
// ({ id, code, leader, max, state, mode, modes, members, invites }) ----------
const NET_URL = (() => { let u = 'wss://rollmodel-game.fly.dev/ws'; try { const o = window.__net || localStorage.getItem('rm.net'); if (o) u = String(o); } catch (e) {} // (a test server, for development)
  return /^(wss:\/\/|ws:\/\/(localhost|127\.0\.0\.1)[:/])[^\s"'<>\\]*$/.test(u) ? u : ''; })();
const ON = { net: null, me: null, queued: null, room: null, match: null, inv: null, invites: [], open: false, gate: null, party: null,
  v: '', err: '', note: '', lost: 0, cp: null, cpEnd: null, ret: null, foundT: 0, unq: 0, qAt: 0, off: false, after: false, retryAt: 0, fails: 0, stale: 0,
  asleep: false, busy: null, lookSent: '', cpu: false, mode: (typeof store === 'object' && store && store.onMode) || 'duel', nope: new Set(), seen: new Set(), sent: new Map(), sig: '', pick: '', later: '' };
// the modes, as the game names them: [server mode, name, under it]
const PY_MODES = [['duel', 'Versus', '1v1'], ['ffa', 'Showdown', 'Free-for-all'], ['duo', '2v2', 'Teams']];
const PY_FULL = { duel: 'Versus', ffa: 'Showdown', duo: 'Showdown 2v2' }; // (the name on its own, as the Online sheet says it)
const PY_EMO = [['wave', '👋'], ['laugh', '😂'], ['wow', '😮'], ['love', '😍'], ['cool', '😎'], ['cry', '😭'], ['angry', '😠'], ['gg', '<b>GG</b>']];
const PY_BUSY = { locker: 'In the locker', shop: 'In the shop', strokes: 'In Strokes', settings: 'In Settings', cpu: 'Playing the CPU', menu: 'Busy' };
// your look as the others see it: paint, eyes, rank, and what you're wearing (only the slots in use; well under the server's 512 bytes)
function onLook() { const w = {}; for (const k of PT_SLOTS) if (myLook[k]) w[k] = myLook[k]; w.iris = myLook.iris; return { c: colorId, e: myLook.eyes, r: frRank(), w }; }
// your name online: your account's username
const onName = () => (typeof acName === 'function' && acName()) || frName();
const onE = (code, src) => Object.assign(new Error(code), { code, why: src && (src.message || src.reason) });
const onOffline = () => typeof navigator !== 'undefined' && navigator.onLine === false;
const onClock = ms => { const s = Math.max(0, Math.round(ms / 1000)); return Math.floor(s / 60) + ':' + String(s % 60).padStart(2, '0'); };
const onZone = () => { try { return Intl.DateTimeFormat().resolvedOptions().timeZone || null; } catch (e) { return null; } };
const sbUid = () => (FR.s && FR.s.uid) || (store.sbs && store.sbs.uid) || null;
const onAcct = () => typeof acctReady === 'function' && acctReady();
function onSay(t) { const el = $('onLive'); if (!el) return; el.textContent = ''; setTimeout(() => { el.textContent = t; }, 60); } // (for screen readers: what just happened)
// in a party with someone (a party of one is just you, with invites out)
const ptOn = () => !!(ON.party && ON.party.members.length > 1);
// someone with you in the lobby, or on the way (an invite out): the spots take the party's places, and the camera steps back
const ptCrowd = () => !!(ON.party && (ON.party.members.length > 1 || ON.party.invites.some(i => i.exp > Date.now())));
const ptMe = () => { const p = ON.party, id = ON.me && ON.me.id; return p && id ? p.members.find(m => m.id === id) || null : null; };
// playing with friends opens with Play online (v359: rank 2, and the Strokes page seen); until then a word on when
const ptLockText = () => repOf(store.xp || 0).lv < ABIL_RANK ? 'Reach rank ' + ABIL_RANK + ' to play with friends' : 'Open Strokes in the lobby to play with friends';
function ptLocked() { if (mpOpen()) return false; AU.nope(); buzz(8); frToast('<span>' + ptLockText() + '</span>'); return true; }
// ---- the connection: kept while you're signed in to an account in the lobby (so an invite gets here at once), and while you're
// in a party, a queue or a match; let go when the app goes to the background (the party keeps your place for a minute)
const onWant = () => !!NET_URL && !document.hidden && !ON.asleep && (!!ON.match || !!ON.queued || ON.open || !!ON.party || (state === 'menu' && onAcct()));
// a heartbeat while it only waits (a phone's radio can rest); two pings a second in a queue, a starting party or a match
const onBusy = () => !!(ON.match || ON.queued || (ON.party && ON.party.state !== 'idle'));
function onBeat() { const b = onBusy() ? 500 : 20000; if (ON.net) ON.net.setBeat(b); return b; }
function onlineConnect() {
  if (!NET_URL || typeof RMNet !== 'function') return Promise.reject(onE('off'));
  if (ON.net && ON.net.connected && ON.me) return Promise.resolve(ON.net);
  if (ON.cp) return ON.cp;
  ON.asleep = false;
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
  const net = new RMNet({ url: NET_URL, name: onName(), look: onLook(), token: store.netTok || null, client: 'rm-391', sb: sbUid(), zone: onZone(), beat: onBusy() ? 500 : 20000 });
  const on = (ev, fn) => net.on(ev, d => { if (ON.net === net) fn(d || {}); }); // (a connection let go says nothing more)
  ON.net = net; ON.me = null; ON.lookSent = JSON.stringify(net.look);
  on('token', t => { if (t.token && t.token !== store.netTok) { store.netTok = t.token; save(); } }); // (who you are on the server, so your rating stays yours)
  on('welcome', w => { ON.me = w; ON.fails = 0; ON.stale = ON.party ? Date.now() + 2500 : 0; onBack(); });
  on('close', e => { ON.me = null; net.name = onName(); net.look = onLook(); net.sb = sbUid(); if (e.willReconnect) onLost(); }); // (the next hello says who you are now)
  on('queued', m => { ON.queued = { mode: m.mode || 'duel', at: ON.queued ? ON.queued.at : (m.requeued && ON.qAt) || Date.now(), party: !!m.party }; onBeat(); onUpd(); });
  on('queueLeft', () => { ON.queued = null; ON.cpu = false; onBeat(); onUpd(); });
  on('party', ptView); on('partyLeft', ptLeft); on('react', m => ptBubble(m.id, m.e)); on('poke', onPoke);
  on('partyNote', m => { if (m.k !== 'declined') return; const k = m.to && ON.sent.get(m.to); if (k) { if (k.told) return; k.told = true; } if (state === 'menu') frToast('<span><b>' + frEsc(hdOf(m.name)) + '</b> can’t play right now</span>'); }); // (once: the inbox may say it too)
  on('matchFound', onFound); on('resume', onResume); on('matchCancelled', onCalledOff); on('fatal', onFatal);
  on('error', e => { if (e.code === 'handler') console.error('online: ' + e.message); }); // (the SDK catches what a handler throws)
  return net;
}
// let go of the connection (and with it the queue and the party, which the server lets go of too, a minute later)
function onlineDrop() {
  const n = ON.net, end = ON.cpEnd; ON.net = null; ON.me = null; ON.cp = null; ON.cpEnd = null; ON.queued = null; ON.party = null; ON.lost = 0; ON.stale = 0; ON.cpu = false;
  if (end) end(onE('closed')); if (n) n.close(); ptRender();
}
// the app went to the background: the connection goes (a match keeps it: the server holds your place there itself)
function onlineSleep() {
  if (ON.match || !ON.net) return; const n = ON.net, end = ON.cpEnd;
  ON.asleep = true; ON.net = null; ON.me = null; ON.cp = null; ON.cpEnd = null; ON.queued = null; ON.lost = 0;
  if (end) end(onE('closed')); n.close();
}
function onlineWake() { if (!ON.asleep) return; ON.asleep = false; if (onWant()) onlineConnect().catch(() => {}); }
document.addEventListener('visibilitychange', () => { if (document.hidden) onlineSleep(); else onlineWake(); });
// the connection dropped and the SDK is getting it back
function onLost() { if (!ON.match && (ON.queued || ON.party)) { ON.lost = ON.lost || Date.now(); onUpd(); } }
// back (or the first time): a queue taken up again (the server let go of it); a party comes back by itself
async function onBack() {
  const lost = ON.lost, net = ON.net; ON.lost = 0; onBeat();
  if (ON.busy && ON.party) net.partyBusy(ON.busy).catch(() => {});
  if (!lost || ON.match) return onUpd();
  try { if (ON.queued && !ON.queued.party) await net.queue(ON.queued.mode); } catch (e) { if (ON.net !== net) return; ON.queued = null; ON.note = 'The connection dropped. Try again.'; }
  onUpd();
}
// refused for good (an old game, or another screen took over): no more tries
function onFatal(e) {
  if (ON.match) return; // (the match module's)
  const old = e.code === 'version'; ON.v = old ? 'old' : 'error';
  ON.err = e.code === 'kicked' && e.message === 'replaced' ? 'You’re playing online on another screen.' : e.code === 'banned' ? 'This device can’t play online.' : 'The game server turned the connection down.';
  ON.retryAt = e.message === 'replaced' ? Infinity : Date.now() + 60000; // (another screen took over: not back until you ask)
  onlineDrop(); onUpd(); if (!ON.open && !old && state === 'menu' && e.message !== 'replaced') frToast('<span>' + frEsc(ON.err) + '</span>');
}
// the connection for an action, with "Connecting…" while it comes up; null (and the error showing) if it doesn't
async function onNet() {
  if (!(ON.net && ON.net.connected && ON.me) && !ON.v) { ON.v = 'connecting'; onRender(); }
  try { const n = await onlineConnect(); if (ON.v === 'connecting') { ON.v = ''; onUpd(); } return n; } catch (e) { onFail(e); return null; }
}
function onFail(e) {
  if (!e || e.code === 'closed' || e.code === 'off') return;
  ON.v = e.code === 'old' ? 'old' : 'error'; ON.err = NET_WALLED ? 'Online play works in the Roll Model app, not in this preview.' : e.code === 'offline' || onOffline() ? 'You’re offline. Online play comes back when you are.' : 'Can’t reach the game server right now.'; onUpd();
}
const onReqText = e => e && e.code === 'timeout' ? 'The game server didn’t answer. Try again.' : e && e.code === 'disconnected' ? 'Lost the connection. Try again.' : e && e.status ? frErrText(e) : 'Something went wrong. Try again.';
const onParties = () => !!(ON.me && Array.isArray(ON.me.caps) && ON.me.caps.includes('party'));
const onModeOn = m => !!(ON.me ? (ON.me.partyModes || ['duel']).includes(m) : m === 'duel');
// ---- matchmaking (on your own): the server looks near you first, then further, then anywhere; nobody waits long
async function onFind(m) {
  ON.note = ''; if (PY_FULL[m] && m !== ON.mode) { ON.mode = m; store.onMode = m; save(); }
  const net = await onNet(); if (!net) return; const mode = ON.mode;
  if (!onModeOn(mode)) { ON.note = PY_FULL[mode] + ' online is coming next. Versus is on now.'; return onRender(); }
  if (ptOn()) { onlineClose(); return frToast('<span>Your party plays together: vote and ready up in the lobby</span>'); }
  try { ON.unq = 0; ON.cpu = false; ON.queued = { mode, at: Date.now() }; onUpd(); onBeat(); await net.queue(mode); onSay('Finding players'); }
  catch (e) { ON.queued = null; ON.note = e.code === 'busy' ? 'Your party plays together: vote and ready up in the lobby.' : onReqText(e); onUpd(); }
}
async function onUnq() { const net = ON.net; ON.unq = Date.now(); ON.queued = null; ON.cpu = false; onUpd(); onBeat(); try { if (net) await net.cancelQueue(); } catch (e) {} }
// nobody around after 30 s: a match against the CPU instead (never a pretend person)
function onCpu() {
  const q = ON.queued ? ON.queued.mode : 'duel', m = q !== 'duel' && typeof evUnlocked === 'function' && evUnlocked() ? q : 'duel';
  onUnq(); onlineClose(); if (menuPage === 'events') closeEvents(); if (mode !== m) setMode(m); setTimeout(() => { if (state === 'menu') start(); }, 120);
}
// ---- a match: the match module takes it from here
function onFound(m) {
  const net = ON.net;
  // found just as you cancelled, or once you'd gone into a game against the CPU: let it go (the others go back in the queue)
  if ((state !== 'menu' && !ON.match) || (!ptOn() && ON.unq && Date.now() - ON.unq < 3000)) { net.leaveMatch().catch(() => {}); return; }
  clearTimeout(ON.foundT); ON.foundT = 0; if (ON.queued) ON.qAt = ON.queued.at;
  ON.match = m; ON.queued = null; ON.lost = 0; ON.note = ''; ON.off = false; ON.after = false; ON.cpu = false; onBeat();
  if (FR.open) closeFriends(); pkClose(); ibClose(); ptEmo(false); ptMenuClose(); noteClose();
  if (typeof window.netMatchFound === 'function') { ON.v = ''; onlineClose(); onCard(); ptRender(); try { window.netMatchFound(m, net); } catch (e) { frameErr(e); } return; }
  ON.v = 'found'; if (!onlineOpen()) onRender(); AU.ready(); buzz([10, 30, 10]); onSay('Match found!');
  ON.foundT = setTimeout(onFoundEnd, 2000);
}
// (a stand-in until the match module is in) out of the match, and back to the start
async function onFoundEnd() { const net = ON.net; ON.foundT = 0; if (ON.v !== 'found') return; ON.match = null; try { if (net && net.match) await net.leaveMatch(); } catch (e) {} ON.v = ''; onUpd(); }
// called off before it began: back where you were, with a word. Once the match screen has taken over it's the match module's
function onCalledOff(m) {
  const was = ON.match; if (!was || (m.matchId && was.matchId !== m.matchId)) return;
  if (state !== 'menu') { ON.off = true; return; }
  clearTimeout(ON.foundT); ON.foundT = 0; ON.match = null; ON.v = ''; ON.note = 'The match was called off'; AU.nope(); onSay(ON.note);
  setTimeout(() => { if (!ON.match) onUpd(); }, 150);
}
// a match to pick up (the app was closed in the middle of one): the match module's if it takes it, otherwise let go (it counts as a loss)
function onResume(m) {
  if (ON.match && ON.match.matchId === m.matchId) return;
  if (typeof window.netMatchResume === 'function') { ON.match = m; onlineClose(); window.netMatchResume(m, ON.net); return; }
  ON.net.leaveMatch().catch(() => {});
}
// the match module, when a match is over: back in the lobby (your party with you); it waits for the menu
function onlineAfterMatch() { ON.after = true; if (state === 'menu') onAfter(); }
function onAfter() {
  const off = ON.off; ON.after = false; ON.off = false; clearTimeout(ON.foundT); ON.foundT = 0; ON.match = null; ON.v = ''; onBeat();
  if (ON.queued && !ON.queued.party) { ON.note = off ? 'The match was called off' : ''; onlineOpen(); return; }
  if (!onWant() && ON.net) onlineDrop();
  ptRender(); onUpd();
}
// ---- parties
// the game server's word on your party: who's in it, ready, votes, its state. A newcomer pops; everyone ready rings
function ptView(v) {
  const was = ON.party, my = ON.me && ON.me.id, now = Date.now(); for (const i of v.invites) i.exp = now + i.left; ON.party = v; ON.stale = 0;
  if (was && was.id === v.id && state === 'menu') {
    for (const m of v.members) if (m.id !== my && !was.members.some(x => x.id === m.id)) { AU.pop(); buzz(12); onSay(hdOf(m.name) + ' joined your party'); }
    if (v.state === 'starting' && was.state !== 'starting') { AU.ready(); buzz([10, 30, 10]); onSay('Everyone’s ready'); }
    if (v.state === 'queued' && was.state !== 'queued') onSay('Finding players');
  } else if (v.members.length > 1 && state === 'menu') { AU.pop(); onSay('You’re in a party'); }
  if (!was) ptLookSync(); // (your look may be newer than the one you said hello with)
  ptRender(); onBeat(); onUpd(); if (PK.open) pkRender();
}
function ptLeft(m) {
  const had = ptOn(); ON.party = null; ptMenuClose(); ptEmo(false);
  if (m.reason === 'removed') frToast('<span>You were removed from the party</span>');
  else if (m.reason === 'gone' && had) frToast('<span>You were away too long, so you left the party</span>');
  ptRender(); onBeat(); onUpd(); if (PK.open) pkRender();
}
// your party (made the first time you invite someone)
async function ptEnsure() {
  const net = await onlineConnect(); if (ON.party) return ON.party;
  if (!onParties()) throw onE('no_party');
  return net.partyCreate();
}
const PT_INV = { not_friends: n => 'You and ' + n + ' aren’t friends any more.', slow_down: () => 'That’s a lot of invites. Wait a bit, then try again.', bad_room: () => 'Couldn’t send the invite. Try again.', bad_mode: () => 'Party invites need a database update. Try again later.' };
// invite a friend: the invite is made in the database (friends only, blocks honoured, 2 minutes), then the game server nudges their
// game; with it go the invite's id and your Supabase token, so a friend whose game is closed gets a notification
async function ptInvite(f) {
  if (!f || !f.id || !NET_URL || state !== 'menu') return;
  if (ptLocked()) return;
  if (!onAcct()) return acctOpen(() => pkOpen());
  ON.pick = ''; const tag = f.id; PK.busy.add(tag); pkRender();
  try {
    const party = await ptEnsure();
    if (party.members.length >= party.max) throw onE('full');
    const r = await sbRpc('rm_invite', { p_to: f.id, p_room: party.code, p_mode: 'party' });
    if (!r || !r.ok) { ON.pick = (PT_INV[r && r.why] || PT_INV.bad_room)(hdOf(f.name)); AU.nope(); return; }
    ON.sent.set(f.id, { id: r.id, at: Date.now(), name: f.name });
    try { await ON.net.partyInvite(f.id, { name: f.name, look: f.look, inv: r.id, sbt: FR.s && FR.s.access_token }); } catch (e) {} // (it's in their inbox either way)
    AU.pop(); onSay('Invited ' + hdOf(f.name)); pushAsk(); if (PK.spot) setTimeout(() => { if (PK.open && PK.spot) pkClose(); }, 650);
  } catch (e) { AU.nope(); ON.pick = e.code === 'full' ? 'Your party is full.' : e.code === 'no_party' ? 'Parties come with the next game server update.' : e.status === 400 ? PT_INV.bad_mode() : e.status ? frErrText(e) : e.code === 'old' ? 'Update the game to play online.' : onReqText(e); }
  finally { PK.busy.delete(tag); pkRender(); ptRender(); }
}
// Join (into their party) or Not now (they hear it). Joining leaves the party you were in
async function ptAnswer(id, yes) {
  const i = ON.invites.find(x => x.id === id); ON.nope.add(id); ON.invites = ON.invites.filter(x => x.id !== id); if (IB.card === id) IB.card = ''; ibBadge(); ibRender(); onCard(); if (FR.open) frRender();
  if (!i) return;
  if (!yes) { sbRpc('rm_answer_invite', { p_id: id, p_accept: false }).catch(() => {}); if (ON.net && ON.me) { ON.net.partyDecline(i.room).catch(() => {}); ON.net.poke(i.from.id, 'answer'); } return; }
  if (state !== 'menu') return;
  ibClose(); if (FR.open) closeFriends();
  const who = i.from.name ? hdOf(i.from.name) : 'your friend'; frToast(frFace(i.from.look) + '<span>Joining <b>' + frEsc(who) + '</b>…</span>');
  let r = null; try { r = await sbRpc('rm_answer_invite', { p_id: id, p_accept: true }); } catch (e) { return frToast('<span>' + frEsc(frErrText(e)) + '</span>'); }
  if (!r || !r.ok || !r.room) { AU.nope(); return frToast('<span>That invite has run out.</span>'); }
  let net = null; try { net = await onlineConnect(); } catch (e) { onFail(e); return frToast('<span>' + frEsc(ON.err || 'Can’t reach the game server right now.') + '</span>'); }
  try { if (ON.queued && !ON.queued.party) await onUnq(); await net.partyJoin(r.room); AU.pop(); buzz(12); pushAsk(); }
  catch (e) { AU.nope(); frToast('<span>' + frEsc(e.code === 'not_found' ? who + '’s party has closed.' : e.code === 'full' ? who + '’s party is full.' : e.code === 'busy' ? who + '’s party is playing. Try again in a minute.' : onReqText(e)) + '</span>'); }
}
function ptReady() {
  const me = ptMe(), p = ON.party; if (!me || !ON.net || !p || p.state === 'match') return;
  if (!p.mode && !me.ready) { AU.nope(); return frToast('<span>None of these modes fit your party yet</span>'); }
  ON.net.partyReady(!(me.ready || p.state === 'starting' || p.state === 'queued')).catch(e => frToast('<span>' + frEsc(onReqText(e)) + '</span>'));
}
function ptVote(m) {
  const p = ON.party; if (!p || !ON.net || p.state === 'match') return; const x = p.modes.find(q => q.mode === m);
  if (!x || !x.on) { AU.nope(); return frToast('<span>' + (x ? 'Coming soon' : 'Not for a party this size') + '</span>'); }
  ON.net.partyVote(m).catch(() => {}); AU.pop();
}
function ptLeave() { if (!ON.net || !ON.party) return; ON.net.partyLeave().catch(() => {}); ON.party = null; ptMenuClose(); ptEmo(false); ptRender(); onBeat(); onUpd(); onSay('You left the party'); }
function ptKick(id) { if (!ON.net) return; ON.net.partyKick(id).catch(e => frToast('<span>' + frEsc(onReqText(e)) + '</span>')); ptMenuClose(); }
function ptReact(e) { if (!ON.net || !ptOn() || !ON.me) return; ON.net.partyReact(e); ptBubble(ON.me.id, e); ptEmo(false); }
// what you're doing in your own game: a trip to the locker, the shop, Strokes or Settings, or a CPU match, un-readies you (the
// others see it on your plate); back in the lobby with a new look, the party gets the new look
function ptBusyNow() { return state !== 'menu' ? (NM ? null : 'cpu') : lookOpen || lkOn() ? 'locker' : shopOpen ? 'shop' : menuPage === 'strokes' ? 'strokes' : !setModal.hidden ? 'settings' : null; }
function ptBusyTick() {
  if (!ON.party) return; const b = ptBusyNow(); if (b === ON.busy) return;
  const was = ON.busy; ON.busy = b; if (ON.net && ON.me) ON.net.partyBusy(b).catch(() => {});
  if ((was === 'locker' || was === 'shop') && !b) ptLookSync();
}
function ptLookSync() { const l = onLook(), s = JSON.stringify(l); if (s === ON.lookSent || !ON.net) return; ON.lookSent = s; ON.net.look = l; if (ON.me && ON.party) ON.net.partyLook(l).catch(() => {}); }
// a nudge from the game server: something new in your inbox (an invite, a friend request, an answer). Read it now
let onPokeT = 0;
function onPoke() { clearTimeout(onPokeT); onPokeT = setTimeout(() => { if (FR.me) { FR.at = 0; frPoll(); } else frTick(); }, 120); }
function onNudge(to, k) { if (ON.net && ON.me && to) ON.net.poke(to, k); }
// ---- the inbox (after every frPoll): party invites to you (a chime, the bell and a card for a new one), and how the ones you sent
// are doing. Until Play online opens, an invite is turned down for you (the friend hears you can't play right now), never shown
function onInbox(b) {
  try {
    const now = Date.now() + FR.skew, list = (b.invites || []).filter(i => i && i.id && i.from && i.mode === 'party' && !ON.nope.has(i.id) && Date.parse(i.expires) > now);
    if (list.length && !mpOpen()) { for (const i of list) { ON.nope.add(i.id); sbRpc('rm_answer_invite', { p_id: i.id, p_accept: false }).catch(() => {}); } list.length = 0; }
    const fresh = list.filter(i => !ON.seen.has(i.id));
    for (const i of list) ON.seen.add(i.id); ON.invites = NET_URL ? list : [];
    // (one that comes in during a match against the CPU: a word on screen now, and its card back in the lobby if it's still open)
    if (NET_URL && fresh.length && state !== 'menu') { ON.later = fresh[0].id; if (state === 'play' && !NM) popText(hdOf(fresh[0].from.name) + ' invited you to their party'); }
    if (NET_URL && fresh.length && state === 'menu') { ptRing(fresh[0]); }
    // (the invite a notification was tapped for: its card, now it's here)
    if (PUSH.open && list.some(i => i.id === PUSH.open)) { const i = list.find(x => x.id === PUSH.open); PUSH.open = ''; if (state === 'menu') { IB.card = i.id; IB.cardAt = Date.now(); IB.hold = true; } else ON.later = i.id; }
    for (const s of b.sent || []) { if (s.mode !== 'party') continue; const k = ON.sent.get(s.to); if (k && k.id === s.id && s.status === 'declined' && !k.told) { k.told = true; if (state === 'menu' && !ON.match) frToast('<span><b>' + frEsc(hdOf(k.name)) + '</b> can’t play right now</span>'); } }
    ibBadge(); if (IB.open) ibRender(); onCard();
  } catch (e) {}
}
// a new invite in the lobby: the chime, a buzz, the bell rings, the card
function ptRing(i) {
  AU.invite(); buzz([12, 40, 12]); onSay(hdOf(i.from.name) + ' invited you to their party');
  IB.card = i.id; IB.cardAt = Date.now(); IB.hold = false; const b = $('ibBtn'); b.classList.remove('ring'); void b.offsetWidth; b.classList.add('ring');
}
// the party invites list, in Friends (above the requests) and in the inbox
function ptInvRow(i) {
  const n = frEsc(hdOf(i.from.name)), id = frEsc(i.id), left = Math.max(0, Date.parse(i.expires) - Date.now() - FR.skew);
  return '<li class="frrow">' + frFace(i.from.look) + '<span class="frwho"><b>' + n + '</b><small>Party invite · <span class="ibtime" data-exp="' + frEsc(i.expires) + '">' + onClock(left) + '</span> left</small></span><span class="frbtns"><button class="frb go" data-py="join" data-id="' + id + '" type="button" aria-label="Join ' + n + '’s party">Join</button><button class="frb ghost ic" data-py="decline" data-id="' + id + '" type="button" aria-label="Not now, ' + n + '">' + FR_X + '</button></span></li>';
}
const onInvList = () => ON.invites.length ? '<section aria-label="Party invites"><h4>Party invites <i>' + ON.invites.length + '</i></h4><ul class="frlist">' + ON.invites.slice(0, 4).map(ptInvRow).join('') + '</ul></section>' : '';
// (Friends) Invite on each friend, into your party: In party, Invited, or locked until Play online opens. A friend under rank 2
// can't play online yet: no button
function onInvBtn(f) {
  if (!NET_URL || !onAcct() || (f.rank != null && (f.rank | 0) < ABIL_RANK)) return ''; const n = frEsc(hdOf(f.name)), st = pkState(f.id);
  if (!mpOpen()) return '<button class="frb ghost lk" data-py="invlock" type="button" aria-disabled="true" aria-label="Invite ' + n + ', locked">' + ABIL_LOCK + 'Invite</button>';
  if (st === 'in') return '<button class="frb pkon" type="button" disabled>In party</button>';
  return '<button class="frb go' + (st === 'sent' ? ' pkon' : '') + '" data-py="inv" data-id="' + frEsc(f.id) + '" type="button"' + (st === 'sent' ? ' disabled' : '') + ' aria-label="' + (st === 'sent' ? 'Invited ' : 'Invite ') + n + '">' + (st === 'sent' ? 'Invited' : 'Invite') + '</button>';
}
// how often the inbox is read: every 6 s with a sheet that shows it open; in the lobby every 8 s with a friend online (20 s
// otherwise), but only every 30 s while the game server can nudge it (an invite or a request then gets here at once); a minute in a match
function onPollGap() {
  const live = !!(ON.net && ON.me && onParties());
  return FR.open || IB.open || PK.open || PUSH.open ? 6000 : state !== 'menu' ? 60000 : live ? 30000 : FR.box && FR.box.friends.some(f => f.online) ? 8000 : 20000;
}
// ---- the inbox: a bell by the menu button, with a count; its sheet: party invites and friend requests
const IB = { open: false, card: '', cardAt: 0, hold: false, ret: null, sig: '' };
function ibCount() { return ON.invites.length + (FR.box && onAcct() ? FR.box.incoming.length : 0); }
function ibBadge() {
  const n = ibCount(), d = $('ibDot'), t = n > 9 ? '9+' : String(n); if (!d) return;
  if (!n) { if (!d.hidden) d.hidden = true; } else { if (d.textContent !== t) d.textContent = t; if (d.hidden) d.hidden = false; }
  $('ibBtn').setAttribute('aria-label', n ? 'Inbox, ' + n + ' new' : 'Inbox');
}
function ibOpen() {
  if (state !== 'menu') return; IB.ret = document.activeElement; IB.open = true; IB.card = ''; onCard(); $('ibModal').hidden = false; ibRender();
  if (SB_CFG && onAcct()) { if (!FR.me) frStart(); else { FR.at = 0; frPoll(); } }
  setTimeout(() => { if (IB.open) $('ibX').focus({ preventScroll: true }); }, 30);
}
function ibClose() { if (!IB.open) return; IB.open = false; $('ibModal').hidden = true; if (IB.ret && IB.ret.focus && document.contains(IB.ret)) IB.ret.focus({ preventScroll: true }); }
function ibRender() {
  const el = $('ibBody'); if (!el || !IB.open) return; let h = '';
  if (!SB_CFG) h = '<div class="frmsg">' + FR_FACES + '<b>Your inbox is on the way</b><p>Invites and friend requests come with online play.</p></div>';
  else if (!onAcct()) h = '<div class="frmsg">' + FR_FACES + '<b>Make an account</b><p>Party invites and friend requests are for players with an account.</p><button class="frb go" data-py="acct" type="button">Make an account</button></div>';
  else if (!FR.me) h = FR.err && !FR.busy ? '<div class="frmsg">' + FR_FACES + '<b>Can’t connect</b><p>' + frEsc(FR.err) + '</p></div>' : '<div class="frmsg"><span class="frspin" aria-hidden="true"></span><p>Checking your inbox…</p></div>';
  else {
    const b = FR.box || { incoming: [] };
    h += onInvList();
    if (b.incoming.length) h += '<section aria-label="Friend requests"><h4>Want to be friends <i>' + b.incoming.length + '</i></h4><ul class="frlist">' + b.incoming.map(r => '<li class="frrow">' + frFace(r.look) + '<span class="frwho"><b>' + frEsc(hdOf(r.name)) + '</b><small>Rank ' + (r.rank | 0) + '</small></span><span class="frbtns"><button class="frb go" data-py="acc" data-id="' + frEsc(r.id) + '" type="button">Accept</button><button class="frb ghost ic" data-py="dec" data-id="' + frEsc(r.id) + '" type="button" aria-label="Decline ' + frEsc(hdOf(r.name)) + '">' + FR_X + '</button></span></li>').join('') + '</ul></section>';
    if (!h) h = '<div class="frmsg">' + FR_FACES + '<b>Nothing new</b><p>Party invites and friend requests show up here.</p></div>';
  }
  if (h === IB.sig) return ibClocks(); IB.sig = h; el.innerHTML = h; ibClocks();
}
// the time left on each invite showing (once a second; only text)
function ibClocks() { for (const s of document.querySelectorAll('.ibtime[data-exp]')) { const t = onClock(Date.parse(s.dataset.exp) - Date.now() - FR.skew); if (s.textContent !== t) s.textContent = t; } }
async function ibRequest(id, yes) {
  try { const r = await sbRpc('rm_answer_request', { p_from: id, p_accept: yes }); if (yes && r && r.ok) { AU.power(); buzz([12, 40, 12]); onNudge(id, 'answer'); } await frPoll(); }
  catch (e) { frToast('<span>' + frEsc(frErrText(e)) + '</span>'); }
  ibRender(); ibBadge();
}
// ---- the invite picker: your friends, online ones first; Invite on each
const PK = { open: false, ret: null, sig: '', busy: new Set(), spot: false };
// a friend and your party: 'in' (in it), 'sent' (an invite waiting), or ''
function pkState(id) {
  const p = ON.party; if (p && p.members.some(m => m.sb === id)) return 'in';
  if (p && p.invites.some(i => i.to === id && i.exp > Date.now())) return 'sent';
  const s = ON.sent.get(id); return s && Date.now() - s.at < 120000 && !s.told ? 'sent' : '';
}
function pkOpen(spot) {
  if (state !== 'menu') return; PK.spot = spot === true;
  if (!NET_URL || !SB_CFG) return openFriends();
  if (ptLocked()) return;
  if (!onAcct()) return acctOpen(() => pkOpen());
  if (FR.open) closeFriends(); ibClose();
  PK.ret = document.activeElement; PK.open = true; ON.pick = ''; $('pkModal').hidden = false; pkRender();
  if (!FR.me) frStart(); else { FR.at = 0; frPoll(); }
  if (!ON.net || !ON.me) onlineConnect().catch(() => {});
  setTimeout(() => { if (PK.open) $('pkX').focus({ preventScroll: true }); }, 30);
}
function pkClose() { if (!PK.open) return; PK.open = false; $('pkModal').hidden = true; if (PK.ret && PK.ret.focus && document.contains(PK.ret)) PK.ret.focus({ preventScroll: true }); }
function pkRender() {
  const el = $('pkBody'); if (!el || !PK.open) return; const p = ON.party, n = p ? p.members.length : 1;
  $('pkSub').textContent = n + '/4'; $('pkSub').setAttribute('aria-label', n + ' of 4 in your party');
  let h = ON.pick ? '<p class="onnote">' + frEsc(ON.pick) + '</p>' : '';
  if (!FR.me) h += FR.err && !FR.busy ? '<div class="frmsg">' + FR_FACES + '<b>Can’t connect</b><p>' + frEsc(FR.err) + '</p></div>' : '<div class="frmsg"><span class="frspin" aria-hidden="true"></span><p>Getting your friends…</p></div>';
  else {
    const fr = (FR.box ? FR.box.friends : []).slice(), rank = f => f.online ? (f.status === 'lobby' ? 0 : 1) : 2;
    fr.sort((a, b) => rank(a) - rank(b) || Date.parse(b.last_seen) - Date.parse(a.last_seen));
    if (!fr.length) h += '<div class="frmsg">' + FR_FACES + '<b>No friends yet</b><p>Add friends with their friend code, then invite them here.</p><button class="frb go" data-py="friends" type="button">Add friends</button></div>';
    else {
      const full = n >= 4, on = fr.filter(f => f.online).length;
      h += '<section><h4>Your friends <i>' + fr.length + '</i>' + (on ? '<em>· ' + on + ' online</em>' : '') + '</h4><ul class="frlist">' + fr.map(f => { const st = pkState(f.id), nm = frEsc(hdOf(f.name)), busy = PK.busy.has(f.id), young = f.rank != null && (f.rank | 0) < ABIL_RANK;
        const btn = st === 'in' ? '<button class="frb pkon" type="button" disabled>In party</button>' : st === 'sent' ? '<button class="frb pkon" type="button" disabled>Invited</button>'
          : young ? '<button class="frb pkon" type="button" disabled aria-label="' + nm + ' plays with friends from rank ' + ABIL_RANK + '">Rank ' + ABIL_RANK + '</button>'
          : '<button class="frb go" data-py="inv" data-id="' + frEsc(f.id) + '" type="button"' + (full || busy ? ' disabled' : '') + ' aria-label="Invite ' + nm + '">' + (busy ? '…' : 'Invite') + '</button>';
        const can = !st && !young && !full && !busy; // (the whole row takes a tap: tap a friend to invite them)
        return '<li class="frrow' + (can ? ' pkcan" data-py="inv" data-id="' + frEsc(f.id) : '') + '">' + frFace(f.look) + '<span class="frwho"><b>' + nm + '</b><small><i class="frst ' + (f.online ? f.status : 'off') + '"></i>' + frWhen(f) + '</small></span><span class="frbtns">' + btn + '</span></li>'; }).join('') + '</ul></section>';
      h += '<p class="frfine">' + (full ? 'Your party is full: four is the most.' : 'Up to four in a party. An invite lasts 2 minutes; a friend whose game is closed gets a notification, or finds it in their inbox.') + '</p>';
    }
  }
  if (h === PK.sig) return; PK.sig = h; const top = el.scrollTop; el.innerHTML = h; el.scrollTop = top;
}
// ---- the Online sheet: on your own, pick a mode and find a match
function onlineOpen() {
  if (state !== 'menu' || (ON.gate && !ON.gate())) return false;
  if (ptOn()) { if (menuPage === 'events') closeEvents(); frToast('<span>Your party plays together: vote and ready up in the lobby</span>'); return false; }
  if (!ON.open) { ON.ret = document.activeElement; ON.open = true; $('onModal').hidden = false; setTimeout(() => { if (ON.open) $('onX').focus({ preventScroll: true }); }, 30); }
  if (ON.v === 'error' || ON.v === 'old') ON.v = '';
  onRender(); onCard();
  if (NET_URL && !ON.v && !(ON.net && (ON.net.connected || ON.lost))) onNet(); // (connected while they choose)
  return true;
}
function onlineClose() {
  if (!ON.open) return; ON.open = false; $('onModal').hidden = true; if (ON.v !== 'found') ON.note = '';
  if (ON.v === 'connecting' || ON.v === 'error' || ON.v === 'old') ON.v = '';
  if (ON.ret && ON.ret.focus && document.contains(ON.ret)) ON.ret.focus({ preventScroll: true });
  if (ON.v !== 'found' && !onWant() && ON.net && !ON.match) onlineDrop(); // (nothing going on: no connection kept)
  onCard();
}
const onUpd = () => { if (ON.open) onRender(true); onCard(); ptRender(); };
function onView() { return !NET_URL ? 'off' : ON.v || (ON.queued && !ON.queued.party ? 'queue' : 'home'); }
// the choice, as Choose Event shows its events: Versus (one real rival: tap it to find one) and Showdown (Free-for-all for up to four,
// or 2 v 2 with a teammate). A mode the game server doesn't offer yet is greyed and marked Coming next
function onEvCards() {
  const ic = id => { const e = $(id), i = e && e.querySelector('.evic'); return i ? i.innerHTML : ''; };
  const vs = onModeOn('duel'), ffa = onModeOn('ffa'), duo = onModeOn('duo'), sd = ffa || duo;
  return '<div class="ongrid">'
    + '<div class="evcard onev' + (vs ? '' : ' soon') + '" style="--ec:#E3122F"><button class="evmain" data-on="find" data-id="duel" data-f type="button" aria-label="Versus: find a 1v1 against a real person"' + (vs ? '' : ' disabled') + '>'
    + '<span class="evbar"><i>One real rival</i></span><span class="evtop"><span class="evic" aria-hidden="true">' + ic('evVs') + '</span><span class="evtx"><b>Versus</b><small>1v1, most paint wins</small></span></span><span class="evart" aria-hidden="true"><img data-art="cathedral" alt=""></span></button></div>'
    + '<div class="evcard onev' + (sd ? ' open' : ' soon') + '" style="--ec:#8E5CFF"><div class="evmain"' + (sd ? '' : ' data-on="soon" data-id="ffa"') + '>'
    + '<span class="evbar"><i>Last one standing</i></span><span class="evtop"><span class="evic" aria-hidden="true">' + ic('evShow') + '</span><span class="evtx"><b>Showdown</b><small>Three hearts each</small></span></span><span class="evart" aria-hidden="true"><img data-art="manor" alt=""></span></div>'
    + (sd ? '<div class="evdrop" role="group" aria-label="Which Showdown"><button type="button" data-on="find" data-id="ffa"' + (ffa ? '' : ' disabled') + ' aria-label="Showdown free-for-all: find a match for up to four"><b>Free-for-all</b><small>Up to four of you</small></button>'
      + '<button type="button" data-on="find" data-id="duo"' + (duo ? '' : ' disabled') + ' aria-label="Showdown 2 v 2: find a match with a teammate"><b>2 v 2</b><small>You and a teammate</small></button></div>' : '<i class="evsoon">Coming next</i>')
    + '</div></div>';
}
function onRender(soft) {
  const el = $('onBody'); if (!el) return; const v = onView(), me = frFace(onLook()), note = ON.note ? '<p class="onnote">' + frEsc(ON.note) + '</p>' : ''; let h = '';
  if (v === 'off') h = '<div class="frmsg">' + FR_FACES + '<b>Online play is on the way</b><p>It isn’t switched on in this version yet.</p></div>';
  else if (v === 'connecting') h = '<div class="frmsg"><span class="frspin" aria-hidden="true"></span><p>Connecting…</p></div>';
  else if (v === 'error') h = '<div class="frmsg">' + FR_FACES + '<b>Can’t connect</b><p>' + frEsc(ON.err || 'Can’t reach the game server right now.') + '</p><button class="frb go" data-on="retry" data-f type="button">Try again</button></div>';
  else if (v === 'old') h = '<div class="frmsg">' + FR_FACES + '<b>Update the game to play online</b><p>This version of Roll Model is too old for online play. Update it, then come back.</p></div>';
  else if (v === 'found') { const m = ON.match, o = m && (m.players || []).find(p => p.slot !== m.you); h = '<div class="frmsg onwait">' + onVs(me, o ? frFace(o.look) : ON_MYS) + '<b>Match found!</b><p>' + (o ? 'You vs ' + frEsc(hdOf(o.name)) : 'Get ready') + '</p></div>'; }
  else if (v === 'queue') {
    const wait = Date.now() - ON.queued.at, qm = ON.queued.mode, nm = PY_FULL[qm] || 'Versus';
    const vs = qm === 'duel' ? onVs(me, ON_MYS) : qm === 'duo' ? '<span class="onvs" aria-hidden="true">' + me + ON_MYS + '<i>vs</i>' + ON_MYS + ON_MYS + '</span>' : '<span class="onvs" aria-hidden="true">' + me + ON_MYS + ON_MYS + ON_MYS + '</span>';
    h = note + '<div class="frmsg onwait">' + vs + '<small class="onmd">' + frEsc(nm) + '</small><b>' + (ON.lost ? 'Reconnecting…' : ON.cpu ? 'It’s quiet right now' : 'Finding players…') + '</b><p class="ontime" id="onTime" role="timer" aria-label="Time looking"></p>'
      + '<p id="onWhere">' + (ON.cpu ? 'Nobody’s free to play ' + frEsc(nm) + ' yet. Keep looking, or play the CPU meanwhile.' : onWhere(wait)) + '</p>'
      + '<div class="onbtns">' + (ON.cpu ? '<button class="frb go" data-on="cpu" data-f type="button">Play the CPU</button>' : '') + '<button class="frb ghost" data-on="unq" data-f type="button">' + (ON.cpu ? 'Stop looking' : 'Cancel') + '</button></div></div>';
  }
  else h = note + '<div class="onhome onpick">' + onEvCards() + '<p class="onhint onnear">Real people, near you first, then from everywhere. Nobody waits long.</p>'
    + '<section class="onfr"><h4>Play with friends</h4><button class="frb onmk" data-py="pick" type="button">Invite friends to your party</button><p class="onhint">Up to four play together, from your lobby.</p></section></div>';
  if (soft && h === ON.sig) return onClocks(); ON.sig = h;
  const a = document.activeElement, inside = a && el.contains(a), key = inside && a.dataset && a.dataset.on ? '[data-on="' + a.dataset.on + '"]' + (a.dataset.id ? '[data-id="' + a.dataset.id + '"]' : '') : '';
  el.innerHTML = h; onClocks();
  for (const im of el.querySelectorAll('img[data-art]')) { const src = stageArtOf(im.dataset.art); if (src) im.src = src; } // (the stage art, as on Choose Event)
  if (inside && ON.open) { const f = (key && el.querySelector(key)) || el.querySelector('[data-f]') || $('onX'); f.focus({ preventScroll: true }); }
}
// where the search has got to: near you, then further, then everywhere (the server's stages: 4 s, 8 s, 12 s)
const onWhere = ms => ms < 4000 ? 'Looking for players near you…' : ms < 8000 ? 'Looking a little further away…' : 'Looking everywhere…';
const ON_MYS = '<span class="onmys" aria-hidden="true">?</span>';
const onVs = (a, b) => '<span class="onvs" aria-hidden="true">' + a + '<i>vs</i>' + b + '</span>';
function onClocks() {
  const q = ON.queued, t = q ? onClock(Date.now() - q.at) : '';
  const a = $('onTime'); if (a && a.textContent !== t) a.textContent = t; const b = $('onChipT'); if (b && b.textContent !== t) b.textContent = t;
  const w = $('onWhere'); if (w && q && !ON.cpu) { const s = onWhere(Date.now() - q.at); if (w.textContent !== s) w.textContent = s; }
}
// the lobby with nothing over it: the only place an invite card or the chip shows
const onCalm = () => state === 'menu' && !lookOpen && !shopOpen && !lkOn() && !irisBusy && $('sideMenu').hidden && !document.querySelector('#stage > .modal:not([hidden])');
const ON_ARR = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 5.5 15.5 12 9 18.5" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>';
// the invite card at the top of the lobby: 12 seconds, or (opened from a notification) until it's answered or runs out
function onCard() {
  const st = $('stage'), calm = onCalm(), i = IB.card && ON.invites.find(x => x.id === IB.card), show = !!(i && calm && !ON.match && (IB.hold || Date.now() - IB.cardAt < 12000)); let c = $('onInvCard');
  if (!show) { if (c) c.remove(); }
  else { if (!c) { c = document.createElement('div'); c.className = 'oninv'; c.id = 'onInvCard'; c.setAttribute('role', 'group'); c.setAttribute('aria-label', 'Party invite'); st.appendChild(c); }
    if (c.dataset.id !== i.id) { const n = frEsc(hdOf(i.from.name)), id = frEsc(i.id); c.dataset.id = i.id; c.innerHTML = frFace(i.from.look) + '<span class="oninvt"><b>' + n + '</b> invited you to their party</span><span class="oninvb"><button class="frb go" data-py="join" data-id="' + id + '" type="button" aria-label="Join ' + n + '’s party">Join</button><button class="frb ghost" data-py="later" data-id="' + id + '" type="button">Not now</button></span>'; } }
  // finding a match on your own with the sheet shut: what's going on, and the way back to it
  const busy = !show && calm && !ON.match && ON.net && ON.queued && !ON.queued.party; let ch = $('onChip');
  if (!busy) { if (ch) ch.remove(); return; }
  if (!ch) { ch = document.createElement('button'); ch.type = 'button'; ch.className = 'onchip'; ch.id = 'onChip'; ch.dataset.on = 'open'; st.appendChild(ch); }
  const t = ON.lost ? 'Reconnecting…' : 'Finding players';
  const h = '<i class="frst lobby" aria-hidden="true"></i><span>' + frEsc(t) + '</span><b id="onChipT"></b>' + ON_ARR;
  if (ch._h !== h) { ch._h = h; ch.innerHTML = h; ch.setAttribute('aria-label', t + '. Open Online'); onClocks(); }
}
function onAct(a, id) {
  if (a === 'find') onFind(id); else if (a === 'unq') { onUnq(); onSay('Stopped looking'); } else if (a === 'cpu') onCpu();
  else if (a === 'soon') { AU.nope(); ON.note = PY_FULL[id] + ' online is coming next. Versus is on now.'; onRender(); }
  else if (a === 'retry') { ON.v = ''; onlineOpen(); } else if (a === 'open') onlineOpen();
}
function pyAct(a, id, el) {
  if (a === 'inv') { const f = FR.box && FR.box.friends.find(x => x.id === id); if (f) ptInvite(f); }
  else if (a === 'invlock') ptLocked();
  else if (a === 'pick') { onlineClose(); pkOpen(); } else if (a === 'friends') { pkClose(); openFriends(); }
  else if (a === 'join' || a === 'decline') ptAnswer(id, a === 'join');
  else if (a === 'later') { IB.card = ''; IB.hold = false; onCard(); }
  else if (a === 'acc' || a === 'dec') ibRequest(id, a === 'acc');
  else if (a === 'leave') ptLeave(); else if (a === 'vote') ptVote(id); else if (a === 'emo') ptEmo(!PY.emo); else if (a === 'react') ptReact(id);
  else if (a === 'plate') ptMenu(id, el); else if (a === 'kick') ptKick(id); else if (a === 'menux') ptMenuClose();
  else if (a === 'acct') { ibClose(); acctOpen(() => ibOpen()); }
}
// one listener for the sheets, the invite card, the chip, the lobby's party pieces and the Invite buttons in Friends
$('stage').addEventListener('click', e => {
  if (PY.emo && !e.target.closest('#pyEmo, #pyReactBtn')) ptEmo(false);
  if (PY.menu && !e.target.closest('#pyMenu, .pyplate')) ptMenuClose();
  const p = e.target.closest('[data-py]'); if (p && !p.disabled) { AU.init(); AU.ui(); return pyAct(p.dataset.py, p.dataset.id, p); }
  const b = e.target.closest('[data-on]'); if (!b || b.disabled) return; AU.init(); AU.ui(); onAct(b.dataset.on, b.dataset.id);
});
$('onX').addEventListener('click', () => { AU.init(); AU.ui(); onlineClose(); });
$('onModal').addEventListener('click', e => { if (e.target === $('onModal')) onlineClose(); });
$('pkX').addEventListener('click', () => { AU.init(); AU.ui(); pkClose(); }); $('pkModal').addEventListener('click', e => { if (e.target === $('pkModal')) pkClose(); });
$('ibX').addEventListener('click', () => { AU.init(); AU.ui(); ibClose(); }); $('ibModal').addEventListener('click', e => { if (e.target === $('ibModal')) ibClose(); });
$('ibBtn').addEventListener('click', () => { AU.init(); AU.ui(); ibOpen(); });
document.addEventListener('keydown', e => {
  if (!ON.open && !PK.open && !IB.open) return; if (e.key === 'Escape') { e.preventDefault(); if (PK.open) pkClose(); else if (IB.open) ibClose(); else onlineClose(); } e.stopPropagation();
}, true); // (the lobby's keys wait while one is up)
{ const sm = $('onModal').querySelector('.tthd small'); if (sm) sm.textContent = 'Real people'; }
// ---- the lobby: your party around you. Members stand in the spots (left of you, right of you, then a third further out), each as
// their own character, with a name plate under them; an empty spot is a +. Positions are worked out each frame from the camera
// (cheap: a few points), and the page is only touched when something on it changes
const PY = { slot: new Map(), slots: null, plates: [], bubs: new Map(), emo: false, menu: '', shown: [false, false, false], pos: new Map(), cx: 0 }, PY_NONE = [null, null, null];
// where each spot stands: across (+ is your right) and toward the camera (- is behind you), in metres. Sideways (v372's line-up)
// the two beside you stand in line with you, where its + spots were, and the third beyond the one on your left, a little back.
// Upright, on your own, the + spots are beside you as before; with a party they stand a step behind you, the third further back,
// so four fit across a narrow screen
const PY_POS_P = [[-1.0, -0.85], [1.0, -0.85], [-1.95, -2.15]];
function pyPos(i, crowd) {
  if (lineupOn()) { const g = lineGap(); return i === 2 ? [-2 * g, -0.55] : [i ? g : -g, 0]; }
  return crowd || i === 2 ? PY_POS_P[i] : [i ? 1.05 : -1.05, 0];
}
const PY_LOOK = () => [LH, L2, L3];
const ptLobby = () => state === 'menu' && menuPage === 'home' && !lookOpen && !shopOpen && !irisBusy && !menu.hidden;
// who stands where: the members other than you keep the spot they got first; invites still waiting take the next free ones
function ptSlots() {
  const p = ON.party, my = ON.me && ON.me.id, others = p ? p.members.filter(m => m.id !== my) : [], now = Date.now(), invs = p ? p.invites.filter(i => i.exp > now) : [];
  const want = new Set([...others.map(m => 'm' + m.id), ...invs.map(i => 'i' + i.to)]);
  for (const [k] of PY.slot) if (!want.has(k)) PY.slot.delete(k);
  const used = new Set(PY.slot.values()), out = [null, null, null];
  for (const m of others) { const k = 'm' + m.id; if (!PY.slot.has(k)) { const f = [0, 1, 2].find(i => !used.has(i)); if (f === undefined) continue; PY.slot.set(k, f); used.add(f); } }
  for (const i of invs) { const k = 'i' + i.to; if (!PY.slot.has(k)) { const f = [0, 1, 2].find(x => !used.has(x)); if (f === undefined) continue; PY.slot.set(k, f); used.add(f); } }
  for (const m of others) { const s = PY.slot.get('m' + m.id); if (s !== undefined) out[s] = { k: 'm', m }; }
  for (const i of invs) { const s = PY.slot.get('i' + i.to); if (s !== undefined && !out[s]) out[s] = { k: 'i', i }; }
  const n = p ? p.members.length : 1, room = n < 4, both = !!(out[0] && out[1]); // (both sides taken: the third + appears)
  for (let s = 0; s < 3; s++) if (!out[s]) out[s] = room && (s < 2 || (both && NET_URL && SB_CFG)) ? { k: '+' } : null;
  return out;
}
// the third spot shows something (a member, an invite or its +): the line-up widens for it
const pyFar = () => { if (!ptLobby()) return false; const s = (PY.slots || ptSlots())[2]; return !!s; };
// the party's pieces of the lobby, when the party changes (never per frame)
function ptRender() {
  const inp = ptOn() && !ON.match, mh = $('mHome'); if (mh.classList.contains('inparty') !== inp) mh.classList.toggle('inparty', inp);
  const dock = $('pyDock'); dock.hidden = !inp;
  const p = ON.party, me = ptMe(), was = PY.slots, slots = PY.slots = ptSlots();
  if (!was || was.some((s, i) => !s !== !slots[i])) heroT = 0; // (a spot came or went: the camera frames the line-up again)
  // the mode vote: the modes that fit the party, each with who voted for it
  if (inp) {
    const votes = k => p.members.filter(m => m.vote === k).map(m => '<i style="--c:' + frCol(m.look) + '" title="' + frEsc(hdOf(m.name)) + '"></i>').join('');
    const mh2 = p.modes.map(x => { const md = PY_MODES.find(q => q[0] === x.mode) || [x.mode, x.mode, '']; const mine = me && me.vote === x.mode, win = p.mode === x.mode;
      return '<button class="pymode' + (win ? ' win' : '') + '" data-py="vote" data-id="' + x.mode + '" type="button" role="radio" aria-checked="' + !!mine + '"' + (x.on ? '' : ' disabled') + ' aria-label="' + md[1] + (win ? ', the party’s pick' : '') + '"><b>' + md[1] + '</b><small>' + (x.plan === 'private' ? 'Just us' : x.mode === 'duo' ? 'Us vs two' : 'With ' + (4 - p.members.length) + ' more') + '</small><span class="pyvotes">' + votes(x.mode) + '</span>' + (x.on ? '' : '<i class="pysoon">Soon</i>') + '</button>'; }).join('');
    const box = $('pyModes'); box.style.setProperty('--n', Math.max(1, p.modes.length)); box.classList.toggle('n3', p.modes.length >= 3); if (box._h !== mh2) { box._h = mh2; box.innerHTML = mh2 || '<p class="onhint">No mode for a party this size yet</p>'; }
  }
  ptPlay();
  // the name plates (yours and each member's) and the spots' look
  const lay = $('pyLayer'); lay.hidden = !inp;
  const plates = []; if (inp && me) plates.push({ key: 'me', m: me, me: true });
  slots.forEach((s, i) => { if (s && s.k === 'm') plates.push({ key: 'm' + s.m.id, m: s.m, slot: i }); });
  const lead = p && p.leader, iLead = !!(me && lead === me.id);
  const html = plates.map(x => { const m = x.m, st = m.away ? 'away' : m.busy ? 'busy' : m.ready ? 'ready' : '', tap = iLead && !x.me;
    return '<div class="pyplate ' + st + (x.me ? ' me' : '') + (tap ? ' tap' : '') + '" data-k="' + x.key + '"' + (tap ? ' data-py="plate" data-id="' + frEsc(m.id) + '" role="button" tabindex="0" aria-label="' + frEsc(hdOf(m.name)) + ': remove from the party"' : '') + '>'
      + (m.id === lead ? '<svg class="pycrown" viewBox="0 0 24 24" aria-label="Leader"><path d="M3.5 8.5 8 12l4-6 4 6 4.5-3.5-1.8 9.5H5.3z" fill="#FFD24A" stroke="#171320" stroke-width="1.6" stroke-linejoin="round"/></svg>' : '')
      + '<i class="pyst" aria-hidden="true">' + (m.ready ? '✓' : '') + '</i><span class="pyn"><b>' + (x.me ? 'You' : frEsc(hdOf(m.name))) + '</b>' + (m.away ? '<small>Away</small>' : m.busy ? '<small>' + frEsc(PY_BUSY[m.busy] || 'Busy') + '</small>' : '') + '</span></div>'; }).join('');
  if (lay._h !== html) { lay._h = html; lay.querySelectorAll('.pyplate').forEach(e => e.remove()); lay.insertAdjacentHTML('afterbegin', html); PY.plates = [...lay.querySelectorAll('.pyplate')]; PY.pos.clear(); }
  // the spots: a + where there's room (the third once both sides are taken), an invited friend's face while their invite waits; a
  // + shows a lock until Play online opens
  const els = [slotL, slotR, $('slotB')], lk = !mpOpen();
  slots.forEach((s, i) => { const el = els[i]; if (!el) return; const kind = s ? (s.k === 'i' ? 'i' + s.i.to : s.k + (lk ? 'l' : '')) : '';
    if (el._k !== kind) { el._k = kind; el.classList.toggle('inv', !!(s && s.k === 'i')); el.classList.toggle('lk', !!(s && s.k === '+' && lk));
      el.innerHTML = s && s.k === 'i' ? frFace(s.i.look) + '<b class="pytime" data-left="' + s.i.exp + '"></b>' : PY_PLUS;
      el.setAttribute('aria-label', s && s.k === 'i' ? 'Waiting for ' + hdOf(s.i.name) : lk ? 'Invite a friend to your party, locked: ' + ptLockText().toLowerCase() : 'Invite a friend to your party'); } });
  ptClocks();
}
const PY_PLUS = '__PLUS__';
const frCol = l => { const c = PALETTE.find(q => q.id === (l && l.c)); return c ? '#' + c.hex.toString(16).padStart(6, '0') : '#999'; };
// the big button: Play on your own; in a party it's Ready (and says what the party is waiting for)
function ptPlay() {
  const b = $('homePlay'), inp = ptOn() && !ON.match, lbl = b.querySelector('.pbl'); let sub = b.querySelector('.pysub');
  if (!sub) { sub = document.createElement('small'); sub.className = 'pysub'; lbl.after(sub); }
  let t = 'Play', s = '', cls = '';
  if (inp) {
    const p = ON.party, me = ptMe(), wait = p.members.filter(m => !m.ready).length;
    if (p.state === 'starting') { t = 'Starting'; s = 'Tap to stop'; cls = 'pygo'; }
    else if (p.state === 'queued') { t = 'Finding'; s = 'Tap to cancel'; cls = 'pygo'; }
    else if (me && me.ready) { t = 'Ready!'; s = wait ? 'Waiting for ' + wait + ' · tap to undo' : ''; cls = 'pyready'; }
    else { t = 'Ready'; s = p.mode ? '' : 'No mode for ' + p.members.length + ' yet'; }
  }
  if (lbl.textContent !== t) lbl.textContent = t; if (sub.textContent !== s) sub.textContent = s;
  for (const c of ['pyready', 'pygo']) if (b.classList.contains(c) !== (cls === c)) b.classList.toggle(c, cls === c);
}
// the clocks in the lobby: an invite's time left on its spot; the party's search
function ptClocks() {
  for (const e of document.querySelectorAll('.slot .pytime')) { const t = onClock(+e.dataset.left - Date.now()); if (e.textContent !== t) e.textContent = t; }
  if (ON.party && ON.party.invites.some(i => !i.over && i.exp <= Date.now())) { for (const i of ON.party.invites) if (i.exp <= Date.now()) i.over = true; ptRender(); } // (an invite ran out: its spot is free again)
  const p = ON.party; if (ptOn() && p.state === 'queued' && ON.net) { const t = 'Finding ' + onClock(ON.net.serverNow() - p.queuedAt), l = $('homePlay').querySelector('.pbl'); if (l.textContent !== t) l.textContent = t; }
  if (ptOn() && p.state === 'starting' && ON.net) { const n = Math.max(1, Math.ceil((p.startAt - ON.net.serverNow()) / 1000)), t = 'Starting ' + n, l = $('homePlay').querySelector('.pbl'); if (l.textContent !== t) l.textContent = t; }
}
// a member's blob in their spot, dressed as they are (their paint, eyes and wearables; a look that changes is put on again)
function ptDress(L, m) {
  const look = m.look && typeof m.look === 'object' ? m.look : {}, w = look.w && typeof look.w === 'object' ? look.w : {}, sig = JSON.stringify(look);
  if (L._pySig === sig && L._pyW === L.wearing) return; L._pySig = sig;
  const ok = (v, slot) => typeof v === 'string' && WEAR.some(x => x.id === v && x.slot === slot) ? v : null;
  L.wearing = { head: ok(w.head, 'head'), back: ok(w.back, 'back'), mouth: ok(w.mouth, 'mouth'), eye: ok(w.eye, 'eye'), side: ok(w.side, 'side'), neck: ok(w.neck, 'neck'), lash: ok(w.lash, 'lash'), arms: ok(w.arms, 'arms'), skin: ok(w.skin, 'skin'), iris: EYE_KEYS.includes(w.iris) ? w.iris : 'brown', eyes: EYE_STYLES[look.e] ? look.e : 'round' };
  L._pyW = L.wearing; L._pyHex = (rivalColOf(look.c) || RIVAL_COLS[0]).hex;
}
// every frame in the lobby (from placePBar): the members' blobs where they stand, and the plates, spots and reactions where those are
const pyV = new THREE.Vector3();
function pyPlace(pbR) {
  const on = ptLobby() && !pbar.hidden, slots = on ? PY.slots || (PY.slots = ptSlots()) : PY_NONE, Ls = PY_LOOK(), crowd = ptCrowd();
  const fx = Math.sin(hero.yaw), fz = Math.cos(hero.yaw), rx = Math.cos(hero.yaw), rz = -Math.sin(hero.yaw);
  for (let i = 0; i < 3; i++) {
    const s = slots[i], L = Ls[i], D = L.D, show = on && !!(s && s.k === 'm');
    if (show) { ptDress(L, s.m); const [a, b] = pyPos(i, crowd); D.x = P.x + rx * a + fx * b; D.z = P.z + rz * a + fz * b; D.y = 0; D.yaw = hero.yaw + (a < 0 ? 0.32 : -0.32); D.st = 'play'; D.lobbyReady = !!s.m.ready; if (L.col.getHex() !== L._pyHex) L.col.setHex(L._pyHex); }
    if (PY.shown[i] !== show) { PY.shown[i] = show; L.drop.visible = show; L.shadow.visible = false; vicLayer(D, show); D.lobbyReady = show ? D.lobbyReady : false; }
  }
  // the + spots and an invited friend's face: on your own where they always were, in a party at the spots the members take
  const els = [slotL, slotR, $('slotB')];
  for (let i = 0; i < 3; i++) {
    const el = els[i]; if (!el) continue; const s = slots[i], vis = on && !!s && s.k !== 'm';
    if (el.hidden === vis) el.hidden = !vis; if (!vis) continue;
    const [a, b] = pyPos(i, crowd); pyV.set(P.x + rx * a + fx * b, P.y + 0.28, P.z + rz * a + fz * b).project(camera);
    pyAt(el, clamp((pyV.x * 0.5 + 0.5) * viewW, Math.max(i === 1 ? 42 : PB.slotLo || 42, 42 + SAI.l), viewW - 42 - SAI.r), (0.5 - pyV.y * 0.5) * viewH, 'left');
  }
  // the name plates under each character's feet. Where they'd cover each other (a party of three or four on an upright screen),
  // yours, in front, drops below the ones beside you, and the one at the back rises above them
  if (PY.plates.length) { const at = [];
    for (const el of PY.plates) {
      const k = el.dataset.k; let x, z, d = 0; if (k === 'me') { x = P.x; z = P.z; } else { const s = PY.slot.get(k); if (s === undefined) continue; const [a, b] = pyPos(s, crowd); x = P.x + rx * a + fx * b; z = P.z + rz * a + fz * b; d = s === 2 && !lineupOn() ? 2 : 1; }
      if (!el._w) { el._w = el.offsetWidth; el._h = el.offsetHeight; } // (measured once a plate is drawn, not every frame)
      pyV.set(x, -0.02, z).project(camera); at.push({ el, d, x: (pyV.x * 0.5 + 0.5) * viewW, y: (0.5 - pyV.y * 0.5) * viewH + 6, w: el._w || 0, h: el._h || 0 });
    }
    const near = (p, q) => q.d === 1 && Math.abs(p.x - q.x) < (p.w + q.w) / 2 + 3 && p.y < q.y + q.h + 3 && p.y + p.h > q.y - 3;
    for (const p of at) { if (p.d !== 1) for (const q of at) if (near(p, q)) p.y = p.d ? q.y - 3 - p.h : q.y + q.h + 3; pyAt(p.el, p.x, p.y, 'plate'); }
  }
  // reactions, over the head of whoever sent them
  if (PY.bubs.size) { const now = performance.now(); for (const [id, b] of PY.bubs) {
    if (now > b.end) { b.el.remove(); PY.bubs.delete(id); continue; }
    let x = P.x, z = P.z, y = charTall(myLook) + 0.32; if (id !== (ON.me && ON.me.id)) { const s = PY.slot.get('m' + id); if (s === undefined) continue; const [a, bb] = pyPos(s, crowd); x = P.x + rx * a + fx * bb; z = P.z + rz * a + fz * bb; y = 1.05; }
    pyV.set(x, y, z).project(camera); pyAt(b.el, (pyV.x * 0.5 + 0.5) * viewW, (0.5 - pyV.y * 0.5) * viewH, 'bub'); } }
  if (PY.menu) { const el = $('pyMenu'), pl = PY.plates.find(e => e.dataset.k === 'm' + PY.menu); if (el && pl) { const r = pl.getBoundingClientRect(), sr = stage.getBoundingClientRect(), hw = (PY.menuW || 160) / 2 + 8; pyAt(el, clamp(r.left + r.width / 2 - sr.left, hw, viewW - hw), r.bottom - sr.top, 'menu'); } } // (kept on the screen)
}
// moves a piece only when it has really moved (half a pixel)
function pyAt(el, x, y, kind) {
  const q = PY.pos.get(el) || {}, rx = Math.round(x * 2) / 2, ry = Math.round(y * 2) / 2; if (q.x === rx && q.y === ry) return; PY.pos.set(el, { x: rx, y: ry });
  if (kind === 'left') { el.style.left = rx + 'px'; el.style.top = ry + 'px'; }
  else el.style.transform = 'translate(' + rx + 'px,' + ry + 'px) translate(-50%,' + (kind === 'bub' ? '-100%' : '0') + ')';
}
// a reaction over its sender for about two seconds
function ptBubble(id, e) {
  const em = PY_EMO.find(x => x[0] === e); if (!em || !ptLobby()) return; const lay = $('pyLayer'); lay.hidden = false;
  const old = PY.bubs.get(id); if (old) old.el.remove();
  const el = document.createElement('div'); el.className = 'pybub'; el.setAttribute('aria-hidden', 'true'); el.innerHTML = '<i>' + em[1] + '</i>'; lay.appendChild(el);
  PY.pos.delete(el); PY.bubs.set(id, { el, end: performance.now() + 2100 }); if (id !== (ON.me && ON.me.id)) { AU.pop(); { const w = ((ON.party && ON.party.members.find(m => m.id === id)) || {}).name; onSay((w ? hdOf(w) : 'Someone') + ' reacted'); } }
}
function ptEmo(on) {
  PY.emo = !!on && ptOn(); const el = $('pyEmo'); el.hidden = !PY.emo; $('pyReactBtn').setAttribute('aria-expanded', String(PY.emo));
  if (PY.emo && !el.children.length) el.innerHTML = PY_EMO.map(([k, v]) => '<button type="button" role="menuitem" data-py="react" data-id="' + k + '" aria-label="' + k + '">' + v + '</button>').join('');
}
// the leader taps a member's plate: Remove from the party
function ptMenu(id, el) {
  const m = ON.party && ON.party.members.find(x => x.id === id); if (!m || !ptMe() || ON.party.leader !== ptMe().id) return;
  ptMenuClose(); PY.menu = id; const d = document.createElement('div'); d.className = 'pymenu'; d.id = 'pyMenu'; d.setAttribute('role', 'dialog'); d.setAttribute('aria-label', hdOf(m.name));
  d.innerHTML = '<span>' + frEsc(hdOf(m.name)) + '</span><button class="frb bad" data-py="kick" data-id="' + frEsc(id) + '" type="button">Remove from party</button><button class="frb ghost" data-py="menux" type="button">Keep</button>';
  $('pyLayer').appendChild(d); PY.pos.delete(d); PY.menuW = d.offsetWidth; setTimeout(() => { const b = d.querySelector('button'); if (b) b.focus({ preventScroll: true }); }, 30);
}
function ptMenuClose() { PY.menu = ''; const d = $('pyMenu'); if (d) d.remove(); }
// ---- notifications while the game is closed (the iPhone app, NotifyBridge.swift): once the player has said yes to notifications
// the app hands over its token, kept with their account in Supabase (rm_push_token) so the game server can reach this phone; a
// tapped invite notification opens the game on that invite
const PUSH = { tok: null, sent: '', busy: false, retryAt: 0, open: '', openAt: 0 };
try { const t = store.pushTok; if (t && /^[0-9a-f]{64,200}$/.test(t.t)) PUSH.tok = { t: t.t, env: t.env === 'development' ? 'development' : 'production' }; } catch (e) {}
window.addEventListener('nativenotify', e => { const d = (e && e.detail) || {};
  if (typeof d.token === 'string' && /^[0-9a-f]{64,200}$/i.test(d.token)) { const t = { t: d.token.toLowerCase(), env: d.env === 'development' ? 'development' : 'production' };
    if (!PUSH.tok || PUSH.tok.t !== t.t || PUSH.tok.env !== t.env) { PUSH.tok = t; store.pushTok = t; save(); PUSH.sent = ''; } pushSync(); }
  if (d.open && d.open.k === 'invite' && typeof d.open.id === 'string') pushOpen(d.open.id); });
// the token with the player signed in now (once a launch, and again for another account)
function pushSync() {
  if (!PUSH.tok || !FR.me || !onAcct() || PUSH.busy || Date.now() < PUSH.retryAt) return; const k = FR.me.id + '|' + PUSH.tok.t + '|' + PUSH.tok.env; if (PUSH.sent === k) return;
  PUSH.busy = true; sbRpc('rm_push_token', { p_token: PUSH.tok.t, p_env: PUSH.tok.env }).then(r => { if (r && r.ok) PUSH.sent = k; else PUSH.retryAt = Date.now() + 600000; })
    .catch(() => { PUSH.retryAt = Date.now() + 120000; }).finally(() => { PUSH.busy = false; }); // (a database without it yet: tried again later)
}
// (logging out) this phone's token taken back from the account, with the token of the session that's ending
async function pushForget(tk) { if (!PUSH.tok || !SB_CFG) return; PUSH.sent = ''; try { await acFetch('POST', '/rest/v1/rpc/rm_push_forget', { p_token: PUSH.tok.t }, tk, 5000); } catch (e) {} }
// a tapped invite: its card in the lobby once the inbox has it (asked for at once); gone by then, a word
function pushOpen(id) { PUSH.open = id; PUSH.openAt = Date.now(); if (FR.me) { FR.at = 0; frPoll(); } else frTick(); }
// the first time you invite someone or join a party, in the app, with notifications not asked about yet: the game's own card first
function pushAsk() {
  if (!noteApp() || NOTE.status !== 'ask' || store.pushAsked) return; store.pushAsked = 1; save();
  setTimeout(() => { if (state !== 'menu' || !$('noteModal').hidden) return; pkClose(); ibClose();
    $('noteNote').innerHTML = 'Get a nudge when a friend invites you to their party, even with the game closed?';
    $('noteModal').hidden = false; setTimeout(() => $('noteYes').focus({ preventScroll: true }), 30); }, 900);
}
// once a second: the clocks; a connection away 20 s given up on; the connection wanted (and kept light) or let go; a party that didn't
// come back; the notification token
function onTick() {
  const now = Date.now();
  if (ON.lost && now - ON.lost > 20000 && !ON.match) { ON.lost = 0; onlineDrop(); ON.v = 'error'; ON.err = NET_WALLED ? 'Online play works in the Roll Model app, not in this preview.' : onOffline() ? 'You’re offline. Online play comes back when you are.' : 'Lost the connection to the game server.'; onUpd(); }
  if (ON.after && state === 'menu') onAfter();
  if (!ON.net && !ON.cp && !ON.match && onWant() && now > ON.retryAt && !NET_WALLED) onlineConnect().catch(e => { ON.fails++; ON.retryAt = Date.now() + Math.min(120000, 10000 * ON.fails); });
  else if (ON.net && !ON.cp && !onWant() && !ON.match && state === 'menu') onlineDrop();
  if (ON.stale && now > ON.stale) { ON.stale = 0; if (ON.party && ON.me) { const had = ptOn(); ON.party = null; ptRender(); onBeat(); if (had) frToast('<span>You were away too long, so you left the party</span>'); } }
  if (ON.queued && !ON.queued.party && !ON.cpu && now - ON.queued.at > 30000) { ON.cpu = true; onUpd(); if (!ON.open && state === 'menu') frToast('<span>It’s quiet right now. Open Online to play the CPU meanwhile.</span>'); }
  // (a party of two finding a Showdown or a 2v2 with nobody about: they can always play each other)
  { const p = ON.party; if (ptOn() && p.state === 'queued' && p.members.length === 2 && ON.net && ON.net.serverNow() - p.queuedAt > 30000 && ON.quiet !== p.queuedAt) { ON.quiet = p.queuedAt; if (state === 'menu') frToast('<span>It’s quiet right now. Keep looking, or vote Versus to play each other</span>'); } }
  if (ON.invites.length) { const t = now + FR.skew, l = ON.invites.filter(x => Date.parse(x.expires) > t); if (l.length !== ON.invites.length) { ON.invites = l; ibBadge(); ibRender(); if (FR.open) frRender(); } }
  if (IB.card && !IB.hold && now - IB.cardAt > 12000) IB.card = '';
  if (IB.card && IB.hold && !ON.invites.some(x => x.id === IB.card)) { IB.card = ''; IB.hold = false; }
  if (ON.later && onCalm() && !ON.match) { const i = ON.invites.find(x => x.id === ON.later); ON.later = ''; if (i) ptRing(i); } // (the invite that came during the match)
  if (PUSH.open && now - PUSH.openAt > 15000 && FR.me && FR.at > PUSH.openAt) { PUSH.open = ''; if (state === 'menu') frToast('<span>That party invite has run out</span>'); }
  pushSync();
  if (PY.emo && !ptLobby()) ptEmo(false);
  if (PY.menu && !ptLobby()) ptMenuClose();
  onCard(); onClocks(); ptClocks(); ibClocks();
}
setInterval(onTick, 1000);
"""

# a two-note chime for an invite (the synth's bells)
INVITE_SFX = "    invite() { bellFx(0, 88, 0.42, 0.085, 0.15); bellFx(0.16, 83, 0.7, 0.09, 0.22); hiss({ k: 'w', type: 'highpass', f: 7000, f1: 10000, dur: 0.35, v: 0.03, a: 0.02, rv: 0.2 }); }, // (v391: a party invite)\n"

def apply(s):
    # ---- the online layer: v306's rooms and duel invites give way to parties (from its first comment to just before onModalEl)
    a = "// ---------- (v306) Online: matchmaking, private rooms and duel invites"
    assert s.count(a) == 1
    i = s.index(a); j = s.index("const onModalEl = $('onModal');\n", i)
    s = s[:i] + JS.replace('__PLUS__', PLUS.replace("'", "\\'")).lstrip('\n') + s[j:]
    # the lobby holds still behind the new sheets too (v308's list of screens that cover it)
    s = rep(s, "['setModal', 'howModal', 'docModal', 'acModal', 'nameModal', 'ttModal']", "['setModal', 'howModal', 'docModal', 'acModal', 'nameModal', 'ttModal', 'pkModal', 'ibModal']")
    # ---- the page: the two sheets, the bell, the third spot, the party's layer and its dock
    s = rep(s, '  <div class="modal" id="docModal" hidden>\n', SHEETS + '  <div class="modal" id="docModal" hidden>\n')
    s = rep(s, '<button class="mbtn" id="hamBtn" type="button"', '<button class="mbtn ibbell" id="ibBtn" type="button" aria-label="Inbox" aria-haspopup="dialog">' + BELL + '<b class="ibdot" id="ibDot" hidden></b></button><button class="mbtn" id="hamBtn" type="button"')
    a = '        <div class="lgo" id="mCta">\n'
    s = rep(s, a, DOCK + a)
    a = '<button class="slot" id="slotR" type="button" hidden aria-label="Bring a friend into your lobby (coming soon)">'
    assert s.count(a) == 1
    k = s.index(a); e = s.index('</button>', k) + len('</button>')
    s = s[:e] + '<button class="slot" id="slotB" type="button" hidden aria-label="Invite a friend to your party">' + PLUS + '</button><div class="pylayer" id="pyLayer" hidden></div>' + s[e:]
    s = rep(s, 'aria-label="Bring a friend into your lobby (coming soon)"', 'aria-label="Invite a friend to your party"', 2)
    i = s.rfind('</style>'); s = s[:i] + CSS + s[i:]
    # ---- the lobby: the + spots open the invite picker; placed (with the members and their plates) by pyPlace each frame
    s = rep(s, "for (const el of [slotL, slotR]) el.addEventListener('click', uiClick(openFriends));",
               "for (const el of [slotL, slotR, $('slotB')]) el.addEventListener('click', uiClick(() => pkOpen(true))); // (v391: invite a friend into your party)")
    s = rep(s, """  for (const [el, s] of [[slotL, -1], [slotR, 1]]) {
    const g = lineupOn() ? lineGap() : 1.05; pbV.set(P.x + pbR.x * s * g, P.y + 0.28, P.z + pbR.z * s * g).project(camera);
    el.style.left = clamp((pbV.x * 0.5 + 0.5) * viewW, Math.max(s < 0 ? PB.slotLo || 42 : 42, 42 + SAI.l), viewW - 42 - SAI.r).toFixed(1) + 'px'; el.style.top = ((0.5 - pbV.y * 0.5) * viewH).toFixed(1) + 'px';
  }
""", "  pyPlace(pbR); // (v391: the + spots, your party where it stands, its plates and reactions)\n")
    s = rep(s, "  if (pbar.hidden === on) { pbar.hidden = !on; slotL.hidden = slotR.hidden = !on; }",
               "  if (pbar.hidden === on) { pbar.hidden = !on; if (!on) { slotL.hidden = slotR.hidden = $('slotB').hidden = true; pyPlace(); } } // (v391: pyPlace shows the spots)\n  ptBusyTick();")
    # (upright, Friends stands just over the spot at your right: over a party member there, where the spot would be)
    s = rep(s, "    if (viewH > viewW && !slotR.hidden) { const natTop = col.getBoundingClientRect().top - sr.top + fb.offsetTop, h = fb.offsetHeight || 62, slotTop = parseFloat(slotR.style.top) - (slotR.offsetHeight || 46) / 2;",
               "    if (viewH > viewW && !slotR.hidden && !ptCrowd()) { const natTop = col.getBoundingClientRect().top - sr.top + fb.offsetTop, h = fb.offsetHeight || 62, slotTop = parseFloat(slotR.style.top) - (slotR.offsetHeight || 46) / 2;")
    # ---- the camera: upright it steps back for a party, so everyone (and the + spots) fits, the feet a little higher for the plates
    # and the vote; sideways the line-up widens for a fourth, and you stand off centre so the four are centred
    s = rep(s, "dist = clamp(Math.max(tall * Hh / (2 * tv * px), wide / (2 * tv * asp * 0.46)), 1.65, 12), ly = 0.36;",
               "dist = clamp(Math.max(tall * Hh / (2 * tv * px), wide / (2 * tv * asp * 0.46), pyNeed(fw / W, tv * asp, !land)), 1.65, 16), ly = 0.36; /* (v391: a party fits) */")
    s = rep(s, "const fw = x1 - x0, fh = y1 - y0, tx = (x0 + x1) / 2, feetY = y0 + fh * (land ? 0.86 : 0.86);",
               "const fw = x1 - x0, fh = y1 - y0, tx = (x0 + x1) / 2, feetY = y0 + fh * (ptCrowd() ? (land ? 0.8 : 0.8) : 0.86);")
    s = rep(s, "  heroDist = dist; hero.mx = P.x; hero.mz = P.z;\n  const lookY = feetY - ly * Hh / (2 * tv * dist);",
               "  heroDist = dist; hero.mx = P.x; hero.mz = P.z; if (PY.cx) { hero.mx += Math.cos(hero.yaw) * PY.cx; hero.mz -= Math.sin(hero.yaw) * PY.cx; } // (v391: the middle of the party)\n  const lookY = feetY - ly * Hh / (2 * tv * dist);")
    s = rep(s, "const tv = Math.tan(LINEUP.lens * Math.PI / 360), ext = lineGap() + 0.45, body = charTall({});",
               "const tv = Math.tan(LINEUP.lens * Math.PI / 360), ext = lineGap() + 0.45, eL = ext + (pyFar() ? lineGap() : 0), body = charTall({}); /* (v391: eL, how far the line-up reaches on your left: a fourth stands out there) */")
    s = rep(s, "ppu = Math.min((hi - lo) / 2 * (lobbySide ? 0.95 : LINEUP.wide) / ext, Hh * LINEUP.tall / body, fh * 0.84 / tall);",
               "ppu = Math.min((hi - lo) * (lobbySide ? 0.95 : LINEUP.wide) / (eL + ext), Hh * LINEUP.tall / body, fh * 0.84 / tall);")
    s = rep(s, "hero.mx = P.x; hero.mz = P.z; heroOff.x = W / 2 - (lo + hi) / 2; heroOff.y = Hh / 2 - (fy - 0.36 * ppu);",
               "hero.mx = P.x; hero.mz = P.z; heroOff.x = W / 2 - ((lo + hi) / 2 + (eL - ext) / 2 * ppu); heroOff.y = Hh / 2 - (fy - 0.36 * ppu);")
    a = "// where the blob stands: the space the top bar, the side plates and the dock leave, its feet low in it\nfunction lobbyFrame() {"
    s = rep(s, a, """// (v391) how far back the upright lobby camera must be for the party to fit across the room it has: you and every spot that shows
// something (a member, an invite, a +), each at its own depth (a spot further back needs less), with room for its half width. The
// camera looks at the middle of the party (PY.cx across from you, in metres), not at you, so a fourth out on the left doesn't leave
// the right side empty. frac: the share of the screen's width the party may use (upright, the whole width: the party stands below
// the side plates); k: tan of half the field of view times the aspect
function pyNeed(frac, k, upright) {
  PY.cx = 0; if (!ptCrowd() || lineupOn()) return 0;
  const sl = PY.slots || ptSlots(), f = (upright ? 0.92 : Math.max(0.3, frac)) * 0.96, pts = [[0, 0]];
  sl.forEach((s, i) => { if (s) pts.push(pyPos(i, true)); });
  const need = c => { let d = 0; for (const [x, z] of pts) d = Math.max(d, (Math.abs(x - c) + 0.55) / (k * f) + z); return d; };
  let lo = -2, hi = 2; for (let n = 0; n < 40; n++) { const a = lo + (hi - lo) / 3, b = hi - (hi - lo) / 3; if (need(a) < need(b)) hi = b; else lo = a; } // (the least distance: the middle that needs it)
  PY.cx = (lo + hi) / 2; return need(PY.cx);
}
""" + a)
    # party members idle calmly in the lobby, and hop when they're ready
    s = rep(s, "    if (D === P && (lookOpen || menuPage === 'home') && !lookIntro && !vsSnap) { sq = idle.sq || 0.04 + 0.035 * Math.sin(clock * 2.3); rise = idle.rise; hop = idle.hop; spinY = idle.spin; } // breathing, plus its little idle bits\n",
               "    if (D === P && (lookOpen || menuPage === 'home') && !lookIntro && !vsSnap) { sq = idle.sq || 0.04 + 0.035 * Math.sin(clock * 2.3); rise = idle.rise; hop = idle.hop; spinY = idle.spin; } // breathing, plus its little idle bits\n"
               "    if (D !== P && D.lobbyReady === false && menuPage === 'home') { sq = 0.04 + 0.035 * Math.sin(clock * 2.1 + D.team); rise = 0; } // (v391: a party member waits calmly; ready, it hops)\n")
    # ---- the big button: Ready in a party
    s = rep(s, "$('homePlay').addEventListener('click', () => { AU.init(); if (state !== 'menu' || building || lookOpen || shopOpen || lkOn()) return;",
               "$('homePlay').addEventListener('click', () => { AU.init(); if (ptOn() && !ON.match) { if (state === 'menu' && !building && !lookOpen && !shopOpen && !lkOn()) { AU.pop(); ptReady(); } return; } if (state !== 'menu' || building || lookOpen || shopOpen || lkOn()) return;")
    # ---- Friends: the inbox reads party invites (rm_inbox2; rm_inbox until the database has it); requests and answers nudge the
    # other game; Invite takes the place of Duel on each friend
    s = rep(s, "try { const b = await sbRpc('rm_inbox', { p_status: frStatus() });", "try { const b = await frInbox();")
    a = "async function frPoll() {"
    s = rep(s, a, """// (v391) the inbox with party invites (rm_inbox2); a database without it yet gets the older one, and no party invites
async function frInbox() {
  if (FR.v2 !== false) { try { return await sbRpc('rm_inbox2', { p_status: frStatus() }); } catch (e) { if (e.status !== 404) throw e; FR.v2 = false; } }
  return sbRpc('rm_inbox', { p_status: frStatus() });
}
""" + a)
    s = rep(s, "    if (r.ok) { FR.typed = ''; i.value = ''; if (r.state === 'friends_now') { AU.power(); buzz([12, 40, 12]); } } await frPoll(); }",
               "    if (r.ok) { FR.typed = ''; i.value = ''; if (r.state === 'friends_now') { AU.power(); buzz([12, 40, 12]); } if (r.id) onNudge(r.id, r.state === 'friends_now' ? 'answer' : 'request'); } await frPoll(); }")
    s = rep(s, "  try { const r = await sbRpc(call[0], call[1]); if (a === 'acc' && r && r.ok) { AU.power(); buzz([12, 40, 12]); }",
               "  try { const r = await sbRpc(call[0], call[1]); if (a === 'acc' && r && r.ok) { AU.power(); buzz([12, 40, 12]); onNudge(id, 'answer'); }")
    # the counts follow every inbox (the bell's: invites and requests; the Friends button's stays the requests'); the token goes up
    s = rep(s, 'frSeen(b); onInbox(b); frBadge(); ', 'frSeen(b); onInbox(b); frBadge(); ibBadge(); pushSync(); ')
    s = rep(s, "    if (NET_URL) h += onInvList(); // (v306: duel invites)\n", "    if (NET_URL) h += onInvList(); // (v391: party invites)\n")
    s = rep(s, "+ '<span class=\"frbtns\">' + onDuelBtn(f) + '<button class=\"frb ghost ic\" data-act=\"more\"", "+ '<span class=\"frbtns\">' + onInvBtn(f) + '<button class=\"frb ghost ic\" data-act=\"more\"")
    s = rep(s, ".frrow .frbtns .frb.lk{color:rgba(23,19,32,.55)}.frrow .frbtns .frb.lk svg{flex:none;width:13px;height:13px} /* (v359: Duel, locked till Play online opens) */",
               ".frrow .frbtns .frb.lk{color:rgba(23,19,32,.55)}.frrow .frbtns .frb.lk svg{flex:none;width:13px;height:13px} /* (v359: playing with friends, locked till Play online opens; v391: Invite) */")
    # ---- Choose Event's Play online card: Versus and Showdown, with real people
    s = rep(s, '<b>Play online</b><small>1v1 against real people</small>', '<b>Play online</b><small>Versus and Showdown</small>')
    s = rep(s, "b.setAttribute('aria-label', on ? 'Play online: 1v1 against real people'", "b.setAttribute('aria-label', on ? 'Play online: Versus and Showdown against real people'")
    # ---- the chime for an invite
    s = rep(s, "    flipBack() { [81, 78, 74].forEach((m, i) => bellFx(i * 0.05, m, 0.25, 0.07, 0.15)); },\n",
               "    flipBack() { [81, 78, 74].forEach((m, i) => bellFx(i * 0.05, m, 0.25, 0.07, 0.15)); },\n" + INVITE_SFX)
    s = rep(s, "const LVL = { go: 1,", "const LVL = { invite: 2, go: 1,")
    # ---- logging out: this phone's notification token is taken back from the account first
    s = rep(s, "  try { const s = await Promise.race([sbSession(), new Promise((_, no) => setTimeout(() => no(new Error('slow')), 6000))]); await acFetch('POST', '/auth/v1/logout?scope=local', null, s.access_token); } catch (e) {}",
               "  try { const s = await Promise.race([sbSession(), new Promise((_, no) => setTimeout(() => no(new Error('slow')), 6000))]); await pushForget(s.access_token); await acFetch('POST', '/auth/v1/logout?scope=local', null, s.access_token); } catch (e) {} // (v391: the notification token first)")
    s = rep(s, "    if (perm || acJwt(t).is_anonymous !== true) await acFetch('POST', '/auth/v1/logout?scope=local', null, t); else",
               "    if (perm || acJwt(t).is_anonymous !== true) { await pushForget(t); await acFetch('POST', '/auth/v1/logout?scope=local', null, t); } else")
    s = rep(s, "  store.sbs = { out: 1, lost: lost ? 1 : 0 }; save(); frBadge(); acPaintAll();",
               "  store.sbs = { out: 1, lost: lost ? 1 : 0 }; save(); frBadge(); acPaintAll(); if (typeof PUSH === 'object') PUSH.sent = ''; // (v391: the next account sends the token again)")
    return s
