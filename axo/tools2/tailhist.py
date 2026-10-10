import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo2')
import numpy as np
from geo import M
m = M('stand')
# slices along z behind the hips: extent in x and y, to find the tail root where the trunk narrows into the tail
for z in np.arange(0.5, -1.1, -0.05):
    sel = np.abs(m.P[:, 2] - z) < 0.025
    if sel.sum() < 5: continue
    q = m.P[sel]; print(f'z={z:+.2f} n={sel.sum():4d} x[{q[:,0].min():+.2f},{q[:,0].max():+.2f}] y[{q[:,1].min():+.2f},{q[:,1].max():+.2f}]')
print('crawl mesh slices along z (head at +z):')
m = M('crawl')
for z in np.arange(0.95, -1.0, -0.1):
    sel = np.abs(m.P[:, 2] - z) < 0.05
    if sel.sum() < 5: continue
    q = m.P[sel]; print(f'z={z:+.2f} n={sel.sum():4d} x[{q[:,0].min():+.2f},{q[:,0].max():+.2f}] y[{q[:,1].min():+.2f},{q[:,1].max():+.2f}]')
