#!/usr/bin/env python3
"""The loading bar as paint: it pours in from above and spreads along the bar with a rounded, wobbling front, the top of it rolling, a wet highlight on it, and drips hanging off the underside that stretch and fall. On top of ui60_patch."""
import subprocess, re
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui60_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)

a = s.index("(() => { const c = document.getElementById('bootC')"); b = s.index("})();\n</script>", a) + len("})();")
s = s[:a] + r'''(() => { const c = document.getElementById('bootC'), bar = document.querySelector('.bootbar'); if (!c || !c.getContext) return; const g = c.getContext('2d'); if (!g) return; let W = 0, H = 0, dpr = 1, t0 = performance.now(), last = t0, lvl = 0, drops = [], drips = [], hang = [], run = true, seed = Math.random() * 9;
  const col = () => getComputedStyle(document.documentElement).getPropertyValue('--ink').trim() || '#E3122F';
  const size = () => { dpr = Math.min(2, window.devicePixelRatio || 1); W = innerWidth; H = innerHeight; c.width = W * dpr | 0; c.height = H * dpr | 0; c.style.width = W + 'px'; c.style.height = H + 'px'; };
  size(); addEventListener('resize', size);
  const rr = (x, y, w, h, r) => { g.beginPath(); if (g.roundRect) g.roundRect(x, y, w, h, r); else g.rect(x, y, w, h); };
  const frame = now => { if (!run) return; const dt = Math.min(0.05, (now - last) / 1000); last = now; const t = (now - t0) / 1000, p = Math.max(0, Math.min(1, window.__bootP || 0));
    try {
    lvl += (p - lvl) * Math.min(1, dt * 1.7); g.setTransform(dpr, 0, 0, dpr, 0, 0); g.clearRect(0, 0, W, H); const ink = col();
    const r = bar ? bar.getBoundingClientRect() : { left: W * 0.2, top: H * 0.6, width: W * 0.6, height: 44 }, L = r.left + 3, T = r.top + 3, Wd = r.width - 6, Hh = r.height - 6, B = T + Hh;
    // how far the paint has spread: its front is rounded, bulging forward in the middle like something thick being poured, and it wobbles
    const xf = L + Math.max(12, lvl * Wd), bul = 7 + 3 * Math.sin(t * 2.3 + seed), wob = 2.2 * Math.sin(t * 5.7) + 1.4 * Math.sin(t * 9.1 + 1);
    const front = y => { const u = (y - T) / Hh; return xf + bul * Math.sin(u * 3.1416) + wob * Math.sin(u * 6.28 + t * 4) - 10 * u * u; };
    const land = Math.max(L + 14, xf - 16 - 6 * Math.sin(t * 1.3)); // (the stream lands just behind the front, so the pour pushes it on)
    // drips: under the filled part of the bar, a drop swells on the underside, stretches, then lets go and falls
    if (hang.length < 4 && Math.random() < dt * 1.6) hang.push({ x: L + 10 + Math.random() * Math.max(4, xf - L - 24), len: 0, w: 4 + Math.random() * 3.5 });
    g.fillStyle = ink; for (let i = hang.length - 1; i >= 0; i--) { const d = hang[i]; d.len += dt * (6 + d.len * 0.9); if (d.len > 26 + d.w * 2) { drips.push({ x: d.x, y: B + d.len, vy: 20, r: d.w * 1.1, life: 1.2 }); hang.splice(i, 1); continue; }
      // a neck that thins as it stretches, and a round head that swells at the end of it
      const k = Math.min(1, d.len / 14), hr = d.w * (0.7 + 0.6 * k), nk = d.w * (1 - 0.6 * k); g.beginPath(); g.moveTo(d.x - d.w, B - 1); g.quadraticCurveTo(d.x - nk, B + d.len * 0.5, d.x - nk * 0.8, B + d.len - hr); g.lineTo(d.x + nk * 0.8, B + d.len - hr); g.quadraticCurveTo(d.x + nk, B + d.len * 0.5, d.x + d.w, B - 1); g.closePath(); g.fill(); g.beginPath(); g.arc(d.x, B + d.len - hr * 0.3, hr, 0, 6.2832); g.fill(); }
    for (let i = drips.length - 1; i >= 0; i--) { const d = drips[i]; d.life -= dt; d.y += d.vy * dt; d.vy += 420 * dt; if (d.life <= 0 || d.y > H + 20) { drips.splice(i, 1); continue; } g.globalAlpha = Math.min(1, d.life * 3); g.beginPath(); g.ellipse(d.x, d.y, d.r * 0.8, d.r * 1.25, 0, 0, 6.2832); g.fill(); } g.globalAlpha = 1;
    // the tank itself is drawn here, under the paint (the bar element above only keeps its border and shadow), then the paint in it, clipped: flat along the bottom, a rolling top edge, the rounded front
    g.fillStyle = 'rgba(255,255,255,.6)'; rr(r.left + 1, r.top + 1, r.width - 2, r.height - 2, 5); g.fill();
    g.save(); rr(L, T, Wd, Hh, 3); g.clip();
    g.fillStyle = ink; g.beginPath(); g.moveTo(L - 4, B + 4); g.lineTo(L - 4, T - 4); const N = 32; for (let i = 0; i <= N; i++) { const x = L + i / N * (xf - L), dl = (x - land) / 18, y = T + 1.5 + 1.2 * Math.sin(i * 0.8 + t * 4.4) + 0.9 * Math.sin(i * 1.9 - t * 6.1) - 3 * Math.exp(-dl * dl) * (0.6 + 0.4 * Math.sin(t * 11)); g.lineTo(Math.min(x, front(y)), y); }
    for (let i = 0; i <= 12; i++) { const y = T + i / 12 * Hh; g.lineTo(front(y), y); } g.lineTo(L - 4, B + 4); g.closePath(); g.fill();
    // the shine on the wet surface: a band along the top, brighter where the paint is freshest, a bead on the front
    g.fillStyle = 'rgba(255,255,255,.3)'; g.beginPath(); g.moveTo(L, T + 4); for (let i = 0; i <= N; i++) { const x = L + i / N * (xf - L - 10); g.lineTo(x, T + 4 + 1.2 * Math.sin(i * 0.8 + t * 4.4)); } g.lineTo(xf - 10, T + 7.5); g.lineTo(L, T + 7.5); g.closePath(); g.fill();
    g.fillStyle = 'rgba(255,255,255,.42)'; g.beginPath(); g.ellipse(front(T + Hh * 0.38) - 5, T + Hh * 0.38, 2.4, 4.5, 0.3, 0, 6.2832); g.fill();
    g.strokeStyle = 'rgba(0,0,0,.2)'; g.lineWidth = 2; g.beginPath(); for (let i = 0; i <= 12; i++) { const y = T + i / 12 * Hh; i ? g.lineTo(front(y) - 1, y) : g.moveTo(front(y) - 1, y); } g.stroke(); g.restore();
    // the stream: from the top of the screen down onto the paint, swaying a touch, thinner as it falls, with a shine down one side
    const sw = 1 + 0.25 * Math.sin(t * 2.1), x0 = land + Math.sin(t * 0.9) * 3, yS = T + 2;
    g.fillStyle = ink; g.beginPath(); g.moveTo(x0 - 20 * sw, -10); g.bezierCurveTo(x0 - 14 * sw, yS * 0.3, x0 - 8, yS * 0.7, x0 - 6 + Math.sin(t * 7) * 1.5, yS + 4); g.lineTo(x0 + 6 + Math.cos(t * 6.3) * 1.5, yS + 4); g.bezierCurveTo(x0 + 8, yS * 0.7, x0 + 14 * sw, yS * 0.3, x0 + 20 * sw, -10); g.closePath(); g.fill();
    g.fillStyle = 'rgba(255,255,255,.22)'; g.beginPath(); g.moveTo(x0 - 11 * sw, 0); g.bezierCurveTo(x0 - 8, yS * 0.35, x0 - 4.5, yS * 0.7, x0 - 3.5, yS); g.lineTo(x0 - 1, yS); g.bezierCurveTo(x0 - 2, yS * 0.7, x0 - 5.5, yS * 0.35, x0 - 7.5 * sw, 0); g.closePath(); g.fill();
    // drops flung up where the stream lands, falling back in
    if (Math.random() < 0.5 && drops.length < 24) drops.push({ x: x0 + (Math.random() - 0.5) * 8, y: yS, vx: (Math.random() - 0.5) * 120, vy: -(60 + Math.random() * 110), r: 1.5 + Math.random() * 3, life: 0.9 });
    g.fillStyle = ink; for (let i = drops.length - 1; i >= 0; i--) { const d = drops[i]; d.life -= dt; d.x += d.vx * dt; d.y += d.vy * dt; d.vy += 520 * dt; if (d.life <= 0 || d.y > yS + 8) { drops.splice(i, 1); continue; } g.beginPath(); g.arc(d.x, d.y, d.r, 0, 6.2832); g.fill(); }
    } catch (e) { run = false; if (bar) bar.classList.add('plain'); return; } // (if the drawing fails, the plain fill comes back)
    requestAnimationFrame(frame); };
  requestAnimationFrame(frame);
  const stop = () => { const b = document.getElementById('boot'); if (b && b.classList.contains('gone')) { run = false; return; } setTimeout(stop, 500); }; setTimeout(stop, 2000);
})();''' + s[b:]
rep(".boot .bootbar i{display:none}", ".boot .bootbar i{display:none}\n.boot .bootbar{background:transparent}\n.boot .bootbar.plain{background:rgba(255,255,255,.55)}\n.boot .bootbar.plain i{display:block}")
m = re.search(r'<p class="ver">Version (\d+)</p>', s); v = int(m.group(1)); s = s.replace(m.group(0), '<p class="ver">Version %d</p>' % (v + 1))
open(DST, 'w').write(s); print('ok', n0, '->', len(s), 'v', v + 1)
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
