#!/usr/bin/env python3
"""The loading screen is wet paint: a stream pours from the top into a glass tank that fills to the loading, its surface sloshing, drops splashing where the stream lands; the wordmark over it. Drawn by a small script of its own so it runs while the game's own script is still being read. On top of ui58_patch."""
import subprocess, re
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
subprocess.run(['python3', '-I', S + '/tools/ui58_patch.py'], check=True)
DST = '/home/claude/paint-the-canvas.html'
s = open(DST).read(); n0 = len(s)
def rep(old, new, count=1):
    global s
    c = s.count(old); assert c == count, f'expected {count}, found {c}: {old[:90]!r}'
    s = s.replace(old, new)

rep('  <div class="boot" id="boot" role="status"><span class="bootdrip" aria-hidden="true"></span><span class="tcard boottc" aria-hidden="true"></span><span class="bootdrop" aria-hidden="true"></span><div class="bootbar" aria-hidden="true"><i id="bootFill"></i></div><p class="bootmsg" id="bootMsg">Loading</p></div>',
    '''  <div class="boot" id="boot" role="status"><canvas class="bootc" id="bootC" aria-hidden="true"></canvas><span class="tcard boottc" aria-hidden="true"></span><div class="bootbar" aria-hidden="true"><i id="bootFill"></i></div><p class="bootmsg" id="bootMsg">Loading</p></div>
<script>
// the paint pouring in while the game loads: a stream from the top into the tank, its surface sloshing up to the loading, drops where it lands
(() => { const c = document.getElementById('bootC'), bar = document.querySelector('.bootbar'); if (!c || !c.getContext) return; const g = c.getContext('2d'); let W = 0, H = 0, dpr = 1, t0 = performance.now(), last = t0, lvl = 0, drops = [], run = true;
  const col = () => getComputedStyle(document.documentElement).getPropertyValue('--ink').trim() || '#E3122F';
  const size = () => { dpr = Math.min(2, window.devicePixelRatio || 1); W = innerWidth; H = innerHeight; c.width = W * dpr | 0; c.height = H * dpr | 0; c.style.width = W + 'px'; c.style.height = H + 'px'; };
  size(); addEventListener('resize', size);
  const frame = now => { if (!run) return; const dt = Math.min(0.05, (now - last) / 1000); last = now; const t = (now - t0) / 1000, p = Math.max(0, Math.min(1, window.__bootP || 0));
    lvl += (p - lvl) * Math.min(1, dt * 2.2); g.setTransform(dpr, 0, 0, dpr, 0, 0); g.clearRect(0, 0, W, H); const ink = col();
    const r = bar ? bar.getBoundingClientRect() : { left: W * 0.2, top: H * 0.6, width: W * 0.6, height: 18 }, cx = r.left + r.width / 2, tankTop = r.top - 2, tankBot = r.top + r.height + 2;
    // the stream: from the top of the screen down to the surface, swaying a touch, thinner as it falls
    const sw = 1 + 0.25 * Math.sin(t * 2.1), x0 = cx + Math.sin(t * 0.9) * 6, yS = tankTop + (1 - lvl) * (tankBot - tankTop) * 0.92;
    g.fillStyle = ink; g.beginPath(); g.moveTo(x0 - 22 * sw, -10); g.bezierCurveTo(x0 - 16 * sw, yS * 0.3, x0 - 9, yS * 0.7, x0 - 7 + Math.sin(t * 7) * 2, yS); g.lineTo(x0 + 7 + Math.cos(t * 6.3) * 2, yS); g.bezierCurveTo(x0 + 9, yS * 0.7, x0 + 16 * sw, yS * 0.3, x0 + 22 * sw, -10); g.closePath(); g.fill();
    g.fillStyle = 'rgba(255,255,255,.22)'; g.beginPath(); g.moveTo(x0 - 12 * sw, 0); g.bezierCurveTo(x0 - 9, yS * 0.35, x0 - 5, yS * 0.7, x0 - 4, yS); g.lineTo(x0 - 1, yS); g.bezierCurveTo(x0 - 2, yS * 0.7, x0 - 6, yS * 0.35, x0 - 8 * sw, 0); g.closePath(); g.fill();
    // the tank: the paint in it, with a surface that rolls and heaves where the stream lands
    g.save(); g.beginPath(); g.roundRect(r.left + 2, r.top + 2, r.width - 4, r.height - 4, 3); g.clip();
    g.fillStyle = ink; g.beginPath(); const N = 40; for (let i = 0; i <= N; i++) { const x = r.left + i / N * r.width, d = (x - cx) / 26, y = yS + 2.5 * Math.sin(i * 0.9 + t * 5.1) + 1.8 * Math.sin(i * 1.7 - t * 7.3) - 7 * Math.exp(-d * d) * (0.6 + 0.4 * Math.sin(t * 9)); i ? g.lineTo(x, y) : g.moveTo(x, y); }
    g.lineTo(r.left + r.width, tankBot + 20); g.lineTo(r.left, tankBot + 20); g.closePath(); g.fill();
    g.fillStyle = 'rgba(255,255,255,.28)'; g.fillRect(r.left, yS + 2, r.width, 3); g.restore();
    // drops flung up where the stream lands, falling back in
    if (Math.random() < 0.5 && drops.length < 24) drops.push({ x: x0 + (Math.random() - 0.5) * 10, y: yS, vx: (Math.random() - 0.5) * 120, vy: -(60 + Math.random() * 110), r: 1.5 + Math.random() * 3, life: 0.9 });
    g.fillStyle = ink; for (let i = drops.length - 1; i >= 0; i--) { const d = drops[i]; d.life -= dt; d.x += d.vx * dt; d.y += d.vy * dt; d.vy += 520 * dt; if (d.life <= 0 || d.y > yS + 6) { drops.splice(i, 1); continue; } g.beginPath(); g.arc(d.x, d.y, d.r, 0, 6.2832); g.fill(); }
    requestAnimationFrame(frame); };
  requestAnimationFrame(frame);
  const stop = () => { const b = document.getElementById('boot'); if (b && b.classList.contains('gone')) { run = false; return; } setTimeout(stop, 500); }; setTimeout(stop, 2000);
})();
</script>''')
# the loading tells the paint where it has got to
rep("function bootTo(p, ceil, dur, msg) {\n  if (msg && bootMsgEl) bootMsgEl.textContent = msg; if (!bootFill) return;", "function bootTo(p, ceil, dur, msg) {\n  if (msg && bootMsgEl) bootMsgEl.textContent = msg; window.__bootP = Math.max(window.__bootP || 0, ceil); if (!bootFill) return;")
rep("  const go = e => { if (!bootHold) return; if (e) { e.preventDefault(); e.stopImmediatePropagation(); } bootHold = false;", "  window.__bootP = 1;\n  const go = e => { if (!bootHold) return; if (e) { e.preventDefault(); e.stopImmediatePropagation(); } bootHold = false;")
css = '''
/* the loading screen: the paint pouring in */
.bootc{position:absolute;inset:0;width:100%;height:100%;pointer-events:none}
.boot .bootbar{width:min(72vw,340px);height:44px;border-radius:6px;background:rgba(255,255,255,.55);border:2.5px solid var(--black);box-shadow:3px 3px 0 var(--black),inset 0 -3px 8px rgba(0,0,0,.18);overflow:visible}
.boot .bootbar i{display:none}
.boot .boottc{position:relative;z-index:1;width:min(60vw,280px)}
.boot .bootmsg{position:relative;z-index:1}
'''
i = s.index('<div id="stage">'); j = s.rfind('</style>', 0, i); s = s[:j] + css + s[j:]
m = re.search(r'<p class="ver">Version (\d+)</p>', s); v = int(m.group(1)); s = s.replace(m.group(0), '<p class="ver">Version %d</p>' % (v + 1))
open(DST, 'w').write(s); print('ok', n0, '->', len(s), 'v', v + 1)
subprocess.run(['python3', S + '/ws/gen/sfx_index.py', S + '/ws/sfx/gains.json'], check=True)
