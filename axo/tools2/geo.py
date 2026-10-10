# geometry helpers on a welded mesh: graph geodesics, extremity tips, ring centroids, connected components
import numpy as np
from scipy.sparse import coo_matrix, csr_matrix
from scipy.sparse.csgraph import dijkstra, connected_components
D = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo2/'
class M:
    def __init__(s, nm, P=None):
        m = np.load(D + nm + '_src.npz', allow_pickle=True); s.P0 = m['P'].astype(np.float64) if P is None else P; s.I0 = m['I'].reshape(-1, 3); s.UV = m['UV']; s.N0 = m['N']; s.src = m
        key = np.round(s.P0, 5); uq, idx, wid = np.unique(key, axis=0, return_index=True, return_inverse=True); s.wid = wid.ravel(); s.P = s.P0[idx]; s.uidx = idx
        T = s.wid[s.I0]; s.T = T; e = np.concatenate([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]]); e = e[e[:, 0] != e[:, 1]]; e = np.unique(np.sort(e, axis=1), axis=0)   # each edge once (duplicates would sum their weights)
        w = np.linalg.norm(s.P[e[:, 0]] - s.P[e[:, 1]], axis=1); n = len(s.P)
        s.G = csr_matrix(coo_matrix((np.r_[w, w], (np.r_[e[:, 0], e[:, 1]], np.r_[e[:, 1], e[:, 0]])), shape=(n, n))); s.E = e; s.n = n
        # vertex normals (welded, area weighted)
        fn = np.cross(s.P[T[:, 1]] - s.P[T[:, 0]], s.P[T[:, 2]] - s.P[T[:, 0]]); vn = np.zeros((n, 3))
        for k in range(3): np.add.at(vn, T[:, k], fn)
        s.N = vn / np.maximum(np.linalg.norm(vn, axis=1, keepdims=True), 1e-12)
    def near(s, p): return int(np.argmin(np.linalg.norm(s.P - np.asarray(p, float), axis=1)))
    def geo(s, src, limit=np.inf, mask=None):
        if mask is None: return dijkstra(s.G, indices=src, limit=limit, min_only=np.ndim(src) > 0)
        keep = np.where(mask)[0]; sub = s.G[keep][:, keep]; loc = {v: i for i, v in enumerate(keep)}
        srcs = [loc[v] for v in (np.atleast_1d(src)) if v in loc]; d = np.full(s.n, np.inf)
        if srcs: d[keep] = dijkstra(sub, indices=srcs, limit=limit, min_only=True)
        return d
    def comps(s, mask):
        keep = np.where(mask)[0]; sub = s.G[keep][:, keep]; nc, lab = connected_components(sub, directed=False); out = np.full(s.n, -1); out[keep] = lab; return nc, out
    def tips(s, dist, mask, r=0.05, k=None):
        cand = np.where(mask & np.isfinite(dist))[0]; cand = cand[np.argsort(-dist[cand])]; taken = np.zeros(s.n, bool); out = []
        for v in cand:
            if taken[v]: continue
            out.append(v); dv = dijkstra(s.G, indices=v, limit=r); taken |= np.isfinite(dv)
            if k and len(out) >= k: break
        return out
