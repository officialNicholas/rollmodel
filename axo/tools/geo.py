# shared geometry helpers: welded graph, geodesics, extremity tips, ring-centroid centerlines
import numpy as np
from scipy.sparse import coo_matrix, csr_matrix
from scipy.sparse.csgraph import dijkstra
D = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo/'
class M:
    def __init__(s, nm):
        m = np.load(D + nm + '_mesh.npz'); s.P0, s.I0, s.UV, s.N0 = m['P'], m['I'].reshape(-1, 3), m['UV'], m['N']
        key = np.round(s.P0, 5); uq, idx, wid = np.unique(key, axis=0, return_index=True, return_inverse=True); s.wid = wid.ravel(); s.P = s.P0[idx]
        T = s.wid[s.I0]; s.T = T; e = np.concatenate([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]]); e = e[e[:, 0] != e[:, 1]]
        w = np.linalg.norm(s.P[e[:, 0]] - s.P[e[:, 1]], axis=1); n = len(s.P)
        s.G = csr_matrix(coo_matrix((np.r_[w, w], (np.r_[e[:, 0], e[:, 1]], np.r_[e[:, 1], e[:, 0]])), shape=(n, n)))
        s.E = e
    def near(s, p): return int(np.argmin(np.linalg.norm(s.P - np.asarray(p), axis=1)))
    def geo(s, src, limit=np.inf): return dijkstra(s.G, indices=src, limit=limit)
    def tips(s, dist, mask, r=0.05, k=None):
        # local maxima of dist within geodesic radius r, among masked vertices, strongest first
        cand = np.where(mask & np.isfinite(dist))[0]; cand = cand[np.argsort(-dist[cand])]; taken = np.zeros(len(s.P), bool); out = []
        for v in cand:
            if taken[v]: continue
            out.append(v); dv = s.geo(v, limit=r * 3); taken |= np.isfinite(dv) & (dv < r * 3)
            if k and len(out) >= k: break
        return out
    def centerline(s, tip, length, n, mask=None, rmax=0.25, step_ring=0.025):
        # rings of equal geodesic distance from the tip, each ring's centroid (tracked so it does not jump to a neighbour part)
        d = s.geo(tip, limit=length + step_ring * 2); pts = []; prev = s.P[tip].copy()
        for t in np.linspace(0, length, n):
            sel = np.isfinite(d) & (np.abs(d - t) < step_ring)
            if mask is not None: sel &= mask
            q = s.P[sel]
            if len(q) == 0: pts.append(prev.copy()); continue
            q = q[np.linalg.norm(q - prev, axis=1) < rmax] if t > 0 else q
            c = q.mean(0) if len(q) else prev; pts.append(c); prev = c
        return np.array(pts)
