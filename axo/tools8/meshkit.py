# Mesh utilities for the rig: welding by position (the Meshy mesh is split along its UV seams), adjacency, geodesic distances, level-set
# skeleton, Laplacian smoothing, closest points on a triangle mesh.
import numpy as np
from scipy.sparse import coo_matrix, csr_matrix
from scipy.sparse.csgraph import dijkstra, connected_components
from scipy.spatial import cKDTree
def weld(P, tol=1e-6):
    """map each vertex to a welded index (vertices at the same place, as along UV seams, become one)"""
    q = np.round(P / tol).astype(np.int64); _, first, inv = np.unique(q, axis=0, return_index=True, return_inverse=True)
    return inv.ravel(), first          # welded id per vertex; a representative vertex per welded id
def edges(T):
    E = np.concatenate([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]]); E = np.sort(E, 1); return np.unique(E, axis=0)
def adjacency(n, E, w=None):
    w = np.ones(len(E)) if w is None else w
    return coo_matrix((np.r_[w, w], (np.r_[E[:, 0], E[:, 1]], np.r_[E[:, 1], E[:, 0]])), shape=(n, n)).tocsr()
def graph(P, T):
    E = edges(T); L = np.linalg.norm(P[E[:, 0]] - P[E[:, 1]], axis=1); return adjacency(len(P), E, L), E
def geodesic(G, src):
    return dijkstra(G, directed=False, indices=src, min_only=True)
def laplacian_smooth(P, E, iters=10, lam=0.5, mask=None, fixed=None):
    n = len(P); A = adjacency(n, E); deg = np.maximum(np.asarray(A.sum(1)).ravel(), 1); P = P.copy()
    for _ in range(iters):
        avg = (A @ P) / deg[:, None]; d = lam * (avg - P)
        if mask is not None: d *= mask[:, None]
        if fixed is not None: d[fixed] = 0
        P += d
    return P
def smooth_scalar(E, n, x, iters=3, lam=0.5):
    A = adjacency(n, E); deg = np.maximum(np.asarray(A.sum(1)).ravel(), 1); x = np.asarray(x, float).copy()
    for _ in range(iters): x = (1 - lam) * x + lam * (A @ x) / deg[:, None] if x.ndim > 1 else (1 - lam) * x + lam * (A @ x) / deg
    return x
def vertex_normals(P, T):
    fn = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]]); N = np.zeros_like(P)
    for k in range(3): np.add.at(N, T[:, k], fn)
    return N / np.maximum(np.linalg.norm(N, axis=1, keepdims=True), 1e-12)
def closest_on_tris(X, P, T, k=12):
    """closest point on the mesh surface to each X (candidate triangles: those of the k nearest vertices)"""
    tree = cKDTree(P); _, nn = tree.query(X, k)
    vt = [[] for _ in range(len(P))]
    for t, tri in enumerate(T):
        for v in tri: vt[v].append(t)
    best = np.full(len(X), np.inf); out = X.copy()
    cand = [np.unique(np.concatenate([vt[v] for v in nn[i]])) for i in range(len(X))]
    for i in range(len(X)):
        tt = T[cand[i]]; a, b, c = P[tt[:, 0]], P[tt[:, 1]], P[tt[:, 2]]; p = closest_point_tri(X[i][None], a, b, c)
        d = np.linalg.norm(p - X[i], axis=1); j = np.argmin(d); best[i] = d[j]; out[i] = p[j]
    return out, best
def closest_point_tri(p, a, b, c):
    # (Ericson, Real-Time Collision Detection 5.1.5), vectorized over triangles for one point (p: 1x3)
    ab = b - a; ac = c - a; ap = p - a
    d1 = (ab * ap).sum(1); d2 = (ac * ap).sum(1)
    bp = p - b; d3 = (ab * bp).sum(1); d4 = (ac * bp).sum(1)
    cp = p - c; d5 = (ab * cp).sum(1); d6 = (ac * cp).sum(1)
    va = d3 * d6 - d5 * d4; vb = d5 * d2 - d1 * d6; vc = d1 * d4 - d3 * d2
    den = np.where(np.abs(va + vb + vc) < 1e-20, 1e-20, va + vb + vc); v = vb / den; w = vc / den
    res = a + ab * v[:, None] + ac * w[:, None]
    m = (d1 <= 0) & (d2 <= 0); res[m] = a[m]
    m2 = (d3 >= 0) & (d4 <= d3); res[m2] = b[m2]
    m3 = (vc <= 0) & (d1 >= 0) & (d3 <= 0); t = d1 / np.where(np.abs(d1 - d3) < 1e-20, 1e-20, d1 - d3); r3 = a + ab * t[:, None]; res[m3 & ~m & ~m2] = r3[m3 & ~m & ~m2]
    m4 = (d6 >= 0) & (d5 <= d6); res[m4 & ~m & ~m2 & ~m3] = c[m4 & ~m & ~m2 & ~m3]
    m5 = (vb <= 0) & (d2 >= 0) & (d6 <= 0); t = d2 / np.where(np.abs(d2 - d6) < 1e-20, 1e-20, d2 - d6); r5 = a + ac * t[:, None]; s5 = m5 & ~m & ~m2 & ~m3 & ~m4; res[s5] = r5[s5]
    m6 = (va <= 0) & ((d4 - d3) >= 0) & ((d5 - d6) >= 0); den6 = (d4 - d3) + (d5 - d6); t = (d4 - d3) / np.where(np.abs(den6) < 1e-20, 1e-20, den6); r6 = b + (c - b) * t[:, None]
    s6 = m6 & ~m & ~m2 & ~m3 & ~m4 & ~m5; res[s6] = r6[s6]
    return res
def levelset_skeleton(P, G, E, src, step=0.03):
    """a curve skeleton from the geodesic distance to src: each connected piece of each distance band becomes a node at its centroid,
    linked to the pieces of the band before it that it touches. returns nodes [(centroid, band, count, verts)], links [(a, b)]"""
    d = geodesic(G, src); band = np.floor(d / step).astype(int); n = len(P)
    A = adjacency(n, E); nodes = []; node_of = np.full(n, -1)
    for b in range(band.max() + 1):
        vs = np.where(band == b)[0]
        if len(vs) == 0: continue
        sub = A[vs][:, vs]; nc, lab = connected_components(sub, directed=False)
        for c in range(nc):
            vv = vs[lab == c]; node_of[vv] = len(nodes); nodes.append((P[vv].mean(0), b, len(vv), vv))
    links = set()
    for a, b_ in E:
        na, nb = node_of[a], node_of[b_]
        if na != nb and abs(nodes[na][1] - nodes[nb][1]) == 1: links.add((min(na, nb), max(na, nb)))
    return d, nodes, sorted(links), node_of
def peaks(d, A, verts, min_persist=0.03):
    """maxima of the scalar d over the vertex subset verts (A: adjacency), by persistence: vertices are added from the highest d down; a
    vertex touching no component yet starts one (a peak); when two components meet, the lower peak dies there. returns
    [(peak vertex, peak d, merge d, member vertices)] for peaks persisting more than min_persist, highest first"""
    order = verts[np.argsort(-d[verts])]; inset = np.zeros(len(d), bool); parent = {}; peak = {}; members = {}
    def find(a):
        while parent[a] != a: parent[a] = parent[parent[a]]; a = parent[a]
        return a
    out = []
    for v in order:
        inset[v] = True; nb = [u for u in A[v].indices if inset[u] and u != v]; roots = list({find(u) for u in nb})
        if not roots: parent[v] = v; peak[v] = v; members[v] = [v]; continue
        roots.sort(key=lambda r: -d[peak[r]]); r0 = roots[0]; parent[v] = r0; members[r0].append(v)
        for r in roots[1:]:
            if d[peak[r]] - d[v] > min_persist: out.append((peak[r], d[peak[r]], d[v], members[r]))
            parent[r] = r0; members[r0] += members[r]
    rs = {find(v) for v in order}
    for r in rs: out.append((peak[r], d[peak[r]], -np.inf, members[r]))
    return sorted(out, key=lambda t: -t[1])
def untangle(P, T, ref_fn=None, rounds=12, verbose=True, fixed=None):
    """triangles turned over (against the reference orientation, or against their vertices' normals): their vertices and one ring
    round them eased toward their neighbours' average until none is turned over"""
    E = edges(T); A = adjacency(len(P), E); deg = np.maximum(np.asarray(A.sum(1)).ravel(), 1); P = P.copy()
    def bad_tris():
        fn = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]]); fn /= np.maximum(np.linalg.norm(fn, axis=1, keepdims=True), 1e-15)
        ref = ref_fn if ref_fn is not None else vertex_normals(P, T)[T].mean(1)
        return np.where((fn * ref).sum(1) < -0.05)[0]
    b0 = len(bad_tris())
    for r in range(rounds):
        bt = bad_tris()
        if len(bt) == 0: break
        m = np.zeros(len(P), bool); m[T[bt].ravel()] = True; m = m | (A @ m.astype(float) > 0)
        if fixed is not None: m &= ~fixed
        for _ in range(4): avg = (A @ P) / deg[:, None]; P[m] = 0.5 * P[m] + 0.5 * avg[m]
    if verbose: print(f'  untangle: {b0} turned-over triangles -> {len(bad_tris())}')
    return P
