import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo2')
import numpy as np
from rigcore import *
m = M('stand'); src = m.src; names = [str(n) for n in src['names']]
JN, WT = src['JN'], src['WT']; Wmx = np.zeros((m.n, len(names))); cnt = np.zeros(m.n)
for c in range(4): np.add.at(Wmx, (m.wid, JN[:, c]), WT[:, c])
np.add.at(cnt, m.wid, 1); Wmx /= cnt[:, None]
toes = np.array([0.269, 0.067, 0.727]); fwdf = unit([0.25, -0.1, 1.0])
wf = Wmx[:, names.index('mixamorig:LeftToeBase')] + Wmx[:, names.index('mixamorig:LeftFoot')]
region = (wf > 0.25) & (m.P[:, 2] > toes[2] - 0.02)
print('region', region.sum(), 'comps', m.comps(region)[0], 'bbox', m.P[region].min(0).round(2), m.P[region].max(0).round(2))
t = (m.P - toes) @ fwdf
for tk in [0.08, 0.06, 0.04, 0.03, 0.02, 0.01, 0.0, -0.02]:
    cap = region & (t > tk); nc, lab = m.comps(cap); print(f'tk {tk:+.2f} cap {cap.sum()} comps {nc} sizes {np.bincount(lab[lab>=0]).tolist()}')
# where are the toe bases in z? print verts of region with t between 0 and 0.03
sel = region & (t > 0.0) & (t < 0.03); print('junction band verts', sel.sum(), 'x', np.round(np.sort(m.P[sel][:, 0]), 2))
