# Mirror symmetry for a nearly symmetric mesh (x = 0 the mirror plane): each vertex is moved halfway toward the mirror image of the
# surface point nearest its own mirror image (the nearest point among triangles facing the same way, so the two sides of a thin flap are
# not confused), a few times over; the welded seams move together (the mesh is welded).
import numpy as np
from scipy.spatial import cKDTree
import meshkit as mk
MIR = np.array([-1.0, 1, 1])
def mirror_partner(P, T, N, k=16, cosmin=0.2):
    fn = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]]); fn /= np.maximum(np.linalg.norm(fn, axis=1, keepdims=True), 1e-12)
    X = P * MIR; NX = N * MIR; tree = cKDTree(P); _, nn = tree.query(X, k)
    vt = [[] for _ in range(len(P))]
    for t, tri in enumerate(T):
        for v in tri: vt[v].append(t)
    out = X.copy(); dist = np.full(len(P), np.inf)
    for i in range(len(P)):
        cand = np.unique(np.concatenate([vt[v] for v in nn[i]])); cand = cand[fn[cand] @ NX[i] > cosmin]
        if len(cand) == 0: continue
        tt = T[cand]; p = mk.closest_point_tri(X[i][None], P[tt[:, 0]], P[tt[:, 1]], P[tt[:, 2]]); d = np.linalg.norm(p - X[i], axis=1); j = np.argmin(d)
        out[i] = p[j]; dist[i] = d[j]
    return out * MIR, dist
def symmetrize(P, T, iters=3, k=0.5, mask=None, dmin=0.012, dmax=0.045, smooth=8, verbose=True):
    """each pass: every vertex's mirror partner, a confidence (1 for a gap under dmin, 0 past dmax, times mask), the move toward the
    partner smoothed over the surface as a normalized convolution (so neighbours move together: no spikes where the partner jumps
    between fingers), then a step k of it"""
    P = P.copy(); E = mk.edges(T); A = mk.adjacency(len(P), E)
    for it in range(iters):
        N = mk.vertex_normals(P, T); Sp, d = mirror_partner(P, T, N, cosmin=0.5)
        ok = np.isfinite(d); c = np.zeros(len(P)); c[ok] = np.clip((dmax - d[ok]) / (dmax - dmin), 0, 1)
        if mask is not None: c *= mask
        D = np.where(ok[:, None], Sp - P, 0.0) * c[:, None]; cw = c.copy()
        for _ in range(smooth): D = 0.5 * D + 0.5 * (A @ D) / np.maximum(np.asarray(A.sum(1)), 1); cw = 0.5 * cw + 0.5 * (A @ cw) / np.maximum(np.asarray(A.sum(1)).ravel(), 1)
        mv = D / np.maximum(cw, 1e-6)[:, None] * np.clip(cw / 0.3, 0, 1)[:, None]
        if mask is not None: mv *= mask[:, None]
        P += k * mv
        if verbose: print(f'  symmetrize pass {it}: gap mean {np.mean(d[ok]):.4f} p95 {np.percentile(d[ok], 95):.4f}; confident {int((c > 0.5).sum())}')
    return P
