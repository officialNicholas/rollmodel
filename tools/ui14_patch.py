#!/usr/bin/env python3
"""Liquid bars: the coverage bars are wet paint, their meeting edges sloshing as the shares move, drops flying off a fast edge. On top of ui13_patch."""
import subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui13_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)

CSS = '''
/* ===== liquid bars ===== */
.liq{position:absolute;inset:0;width:100%;height:100%;display:block;pointer-events:none}
.jbar.liq-on i,.tug.liq-on i{display:none}
.jbar u{z-index:1}
.jbar{height:30px;border-radius:8px;background:#2A2338;transform:skewX(-12deg)}
@media (max-height:720px) and (max-aspect-ratio:1/1){.jbar{height:22px}}
@media (max-height:520px) and (min-aspect-ratio:1/1){.jbar{height:20px}}
'''
k = s.index('<div id="stage">'); j = s.rindex('</style>', 0, k); s = s[:j] + CSS + s[j:]

rep("function countUp(el, to, dur) {", r"""// ---------- a bar of wet paint: each share a body of color, its free edges rippling, sloshing harder the faster the share moves, drops
// flung off an edge on the move; a sheen along the top and a shadow along the bottom of the paint ----------
function makeLiquid(host) {
  const c = document.createElement('canvas'); c.className = 'liq'; host.appendChild(c); host.classList.add('liq-on'); const g = c.getContext('2d');
  const L = { segs: [], drops: [], last: 0, host: host };
  L.set = segs => { segs.forEach((n, i) => { const o = L.segs[i]; n.ph = i * 2.1; if (o) { n.v0 = n.x0 - o.x0; n.v1 = n.x1 - o.x1; n.a0 = (o.a0 || 0) * 0.86 + Math.abs(n.v0); n.a1 = (o.a1 || 0) * 0.86 + Math.abs(n.v1); } else { n.v0 = n.v1 = 0; n.a0 = n.a1 = 0; } }); L.segs = segs; };
  L.tick = now => {
    const w = host.clientWidth, h = host.clientHeight; if (!w || !h || !L.segs.length) return; const dpr = Math.min(2, window.devicePixelRatio || 1);
    if (c.width !== (w * dpr | 0) || c.height !== (h * dpr | 0)) { c.width = w * dpr | 0; c.height = h * dpr | 0; }
    const dt = Math.min(0.05, (now - (L.last || now)) / 1000); L.last = now; const t = now / 1000;
    g.setTransform(dpr, 0, 0, dpr, 0, 0); g.clearRect(0, 0, w, h);
    const edge = (x, a, ph, y) => x * w + a * (Math.sin(y / h * 3.1 + ph + t * 3.4) * 0.5 + Math.sin(y / h * 6.9 - t * 4.6 + ph * 1.7) * 0.28 + Math.sin(y / h * Math.PI) * 0.7 * Math.sign(Math.sin(t * 1.7 + ph)));
    const N = 12;
    for (const sg of L.segs) {
      const a0 = sg.x0 <= 0.0005 ? 0 : h * (0.1 + Math.min(0.9, sg.a0 * 40)), a1 = sg.x1 >= 0.9995 ? 0 : h * (0.1 + Math.min(0.9, sg.a1 * 40));
      if (sg.x1 - sg.x0 <= 0.0005) continue;
      g.beginPath();
      for (let i = 0; i <= N; i++) { const y = i / N * h, x = a0 ? edge(sg.x0, a0, sg.ph, y) : -6; i ? g.lineTo(x, y) : g.moveTo(x, y); }
      for (let i = N; i >= 0; i--) { const y = i / N * h, x = a1 ? edge(sg.x1, a1, sg.ph + 1.3, y) : w + 6; g.lineTo(x, y); }
      g.closePath(); g.fillStyle = sg.col; g.fill();
      // drops off a moving edge
      if (h >= 18) for (const [x, v] of [[sg.x0, sg.v0], [sg.x1, sg.v1]]) if (Math.abs(v) > 0.0035 && L.drops.length < 28 && Math.random() < 0.7) L.drops.push({ x: x * w, y: h * (0.2 + Math.random() * 0.6), vx: Math.sign(v) * (40 + Math.random() * 120), vy: -30 - Math.random() * 60, r: 1.5 + Math.random() * (h * 0.09), col: sg.col, life: 0.5 });
    }
    // the sheen and the shadow, on the paint only
    g.globalCompositeOperation = 'source-atop';
    g.fillStyle = 'rgba(255,255,255,.26)'; g.fillRect(0, h * 0.08, w, h * 0.22); g.fillStyle = 'rgba(255,255,255,.08)'; g.fillRect(0, h * 0.3, w, h * 0.2);
    g.fillStyle = 'rgba(0,0,0,.16)'; g.fillRect(0, h * 0.8, w, h * 0.2);
    g.globalCompositeOperation = 'source-over';
    for (let i = L.drops.length - 1; i >= 0; i--) { const d = L.drops[i]; d.life -= dt; if (d.life <= 0) { L.drops.splice(i, 1); continue; } d.x += d.vx * dt; d.y += d.vy * dt; d.vy += 420 * dt; g.globalAlpha = Math.min(1, d.life * 3); g.fillStyle = d.col; g.beginPath(); g.arc(d.x, d.y, d.r, 0, 6.2832); g.fill(); }
    g.globalAlpha = 1;
  };
  return L;
}
let jLiq = null, jLiqRun = 0, jLiqFinal = null;
// the results bar: the shares pour in from their ends over the same beat as the numbers, overshoot a touch, and keep sloshing while the sheet is up
function liqReveal(t0) {
  cancelAnimationFrame(jLiqRun); if (!jLiq || !jLiqFinal) return;
  const step = now => { if (end.hidden) return; const u = clamp((now - t0) / 1000, 0, 1), e = 1 - Math.pow(1 - u, 3), kk = e * (1 + 0.09 * Math.sin(u * Math.PI) * (1 - u));
    const segs = jLiqFinal.map(f => { const wdt = (f.x1 - f.x0) * kk; return { x0: f.anchor === 'left' ? 0 : f.anchor === 'right' ? 1 - wdt : (f.x0 + f.x1) / 2 - wdt / 2, x1: f.anchor === 'left' ? wdt : f.anchor === 'right' ? 1 : (f.x0 + f.x1) / 2 + wdt / 2, col: f.col }; });
    jLiq.set(segs); jLiq.tick(now); jLiqRun = requestAnimationFrame(step); };
  jLiqRun = requestAnimationFrame(step);
}
function countUp(el, to, dur) {""")
# the results: the final shares are kept for the pour
rep("""    jb = '<i style="--c:var(--ink);left:0;width:' + Math.min(100, you).toFixed(2) + '%"></i>' + (best && !info.newBest ? '<u style="left:' + Math.min(100, best) + '%"></u>' : '');""",
    """    jb = '<i style="--c:var(--ink);left:0;width:' + Math.min(100, you).toFixed(2) + '%"></i>' + (best && !info.newBest ? '<u style="left:' + Math.min(100, best) + '%"></u>' : '');
    jLiqFinal = [{ x0: 0, x1: Math.min(1, you / 100), col: TEAMS[0].css, anchor: 'left' }];""")
rep("""    const order = trio ? [P, H2, H] : [P, H], tot = order.reduce((s, D) => s + covOf(D), 0); let x = 0;
    order.forEach((D, i) => {""", """    const order = trio ? [P, H2, H] : [P, H], tot = order.reduce((s, D) => s + covOf(D), 0); let x = 0; jLiqFinal = [];
    order.forEach((D, i) => {
      { const sh = tot > 0 ? covOf(D) / tot : 1 / order.length; jLiqFinal.push({ x0: x / 100, x1: x / 100 + sh, col: TEAMS[D.team].css, anchor: i === 0 ? 'left' : i === order.length - 1 ? 'right' : 'center' }); }""")
rep("  $('jBar').innerHTML = jb; $('jNums').innerHTML = jn; $('judge').classList.remove('go');",
    "  $('jBar').innerHTML = jb; $('jNums').innerHTML = jn; $('judge').classList.remove('go'); jLiq = makeLiquid($('jBar')); jLiq.set(jLiqFinal.map(f => ({ x0: f.anchor === 'right' ? 1 : f.anchor === 'left' ? 0 : (f.x0 + f.x1) / 2, x1: f.anchor === 'right' ? 1 : f.anchor === 'left' ? 0 : (f.x0 + f.x1) / 2, col: f.col }))); jLiq.tick(performance.now());")
rep("  const t0 = performance.now() + 300, id = runId;\n  const tick = now => { if (id !== runId || end.hidden) return;", "  const t0 = performance.now() + 300, id = runId; liqReveal(t0);\n  const tick = now => { if (id !== runId || end.hidden) return;")
rep("  if (reduceMotion || window.__instant) { $('judge').classList.add('go'); return; }", "  if (reduceMotion || window.__instant) { $('judge').classList.add('go'); if (jLiq && jLiqFinal) { jLiq.set(jLiqFinal.map(f => ({ x0: f.x0, x1: f.x1, col: f.col }))); requestAnimationFrame(now => jLiq.tick(now)); } return; }")
# the match meter: live paint in the strip, you from the left, the rivals from the right
rep("const tankEl = $('bar'), tankTrack = $('ttrack');", "const tugLiq = makeLiquid($('meter'));\nconst tankEl = $('bar'), tankTrack = $('ttrack');")
rep("  if (mode === 'solo') { const best = (store.bestCov && store.bestCov.solo) || 0, bt = best ? best + '%' : '-'; if (ec.textContent !== bt) ec.textContent = bt; $('tugYou').style.width = Math.min(100, you / Math.max(best, 10) * 100).toFixed(2) + '%'; }",
    "  if (mode === 'solo') { const best = (store.bestCov && store.bestCov.solo) || 0, bt = best ? best + '%' : '-'; if (ec.textContent !== bt) ec.textContent = bt; $('tugYou').style.width = Math.min(100, you / Math.max(best, 10) * 100).toFixed(2) + '%'; tugLiq.set([{ x0: 0, x1: Math.min(1, you / Math.max(best, 10)), col: TEAMS[0].css }]); tugLiq.tick(performance.now()); }")
rep("    $('tugYou').style.width = you.toFixed(2) + '%'; $('tugCpu').style.width = cpu.toFixed(2) + '%';",
    "    $('tugYou').style.width = you.toFixed(2) + '%'; $('tugCpu').style.width = cpu.toFixed(2) + '%';\n    { const c2 = mode === 'trio' ? teamCov(2) : 0, segs = [{ x0: 0, x1: you / 100, col: TEAMS[0].css }, { x0: 1 - cpu / 100, x1: 1, col: TEAMS[1].css }]; if (mode === 'trio') segs.push({ x0: 1 - (cpu + c2) / 100, x1: 1 - cpu / 100, col: TEAMS[2].css }); tugLiq.set(segs); tugLiq.tick(performance.now()); }")
rep('<p class="ver">Version 83</p>', '<p class="ver">Version 84</p>')
open(DST, 'w').write(s); print('ok', n0, '->', len(s))
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
