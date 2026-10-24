"""v474: the paint in the results bar, polished. The user: "the sloshing paint itself was the concern".

- The seam where the two paints meet used to flip its bulge with a sudden jump every couple of seconds; it now rolls smoothly from
  one side to the other, and on the results bar it's a gentle S-curve rather than a wild wobble (about a third as wide).
- The seam is drawn clean: a thin dark line with a fine light edge along it, so the two colours butt up crisply.
- The surface is calmer: a slow, low swell that only sloshes up when the shares are moving, then settles.
- No more stray drips: the random drops running down the glass and the drops flung off the edges are gone from the results bar
  (the speck at the bottom-left), so it reads as one clean tank of paint. The glossy band on the paint is a touch brighter.
"""

def rep(s, a, b, n=1):
    c = s.count(a); assert c == n, (c, n, a[:160]); return s.replace(a, b)

def apply(s):
    s = rep(s, "Math.sin(y / h * Math.PI) * 0.7 * Math.sign(Math.sin(t * 1.7 + ph)));", "Math.sin(y / h * Math.PI) * 0.7 * Math.sin(t * 1.7 + ph)); // (v474: the bulge rolls over smoothly, no jump)")
    s = rep(s, "const wild = L.surf ? 2.2 : 1,", "const wild = L.surf ? 0.7 : 1,")
    s = rep(s, "surf = x => !L.surf ? 0 : h * (0.13 + 0.045 * Math.sin(x / w * 6.3 + t * 1.9 + sg.ph) + 0.025 * Math.sin(x / w * 13.1 - t * 2.7 + sg.ph * 2.0) + sl * 0.12 * Math.sin(x / w * 9.0 + t * 7.0));",
               "surf = x => !L.surf ? 0 : h * (0.11 + 0.022 * Math.sin(x / w * 5.2 + t * 1.3 + sg.ph) + 0.01 * Math.sin(x / w * 11.0 - t * 1.9 + sg.ph * 2.0) + sl * 0.08 * Math.sin(x / w * 8.0 + t * 6.0)); // (v474: a calmer swell)")
    s = rep(s, "g.save(); g.clip(); g.lineWidth = 5; g.strokeStyle = 'rgba(0,0,0,.2)';", "g.save(); g.clip(); g.lineWidth = 3.5; g.strokeStyle = 'rgba(0,0,0,.28)';")
    s = rep(s, "i ? g.lineTo(ex, y) : g.moveTo(ex, y); } g.stroke(); }",
               "i ? g.lineTo(ex, y) : g.moveTo(ex, y); } g.stroke(); g.save(); g.lineWidth = 1.3; g.strokeStyle = 'rgba(255,255,255,.45)'; g.stroke(); g.restore(); } // (v474: a fine light edge along the seam)")
    s = rep(s, "g.lineWidth = 2; g.strokeStyle = 'rgba(255,255,255,.5)';", "g.lineWidth = 1.6; g.strokeStyle = 'rgba(255,255,255,.55)';")
    s = rep(s, "if (L.surf && h >= 12 && L.drops.length < 28 && Math.random() < 0.012)", "if (false && L.surf && h >= 12 && L.drops.length < 28 && Math.random() < 0.012)")
    s = rep(s, "if (h >= 18) for (const [x, v] of [[sg.x0, sg.v0], [sg.x1, sg.v1]])", "if (h >= 18 && !L.surf) for (const [x, v] of [[sg.x0, sg.v0], [sg.x1, sg.v1]])")
    s = rep(s, "sh.addColorStop(L.surf ? 0.2 : 0.1, L.surf ? 'rgba(255,255,255,.24)' : 'rgba(255,255,255,.26)');", "sh.addColorStop(L.surf ? 0.24 : 0.1, L.surf ? 'rgba(255,255,255,.32)' : 'rgba(255,255,255,.26)');")
    return s

# (second pass, after seeing it) the two paints each drew their own wavy edge with a different phase, and each sat its surface at a
# different height, so at the seam they left a dark gap at the top and a sharp wedge where one overlapped the other; the slosh could
# also swing the edge nearly the bar's full height. On the results bar the two sides of a seam now share one curve and one slosh,
# every edge starts at the surface where it stands, the surface is one continuous swell across both paints, and the slosh is capped.
NEW_BLOCK = """    const N = 12, SG = L.segs;
    // (v474) on the results bar, two paints that meet share one seam (one curve, one slosh) and one surface: no gap, no wedge
    let sl = 0;
    if (L.surf) { SG.forEach(q => { q.e0 = q.ph; q.e1 = q.ph + 1.3; q.m0 = q.a0; q.m1 = q.a1; sl = Math.max(sl, q.a0 + q.a1); });
      for (let i = 0; i + 1 < SG.length; i++) { const p = SG[i], n = SG[i + 1]; if (Math.abs(p.x1 - n.x0) < 0.004) { n.e0 = p.e1; p.m1 = n.m0 = Math.max(p.a1, n.a0); } }
      sl = Math.min(1, sl * 30); }
    // the surface of the paint, when it shows: a little below the top, one slow swell across every share, a slosh while they move
    const surf = x => !L.surf ? 0 : h * (0.11 + 0.022 * Math.sin(x / w * 5.2 + t * 1.3) + 0.01 * Math.sin(x / w * 11.0 - t * 1.9 + 1.7) + sl * 0.06 * Math.sin(x / w * 8.0 + t * 6.0));
    const amp = m => L.surf ? h * (0.07 + Math.min(0.12, m * 12)) : h * (0.1 + Math.min(0.9, m * 40));
    for (const sg of L.segs) {
      const a0 = sg.x0 <= 0.0005 ? 0 : amp(L.surf ? sg.m0 : sg.a0), a1 = sg.x1 >= 0.9995 ? 0 : amp(L.surf ? sg.m1 : sg.a1), p0 = L.surf ? sg.e0 : sg.ph, p1 = L.surf ? sg.e1 : sg.ph + 1.3;
      if (sg.x1 - sg.x0 <= 0.0005) continue;
      // each side runs from the surface where it stands down to the floor
      const ex0 = y => a0 ? edge(sg.x0, a0, p0, y) : -6, ex1 = y => a1 ? edge(sg.x1, a1, p1, y) : w + 6, yA = surf(sg.x0 * w), yB = surf(sg.x1 * w);
      g.beginPath();
      for (let i = 0; i <= N; i++) { const y = yA + i / N * (h - yA), x = ex0(y); i ? g.lineTo(x, y) : g.moveTo(x, y); }
      for (let i = N; i >= 0; i--) { const y = yB + i / N * (h - yB); g.lineTo(ex1(y), y); }
      if (L.surf) { const xa = ex1(yB), xb = ex0(yA), M = 16; for (let j = 1; j < M; j++) { const x = xa + (xb - xa) * j / M; g.lineTo(x, surf(x)); } }
      g.closePath();
      if (L.surf) { const gr = g.createLinearGradient(0, 0, 0, h); gr.addColorStop(0, liqShade(sg.col, 0.2)); gr.addColorStop(0.42, sg.col); gr.addColorStop(1, liqShade(sg.col, -0.32)); g.fillStyle = gr; } else g.fillStyle = sg.col; g.fill();
      if (L.surf) { // a clean seam (a thin dark line with a fine light edge) where this paint meets the next, and a wet crest along its surface
        g.save(); g.clip();
        for (const [ex, a, y0] of [[ex0, a0, yA], [ex1, a1, yB]]) if (a) { g.beginPath(); for (let i = 0; i <= N; i++) { const y = y0 + i / N * (h - y0), x = ex(y); i ? g.lineTo(x, y) : g.moveTo(x, y); }
          g.lineWidth = 3.5; g.strokeStyle = 'rgba(0,0,0,.28)'; g.stroke(); g.lineWidth = 1.3; g.strokeStyle = 'rgba(255,255,255,.45)'; g.stroke(); }
        const xa = ex1(yB), xb = ex0(yA); g.lineWidth = 1.6; g.strokeStyle = 'rgba(255,255,255,.55)'; g.beginPath(); for (let j = 0; j <= 24; j++) { const x = xb + (xa - xb) * j / 24, y = surf(x) + 1.4; j ? g.lineTo(x, y) : g.moveTo(x, y); } g.stroke();
        g.restore(); }
"""

_apply1 = apply
def apply(s):
    s = _apply1(s)
    a = s.index("    const N = 12;\n    for (const sg of L.segs) {"); b = s.index("      // now and then a drop breaks off the surface", a)
    assert s.count(s[a:b]) == 1 and b - a < 6000
    return s[:a] + NEW_BLOCK + s[b:]
