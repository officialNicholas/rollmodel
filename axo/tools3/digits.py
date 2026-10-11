# digits from the geometry: in the hand (beyond the wrist plane) the geodesic distance from the wrist rises along each digit to its tip;
# the merge tree of its super-level sets (adding vertices from the far end down) gives one branch per digit, born at the tip and merging
# into the palm at the webbing. The k most persistent branches are the digits.
import numpy as np
def unit(v): v = np.asarray(v, float); return v / (np.linalg.norm(v, axis=-1, keepdims=True) + 1e-12)
def segment(m, region, f, k=4, min_pers=0.02):
    """m: Mesh, region: bool mask (the hand), f: per-vertex scalar (distance from the wrist). Returns a list of digits (most persistent
    first): dict tip (vertex), base level, verts (the branch at its merge)"""
    rows = m.rows(); order = np.where(region)[0]; order = order[np.argsort(-f[order])]
    par = {}; tip = {}; members = {}
    def find(a):
        while par[a] != a: par[a] = par[par[a]]; a = par[a]
        return a
    branches = []
    for v in order:
        par[v] = v; tip[v] = v; members[v] = [v]
        roots = {find(u) for u in rows[v] if u in par and u != v}
        roots.discard(v)
        if not roots: continue
        roots = sorted(roots, key=lambda r: -f[tip[r]])   # the component with the highest tip survives
        main = roots[0]
        for r in roots[1:]:
            pers = f[tip[r]] - f[v]
            if pers > min_pers: branches.append(dict(tip=tip[r], base=f[v], pers=pers, verts=np.array(members[r])))
            par[r] = main; members[main] += members[r]; members[r] = []
        par[v] = main; members[main].append(v); members[v] = []
    # the surviving component's own tip is a digit too (the longest); its branch at the moment the next-longest merged into it
    final = find(order[0]); best = None
    for b in branches:
        if best is None or b['base'] > best['base']: best = b
    # the longest digit: the vertices of the final component above the highest merge level among the branches merged into it
    lvl = max([b['base'] for b in branches], default=f[order[-1]])
    vs = np.array([v for v in members[final] if f[v] > lvl]) if True else None
    # restrict to the connected part containing the final tip
    if len(vs):
        sel = np.zeros(m.n, bool); sel[vs] = True; nc, comp = m.comps(sel); vs = np.where(comp == comp[tip[final]])[0]
    branches.append(dict(tip=tip[final], base=lvl, pers=f[tip[final]] - lvl, verts=vs))
    branches.sort(key=lambda b: -b['pers'])
    return branches[:k], branches[k:]
from xsec import plane_loops
def descent_path(m, f, start, region):
    """steepest descent of f over the mesh graph from `start` (a vertex) down to f's minimum"""
    rows = m.rows(); path = [start]; v = start
    while True:
        nb = [u for u in rows[v] if region[u] and np.isfinite(f[u])]
        if not nb: break
        u = min(nb, key=lambda x: f[x])
        if f[u] >= f[v]: break
        path.append(u); v = u
    return np.array(path)
def digit_axis(m, tip, f, region, step=0.006, jump=1.6, maxlen=0.2):
    """march cross-section loops from a digit's tip back toward the palm: returns centroids, radii and the index where the digit joins the
    palm (its loop merges with the palm's: the perimeter jumps)"""
    P = m.P; path = P[descent_path(m, f, tip, region)]
    cum = np.r_[0, np.cumsum(np.linalg.norm(np.diff(path, axis=0), axis=1))]
    s = np.arange(step * 1.5, min(cum[-1], maxlen), step); pts = np.array([[np.interp(x, cum, path[:, k]) for k in range(3)] for x in s])
    for _ in range(3): pts[1:-1] = 0.25 * pts[:-2] + 0.5 * pts[1:-1] + 0.25 * pts[2:]
    tang = unit(np.gradient(pts, axis=0)) if len(pts) > 2 else np.tile(unit(path[-1] - path[0]), (len(pts), 1))
    cs, rs, keep = [], [], []; started = False
    for i in range(len(pts)):
        lp = plane_loops(P, m.T, pts[i], tang[i], near=pts[i], rmax=0.35)
        if not lp: break
        l = lp[0]; r = l['length'] / (2 * np.pi)
        if not started:
            if l['closed'] and r < 0.06: started = True
            else: continue
        if not l['closed'] or (len(rs) >= 3 and r > jump * np.median(rs[1:])): break
        cs.append(l['centroid']); rs.append(r); keep.append(i)
    keep = np.array(keep, int)
    return np.array(cs), np.array(rs), pts[keep], tang[keep]
def find_digits(m, wrist, knuck, side_mask=None, k=4, xmin=0.05):
    """the k digits of a hand / foot: tip vertex, axis (centroids from the base to the tip), radius, base point and axis, the vertices on
    the digit's side of its base plane"""
    P = m.P; pax = unit(knuck - wrist)
    region = (np.linalg.norm(P - wrist, axis=1) < 0.26) & (P[:, 0] > xmin)
    if side_mask is not None: region &= side_mask
    nc, comp = m.comps(region); region = comp == comp[m.near(knuck)]
    src = np.argsort(np.linalg.norm(P - wrist, axis=1))[:12]; f = m.geo(src, mask=region)
    D, rest = segment(m, region & np.isfinite(f), f, k=12, min_pers=0.012)
    hand = [d for d in D if (P[d['tip']] - wrist) @ pax > 0.02][:k]
    out = []
    for d in hand:
        cs, rs, pts, tg = digit_axis(m, d['tip'], f, region)
        base = cs[-1]; bdir = unit(cs[max(0, len(cs) - 4)] - cs[-1])   # toward the tip
        pos = (P - base) @ bdir; nc2, comp2 = m.comps(region & (pos > 0)); vs = np.where(comp2 == comp2[d['tip']])[0]
        tipP = P[d['tip']]; ax = cs[::-1]   # base -> tip
        out.append(dict(tip=d['tip'], tipP=tipP, base=base, bdir=bdir, axis=np.vstack([ax, tipP]), rad=float(np.median(rs)), verts=vs, f=f))
    return out
