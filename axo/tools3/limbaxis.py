# the limb's axis from exact cross-sections: planes perpendicular to a provisional (geodesic-ring) centre line cut the limb into closed loops;
# where a loop merges with the body's section the limb emerges. Returns loop centroids / radii from the digits to the emergence.
import numpy as np
from xsec import plane_loops
def unit(v): v = np.asarray(v, float); return v / (np.linalg.norm(v, axis=-1, keepdims=True) + 1e-12)
def loops_along(P, T, pts, ext=0.0):
    """exact loops at each point of a polyline (plane normal = the local tangent)"""
    tang = unit(np.gradient(pts, axis=0)); out = []
    for i in range(len(pts)):
        lp = plane_loops(P, T, pts[i], tang[i], near=pts[i])
        if not lp: out.append(None); continue
        l = lp[0]; out.append(dict(c=l['centroid'], req=l['length'] / (2 * np.pi), off=float(np.linalg.norm(l['centroid'] - pts[i])), segs=l['segs'], closed=l['closed']))
    return out
def emergence(L, start=4, k=1.55):
    """first loop index whose loop is much longer than the limb's (median of the preceding ones) or jumps off the axis; returns the last good index"""
    for i in range(start, len(L)):
        if L[i] is None: return i - 1
        prev = [l['req'] for l in L[max(0, i - 6):i] if l is not None]; med = np.median(prev)
        if L[i]['req'] > k * med or L[i]['off'] > 1.5 * med: return i - 1
    return len(L) - 1
