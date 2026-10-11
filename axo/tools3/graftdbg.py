# angle-space picture of the back of the head: where each mesh's gills root, how far the (pre-morphed) crawl skull is from the stand's
import numpy as np, sys
from PIL import Image, ImageDraw
sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo3')
import headgraft as H
from remesh import Surface, edges_of
import json
O = H.O
s = np.load(O + 'stand7_rig.npz', allow_pickle=True); c = np.load(O + 'crawl7_rig.npz', allow_pickle=True)
cm = json.load(open(O + 'www/c7/axo_crawl.json')); names = [b['name'] for b in cm['bones']]; bi = {k: i for i, k in enumerate(names)}; NB = len(names)
Ws, Wc = H.dense(s, NB), H.dense(c, NB); gb = [bi[k] for k in names if k.startswith('gill')]
t = c['C'] - s['C']; C = c['C']; Ps = s['P'] + t; Ts = s['T']; Pc = c['P'].copy(); Tc = c['T']
gWs, gWc = Ws[:, gb].sum(1), Wc[:, gb].sum(1); hWs = Ws[:, bi['head']] + Ws[:, bi['headfront']] + gWs; hWc = Wc[:, bi['head']] + Wc[:, bi['headfront']] + gWc
skull_s = Ts[(gWs[Ts] < 0.5).all(1) & (hWs[Ts] > 0.12).all(1)]; Ssk = Surface(Ps, skull_s)
q = Pc - C; r = np.linalg.norm(q, axis=1); yaw = np.degrees(np.arctan2(np.abs(q[:, 0]), q[:, 2]))
cand = (gWc < 0.3) & (hWc > 0.02) & (r < 0.7); d = np.zeros_like(Pc); d[cand] = Ssk.project(Pc[cand]) - Pc[cand]
f = H.ss((yaw - 70) / 30) * H.ss(hWc / 0.75) * (np.linalg.norm(d, axis=1) < 0.15) * cand; D = d * f[:, None]
keep = (f > 0.6) | (hWc < 0.01) | (yaw < 68) | (gWc > 0.3); D = H.fill(len(Pc), Tc, ~keep, D, order=2); Pc2 = Pc + D
def ang(P):
    q = P - C; r = np.linalg.norm(q, axis=1); return np.degrees(np.arctan2(q[:, 0], q[:, 2])), np.degrees(np.arcsin(np.clip(q[:, 1] / r, -1, 1))), r
# gill bases: gill vertices with a non-gill neighbour
def bases(P, T, g):
    E = edges_of(T)[0]; m = g[E[:, 0]] != g[E[:, 1]]; v = np.unique(E[m].ravel()); return v[g[v]]
bs = bases(Ps, Ts, gWs > 0.5); bc = bases(Pc2, Tc, gWc > 0.3)
W, Hh = 900, 700; y0, y1, p0, p1 = 60, 200, -60, 80
def px(y, p): return ((y - y0) / (y1 - y0) * W, (p1 - p) / (p1 - p0) * Hh)
im = Image.new('RGB', (W, Hh), 'white'); dr = ImageDraw.Draw(im)
# deviation heat of the crawl skull (non-gill, left side, behind yaw 60) from the stand's skull, after the pre-morph
cs = (gWc < 0.3) & (Pc2[:, 0] > 0) & (r < 0.75); yc, pc, rc = ang(Pc2[cs]); dev = np.linalg.norm(Ssk.project(Pc2[cs]) - Pc2[cs], axis=1)
for y_, p_, d_ in zip(yc, pc, dev):
    if y0 <= y_ <= y1 and p0 <= p_ <= p1:
        k = min(1, d_ / 0.03); col = (int(255 * k), int(200 * (1 - k)), 60); x, y = px(y_, p_); dr.rectangle([x - 2, y - 2, x + 2, y + 2], fill=col)
for v, col in ((bs, (0, 0, 255)), (bc, (0, 0, 0))):
    yy, pp, _ = ang((Ps if col[2] else Pc2)[v])
    for y_, p_ in zip(yy, pp):
        if y_ > 0: x, y = px(y_, p_); dr.ellipse([x - 3, y - 3, x + 3, y + 3], outline=col)
for g in range(70, 200, 10): dr.line([px(g, p0), px(g, p1)], fill=(220, 220, 220)); dr.text(px(g, p0 + 3), str(g), fill=(0, 0, 0))
for g in range(-50, 80, 10): dr.line([px(y0, g), px(y1, g)], fill=(220, 220, 220)); dr.text(px(y0 + 1, g), str(g), fill=(0, 0, 0))
dr.text((5, 5), 'yaw (x) / pitch (y) about the face centre; crawl skull deviation from the stand skull after the move: green 0 .. red >= 30 mm; blue o stand gill roots, black o crawl gill roots', fill=(0, 0, 0))
im.save(O + 'out/graft_angles.png'); print('ok', len(bs), len(bc))
