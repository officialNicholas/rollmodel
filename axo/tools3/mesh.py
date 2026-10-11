# a welded triangle mesh with the graph helpers the rig tools expect (P, T, N, E, G, n, geo, comps, near), from any P / T
import numpy as np
from scipy.sparse import coo_matrix, csr_matrix
from scipy.sparse.csgraph import dijkstra, connected_components
from scipy.spatial import cKDTree
class Mesh:
    def __init__(s, P, T):
        s.P = np.asarray(P, float); s.T = np.asarray(T, np.int64); s.n = len(s.P)
        e = np.concatenate([s.T[:, [0, 1]], s.T[:, [1, 2]], s.T[:, [2, 0]]]); e = np.unique(np.sort(e, 1), axis=0); e = e[e[:, 0] != e[:, 1]]; s.E = e
        w = np.linalg.norm(s.P[e[:, 0]] - s.P[e[:, 1]], axis=1)
        s.G = csr_matrix(coo_matrix((np.r_[w, w], (np.r_[e[:, 0], e[:, 1]], np.r_[e[:, 1], e[:, 0]])), shape=(s.n, s.n)))
        fn = np.cross(s.P[s.T[:, 1]] - s.P[s.T[:, 0]], s.P[s.T[:, 2]] - s.P[s.T[:, 0]]); vn = np.zeros((s.n, 3))
        for k in range(3): np.add.at(vn, s.T[:, k], fn)
        s.N = vn / np.maximum(np.linalg.norm(vn, axis=1, keepdims=True), 1e-12)
        s.wid = np.arange(s.n); s._rows = None
    def near(s, p): return int(np.argmin(np.linalg.norm(s.P - np.asarray(p, float), axis=1)))
    def geo(s, src, limit=np.inf, mask=None):
        if mask is None: return dijkstra(s.G, indices=src, limit=limit, min_only=np.ndim(src) > 0)
        keep = np.where(mask)[0]; sub = s.G[keep][:, keep]; loc = -np.ones(s.n, int); loc[keep] = np.arange(len(keep))
        srcs = [loc[v] for v in np.atleast_1d(src) if loc[v] >= 0]; d = np.full(s.n, np.inf)
        if srcs: d[keep] = dijkstra(sub, indices=srcs, limit=limit, min_only=True)
        return d
    def comps(s, mask):
        keep = np.where(mask)[0]; sub = s.G[keep][:, keep]; nc, lab = connected_components(sub, directed=False); out = np.full(s.n, -1); out[keep] = lab; return nc, out
    def rows(s):
        if s._rows is None: s._rows = s.G.tolil().rows
        return s._rows
def mirror_map(P, tol=2e-4):
    """for a mirror-symmetric mesh (about x = 0): each vertex's partner index"""
    kd = cKDTree(P); d, j = kd.query(P * np.array([-1, 1, 1])); bad = d > tol
    if bad.any(): print(f'  mirror map: {int(bad.sum())} vertices without an exact partner (max gap {d.max() * 1000:.2f} mm)')
    return j
