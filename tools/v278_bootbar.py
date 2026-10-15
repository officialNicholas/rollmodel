"""v278: the loading screen's bar made premium with Ludo.ai art. It was a white box with paint drawn in code; now it's a cream capsule
with a chunky glossy rim and a deep navy track (Ludo), the paint in the track is a real roller stroke's streaks (Ludo) in your own ink,
and a paint roller (Ludo, stood upright, its paint recoloured to your ink) rides the front of the paint, pushing it along: bobbing on
the track, leaning in when it hurries, flinging a few flecks and the odd drip, then lifting away when the bar is full. The paint is
shinier where it's fresh, a shine sweeps along it now and then, and the track's inner shadow sits over it so it looks poured in.
Under the bar the message sits on the left and the percent on the right. If any of it fails to draw, the plain fill comes back."""
import base64, os
A = os.path.dirname(os.path.abspath(__file__)) + '/assets/'
def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)
def region(s, a, b, new):
    assert s.count(a) == 1, (s.count(a), a[:120]); i = s.index(a); j = s.index(b, i) + len(b); return s[:i] + new + s[j:]
def uri(k):
    return 'data:image/webp;base64,' + base64.b64encode(open(A + 'boot_' + k + '.webp', 'rb').read()).decode()

JS = r"""(() => { const c = document.getElementById('bootC'), bar = document.querySelector('.bootbar'), pctEl = document.getElementById('bootPct'); if (!c || !c.getContext || !bar) return; const g = c.getContext('2d'); if (!g) return;
  // (v278) the bar is Ludo art: a cream capsule with a deep navy track, the paint in it (a roller stroke's streaks, in your ink), and a paint roller riding the front of the paint
  const SRC = { frame: '@frame@', track: '@track@', shade: '@trackshade@', tone: '@paint_tone@', rb: '@roller_base@', rp: '@roller_paint@', rt: '@roller_tone@' }, IM = {};
  let ok = 0, n = 0, run = true;
  const fail = () => { if (!run) return; run = false; try { g.setTransform(1, 0, 0, 1, 0, 0); g.clearRect(0, 0, c.width, c.height); } catch (e) {} bar.classList.add('plain'); }; // (if any of it fails, the plain fill comes back)
  for (const k in SRC) { n++; const im = new Image(); im.onload = () => { ok++; }; im.onerror = fail; im.src = SRC[k]; IM[k] = im; }
  let W = 0, H = 0, dpr = 1, t0 = performance.now(), last = t0, lvl = 0, spd = 0, ink = '', pct = -1, inA = 0, outT = 0, dripT = 0.8;
  const off = document.createElement('canvas'), og = off.getContext('2d'), mk = document.createElement('canvas'), mg = mk.getContext('2d'), rol = document.createElement('canvas'), rg = rol.getContext('2d'), drops = [];
  const col = () => getComputedStyle(document.documentElement).getPropertyValue('--ink').trim() || '#E3122F';
  const size = () => { dpr = Math.min(2, window.devicePixelRatio || 1); W = c.clientWidth || innerWidth; H = c.clientHeight || innerHeight; c.width = W * dpr | 0; c.height = H * dpr | 0; };
  size(); addEventListener('resize', size);
  // three slices: the capsule's round ends keep their shape and the middle stretches to the bar's width
  const s3 = (x, im, X, Y, w, h) => { const ih = im.naturalHeight, iw = im.naturalWidth, cap = ih >> 1, cw = cap * h / ih; x.drawImage(im, 0, 0, cap, ih, X, Y, cw, h); x.drawImage(im, cap, 0, iw - 2 * cap, ih, X + cw - 0.5, Y, Math.max(0, w - 2 * cw) + 1, h); x.drawImage(im, iw - cap, 0, cap, ih, X + w - cw, Y, cw, h); };
  // the roller in your ink: its paint is a mask and a light-and-shade layer, its frame and handle go over the top
  const tintRoller = k => { rol.width = IM.rb.naturalWidth; rol.height = IM.rb.naturalHeight; rg.globalCompositeOperation = 'source-over'; rg.clearRect(0, 0, rol.width, rol.height); rg.drawImage(IM.rp, 0, 0); rg.globalCompositeOperation = 'source-in'; rg.fillStyle = k; rg.fillRect(0, 0, rol.width, rol.height); rg.globalCompositeOperation = 'source-over'; rg.drawImage(IM.rt, 0, 0); rg.drawImage(IM.rb, 0, 0); };
  const frame = now => { if (!run) return; const dt = Math.min(0.05, (now - last) / 1000), dtR = Math.min(0.3, (now - last) / 1000); last = now; const t = (now - t0) / 1000, p = Math.max(0, Math.min(1, window.__bootP || 0));
    try {
    if (c.clientWidth && (c.clientWidth !== W || c.clientHeight !== H)) size();
    g.setTransform(dpr, 0, 0, dpr, 0, 0); g.clearRect(0, 0, W, H); g.globalAlpha = 1;
    if (ok < n) { requestAnimationFrame(frame); return; }
    const k = col(); if (k !== ink) { ink = k; tintRoller(k); }
    // the roller pushes the paint along: quick when there's far to go, easing in as it nears how far the loading has got (by the real time passed: loading keeps the page busy and frames come slowly)
    const gap = p - lvl, want = gap > 0.001 ? Math.min(0.9, Math.max(0.18, gap * 2)) : 0; spd += (want - spd) * Math.min(1, dtR * 6); lvl = Math.min(Math.max(lvl, p), lvl + spd * dtR); inA = Math.min(1, inA + dt * 3);
    const cr = c.getBoundingClientRect(), rb = bar.getBoundingClientRect(), X = rb.left - cr.left, Y = rb.top - cr.top, bw = rb.width, bh = rb.height, K = bh / 120;
    if (bw < 20 || bh < 10) { requestAnimationFrame(frame); return; }
    const tL = X + 25 * K, tR = X + bw - 26 * K, tT = Y + 25 * K, tB = Y + 94 * K, tH = tB - tT, fx = tL + lvl * (tR - tL), done = lvl > 0.995;
    g.globalAlpha = inA; s3(g, IM.frame, X, Y, bw, bh);
    // the paint, drawn apart and cut to the track: your ink, the stroke's streaks over it, wetter near the roller, and a shine sweeping along now and then
    const ow = Math.ceil(bw * dpr), oh = Math.ceil(bh * dpr); if (off.width !== ow || off.height !== oh) { off.width = mk.width = ow; off.height = mk.height = oh; mg.setTransform(dpr, 0, 0, dpr, 0, 0); s3(mg, IM.track, 0, 0, bw, bh); } // (the track's shape, put together once: cutting with it a slice at a time would wipe the rest)
    og.setTransform(dpr, 0, 0, dpr, 0, 0); og.globalCompositeOperation = 'source-over'; og.clearRect(0, 0, bw, bh);
    if (fx > tL + 0.5) { const fw = fx - X;
      og.fillStyle = k; og.fillRect(0, 0, fw, bh);
      og.globalCompositeOperation = 'source-atop'; og.drawImage(IM.tone, tL - X, tT - Y, tR - tL, tH);
      const gl = og.createLinearGradient(0, tT - Y, 0, tB - Y); gl.addColorStop(0, 'rgba(255,255,255,.34)'); gl.addColorStop(0.22, 'rgba(255,255,255,.1)'); gl.addColorStop(0.5, 'rgba(255,255,255,0)'); gl.addColorStop(0.78, 'rgba(0,0,0,0)'); gl.addColorStop(1, 'rgba(0,0,0,.22)'); og.fillStyle = gl; og.fillRect(0, 0, fw, bh); // (a rounded, glossy body to the paint: lit along the top, shaded along the bottom)
      const wet = og.createLinearGradient(fw - 70, 0, fw, 0); wet.addColorStop(0, 'rgba(255,255,255,0)'); wet.addColorStop(1, 'rgba(255,255,255,.2)'); og.fillStyle = wet; og.fillRect(Math.max(0, fw - 70), 0, 70, bh);
      const sx = (tL - X) - 50 + ((t % 2.8) / 2.8) * (bw + 100); if (sx < fw + 30) { const sh = og.createLinearGradient(sx - 30, 0, sx + 30, 0); sh.addColorStop(0, 'rgba(255,255,255,0)'); sh.addColorStop(0.5, 'rgba(255,255,255,.3)'); sh.addColorStop(1, 'rgba(255,255,255,0)'); og.fillStyle = sh; og.beginPath(); og.moveTo(sx - 8, 0); og.lineTo(sx + 26, 0); og.lineTo(sx + 8, bh); og.lineTo(sx - 26, bh); og.closePath(); og.fill(); }
      og.setTransform(1, 0, 0, 1, 0, 0); og.globalCompositeOperation = 'destination-in'; og.drawImage(mk, 0, 0); og.globalCompositeOperation = 'source-over';
      g.drawImage(off, X, Y, bw, bh); }
    s3(g, IM.shade, X, Y, bw, bh);
    // flecks flung off the back of the roller as it hurries, and now and then a drip off its foot
    const cyl = tH * 1.24, moving = Math.min(1, spd * 7) * (done ? 0 : 1);
    if (Math.random() < dt * 26 * moving) drops.push({ x: fx - 3, y: tT + Math.random() * tH, vx: -30 - Math.random() * 50, vy: -50 + Math.random() * 60, r: 0.8 + Math.random() * 1.3, life: 0.5 + Math.random() * 0.3, fleck: 1 });
    dripT -= dt * moving; if (dripT <= 0) { dripT = 0.9 + Math.random() * 1.4; drops.push({ x: fx + 1, y: (tT + tB) / 2 + cyl * 0.48, vx: 0, vy: 10, r: 1.8 + Math.random() * 1.2, life: 1.3 }); }
    g.fillStyle = k; for (let i = drops.length - 1; i >= 0; i--) { const d = drops[i]; d.life -= dt; d.vy += 420 * dt; d.x += d.vx * dt; d.y += d.vy * dt; if (d.life <= 0 || d.y > H + 20) { drops.splice(i, 1); continue; } g.globalAlpha = inA * Math.min(1, d.life * 3); g.beginPath(); if (d.fleck) g.arc(d.x, d.y, d.r, 0, 6.2832); else g.ellipse(d.x, d.y, d.r * 0.8, d.r * (1.2 + Math.min(0.8, d.vy / 300)), 0, 0, 6.2832); g.fill(); }
    // the roller rides the front: bobbing on the track, leaning in the faster it goes; when the bar is full it lifts away
    outT = done ? Math.min(1, outT + dt * 2.4) : Math.max(0, outT - dt * 4);
    const ra = inA * (1 - outT); if (ra > 0.01) { const sc = cyl / 103, bob = Math.sin(t * 19) * 0.8 * moving, lean = Math.min(0.12, spd * 0.45) - 0.02 + outT * 0.25;
      g.save(); g.globalAlpha = ra; g.translate(fx + outT * 16, (tT + tB) / 2 + bob - outT * 12); g.rotate(lean); g.drawImage(rol, -116 * sc, -55.5 * sc, 147 * sc, 120 * sc); g.restore(); }
    g.globalAlpha = 1;
    const pc = Math.round(lvl * 100); if (pctEl && pc !== pct) { pct = pc; pctEl.textContent = pc + '%'; }
    } catch (e) { fail(); return; }
    requestAnimationFrame(frame); };
  requestAnimationFrame(frame);
  const stop = () => { const b = document.getElementById('boot'); if (b && b.classList.contains('gone')) { run = false; return; } setTimeout(stop, 500); }; setTimeout(stop, 2000);
})();"""

CSS = ("\n/* (v278) the loading bar: Ludo's capsule drawn on the canvas, so the box itself is only a place to put it; the message left and the percent right under it */"
       "\n#boot .bootbar{width:min(76vw,330px);height:58px;border:0;border-radius:0;background:transparent;box-shadow:none;overflow:visible}"
       "\n#boot .bootbar.plain{height:40px;border:2.5px solid var(--black);border-radius:6px;background:rgba(255,255,255,.55);box-shadow:3px 3px 0 var(--black);overflow:hidden}"
       "\n#boot .bootpct{position:absolute;right:6px;top:calc(100% + 16px);font:900 14px/1.4 var(--font-head);letter-spacing:.06em;color:#2A2437;font-variant-numeric:tabular-nums;transition:opacity .3s}"
       "\n#boot .bootbar.plain .bootpct{display:none}"
       "\n#boot .bootmsg{width:min(76vw,330px);max-width:none;box-sizing:border-box;padding:0 6px;text-align:left;margin-top:-2px}"
       "\n#boot.tap .bootmsg{text-align:center}#boot.tap .bootpct{opacity:0}\n")

def apply(s):
    js = JS
    for k in ['frame', 'track', 'trackshade', 'paint_tone', 'roller_base', 'roller_paint', 'roller_tone']:
        js = js.replace('@' + k + '@', uri(k))
    assert '@frame@' not in js and '@roller_tone@' not in js
    s = region(s, "(() => { const c = document.getElementById('bootC')", "setTimeout(stop, 2000);\n})();", js)
    s = rep(s, '<div class="bootbar" aria-hidden="true"><i id="bootFill"></i></div>', '<div class="bootbar" aria-hidden="true"><i id="bootFill"></i><b class="bootpct" id="bootPct">0%</b></div>')
    a = '.boot .bootmsg{position:relative;z-index:1}'
    s = rep(s, a, a + CSS)
    return s
