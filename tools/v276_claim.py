"""v276: commissions pay out when you claim them. A finished job's XP and dabs used to be added at the end of the match; now they wait on
its card. Open Commissions and each newly finished job gets its green Completed ribbon slapped on, one after another, each with its own
sound (made with Ludo: a quick whoosh into a two-note bell chime), and under the ribbon a gold Claim reward button pops up. Tap it: a
burst of dabs (Ludo coins sound) flies off the button and up into your dabs counter, which is lifted over the panel's dim for as long
as the panel is open, ticking up a clink at a time (a Ludo coin clink), with +60 XP floating off the button. The lobby's Commissions
badge counts the rewards waiting to be claimed and pulses; the end of a match says "Claim it in Commissions". Jobs finished before this
version were already paid, so they show as claimed; a reward left unclaimed at the day's reset is paid then rather than lost."""
def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)
def region(s, a, b, new):
    assert s.count(a) == 1, (s.count(a), a[:120]); i = s.index(a); j = s.index(b, i); return s[:i] + new + s[j:]

AUDIO = r"""  function sbLoad() { sbFetch('m'); sbFetch('s'); }
  // (v276) a few effects of their own outside the sheets (the commissions' ribbon and coins): fetched and decoded when first wanted
  const XB = {};
  function xGet(n) { if (XB[n] || !ctx || typeof fetch !== 'function' || location.protocol === 'file:') return; XB[n] = 'busy';
    fetch(SFX_BASE + n + '.mp3').then(r => { if (!r.ok) throw new Error('missing'); return r.arrayBuffer(); }).then(b => new Promise((ok, bad) => { const p = ctx.decodeAudioData(b, ok, bad); if (p && p.catch) p.catch(bad); })).then(buf => { XB[n] = buf; }).catch(() => { XB[n] = null; }); }
  function xPlay(n, o) { o = o || {}; const b = XB[n]; if (!ctx || !b || b === 'busy' || ctx.state !== 'running') { xGet(n); return false; }
    try { const src = ctx.createBufferSource(), g = ctx.createGain(); src.buffer = b; src.playbackRate.value = o.rate || 1; g.gain.value = (o.v == null ? 1 : o.v) * cur.g0; src.connect(g); g.connect(sfx); src.start(T() + (o.d || 0) + 0.004); } catch (e) { return false; } return true; }
"""

JS = r"""// (v276) a finished job keeps its reward on its card under the Completed ribbon until you claim it
const COMM_CHECK = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4.5 12.5l4.6 4.6L19.5 6.7" fill="none" stroke="currentColor" stroke-width="3.6" stroke-linecap="round" stroke-linejoin="round"/></svg>';
const commUnclaimed = c => { c = c || commState(); return c.done.filter(id => !c.claimed.includes(id)); };
function commBadgePaint() { const n = commsDue() ? commUnclaimed().length : 0, b = $('commBadge'); b.hidden = n <= 0; b.textContent = n; b.classList.toggle('claim', n > 0); if (n > 0) { AU.xwant('ribbon'); AU.xwant('coins'); AU.xwant('coin'); } }
function renderComms() { const c = commState(), seen = store.commSeen || 0, note = '<p class="cnote">Every commission done. The critics are speechless.</p>';
  const cards = c.active.map(id => { const k = COMMS.find(x => x.id === id), di = c.done.indexOf(id), fin = di >= 0, got = fin && c.claimed.includes(id), p = fin ? k.n : c.prog[id] || 0;
    return '<div class="comm' + (fin ? ' fin' + (di >= seen ? ' fresh' : '') + (got ? ' got' : ' claim') : '') + '" data-id="' + id + '" style="--p:' + Math.round(100 * p / k.n) + '"><div class="ring" data-n="' + p + '/' + k.n + '"></div><div class="ct"><b>' + k.t + '</b><small>' + k.d + '</small></div><b class="cr"><span>+' + COMM_XP + ' XP</span><span>+' + COMM_DABS + DROP_SVG + '</span></b>'
      + (fin ? '<i class="cstripe">' + COMM_CHECK + 'Completed</i>' : '')
      + (fin && !got ? '<button class="cclaim" type="button" data-id="' + id + '"><span>Claim reward</span><b>+' + COMM_DABS + DROP_SVG + '</b><b>+' + COMM_XP + ' XP</b></button>' : '') + '</div>'; }).join('');
  $('commList').innerHTML = cards + (!cards || c.active.every(id => c.done.includes(id)) ? note : ''); }
// your dabs counter, lifted over the panel's dim (a copy of it in the same place) so you can watch the claim land
function commWallet(on) {
  const m = $('commModal'); let w = $('commWallet'); if (!on) { if (w) w.remove(); return; }
  const src = $('dabsBtn'), r = src && src.getClientRects().length ? src.getBoundingClientRect() : null, mr = m.getBoundingClientRect();
  if (!w) { w = src ? src.cloneNode(true) : document.createElement('span'); for (const el of w.querySelectorAll('[id]')) el.removeAttribute('id'); w.id = 'commWallet'; w.removeAttribute('title'); w.setAttribute('aria-hidden', 'true'); w.tabIndex = -1; w.classList.add('cwallet'); m.appendChild(w); }
  w.style.left = ((r ? r.left : 16) - mr.left).toFixed(1) + 'px'; w.style.top = ((r ? r.top : 16) - mr.top).toFixed(1) + 'px';
  const b = w.querySelector('b'); if (b && !w.dataset.fly) b.textContent = String(store.drops || 0);
}
window.addEventListener('resize', () => { if (!$('commModal').hidden) commWallet(true); });
// the dabs: a burst off the button, each on its own arc up into the counter, the count going up a clink at a time
function commCoins(btn, from, to) {
  const m = $('commModal'), w = $('commWallet'), num = w && w.querySelector('b'); if (!w || !num || reduceMotion) { if (num) num.textContent = String(to); if (w) kick(w, 'cbump'); return; }
  const mr = m.getBoundingClientRect(), br = btn.getBoundingClientRect(), dc = w.querySelector('.dcoin') || w, wr = dc.getBoundingClientRect(), svg = (dc.querySelector('svg') || {}).outerHTML || '';
  const tx = wr.left + wr.width / 2 - mr.left, ty = wr.top + wr.height / 2 - mr.top, sx = br.left + br.width * 0.5 - mr.left, sy = br.top + br.height * 0.5 - mr.top, N = 10, coins = [];
  w.dataset.fly = '1';
  for (let i = 0; i < N; i++) { const el = document.createElement('i'); el.className = 'ccoin'; el.innerHTML = svg; el.style.opacity = '0'; m.appendChild(el);
    const a = -Math.PI / 2 + (Math.random() - 0.5) * 2.6, sp = 60 + Math.random() * 90;
    coins.push({ el, t0: i * 0.05, dur: 0.6 + Math.random() * 0.25, x0: sx + (Math.random() - 0.5) * br.width * 0.5, y0: sy + (Math.random() - 0.5) * 10, cx: sx + Math.cos(a) * sp * 1.5, cy: sy + Math.sin(a) * sp - 40, s: 0.85 + Math.random() * 0.35, rot: (Math.random() - 0.5) * 540, done: false }); }
  let T0 = null, landed = 0;
  const step = ts => {
    if (T0 === null) T0 = ts; const t = (ts - T0) / 1000, gone = m.hidden;
    for (const c of coins) { if (c.done) continue; if (t < c.t0 && !gone) continue; const u = gone ? 1 : Math.min(1, (t - c.t0) / c.dur), v = 1 - u;
      const x = v * v * c.x0 + 2 * v * u * c.cx + u * u * tx, y = v * v * c.y0 + 2 * v * u * c.cy + u * u * ty, s = c.s * (1 - 0.4 * u * u);
      c.el.style.opacity = '1'; c.el.style.transform = 'translate(' + (x - 17).toFixed(1) + 'px,' + (y - 17).toFixed(1) + 'px) rotate(' + (c.rot * u).toFixed(0) + 'deg) scale(' + s.toFixed(3) + ')';
      if (u >= 1) { c.done = true; c.el.remove(); landed++; num.textContent = String(Math.round(from + (to - from) * landed / N)); if (!gone) { kick(w, 'cbump'); AU.xplay('coin', { v: 0.5, rate: 0.96 + landed * 0.035 }) || (landed % 3 === 1 && AU.pop()); } } }
    if (coins.some(c => !c.done)) requestAnimationFrame(step); else { num.textContent = String(to); delete w.dataset.fly; if (!gone) { kick(w, 'cbig'); buzz(15); } }
  };
  requestAnimationFrame(step);
}
function commXp(btn) { const m = $('commModal'), mr = m.getBoundingClientRect(), br = btn.getBoundingClientRect(), el = document.createElement('b'); el.className = 'cxpf'; el.textContent = '+' + COMM_XP + ' XP'; el.style.left = (br.right - mr.left - 46).toFixed(0) + 'px'; el.style.top = (br.top - mr.top - 4).toFixed(0) + 'px'; m.appendChild(el); setTimeout(() => el.remove(), 1500); }
function commClaim(id, btn) {
  const c = commState(); if (!c.done.includes(id) || c.claimed.includes(id)) return;
  c.claimed.push(id); const from = store.drops || 0; store.drops = from + COMM_DABS; store.xp = (store.xp || 0) + COMM_XP; save();
  const card = btn.closest('.comm'); btn.disabled = true; btn.classList.add('took'); btn.innerHTML = '<span>' + COMM_CHECK + 'Claimed</span>';
  AU.xplay('coins', { v: 0.8 }) || AU.power(); buzz([12, 40, 12]);
  commXp(btn); commCoins(btn, from, store.drops); commBadgePaint();
  setTimeout(() => { if (card.isConnected) { card.classList.remove('claim'); card.classList.add('got'); btn.remove(); } }, 1350); // (the button folds away; the card is a finished one)
}
$('commList').addEventListener('click', e => { const b = e.target.closest('.cclaim'); if (!b || b.disabled) return; AU.init(); commClaim(b.dataset.id, b); });
function openComms() { if (state !== 'menu' || lookOpen || !commsDue()) return;
  const c = commState(); renderComms(); store.commSeen = c.done.length; save(); $('commModal').hidden = false; commWallet(true); commBadgePaint();
  // each newly finished job: its ribbon slaps on, one after another, with its sound; then its Claim button pops up under it
  let i = 0; for (const card of $('commList').querySelectorAll('.comm.fresh')) { const d = 0.3 + i * 0.45, st = card.querySelector('.cstripe'), b = card.querySelector('.cclaim');
    if (st) st.style.animationDelay = d.toFixed(2) + 's'; if (b) b.style.animationDelay = (d + 0.55).toFixed(2) + 's';
    setTimeout(() => { if (!$('commModal').hidden) AU.xplay('ribbon', { v: 0.85 }) || AU.pop(); }, d * 1000); i++; }
  setTimeout(() => { const b = $('commList').querySelector('.cclaim'); (b || $('commClose')).focus({ preventScroll: true }); }, i ? 300 + i * 450 + 600 : 30);
}
"""

CSS = r"""
/* (v276) a finished job's reward waits on its card: Claim reward under the ribbon; the dabs fly up into a copy of your counter over the dim */
.comm.claim{background:#FFFDF6}
.comm.claim>.ct,.comm.claim>.cr{opacity:.72;filter:grayscale(.25)}
.comm.claim .cstripe{top:44px}
.comm .cclaim{grid-column:1/-1;appearance:none;display:flex;align-items:center;justify-content:center;gap:9px;max-height:64px;margin:14px 2px 2px;padding:11px 12px 10px;border:2.5px solid var(--black);border-radius:10px;background:linear-gradient(180deg,#FFE7A0 0%,#F2C14E 58%,#E2A62A 100%);color:var(--black);font:900 15px/1 var(--font-head);letter-spacing:.06em;text-transform:uppercase;box-shadow:inset 0 2px 0 rgba(255,255,255,.55),0 4px 0 var(--black);cursor:pointer;-webkit-tap-highlight-color:transparent;overflow:hidden;animation:cclaimin .45s .1s cubic-bezier(.3,1.6,.5,1) both}
.comm .cclaim span{display:inline-flex;align-items:center;gap:6px;white-space:nowrap}
.comm .cclaim b{display:inline-flex;align-items:center;gap:3px;padding:4px 7px 3px;border-radius:999px;background:rgba(23,19,32,.13);font:900 12px/1 var(--font-head);letter-spacing:.02em;white-space:nowrap}
.comm .cclaim .dropi{width:14px;height:14px}
.comm .cclaim:active:not(:disabled){transform:translateY(3px);box-shadow:inset 0 2px 0 rgba(255,255,255,.55),0 1px 0 var(--black)}
.comm .cclaim:focus-visible{outline:3px solid #7CC8FF;outline-offset:2px}
.comm .cclaim.took{background:#fff;color:#1C7A3D;cursor:default;animation:cclaimout .32s 1s ease-in forwards}
.comm .cclaim.took svg{width:16px;height:16px}
@keyframes cclaimin{from{opacity:0;transform:translateY(10px) scale(.86)}}
@keyframes cclaimout{to{opacity:0;max-height:0;margin-top:0;margin-bottom:0;padding-top:0;padding-bottom:0;border-width:0}}
#commModal .cwallet{position:absolute!important;z-index:3;margin:0;pointer-events:none!important;animation:fadein .2s both}
#commModal .cwallet .dshop{display:none}
#commModal .cwallet.cbump .dcoin{animation:cbump .22s ease-out}
#commModal .cwallet.cbump b,#commModal .cwallet.cbig b{animation:cbumpn .26s ease-out}
#commModal .cwallet.cbig .dcoin{animation:cbig .45s cubic-bezier(.3,1.6,.5,1)}
@keyframes cbump{45%{transform:scale(1.22) rotate(-8deg)}}
@keyframes cbig{40%{transform:scale(1.4) rotate(10deg)}}
@keyframes cbumpn{45%{transform:scale(1.16);color:#FFE08A}}
#commModal .ccoin{position:absolute;left:0;top:0;z-index:4;width:34px;height:34px;pointer-events:none;will-change:transform;filter:drop-shadow(0 2px 0 rgba(23,19,32,.35))}
#commModal .ccoin svg{display:block;width:100%;height:100%}#commModal .ccoin .dabk{fill:var(--ink)}
#commModal .cxpf{position:absolute;z-index:4;pointer-events:none;font:900 18px/1 var(--font-head);color:#fff;text-shadow:0 0 0 #171320,1.5px 1.5px 0 #171320,-1.5px 1.5px 0 #171320,1.5px -1.5px 0 #171320,-1.5px -1.5px 0 #171320,0 3px 0 #171320;white-space:nowrap;animation:cxpf 1.4s ease-out forwards}
@keyframes cxpf{0%{opacity:0;transform:translateY(8px) scale(.7)}14%{opacity:1;transform:translateY(-6px) scale(1.1)}70%{opacity:1}100%{opacity:0;transform:translateY(-60px) scale(1)}}
#commBadge.claim{animation:cbadge 1.4s ease-in-out infinite}
@keyframes cbadge{0%,100%{transform:scale(1)}50%{transform:scale(1.2)}}
@media (prefers-reduced-motion:reduce){.comm .cclaim,#commModal .cwallet,#commBadge.claim,#commModal .cxpf{animation:none}.comm .cclaim.took{display:none}}
"""

def apply(s):
    # the sounds
    s = rep(s, "  function sbLoad() { sbFetch('m'); sbFetch('s'); }\n", AUDIO)
    s = rep(s, "  const api = {\n", "  const api = {\n    xwant(n) { xGet(n); }, xplay(n, o) { return xPlay(n, o); }, // (v276)\n")
    # the day's set keeps who's been paid; jobs done before this version were paid at the match's end; a reward left unclaimed when the
    # day's set turns over is paid then
    s = rep(s, "if (!store.comm || !store.comm.active) store.comm = { active: [], prog: {}, done: [] }; const c = store.comm;",
            "if (!store.comm || !store.comm.active) store.comm = { active: [], prog: {}, done: [], claimed: [], v276: 1 }; const c = store.comm; if (!c.v276) { c.v276 = 1; c.claimed = (c.done || []).slice(); } if (!Array.isArray(c.claimed)) c.claimed = [];")
    s = rep(s, "if (c.day) { c.active = []; c.prog = {}; c.done = []; store.commSeen = 0; }",
            "if (c.day) { const owe = c.done.filter(id => !c.claimed.includes(id)).length; if (owe) { store.drops = (store.drops || 0) + owe * COMM_DABS; store.xp = (store.xp || 0) + owe * COMM_XP; } c.active = []; c.prog = {}; c.done = []; c.claimed = []; store.commSeen = 0; }")
    # no longer paid at the match's end
    s = rep(s, "const fin = commProgress(endInfo); gain += fin.length * COMM_XP; endInfo.xp0", "const fin = commProgress(endInfo); endInfo.xp0", 2)
    s = rep(s, " + fin.length * COMM_DABS;", ";", 2)
    s = rep(s, "Commission done: ' + k.t + '<b>+' + COMM_XP + ' XP &middot; +' + COMM_DABS + ' dabs</b></div>'", "Commission done: ' + k.t + '<b>Claim it in Commissions</b></div>'")
    s = rep(s, '<p class="cnote small">Three jobs a day. Each one pays XP and dabs once.</p>', '<p class="cnote small">Three jobs a day. Finish one, then claim its XP and dabs.</p>')
    # the panel, the claim
    s = region(s, "function renderComms() {", "function closeComms() {", JS)
    s = rep(s, "function closeComms() { $('commModal').hidden = true;", "function closeComms() { $('commModal').hidden = true; commWallet(false); for (const el of $('commModal').querySelectorAll('.ccoin,.cxpf')) el.remove(); renderLobbyUI();")
    # the lobby's badge: the rewards waiting
    s = rep(s, "  const c = commState(), fresh = c.done.length - (store.commSeen || 0); $('commBadge').hidden = fresh <= 0; $('commBadge').textContent = fresh;", "  commBadgePaint();")
    i = s.index('</style>', s.index('.stpnote[hidden]{display:none}')); s = s[:i] + CSS + s[i:]
    return s
