import sys; sys.path.insert(0, '.')
import numpy as np
import rig7crawl as R
from mesh import Mesh
z = np.load(R.O + 'crawl7_geo.npz', allow_pickle=True); P, T, lab = z['P'], z['T'], z['lab']
m = Mesh(P, T)
for kind in ('leg', 'arm'):
    L = R.limb_line(m, lab, 'L', kind)
    print(kind, 'iw', L['iw'], 'ie', L['ie'], 'n', len(L['pts']), 'Lt', round(L['cum'][-1], 3))
    for i, (p, r, c) in enumerate(zip(L['pts'], L['rad'], L['cum'])):
        print(f'  {i:3d} s {c:.3f} r {r:.3f} c {p.round(3)}')
