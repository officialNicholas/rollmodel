import numpy as np
def slice_z(P, T, z0):
    """segments where the plane z = z0 cuts the triangles T: returns an (k, 2, 3) array"""
    d = P[T][:, :, 2] - z0; s = np.sign(d); s[s == 0] = 1e-9
    cut = (s.min(1) < 0) & (s.max(1) > 0); segs = []
    for t in np.where(cut)[0]:
        pts = []
        for a, b in ((0, 1), (1, 2), (2, 0)):
            da, db = d[t, a], d[t, b]
            if (da < 0) != (db < 0): u = da / (da - db); pts.append(P[T[t, a]] + u * (P[T[t, b]] - P[T[t, a]]))
        if len(pts) == 2: segs.append(pts)
    return np.array(segs)
