# adaptive refinement of a welded triangle mesh: longest-edge bisection of every edge longer than Lmax, the new vertex on the PN-triangle
# (cubic) curve of its edge, so the surface gets rounder rather than just denser. Per-vertex attributes are carried as edge midpoints.
import numpy as np
def vnormals(P, T):
    fn = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]]); vn = np.zeros_like(P)
    for k in range(3): np.add.at(vn, T[:, k], fn)
    return vn / np.maximum(np.linalg.norm(vn, axis=1, keepdims=True), 1e-12)
def refine(P, T, Lmax, attrs=None, max_rounds=12, mask=None, verbose=True):
    """P (n,3), T (m,3); attrs: dict name -> (n,k) arrays interpolated linearly; mask: optional per-vertex bool, an edge splits only if both
    ends are in the mask. Returns P, T, attrs, parent (for each new vertex the two ends it came from, -1 for originals)"""
    P = P.astype(float).copy(); T = T.copy(); attrs = {k: np.asarray(v, float).copy() for k, v in (attrs or {}).items()}
    par = [(-1, -1)] * len(P); msk = None if mask is None else mask.copy()
    for rnd in range(max_rounds):
        N = vnormals(P, T)
        # the longest edge of each triangle, if over Lmax
        e = np.stack([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]], 1); L = np.linalg.norm(P[e[:, :, 0]] - P[e[:, :, 1]], axis=2)
        k = np.argmax(L, 1); Lk = L[np.arange(len(T)), k]; cand = Lk > Lmax
        if msk is not None: ee = e[np.arange(len(T)), k]; cand &= msk[ee[:, 0]] & msk[ee[:, 1]]
        if not cand.any(): break
        ek = np.sort(e[np.arange(len(T)), k][cand], 1); ek = np.unique(ek, axis=0)
        # new vertices on the PN curve: (Pa + Pb)/2 - (wab Na + wba Nb)/8
        a, b = ek[:, 0], ek[:, 1]; d = P[b] - P[a]; wab = np.einsum('ij,ij->i', d, N[a]); wba = np.einsum('ij,ij->i', -d, N[b])
        mid = (P[a] + P[b]) / 2 - (wab[:, None] * N[a] + wba[:, None] * N[b]) / 8
        base = len(P); key = {(int(x), int(y)): base + i for i, (x, y) in enumerate(ek)}
        P = np.vstack([P, mid]); par += [(int(x), int(y)) for x, y in ek]
        for nm in attrs: attrs[nm] = np.vstack([attrs[nm], (attrs[nm][a] + attrs[nm][b]) / 2])
        if msk is not None: msk = np.r_[msk, np.ones(len(ek), bool)]
        # split every triangle that has a split edge (one, two or three of its edges): fan from the new vertices
        newT = []
        for t in T:
            m01 = key.get((min(t[0], t[1]), max(t[0], t[1]))); m12 = key.get((min(t[1], t[2]), max(t[1], t[2]))); m20 = key.get((min(t[2], t[0]), max(t[2], t[0])))
            ms = [m01, m12, m20]; cnt = sum(x is not None for x in ms)
            if cnt == 0: newT.append(t); continue
            # rotate so the first split edge starts at index 0
            v = list(t); mm = ms
            if cnt == 1:
                i = [j for j in range(3) if mm[j] is not None][0]; A, B, C = v[i], v[(i + 1) % 3], v[(i + 2) % 3]; M_ = mm[i]
                newT += [[A, M_, C], [M_, B, C]]
            elif cnt == 2:
                i = [j for j in range(3) if mm[j] is None][0]   # the unsplit edge is (v[i], v[i+1])
                A, B, C = v[i], v[(i + 1) % 3], v[(i + 2) % 3]; Mbc = mm[(i + 1) % 3]; Mca = mm[(i + 2) % 3]
                # quad A,B,Mbc,Mca + triangle Mbc,C,Mca: split the quad along its shorter diagonal
                newT.append([Mbc, C, Mca])
                if np.linalg.norm(P[A] - P[Mbc]) < np.linalg.norm(P[B] - P[Mca]): newT += [[A, B, Mbc], [A, Mbc, Mca]]
                else: newT += [[A, B, Mca], [B, Mbc, Mca]]
            else:
                A, B, C = v; Mab, Mbc, Mca = mm; newT += [[A, Mab, Mca], [Mab, B, Mbc], [Mca, Mbc, C], [Mab, Mbc, Mca]]
        T = np.array(newT, dtype=np.int64)
        if verbose: print(f'   refine round {rnd}: split {len(ek)} edges -> {len(P)} verts, {len(T)} tris')
    return P, T, attrs, np.array(par)
def taubin_smooth(P, T, mask, iters=6, lam=0.5, mu=-0.53):
    from scipy.sparse import coo_matrix
    n = len(P); e = np.unique(np.sort(np.concatenate([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]]), 1), axis=0)
    A = coo_matrix((np.ones(2 * len(e)), (np.r_[e[:, 0], e[:, 1]], np.r_[e[:, 1], e[:, 0]])), shape=(n, n)).tocsr(); deg = np.asarray(A.sum(1)).ravel(); deg[deg == 0] = 1
    P = P.copy(); w = mask.astype(float)[:, None]
    for _ in range(iters):
        for k in (lam, mu): P += k * w * ((A @ P) / deg[:, None] - P)
    return P
