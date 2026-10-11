# side sections (x = const) of the stand head (moved onto the crawl's face centre) and the crawl, overlaid (PIL plot)
import numpy as np, sys
from PIL import Image, ImageDraw, ImageFont
sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo3')
s = np.load('stand7_rig.npz', allow_pickle=True); c = np.load('crawl7_rig.npz', allow_pickle=True)
names = list(s['names']); gi = [i for i, n in enumerate(names) if n.startswith('gill')]; hi = names.index('head')
t = c['C'] - s['C']; C = c['C']
def seg(P, T, x0):
    p = P[T]; d = p[:, :, 0] - x0; out = []
    for a, b in ((0, 1), (1, 2), (2, 0)):
        m = (d[:, a] > 0) != (d[:, b] > 0); u = d[m, a] / (d[m, a] - d[m, b]); out.append((m, p[m, a] + u[:, None] * (p[m, b] - p[m, a])))
    segs = []
    pts = {}
    for k, (m, q) in enumerate(out):
        for i, v in zip(np.where(m)[0], q): pts.setdefault(i, []).append(v)
    return [v for v in pts.values() if len(v) == 2]
def dom(z): return z['idx'][np.arange(len(z['idx'])), z['w'].argmax(1)]
W, H = 600, 600; sc = 480; ox, oy = 0.75, 0.62   # z in [-0.75, 0.45], y in [-0.58, 0.62]
def px(zr, yr): return ((zr + ox) * sc, (oy - yr) * sc)
ims = []
for x0 in (0.0, 0.12, 0.24, 0.36):
    im = Image.new('RGB', (W, H), 'white'); d = ImageDraw.Draw(im)
    for g in np.arange(-0.7, 0.5, 0.1):
        d.line([px(g, -0.6), px(g, 0.62)], fill=(230, 230, 230)); d.line([px(-0.75, g), px(0.45, g)], fill=(230, 230, 230))
    d.ellipse([px(-0.329, 0.329), px(0.329, -0.329)], outline=(170, 170, 170))
    for z, col, off in ((s, (220, 40, 40), t), (c, (40, 90, 220), 0)):
        P = z['P'] + off; dd = dom(z)
        for a, b in seg(P, z['T'], x0): d.line([px(a[2] - C[2], a[1] - C[1]), px(b[2] - C[2], b[1] - C[1])], fill=col, width=2)
        g = np.isin(dd, gi) & (np.abs(P[:, 0] - x0) < 0.02)
        for p in P[g]: x, y = px(p[2] - C[2], p[1] - C[1]); d.point((x, y), fill=tuple(int(0.5 * v + 127) for v in col))
        hv = (dd == hi) & (np.abs(P[:, 0] - x0) < 0.012)
        for p in P[hv]: x, y = px(p[2] - C[2], p[1] - C[1]); d.rectangle([x - 1, y - 1, x + 1, y + 1], fill=(0, 0, 0) if col[0] > 100 else (0, 160, 0))
    d.text((6, 6), f'x = {x0}  red: stand head (moved), blue: crawl; dots gills; black/green: head-dominated', fill=(0, 0, 0))
    ims.append(im)
out = Image.new('RGB', (W * 4, H), 'white')
for k, im in enumerate(ims): out.paste(im, (k * W, 0))
out.save('out/headsec.png')
for nm, z, off in (('stand', s, t), ('crawl', c, 0)):
    P = z['P'] + off; dd = dom(z); g = np.isin(dd, gi); q = P[g] - C
    print(nm, 'gill verts: y_rel min %.3f  z_rel range %.3f..%.3f  |x| max %.3f' % (q[:, 1].min(), q[:, 2].min(), q[:, 2].max(), np.abs(q[:, 0]).max()))
    hv = dd == hi; q = P[hv] - C; print(nm, 'head-dominated: y_rel min %.3f, z_rel min %.3f' % (q[:, 1].min(), q[:, 2].min()))
