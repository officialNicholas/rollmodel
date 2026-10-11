# exact planar cross-sections of a welded mesh: the loops (connected chains of cut segments, keyed by the mesh edges they cross)
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
def plane_loops(P, T, o, nrm, near=None, rmax=None):
    """cut by the plane through o with normal nrm; returns a list of loops (each: dict pts (k,3) segment endpoints, segs (m,2,3), length, centroid);
    with `near`, only the loop that passes closest to that point (and with rmax, only segments within rmax of it are considered)"""
    nrm = np.asarray(nrm, float); nrm = nrm / np.linalg.norm(nrm); d = (P - o) @ nrm
    dt = d[T]; cut = (dt.min(1) < 0) & (dt.max(1) > 0)
    if rmax is not None and near is not None:
        cc = P[T].mean(1); cut &= np.linalg.norm(cc - near, axis=1) < rmax
    ts = np.where(cut)[0]; keys = {}; segs = []; ek = []
    for t in ts:
        e = []
        for a, b in ((0, 1), (1, 2), (2, 0)):
            ia, ib = T[t, a], T[t, b]; da, db = d[ia], d[ib]
            if (da < 0) != (db < 0):
                k = (min(ia, ib), max(ia, ib))
                if k not in keys: u = da / (da - db); keys[k] = (len(keys), P[ia] + u * (P[ib] - P[ia]))
                e.append(keys[k][0])
        if len(e) == 2: ek.append(e)
    if not ek: return []
    ek = np.array(ek); nk = len(keys); pos = np.zeros((nk, 3))
    for k, (i, p) in keys.items(): pos[i] = p
    A = coo_matrix((np.ones(len(ek)), (ek[:, 0], ek[:, 1])), shape=(nk, nk)); nc, lab = connected_components(A, directed=False)
    loops = []
    for c in range(nc):
        se = ek[lab[ek[:, 0]] == c]; sp = pos[se]; L = np.linalg.norm(sp[:, 0] - sp[:, 1], axis=1)
        mid = sp.mean(1); cen = (mid * L[:, None]).sum(0) / max(L.sum(), 1e-12)
        loops.append(dict(segs=sp, length=float(L.sum()), centroid=cen, closed=bool(np.all(np.bincount(se.ravel(), minlength=nk)[np.unique(se)] == 2))))
    if near is not None:
        best = min(loops, key=lambda l: np.linalg.norm(l['segs'].mean(1) - near, axis=1).min()); return [best]
    return loops
