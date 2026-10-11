# As-rigid-as-possible surface deformation (Sorkine & Alexa 2007): handles fixed, everything else keeps its rest shape locally.
# Cotangent weights (clamped), a soft pull toward a guess on every vertex (keeps unconstrained islands in place, regularizes), prefactored solve.
import numpy as np
from scipy.sparse import coo_matrix, csc_matrix, diags
from scipy.sparse.linalg import splu
def cot_weights(P, T, clamp=(1e-3, 50.0)):
    n = len(P); I = []; J = []; Wt = []
    for k in range(3):
        a, b, c = T[:, k], T[:, (k + 1) % 3], T[:, (k + 2) % 3]
        u = P[a] - P[c]; v = P[b] - P[c]; cot = np.einsum('ij,ij->i', u, v) / np.maximum(np.linalg.norm(np.cross(u, v), axis=1), 1e-12)
        I.append(a); J.append(b); Wt.append(0.5 * cot)
    I = np.concatenate(I); J = np.concatenate(J); Wt = np.clip(np.concatenate(Wt), *clamp)
    Wm = coo_matrix((np.r_[Wt, Wt], (np.r_[I, J], np.r_[J, I])), shape=(n, n)).tocsr(); Wm.sum_duplicates(); return Wm
def arap(P0, T, guess, fixed, iters=20, soft=1e-3, verbose=False, W=None):
    """P0 rest positions, guess initial deformed positions (fixed vertices take their guess positions), fixed: bool mask"""
    n = len(P0); W = cot_weights(P0, T) if W is None else W; W = W.tocsr(); E = W.tocoo(); ei, ej, ew = E.row, E.col, E.data
    deg = np.asarray(W.sum(1)).ravel(); L = (diags(deg) - W).tocsr()
    free = ~fixed; fi = np.where(free)[0]; hi = np.where(fixed)[0]
    A = (L[fi][:, fi] + diags(np.full(len(fi), soft * deg[fi].mean()))).tocsc(); lu = splu(A)
    X = guess.copy(); Lfh = L[fi][:, hi]
    e0 = P0[ei] - P0[ej]
    for it in range(iters):
        # local: best rotation per vertex
        e1 = X[ei] - X[ej]; S = np.zeros((n, 3, 3)); np.add.at(S, ei, ew[:, None, None] * e0[:, :, None] * e1[:, None, :])
        U, s, Vt = np.linalg.svd(S); R = np.einsum('nji,nkj->nik', Vt, U)   # R = V U^T
        bad = np.linalg.det(R) < 0
        if bad.any(): U2 = U[bad].copy(); U2[:, :, 2] *= -1; R[bad] = np.einsum('nji,nkj->nik', Vt[bad], U2)
        # global: L x = b
        b = np.zeros((n, 3)); np.add.at(b, ei, 0.5 * ew[:, None] * np.einsum('nij,nj->ni', R[ei] + R[ej], e0))
        rhs = b[fi] - Lfh @ X[hi] + soft * deg[fi].mean() * guess[fi]
        X[fi] = np.stack([lu.solve(rhs[:, k]) for k in range(3)], 1)
        if verbose and (it % 5 == 0 or it == iters - 1):
            e1 = X[ei] - X[ej]; err = np.sum(ew * np.sum((e1 - np.einsum('nij,nj->ni', R[ei], e0)) ** 2, 1)); print(f'   arap it {it}: energy {err:.5f}')
    return X
