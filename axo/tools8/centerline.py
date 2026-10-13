# Centre lines of the limbs, the tail and the ears from geodesic rings: the (smoothed) geodesic distance from a tip, banded, each band's
# largest connected piece's centroid and mean radius.
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import meshkit as mk
from scipy.sparse.csgraph import connected_components
def rings(Pw, G, E, A, seeds, step=0.03, width=0.06, maxd=1.5, rmax=0.3, smooth=6):
    d = mk.geodesic(G, seeds); d = mk.smooth_scalar(E, len(Pw), d, iters=smooth, lam=0.5); out = []
    for b in range(int(maxd / step)):
        lo = b * step; vs = np.where((d >= lo) & (d < lo + width))[0]
        if len(vs) < 3: continue
        nc, lab = connected_components(A[vs][:, vs], directed=False); big = np.argmax(np.bincount(lab)); vv = vs[lab == big]
        cen = Pw[vv].mean(0); rad = np.linalg.norm(Pw[vv] - cen, axis=1).mean(); out.append((lo + width / 2, cen, rad, nc))
        if rad > rmax: break
    return d, out
