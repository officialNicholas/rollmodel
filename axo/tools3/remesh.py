# Isotropic remeshing (Botsch & Kobbelt 2004) of a welded triangle mesh with a sizing field: split long edges, collapse short ones, flip
# toward valence 6, tangential relaxation, projection back onto the original surface. Built for the half meshes of a mirror-symmetric
# character: boundary vertices on the symmetry plane (x = 0) stay on it and only slide along it; frozen vertices (thin frills) are kept
# exactly. Every operation runs in rounds of independent edits on a fully rebuilt mesh, which keeps the code simple and the result valid.
import numpy as np
from scipy.spatial import cKDTree

def unit(v): v = np.asarray(v, float); return v / (np.linalg.norm(v, axis=-1, keepdims=True) + 1e-12)
def tri_normals(P, T):
    n = np.cross(P[T[:, 1]] - P[T[:, 0]], P[T[:, 2]] - P[T[:, 0]]); return n
def vert_normals(P, T):
    fn = tri_normals(P, T); vn = np.zeros_like(P)
    for k in range(3): np.add.at(vn, T[:, k], fn)
    return unit(vn)
def edges_of(T):
    """unique undirected edges, and for each the (up to two) triangles and the opposite vertices"""
    m = len(T); e = np.concatenate([T[:, [0, 1]], T[:, [1, 2]], T[:, [2, 0]]]); opp = np.concatenate([T[:, 2], T[:, 0], T[:, 1]]); tri = np.tile(np.arange(m), 3)
    key = np.sort(e, 1); order = np.lexsort((key[:, 1], key[:, 0])); key = key[order]; tri = tri[order]; opp = opp[order]; e = e[order]
    first = np.r_[True, np.any(key[1:] != key[:-1], 1)]; gid = np.cumsum(first) - 1; ne = gid[-1] + 1
    E = key[first]; t2 = -np.ones((ne, 2), int); o2 = -np.ones((ne, 2), int); dirn = np.zeros((ne, 2, 2), int); cnt = np.zeros(ne, int)
    for i in range(len(key)):
        g = gid[i]; c = cnt[g]
        if c < 2: t2[g, c] = tri[i]; o2[g, c] = opp[i]; dirn[g, c] = e[i]
        cnt[g] += 1
    return E, t2, o2, cnt, dirn
def vert_sharpness(P, T, E=None, t2=None, cnt=None):
    """per vertex: the largest dihedral angle (degrees) among its edges"""
    if E is None: E, t2, o2, cnt, _ = edges_of(T)
    fn = unit(tri_normals(P, T)); inner = cnt >= 2; dh = np.zeros(len(E))
    dh[inner] = np.degrees(np.arccos(np.clip((fn[t2[inner, 0]] * fn[t2[inner, 1]]).sum(1), -1, 1)))
    v = np.zeros(len(P)); np.maximum.at(v, E[:, 0], dh); np.maximum.at(v, E[:, 1], dh); return v
def boundary_verts(n, E, cnt):
    b = np.zeros(n, bool); b[E[cnt == 1].ravel()] = True; return b
def compact(P, T, extra=None):
    used = np.zeros(len(P), bool); used[T.ravel()] = True; remap = -np.ones(len(P), int); remap[used] = np.arange(used.sum())
    out = [P[used], remap[T]]
    if extra is not None: out.append({k: v[used] for k, v in extra.items()})
    return out

# ---------------- closest points on the original surface ----------------
def closest_on_tris(p, A, B, C):
    """closest points on triangles (A, B, C) to points p (all (k,3)); Ericson's region test, vectorized"""
    ab = B - A; ac = C - A; ap = p - A
    d1 = (ab * ap).sum(1); d2 = (ac * ap).sum(1)
    bp = p - B; d3 = (ab * bp).sum(1); d4 = (ac * bp).sum(1)
    cp = p - C; d5 = (ab * cp).sum(1); d6 = (ac * cp).sum(1)
    vc = d1 * d4 - d3 * d2; vb = d5 * d2 - d1 * d6; va = d3 * d6 - d5 * d4
    denom = 1.0 / np.maximum(va + vb + vc, 1e-30); v = vb * denom; w = vc * denom
    res = A + ab * v[:, None] + ac * w[:, None]
    m = (d1 <= 0) & (d2 <= 0); res[m] = A[m]
    m = (d3 >= 0) & (d4 <= d3); res[m] = B[m]
    m = (d6 >= 0) & (d5 <= d6); res[m] = C[m]
    m = (vc <= 0) & (d1 >= 0) & (d3 <= 0); t = d1 / np.maximum(d1 - d3, 1e-30); res[m] = (A + ab * t[:, None])[m]
    m = (vb <= 0) & (d2 >= 0) & (d6 <= 0); t = d2 / np.maximum(d2 - d6, 1e-30); res[m] = (A + ac * t[:, None])[m]
    m = (va <= 0) & ((d4 - d3) >= 0) & ((d5 - d6) >= 0); t = (d4 - d3) / np.maximum((d4 - d3) + (d5 - d6), 1e-30); res[m] = (B + (C - B) * t[:, None])[m]
    return res
class Surface:
    """the original surface to project onto (with normals, so a thin sheet's two sides are told apart)"""
    def __init__(s, P, T):
        s.P = P.copy(); s.T = T.copy(); s.c = P[T].mean(1); s.kd = cKDTree(s.c); fn = tri_normals(P, T); s.fn = unit(fn)
        s.r = np.max(np.linalg.norm(P[T] - s.c[:, None], axis=2), 1)
    def project_bary(s, q, k=24):
        """closest point on the surface: (triangle index, barycentric weights) for each query point"""
        k = min(k, len(s.c)); _, cand = s.kd.query(q, k); best = np.full(len(q), np.inf); bt = np.zeros(len(q), int); bp = q.copy()
        for j in range(k):
            t = cand[:, j]; cp = closest_on_tris(q, s.P[s.T[t, 0]], s.P[s.T[t, 1]], s.P[s.T[t, 2]]); d = np.linalg.norm(cp - q, axis=1)
            better = d < best; best[better] = d[better]; bt[better] = t[better]; bp[better] = cp[better]
        A, B, C = s.P[s.T[bt, 0]], s.P[s.T[bt, 1]], s.P[s.T[bt, 2]]; v0 = B - A; v1 = C - A; v2 = bp - A
        d00 = (v0 * v0).sum(1); d01 = (v0 * v1).sum(1); d11 = (v1 * v1).sum(1); d20 = (v2 * v0).sum(1); d21 = (v2 * v1).sum(1); den = np.maximum(d00 * d11 - d01 * d01, 1e-30)
        v = (d11 * d20 - d01 * d21) / den; w = (d00 * d21 - d01 * d20) / den; u = 1 - v - w
        bc = np.clip(np.stack([u, v, w], 1), 0, 1); bc /= bc.sum(1, keepdims=True); return bt, bc, best
    def project(s, q, qn=None, k=24):
        k = min(k, len(s.c)); _, cand = s.kd.query(q, k); out = q.copy(); best = np.full(len(q), np.inf)
        for j in range(k):
            t = cand[:, j]; cp = closest_on_tris(q, s.P[s.T[t, 0]], s.P[s.T[t, 1]], s.P[s.T[t, 2]]); d = np.linalg.norm(cp - q, axis=1)
            if qn is not None: d = d + 10.0 * np.maximum(0, 0.2 - (s.fn[t] * qn).sum(1))   # the wrong side of a thin sheet costs extra
            better = d < best; best[better] = d[better]; out[better] = cp[better]
        return out

# ---------------- the operations ----------------
def split_long(P, T, Lf, frozen, bnd_plane, extra):
    E, t2, o2, cnt, _ = edges_of(T); a, b = E[:, 0], E[:, 1]; L = np.linalg.norm(P[a] - P[b], axis=1); target = 0.5 * (Lf[a] + Lf[b])
    sp = (L > 4.0 / 3.0 * target) & ~(frozen[a] & frozen[b])
    if not sp.any(): return P, T, Lf, frozen, extra, 0
    ek = E[sp]; base = len(P); key = {(int(x), int(y)): base + i for i, (x, y) in enumerate(ek)}
    mid = 0.5 * (P[ek[:, 0]] + P[ek[:, 1]]); onb = (np.abs(P[ek[:, 0], 0]) < bnd_plane) & (np.abs(P[ek[:, 1], 0]) < bnd_plane); mid[onb, 0] = 0.0
    P = np.vstack([P, mid]); Lf = np.r_[Lf, 0.5 * (Lf[ek[:, 0]] + Lf[ek[:, 1]])]; frozen = np.r_[frozen, np.zeros(len(ek), bool)]
    extra = {k: np.concatenate([v, v[ek[:, 0]]]) for k, v in extra.items()}   # attributes (labels): take the first end's
    newT = []
    for t in T:
        ms = [key.get((min(t[0], t[1]), max(t[0], t[1]))), key.get((min(t[1], t[2]), max(t[1], t[2]))), key.get((min(t[2], t[0]), max(t[2], t[0])))]
        cnt_ = sum(x is not None for x in ms)
        if cnt_ == 0: newT.append(t); continue
        v = list(t)
        if cnt_ == 1:
            i = [j for j in range(3) if ms[j] is not None][0]; A, B, C = v[i], v[(i + 1) % 3], v[(i + 2) % 3]; M_ = ms[i]; newT += [[A, M_, C], [M_, B, C]]
        elif cnt_ == 2:
            i = [j for j in range(3) if ms[j] is None][0]; A, B, C = v[i], v[(i + 1) % 3], v[(i + 2) % 3]; Mbc = ms[(i + 1) % 3]; Mca = ms[(i + 2) % 3]
            newT.append([Mbc, C, Mca])
            if np.linalg.norm(P[A] - P[Mbc]) < np.linalg.norm(P[B] - P[Mca]): newT += [[A, B, Mbc], [A, Mbc, Mca]]
            else: newT += [[A, B, Mca], [B, Mbc, Mca]]
        else:
            A, B, C = v; Mab, Mbc, Mca = ms; newT += [[A, Mab, Mca], [Mab, B, Mbc], [Mca, Mbc, C], [Mab, Mbc, Mca]]
    return P, np.array(newT, np.int64), Lf, frozen, extra, int(sp.sum())

def collapse_short(P, T, Lf, frozen, bnd, rounds=6):
    """greedy rounds of independent collapses of edges shorter than 4/5 of the target"""
    total = 0
    for rnd in range(rounds):
        E, t2, o2, cnt, _ = edges_of(T); n = len(P); a, b = E[:, 0], E[:, 1]; L = np.linalg.norm(P[a] - P[b], axis=1); target = 0.5 * (Lf[a] + Lf[b])
        cand = np.where((L < 0.8 * target) & ~frozen[a] & ~frozen[b])[0]
        if not len(cand): break
        cand = cand[np.argsort(L[cand])]
        # vertex -> neighbours, vertex -> triangles
        nb = [set() for _ in range(n)]
        for x, y in E: nb[x].add(y); nb[y].add(x)
        vt = [[] for _ in range(n)]
        for ti, t in enumerate(T):
            for v in t: vt[v].append(ti)
        sharp = vert_sharpness(P, T, E, t2, cnt)
        isb = bnd; locked = np.zeros(n, bool); dead = np.zeros(n, bool); dead_t = np.zeros(len(T), bool); T = T.copy(); P = P.copy(); done = 0
        for ei in cand:
            x, y = int(a[ei]), int(b[ei])
            if locked[x] or locked[y] or cnt[ei] > 2: continue
            bx, by = isb[x], isb[y]
            if bx and by and cnt[ei] != 1: continue          # two boundary vertices joined through the inside: no
            if by and not bx: x, y = y, x; bx, by = by, bx    # keep the boundary vertex
            # link condition
            common = nb[x] & nb[y]; opp = {int(o) for o in o2[ei] if o >= 0}
            if common != opp: continue
            if not (bx or by) and sharp[y] > sharp[x] + 15: x, y = y, x
            pn = P[x].copy() if (bx and not by) or (sharp[x] > sharp[y] + 15) else 0.5 * (P[x] + P[y])
            if bx and by: pn[0] = 0.0
            # no long edges, no folded triangles
            ok = True
            for v in (nb[x] | nb[y]) - {x, y}:
                if np.linalg.norm(pn - P[v]) > 4.0 / 3.0 * 0.5 * (Lf[v] + Lf[x]): ok = False; break
            if not ok: continue
            for ti in set(vt[x]) | set(vt[y]):
                t = T[ti]
                if x in t and y in t: continue
                q = P[t].copy(); n0 = np.cross(q[1] - q[0], q[2] - q[0])
                for k in range(3):
                    if t[k] in (x, y): q[k] = pn
                n1 = np.cross(q[1] - q[0], q[2] - q[0]); l0, l1 = np.linalg.norm(n0), np.linalg.norm(n1)
                if l1 < 1e-12 or (n0 @ n1) < 0.5 * l0 * l1: ok = False; break
            if not ok: continue
            # do it: y merges into x
            P[x] = pn; dead[y] = True
            for ti in vt[y]:
                t = T[ti]
                if x in t: dead_t[ti] = True; continue
                T[ti] = np.where(t == y, x, t)
            vt[x] = [ti for ti in set(vt[x]) | set(vt[y]) if not dead_t[ti]]
            for v in nb[y]:
                if v != x: nb[v].discard(y); nb[v].add(x); nb[x].add(v)
            nb[x].discard(y)
            for v in nb[x]: locked[v] = True
            locked[x] = True; Lf[x] = 0.5 * (Lf[x] + Lf[y]); frozen[x] = frozen[x] or frozen[y]; done += 1
        T = T[~dead_t]; total += done
        if done == 0: break
    return P, T, Lf, frozen, total

def flip_valence(P, T, frozen, bnd, rounds=6, max_dihedral=25.0):
    total = 0; cosmax = np.cos(np.radians(max_dihedral))
    for rnd in range(rounds):
        E, t2, o2, cnt, dirn = edges_of(T); n = len(P)
        val = np.bincount(E.ravel(), minlength=n); tgt = np.where(bnd, 4, 6)
        inner = np.where((cnt == 2) & ~(bnd[E[:, 0]] & bnd[E[:, 1]]))[0]
        a, b = E[inner, 0], E[inner, 1]; c, d = o2[inner, 0], o2[inner, 1]
        dev0 = np.abs(val[a] - tgt[a]) + np.abs(val[b] - tgt[b]) + np.abs(val[c] - tgt[c]) + np.abs(val[d] - tgt[d])
        dev1 = np.abs(val[a] - 1 - tgt[a]) + np.abs(val[b] - 1 - tgt[b]) + np.abs(val[c] + 1 - tgt[c]) + np.abs(val[d] + 1 - tgt[d])
        good = (dev1 < dev0) & ~frozen[a] & ~frozen[b] & ~frozen[c] & ~frozen[d]
        fn = unit(tri_normals(P, T)); n1 = fn[t2[inner, 0]]; n2 = fn[t2[inner, 1]]
        good &= (n1 * n2).sum(1) > cosmax
        idx = inner[good]
        if not len(idx): break
        existing = set(map(tuple, E.tolist())); usedt = np.zeros(len(T), bool); T = T.copy(); done = 0
        for ei in idx:
            ta, tb = t2[ei]
            if usedt[ta] or usedt[tb]: continue
            # orientation: triangle ta has edge u->v, its opposite vertex c; tb has v->u, opposite d
            u, v = dirn[ei, 0]; c_, d_ = o2[ei, 0], o2[ei, 1]
            key = (min(c_, d_), max(c_, d_))
            if key in existing or c_ == d_: continue
            nt1 = np.array([c_, u, d_]); nt2 = np.array([d_, v, c_])
            # check the orientation of the replacement: (c, u, d) and (d, v, c) for ta = (u, v, c), tb = (v, u, d)
            q1 = np.cross(P[nt1[1]] - P[nt1[0]], P[nt1[2]] - P[nt1[0]]); q2 = np.cross(P[nt2[1]] - P[nt2[0]], P[nt2[2]] - P[nt2[0]])
            nav = fn[ta] + fn[tb]
            if (unit(q1) @ unit(nav)) < 0.7 or (unit(q2) @ unit(nav)) < 0.7: continue
            T[ta] = nt1; T[tb] = nt2; usedt[ta] = usedt[tb] = True; existing.add(key); done += 1
        total += done
        if done == 0: break
    return T, total

def relax(P, T, frozen, bnd, surf, lam=0.5, iters=1):
    n = len(P)
    for _ in range(iters):
        E, t2, o2, cnt, _ = edges_of(T); N = vert_normals(P, T)
        acc = np.zeros_like(P); deg = np.zeros(n)
        # interior: all neighbours; boundary: boundary neighbours along boundary edges only
        be = cnt == 1
        for (x, y), isbe in zip(E, be):
            if bnd[x] and not (isbe): pass
            else: acc[x] += P[y]; deg[x] += 1
            if bnd[y] and not (isbe): pass
            else: acc[y] += P[x]; deg[y] += 1
        cen = acc / np.maximum(deg, 1)[:, None]; mv = cen - P
        sh = vert_sharpness(P, T, E, t2, cnt); keepk = np.clip((sh - 35.0) / 45.0, 0, 1); mv *= (1 - keepk)[:, None]
        mv = mv - N * (mv * N).sum(1, keepdims=True) * (~bnd)[:, None]   # tangential for interior vertices
        mv[frozen | (deg == 0)] = 0
        Pn = P + lam * mv
        Pn = np.where(frozen[:, None], P, surf.project(Pn, N))
        Pn[bnd & (np.abs(P[:, 0]) < 1e-9), 0] = 0.0
        P = Pn
    return P

def remesh(P, T, Lf, frozen=None, iters=5, plane_tol=1e-6, labels=None, verbose=True):
    """P, T: the half mesh (x >= 0, its open boundary on x = 0); Lf: per-vertex target edge length; frozen: per-vertex bool (kept as is);
    labels: optional per-vertex array carried by nearest-vertex transfer. Returns P, T (and labels)"""
    surf = Surface(P, T); frozen = np.zeros(len(P), bool) if frozen is None else frozen.copy(); Lf = Lf.astype(float).copy()
    extra = {} if labels is None else {'lab': np.asarray(labels)}
    for it in range(iters):
        P, T, Lf, frozen, extra, ns = split_long(P, T, Lf, frozen, 1e-7, extra)
        E, t2, o2, cnt, _ = edges_of(T); bnd = boundary_verts(len(P), E, cnt)
        P, T, Lf, frozen, nc = collapse_short(P, T, Lf, frozen, bnd)
        P, T, keep = compact(P, T, {'Lf': Lf, 'frozen': frozen, **extra}); Lf = keep['Lf']; frozen = keep['frozen']; extra = {k: keep[k] for k in extra}
        E, t2, o2, cnt, _ = edges_of(T); bnd = boundary_verts(len(P), E, cnt)
        T, nf = flip_valence(P, T, frozen, bnd)
        P = relax(P, T, frozen, bnd, surf)
        if verbose:
            q = quality(P, T); print(f'   remesh it {it}: split {ns} collapse {nc} flip {nf} -> {len(P)} verts {len(T)} tris; quality min {q.min():.3f} p1 {np.percentile(q, 1):.3f} median {np.median(q):.3f}')
    T, nd = fix_degenerate(P, T)
    if verbose and nd: print(f'   remesh: {nd} sliver flips')
    return (P, T, extra['lab']) if labels is not None else (P, T)
def fix_degenerate(P, T, qmin=0.06, rounds=6):
    """flip the longest edge of near-degenerate triangles (collinear slivers) when the two new triangles are better than the old pair"""
    total = 0
    for rnd in range(rounds):
        q = quality(P, T); bad = np.where(q < qmin)[0]
        if not len(bad): break
        E, t2, o2, cnt, dirn = edges_of(T); key = {(int(a), int(b)): i for i, (a, b) in enumerate(E)}; existing = set(key); T = T.copy(); used = np.zeros(len(T), bool); done = 0
        for t in bad:
            if used[t]: continue
            v = T[t]; L = [np.linalg.norm(P[v[(k + 1) % 3]] - P[v[k]]) for k in range(3)]; k = int(np.argmax(L)); a, b = int(v[k]), int(v[(k + 1) % 3])
            ei = key.get((min(a, b), max(a, b)))
            if ei is None or cnt[ei] != 2: continue
            ta, tb = t2[ei]
            if used[ta] or used[tb]: continue
            u_, w_ = dirn[ei, 0]; c_, d_ = o2[ei, 0], o2[ei, 1]
            if (min(c_, d_), max(c_, d_)) in existing or c_ == d_: continue
            nt1 = np.array([c_, u_, d_]); nt2 = np.array([d_, w_, c_])
            qo = min(q[ta], q[tb]); qn = min(quality(P, nt1[None])[0], quality(P, nt2[None])[0])
            n_old = tri_normals(P, T[[ta, tb]]).sum(0); n1 = tri_normals(P, nt1[None])[0]; n2 = tri_normals(P, nt2[None])[0]
            if qn <= qo or (n1 @ n_old) <= 0 or (n2 @ n_old) <= 0: continue
            T[ta] = nt1; T[tb] = nt2; used[ta] = used[tb] = True; existing.add((min(c_, d_), max(c_, d_))); done += 1
        total += done
        if not done: break
    return T, total
def quality(P, T):
    a = P[T[:, 1]] - P[T[:, 0]]; b = P[T[:, 2]] - P[T[:, 0]]; c = P[T[:, 2]] - P[T[:, 1]]
    A = np.linalg.norm(np.cross(a, b), axis=1) / 2; s2 = (a * a).sum(1) + (b * b).sum(1) + (c * c).sum(1); return 4 * np.sqrt(3) * A / np.maximum(s2, 1e-30)
