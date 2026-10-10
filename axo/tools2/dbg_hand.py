import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo2')
import numpy as np, json
from rigcore import *
m = M('stand'); src = m.src; names = [str(n) for n in src['names']]
JN, WT = src['JN'], src['WT']; Wmx = np.zeros((m.n, len(names))); cnt = np.zeros(m.n)
for c in range(4): np.add.at(Wmx, (m.wid, JN[:, c]), WT[:, c])
np.add.at(cnt, m.wid, 1); Wmx /= cnt[:, None]
print('welded verts', m.n, 'edges', len(m.E), 'graph components', m.comps(np.ones(m.n, bool))[0])
hand = np.array([0.478, 0.705, 0.766]); fa = np.array([0.331, 0.87, 0.666]); fwdh = unit(hand - fa)
hw = Wmx[:, names.index('mixamorig:LeftHand')]
for thr in (0.25, 0.5, 0.8):
    reg = hw > thr; print('Hand.L weight >', thr, ':', reg.sum(), 'verts, bbox', m.P[reg].min(0).round(2), m.P[reg].max(0).round(2), 'components', m.comps(reg)[0])
reg = (hw > 0.25) & (((m.P - hand) @ fwdh) > -0.02); print('region fwd', reg.sum(), 'comps', m.comps(reg)[0])
nc, lab = m.comps(reg); print('comp sizes', np.bincount(lab[lab >= 0]))
srcv = np.where(reg)[0]; srcv = srcv[np.argmin(np.linalg.norm(m.P[srcv] - hand, axis=1))]; print('source', m.P[srcv].round(3), 'dist to wrist', np.linalg.norm(m.P[srcv] - hand).round(3))
d = m.geo(srcv, limit=1.0, mask=reg); fin = np.isfinite(d); print('reached', fin.sum(), 'dmax', d[fin].max().round(3))
far = np.argsort(-np.where(fin, d, -1))[:10]; print('farthest', [(round(float(d[v]), 3), m.P[v].round(3).tolist(), round(float(np.linalg.norm(m.P[v] - hand)), 3)) for v in far])
# euclid vs geodesic for the region: ratio
eu = np.linalg.norm(m.P[fin] - m.P[srcv], axis=1); print('geo/euclid ratio p50 p90', np.percentile(d[fin] / np.maximum(eu, 1e-6), [50, 90]).round(2))
# edge lengths
el = np.linalg.norm(m.P[m.E[:, 0]] - m.P[m.E[:, 1]], axis=1); print('edge len p50 p90 max', np.percentile(el, [50, 90, 100]).round(4))
# is the mesh graph built right? welded: check the number of unique positions
print('unique pos', len(np.unique(np.round(m.P0, 5), axis=0)), 'P0', len(m.P0))
