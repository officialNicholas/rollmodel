"""pn01: the performance readout (v308: tap the version line in Settings five times) measures a whole session on the phone,
online play included.

- Two new lines under the frame numbers:
  - launch: how long from opening the app to the menu, and how long the last match took from Play to its first frame (the
    wipe, laying out the canvas and getting its drawing ready).
  - online, in an online match: the round trip and its jitter, how far in the past the rival is drawn, corrections from
    the server, and the traffic each way.
- Every screen keeps a tally while the readout is on (the lobby, the locker, each stage and mode, online duels): frames, the
  average frame rate, frames that took over 25 ms (a missed beat at 60 a second), the worst frame, and the game's own work
  per frame. In the menu the readout can be tapped: it opens the tally, and tapping again copies it to paste back (and
  closes it). In a match it can't be tapped, so it never takes a touch meant for the game.
- The readout costs nothing while it's off, except one check a frame until the menu first shows (for the launch time)."""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

JS = r"""
// ---------- (pn01) the readout's session tally: launch and match-start times, the online link, and frame numbers screen by screen ----------
const PHX = { launch: 0, startAt: 0, startMs: 0, tally: new Map(), open: false, copied: 0 };
function phxKey() {
  if (state === 'menu') return menuPage === 'locker' ? 'locker' : menuPage === 'home' ? 'lobby' : 'menu ' + menuPage;
  if (state !== 'play') return null;
  const m = { duel: 'versus', trio: 'trio', ffa: 'showdown', duo: 'showdown 2v2', solo: 'time trial' }[mode] || mode;
  return (NM ? 'online ' : '') + m + ' ' + (NM ? '' : stageSel);
}
function phxFrame(ft) {
  if (!PHX.launch && booted && state === 'menu' && $('boot').classList.contains('gone')) PHX.launch = performance.now();
  if (PHX.startAt && state !== 'menu') { PHX.startMs = performance.now() - PHX.startAt; PHX.startAt = 0; }
  if (!PH.on) return;
  const k = phxKey(); if (!k || !(ft > 0 && ft < 0.5)) return;
  let t = PHX.tally.get(k); if (!t) PHX.tally.set(k, t = { n: 0, time: 0, slow: 0, worst: 0, js: 0 });
  t.n++; t.time += ft; if (ft > 0.025) t.slow++; if (ft > t.worst) t.worst = ft; t.js += lastCpu;
}
function phxLines() {
  let s = '\nlaunch ' + (PHX.launch ? (PHX.launch / 1000).toFixed(1) + ' s' : '...') + (PHX.startMs ? '   last match start ' + (PHX.startMs / 1000).toFixed(1) + ' s' : '');
  if (NM && NM.net) { const st = NM.net.stats();
    s += '\nonline ping ' + Math.round(st.rtt) + ' ms ±' + Math.round(st.jitter) + '   rival ' + Math.round(st.interpDelay + st.rtt / 2) + ' ms behind   fixes ' + st.corrections
      + '\n       in ' + (PHX.bIn !== undefined ? ((st.bytesIn - PHX.bIn) / 1024).toFixed(1) : '-') + ' KB/s   out ' + (PHX.bOut !== undefined ? ((st.bytesOut - PHX.bOut) / 1024).toFixed(1) : '-') + ' KB/s   ' + (NM.net.connected ? 'connected' : 'reconnecting');
    PHX.bIn = st.bytesIn; PHX.bOut = st.bytesOut; }
  else PHX.bIn = PHX.bOut = undefined;
  return s;
}
function phxTable() {
  let s = 'screen             fps  >25ms  worst  game\n';
  for (const [k, t] of PHX.tally) s += (k + '                   ').slice(0, 18) + ' ' + String(Math.round(t.n / Math.max(0.001, t.time))).padStart(3) + '  ' + (Math.round(1000 * t.slow / t.n) / 10 + '%').padStart(5) + '  ' + String(Math.round(t.worst * 1000)).padStart(4) + 'ms ' + (t.js / t.n * 1000).toFixed(1).padStart(4) + 'ms\n';
  return s + 'launch ' + (PHX.launch / 1000).toFixed(1) + ' s, ' + (NATIVE ? 'app' : 'web') + ', tier ' + DEV_TIER + ', ' + (GFX === 'hi' ? 'Graphics' : 'Performance') + ', ' + innerWidth + 'x' + innerHeight + ' @' + (window.devicePixelRatio || 1);
}
function phxTap() {
  if (state !== 'menu') return;
  if (!PHX.open) { PHX.open = true; PH.el.classList.add('open'); PH.el.textContent = phxTable() + '\n\ntap to copy'; return; }
  const txt = phxTable(); PHX.open = false; PH.el.classList.remove('open');
  try { navigator.clipboard.writeText(txt).then(() => { PH.el.textContent = 'Copied'; }, () => { PH.el.textContent = 'Could not copy'; }); } catch (e) {}
}
"""

CSS = r'''
/* (pn01) the readout opens its tally when tapped, in the menu */
.perfhud.tap{pointer-events:auto;cursor:pointer}
.perfhud.open{color:#FFF6B0}
'''

def apply(s):
    # the tally and the new lines, beside the readout
    a = "$('setVer').addEventListener('click', () => {"
    s = rep(s, a, JS.lstrip('\n') + a)
    # once a second: the extra lines, and tappable only in the menu (the tally, when open, stays put until tapped again)
    s = rep(s, "    + 'held ' + renderer.info.memory.textures + ' pictures, ' + renderer.info.memory.geometries + ' meshes, ' + thLru.length + ' canvases'; // (v309)\n",
               "    + 'held ' + renderer.info.memory.textures + ' pictures, ' + renderer.info.memory.geometries + ' meshes, ' + thLru.length + ' canvases' // (v309)\n"
               "    + phxLines(); // (pn01)\n"
               "  if (PHX.open && state === 'menu') PH.el.textContent = phxTable() + '\\n\\ntap to copy'; else if (PHX.open) { PHX.open = false; PH.el.classList.remove('open'); }\n"
               "  PH.el.classList.toggle('tap', state === 'menu');\n")
    s = rep(s, "  if (PH.on && !PH.el) { PH.el = document.createElement('pre'); PH.el.className = 'perfhud'; PH.el.setAttribute('aria-hidden', 'true'); document.body.appendChild(PH.el); }",
               "  if (PH.on && !PH.el) { PH.el = document.createElement('pre'); PH.el.className = 'perfhud'; PH.el.setAttribute('aria-hidden', 'true'); document.body.appendChild(PH.el); PH.el.addEventListener('click', phxTap); }")
    # every frame (cheap: the launch check stops once it's known; the tally only while the readout is on)
    s = rep(s, "  lastCpu = (performance.now() - cpu0) / 1000;\n  if (PH.on) perfHudFrame(rawDt);\n}",
               "  lastCpu = (performance.now() - cpu0) / 1000;\n  if (PH.on || !PHX.launch) phxFrame(rawDt); // (pn01)\n  if (PH.on) perfHudFrame(rawDt);\n}")
    # Play pressed: the clock for the match start
    s = rep(s, "function start() {\n  if (building || irisBusy) return;\n", "function start() {\n  if (building || irisBusy) return;\n  PHX.startAt = performance.now(); // (pn01)\n")
    i = s.rfind('</style>'); s = s[:i] + CSS + s[i:]
    return s
