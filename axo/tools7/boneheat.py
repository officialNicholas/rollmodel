# Bone heat skinning weights (Baran and Popovic, Pinocchio 2007) on a closed triangle mesh: each bone's weight is the solution of
# (-L + M H) w = M H p, L the cotangent Laplacian, M the lumped (barycentric) vertex areas, H = c / d^2 for a vertex whose nearest bone it
# can see (the straight line from the vertex to the bone stays inside the mesh), d that distance, p = 1 where this bone is the nearest
# visible one. Smooth weights that follow the surface: an arm's weights do not leak to the head because the head cannot see the arm bone.
import numpy as np
from scipy.sparse import coo_matrix, diags
from scipy.sparse.linalg import splu
def cot_laplacian(P, T):
    n = len(P); I = []; J = []; V = []; area = np.zeros(n)
    for k in range(3):
        i, j, l = T[:, k], T[:, (k + 1) % 3], T[:, (k + 2) % 3]
        a, b = P[i] - P[l], P[j] - P[l]; cr = np.linalg.norm(np.cross(a, b), axis=1); cot = (a * b).sum(1) / np.maximum(cr, 1e-12)
        cot = np.clip(cot, -10, 10); I += [i, j]; J += [j, i]; V += [0.5 * cot, 0.5 * cot]
    fa = 0.5 * np.linalg.norm(np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]]), axis=1)
    for k in range(3): np.add.at(area, T[:, k], fa / 3)
    W = coo_matrix((np.concatenate(V), (np.concatenate(I), np.concatenate(J))), shape=(n, n)).tocsr()
    L = W - diags(np.asarray(W.sum(1)).ravel()); return L, area
def seg_closest(X, a, b):
    ab = b - a; t = np.clip(((X - a) @ ab) / max(ab @ ab, 1e-12), 0, 1); return a + t[:, None] * ab
class TriGrid:
    """a uniform grid over the triangles, for segment / mesh intersection tests"""
    def __init__(self, P, T, cell=0.04):
        self.P, self.T, self.cell = P, T, cell; self.lo = P.min(0) - 1e-3; tri = P[T]; mn = np.floor((tri.min(1) - self.lo) / cell).astype(int); mx = np.floor((tri.max(1) - self.lo) / cell).astype(int)
        self.cells = {}
        for t in range(len(T)):
            for x in range(mn[t, 0], mx[t, 0] + 1):
                for y in range(mn[t, 1], mx[t, 1] + 1):
                    for z in range(mn[t, 2], mx[t, 2] + 1): self.cells.setdefault((x, y, z), []).append(t)
        self.A, self.B, self.C = P[T[:, 0]], P[T[:, 1]], P[T[:, 2]]
    def hits(self, p, q, skip=()):
        """does the open segment p-q cross a triangle (other than those in skip)?"""
        L = np.linalg.norm(q - p); n = max(2, int(L / (self.cell * 0.5)) + 2); cs = set()
        for s in np.linspace(0, 1, n):
            c = np.floor((p + (q - p) * s - self.lo) / self.cell).astype(int)
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    for dz in (-1, 0, 1): cs.update(self.cells.get((c[0] + dx, c[1] + dy, c[2] + dz), ()))
        if not cs: return False
        tt = np.array([t for t in cs if t not in skip])
        if len(tt) == 0: return False
        d = q - p; e1 = self.B[tt] - self.A[tt]; e2 = self.C[tt] - self.A[tt]; h = np.cross(d, e2); a = (e1 * h).sum(1); ok = np.abs(a) > 1e-14
        f = np.where(ok, 1 / np.where(ok, a, 1), 0); s_ = p - self.A[tt]; u = f * (s_ * h).sum(1); qv = np.cross(s_, e1); v = f * (qv @ d); t = f * (qv * e2).sum(1)
        return bool(np.any(ok & (u >= -1e-9) & (v >= -1e-9) & (u + v <= 1 + 1e-9) & (t > 1e-4) & (t < 1 - 1e-4)))
def bone_heat(P, T, N, segs, allowed=None, c=1.0, kvis=5, inset=0.004, verbose=True):
    """segs: [(a, b)] bone segments; allowed: optional (n, nb) bool mask of bones a vertex may take. returns (n, nb) weights"""
    n, nb = len(P), len(segs); D = np.zeros((n, nb)); Q = np.zeros((n, nb, 3))
    for b, (a, e) in enumerate(segs): Q[:, b] = seg_closest(P, np.asarray(a, float), np.asarray(e, float)); D[:, b] = np.linalg.norm(P - Q[:, b], axis=1)
    if allowed is not None: D = np.where(allowed, D, np.inf)
    grid = TriGrid(P, T); vt = [[] for _ in range(n)]
    for t, tri in enumerate(T):
        for v in tri: vt[v].append(t)
    near = np.full(n, -1); dn = np.full(n, np.inf); nvis = 0
    order = np.argsort(D, 1)
    for v in range(n):
        p0 = P[v] - N[v] * inset; skip = set(vt[v])
        for b in order[v, :kvis]:
            if not np.isfinite(D[v, b]): break
            if not grid.hits(p0, Q[v, b], skip):
                near[v] = b; dn[v] = D[v, b]; break
        if near[v] < 0: nvis += 1
    if verbose: print(f'  bone heat: {n} verts, {nb} bones, {nvis} with no visible bone among their {kvis} nearest')
    L, area = cot_laplacian(P, T)
    # (ties: every bone within 1.0001 of the nearest visible distance shares p)
    H = np.where(near >= 0, c / np.maximum(dn, 1e-3) ** 2, 0.0)
    A_ = (-L + diags(area * H)).tocsc(); lu = splu(A_)
    W = np.zeros((n, nb))
    for b in range(nb):
        p = ((near == b) | ((near >= 0) & (D[:, b] <= dn * 1.0001) & np.isfinite(D[:, b]))).astype(float)
        if p.sum() == 0: continue
        W[:, b] = lu.solve(area * H * p)
    if allowed is not None: W = np.where(allowed, W, 0)
    W = np.clip(W, 0, None); s = W.sum(1, keepdims=True); W = np.where(s > 1e-9, W / np.maximum(s, 1e-12), 0)
    # vertices with nothing (no visible bone anywhere near and no heat reaching them): their nearest bone
    lost = W.sum(1) < 1e-6
    if lost.any(): W[lost, np.argmin(np.where(np.isfinite(D[lost]), D[lost], 1e9), 1)] = 1
    return W, near
