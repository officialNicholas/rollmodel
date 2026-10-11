# radial maps of a head: rays from a centre over a yaw / pitch grid, first hit on the given triangles (gills excluded), and a sphere fit to the
# face cone. Used to choose the shared face sphere and to measure how far each head is from it.
import numpy as np
def ray_hits(P, T, o, dirs, chunk=4000):
    """first hit distance along each direction from o (inf where none). Moller-Trumbore, vectorised over triangles."""
    v0 = P[T[:, 0]]; e1 = P[T[:, 1]] - v0; e2 = P[T[:, 2]] - v0; out = np.full(len(dirs), np.inf); tid = np.full(len(dirs), -1)
    s = o - v0
    for k, d in enumerate(dirs):
        p = np.cross(d, e2); det = np.einsum('ij,ij->i', e1, p); ok = np.abs(det) > 1e-12; inv = np.zeros_like(det); inv[ok] = 1.0 / det[ok]
        u = np.einsum('ij,ij->i', s, p) * inv; q = np.cross(s, e1); v = (q @ d) * inv; t = np.einsum('ij,ij->i', e2, q) * inv
        hit = ok & (u >= 0) & (v >= 0) & (u + v <= 1) & (t > 1e-6)
        if hit.any(): j = np.where(hit)[0][np.argmin(t[hit])]; out[k] = t[j]; tid[k] = j
    return out, tid
def dir_of(yaw, pitch): return np.stack([np.sin(yaw) * np.cos(pitch), np.sin(pitch), np.cos(yaw) * np.cos(pitch)], -1)
def radial_map(P, T, c, yaws, pitches):
    Y, X = np.meshgrid(pitches, yaws, indexing='ij'); D = dir_of(X.ravel(), Y.ravel()); r, tid = ray_hits(P, T, c, D)
    return r.reshape(Y.shape), D.reshape(Y.shape + (3,))
def fit_sphere(Q, w=None):
    w = np.ones(len(Q)) if w is None else w; A = np.c_[2 * Q, np.ones(len(Q))] * w[:, None]; b = (Q ** 2).sum(1) * w; sol, *_ = np.linalg.lstsq(A, b, rcond=None)
    c = sol[:3]; R = np.sqrt(max(1e-9, sol[3] + c @ c)); return c, R
