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
