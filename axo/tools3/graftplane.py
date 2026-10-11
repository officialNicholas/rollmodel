# choose the graft plane: all gills of both meshes behind it (margin m), the crawl's cut loop as close to the stand's surface as possible
import numpy as np, sys
sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo3')
from remesh import Surface
s = np.load('stand7_rig.npz', allow_pickle=True); c = np.load('crawl7_rig.npz', allow_pickle=True)
names = list(s['names']); gi = [i for i, n in enumerate(names) if n.startswith('gill')]
def dom(z): return z['idx'][np.arange(len(z['idx'])), z['w'].argmax(1)]
t = c['C'] - s['C']; C = c['C']; Ps = s['P'] + t; Pc = c['P']; ds, dc = dom(s), dom(c)
gs = np.isin(ds, gi); gc = np.isin(dc, gi)
Ss = Surface(Ps, s['T'][~gs[s['T']].any(1)])   # the stand's skull without its gill stalks
G = np.vstack([Ps[gs], Pc[gc]]) - C
def loop_dev(P, T, n, d, near=0.62):
    q = P - C; f = q @ n - d; e = np.concatenate([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]]); e = np.unique(np.sort(e, 1), axis=0)
    cr = e[(np.sign(f[e[:, 0]]) != np.sign(f[e[:, 1]])) & (np.linalg.norm(q[e[:, 0]], axis=1) < near)]
    u = f[cr[:, 0]] / (f[cr[:, 0]] - f[cr[:, 1]]); pts = P[cr[:, 0]] + u[:, None] * (P[cr[:, 1]] - P[cr[:, 0]]); return pts
for m in (0.012, 0.02):
    print('margin', m)
    for a in range(0, 91, 10):
        ar = np.radians(a); n = np.array([0, np.sin(ar), -np.cos(ar)]); d = (G @ n).min() - m
        pts = loop_dev(Pc, c['T'], n, d); q = Ss.project(pts); dev = np.linalg.norm(q - pts, axis=1)
        rel = pts - C; yaw = np.degrees(np.arctan2(np.abs(rel[:, 0]), rel[:, 2])); pit = np.degrees(np.arcsin(np.clip(rel[:, 1] / np.linalg.norm(rel, axis=1), -1, 1)))
        # where the plane crosses the midline top and back
        mid = np.abs(rel[:, 0]) < 0.02
        print(f'  a {a:3d}: d {d:+.3f}  loop pts {len(pts)}  dev p50 {np.median(dev)*1000:5.1f} p90 {np.percentile(dev, 90)*1000:5.1f} max {dev.max()*1000:5.1f} mm   '
              f'midline crossings (z,y): {np.round(rel[mid][:, [2, 1]][np.argsort(rel[mid][:, 1])][[0, -1]], 3).tolist() if mid.sum() > 1 else "-"}  yaw range {yaw.min():.0f}..{yaw.max():.0f}')
