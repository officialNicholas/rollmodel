#!/usr/bin/env python3
"""Rounds the axolotl's head like the old character's: the flat plate under its head and the hard edge along its jaw are filled out
toward a ball round the face sphere's centre, so its chin curves away under the face and melts into the throat. Nothing is pulled in
(the sides where the gills grow, the top), only filled out underneath; the change fades with the head mask down the neck and away
toward the back of the head, and stays clear of the gills. Normals are worked out again where the surface moved (welded by position,
so no seams), and the baked shadow in the old crease is lifted.
usage: headround.py <in runtime dir> <out runtime dir> [target radius] [strength]"""
import json, os, shutil, sys, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import axomesh
SRC, DST = sys.argv[1], sys.argv[2]
RT = float(sys.argv[3]) if len(sys.argv) > 3 else 0.31
K = float(sys.argv[4]) if len(sys.argv) > 4 else 1.0
os.makedirs(DST, exist_ok=True)
for f in os.listdir(SRC):
    if os.path.isfile(os.path.join(SRC, f)) and not f.startswith('axo_'): shutil.copy(os.path.join(SRC, f), os.path.join(DST, f))
ss = lambda a, b, x: np.clip((x - a) / (b - a), 0, 1) ** 2 * (3 - 2 * np.clip((x - a) / (b - a), 0, 1))
def vertex_normals(P, I):
    T = I.reshape(-1, 3); a, b, c = P[T[:, 0]], P[T[:, 1]], P[T[:, 2]]; fn = np.cross(b - a, c - a)
    N = np.zeros_like(P);
    for k in range(3): np.add.at(N, T[:, k], fn)
    return N
for nm in ('crawl', 'stand'):
    d = axomesh.load(os.path.join(SRC, 'axo_' + nm)); m = d['meta']; P = d['position'].astype(np.float64); n = len(P)
    J = d['jelly'] / 255.0; M = d['mat'] / 255.0; c = np.array(m['face']['c'], float)
    H, G = J[:, 3], M[:, 1]
    D = P - c; L = np.linalg.norm(D, axis=1); U = D / np.maximum(L, 1e-9)[:, None]
    # how much each vertex may move: on the head (fading down the neck), not the gills or near them, not toward the back of the head,
    # mostly underneath (the stand's head sits on its neck: only its chin, out front)
    gills = P[G > 0.3]
    from scipy.spatial import cKDTree
    dg, _ = cKDTree(gills).query(P) if len(gills) else (np.full(n, 9.0), None)
    w = ss(0.15, 0.9, H) * ss(0.03, 0.11, dg) * (G < 0.25)
    under = ss(0.35, -0.15, U[:, 1])            # the lower half (and a little above the equator, softly)
    front = ss(-0.55, 0.05, U[:, 2])            # not the back of the head, where the neck joins
    if nm == 'stand': front = front * ss(-0.1, 0.35, U[:, 2])
    k = w * under * front * K
    # fill out toward the ball: never in
    Ln = L + np.maximum(0.0, RT - L) * k
    Pn = c + U * Ln[:, None]
    disp = np.linalg.norm(Pn - P, axis=1)
    # one pass of smoothing on what moved, so the new curve has no ripples where the old edge was
    I = d['index'].astype(np.int64); T = I.reshape(-1, 3)
    nb = [[] for _ in range(n)]
    for a, b, cc in T: nb[a] += [b, cc]; nb[b] += [a, cc]; nb[cc] += [a, b]
    moved = disp > 1e-5
    for it in range(2):
        Q = Pn.copy()
        for i in np.where(moved)[0]:
            if nb[i]: Q[i] = Pn[i] * 0.5 + Pn[list(set(nb[i]))].mean(0) * 0.5
        lam = np.clip(disp / 0.02, 0, 1)[:, None] * 0.6
        Pn = Pn * (1 - lam) + Q * lam
    disp = np.linalg.norm(Pn - P, axis=1); moved = disp > 1e-5
    # normals where it moved (and the ring round it), welded by position so a split vertex doesn't show a seam
    key = np.round(Pn * 2e4).astype(np.int64); _, wid, inv = np.unique(key, axis=0, return_index=True, return_inverse=True); inv = inv.reshape(-1)
    Nf = vertex_normals(Pn, I); Nw = np.zeros((inv.max() + 1, 3)); np.add.at(Nw, inv, Nf); Nn = Nw[inv]; Nn /= np.maximum(np.linalg.norm(Nn, axis=1), 1e-12)[:, None]
    # (the old edge's normals were averaged across it and tip down: every normal within reach of what moved is worked out again,
    # fading back to the original ones further off)
    dm, _ = cKDTree(Pn[moved]).query(Pn) if moved.any() else (np.full(n, 9.0), None)
    ring = (dm < 0.09) & (G < 0.25)
    No = d['normal'][:, :3].astype(np.float64) / 127.0
    blend = np.where(moved, 1.0, 1.0 - ss(0.04, 0.09, dm))[:, None]
    Nx = No * (1 - blend) + Nn * blend; Nx /= np.maximum(np.linalg.norm(Nx, axis=1), 1e-12)[:, None]
    d['normal'][ring, :3] = np.clip(np.round(Nx[ring] * 127), -127, 127).astype(np.int8)
    # the old crease's baked shadow, lifted where the skin came out
    ao = d['fill'][:, 2].astype(np.float64); ao *= 1 - 0.85 * np.clip(disp / 0.06, 0, 1); d['fill'][:, 2] = np.round(ao).astype(np.uint8)
    # the skin's pattern (pores, spots) is laid out by the canonical place: it moves with the skin, so nothing stretches (the head's rest
    # frame is the same in both bodies, so the move is the same there)
    cs = float(m.get('cpScale', 4.0)); cp = d['cpos'][:, :3].astype(np.float64) + (Pn - P) / cs * 32767.0
    d['cpos'][:, :3] = np.clip(np.round(cp), -32767, 32767).astype(np.int16)
    d['position'] = Pn.astype(np.float32)
    lo, hi = Pn.min(0), Pn.max(0); m['bbox'] = [lo.round(4).tolist(), hi.round(4).tolist()]
    axomesh.save(d, os.path.join(DST, 'axo_' + nm))
    D2 = Pn - c; L2 = np.linalg.norm(D2, axis=1); U2 = D2 / L2[:, None]; head = (H > 0.9) & (G < 0.1)
    rad = lambda v: L2[head][(U2[head] @ (np.array(v) / np.linalg.norm(v))) > 0.95].mean()
    print(f'{nm}: moved {moved.sum()} verts, max {disp.max():.3f} m; radius bottom {rad([0,-1,0]):.3f} chin {rad([0,-.7,.7]):.3f} front {rad([0,0,1]):.3f} side {rad([1,0,0]):.3f}')
print('ok ->', DST)
