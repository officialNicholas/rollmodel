# Step 2 of the crawl rebuild: a symmetric crawl body. The straightened sculpt (straighten.py) still carries a few cm of lateral drift and a
# turned head; this fits the true mirror plane per slab (Chamfer symmetry of dense surface samples), turns the head + gills rigidly onto the
# body axis (head yaw from its own symmetry), then cuts at x = 0, keeps the character's left half (+x: the four-toed hind foot) and mirrors it.
import sys, os, json
sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo2'); sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo3')
import numpy as np
from scipy.spatial import cKDTree
from geo import M, D
from straighten import write_view
O = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo3/'
def unit(v): v = np.asarray(v, float); return v / (np.linalg.norm(v, axis=-1, keepdims=True) + 1e-12)
def surf_samples(P, T, n=60000, seed=1):
    a = P[T[:, 0]]; b = P[T[:, 1]]; c = P[T[:, 2]]; ar = 0.5 * np.linalg.norm(np.cross(b - a, c - a), axis=1); rng = np.random.default_rng(seed)
    t = rng.choice(len(T), n, p=ar / ar.sum()); u = rng.random(n); v = rng.random(n); f = u + v > 1; u[f] = 1 - u[f]; v[f] = 1 - v[f]
    return a[t] + u[:, None] * (b[t] - a[t]) + v[:, None] * (c[t] - a[t])
def sym_fit_x0(S, x_range=(-0.15, 0.15), steps=61):
    """best mirror plane x = x0 for samples S (reflect, Chamfer to themselves)"""
    kd = cKDTree(S); best = None
    for x0 in np.linspace(*x_range, steps):
        R = S.copy(); R[:, 0] = 2 * x0 - R[:, 0]; d, _ = kd.query(R); e = np.mean(np.minimum(d, 0.05) ** 2)
        if best is None or e < best[0]: best = (e, x0)
    lo, hi = best[1] - (x_range[1] - x_range[0]) / steps, best[1] + (x_range[1] - x_range[0]) / steps
    for x0 in np.linspace(lo, hi, 21):
        R = S.copy(); R[:, 0] = 2 * x0 - R[:, 0]; d, _ = kd.query(R); e = np.mean(np.minimum(d, 0.05) ** 2)
        if e < best[0]: best = (e, x0)
    return best[1], best[0]
def sym_fit_plane(S, c, yaw_range=np.radians(40)):
    """best vertical mirror plane through a point near c: yaw angle and lateral offset (head)"""
    kd = cKDTree(S); best = None
    for th in np.linspace(-yaw_range, yaw_range, 41):
        nrm = np.array([np.cos(th), 0, -np.sin(th)])
        for off in np.linspace(-0.12, 0.12, 25):
            p0 = c + nrm * off; d0 = (S - p0) @ nrm; R = S - 2 * d0[:, None] * nrm[None]; d, _ = kd.query(R); e = np.mean(np.minimum(d, 0.05) ** 2)
            if best is None or e < best[0]: best = (e, th, off)
    e, th, off = best
    for th2 in np.linspace(th - np.radians(1), th + np.radians(1), 9):
        nrm = np.array([np.cos(th2), 0, -np.sin(th2)])
        for off2 in np.linspace(off - 0.01, off + 0.01, 11):
            p0 = c + nrm * off2; d0 = (S - p0) @ nrm; R = S - 2 * d0[:, None] * nrm[None]; d, _ = kd.query(R); e2 = np.mean(np.minimum(d, 0.05) ** 2)
            if e2 < best[0]: best = (e2, th2, off2)
    return best
def main():
    m = M('crawl'); T = m.T; z = np.load(O + 'crawl_straight.npz', allow_pickle=True); P = z['P'].copy(); lab = z['labels']
    r = np.load(D + 'crawl_rig.npz', allow_pickle=True); names = list(r['names']); W = np.zeros((m.n, len(names)))
    for c in range(4): np.add.at(W, (np.arange(m.n), r['idx'][:, c]), r['w'][:, c])
    bi = {k: i for i, k in enumerate(names)}; ws = lambda pre: np.clip(W[:, [i for k, i in bi.items() if k.startswith(pre)]].sum(1), 0, 1)
    isg = np.array([l.startswith('gill') for l in lab]); head = lab == 'head'
    # ---- 1. the head (+ gills) as one rigid piece: its own mirror plane, turned onto the body axis
    th_ = (T[:, None] == np.where(head)[0][None, None]).any(-1) if False else head[T].all(1)
    Sh = surf_samples(P, T[th_], 30000); hc = P[head].mean(0)
    e, th, off = sym_fit_plane(Sh, hc); nrm = np.array([np.cos(th), 0, -np.sin(th)]); p0 = hc + nrm * off
    print(f'head mirror plane: yaw {np.degrees(th):+.1f} deg, offset {off:+.3f}, chamfer rms {np.sqrt(e) * 1000:.1f} mm')
    # rotate about y by -th (so the plane normal becomes +x) about p0, then move p0 onto x = 0
    c_, s_ = np.cos(-th), np.sin(-th); Ry = np.array([[c_, 0, s_], [0, 1, 0], [-s_, 0, c_]])
    Rn = Ry @ nrm; print('  head plane normal after turn', Rn.round(3))
    headk = np.clip(ws('head') + ws('headfront') + ws('gill') + 0.0, 0, 1); headk = np.maximum(headk, (head | isg).astype(float))
    neckw = ws('neck'); headk = np.clip(headk + 0.5 * neckw * (P[:, 2] > hc[2] - 0.25), 0, 1)   # the neck eases in
    Ph = (P - p0) @ Ry.T + np.array([0, p0[1], p0[2]]); Ph[:, 0] -= 0.0
    k = headk * headk * (3 - 2 * headk); P1 = P * (1 - k[:, None]) + Ph * k[:, None]
    # ---- 2. trunk and tail: the mirror plane per slab, a smooth lateral shift
    body = np.isin(lab, ['trunk', 'tail']); tb = body[T].all(1); Sb = surf_samples(P1, T[tb], 80000)
    zs = np.arange(Sb[:, 2].max() - 0.04, Sb[:, 2].min() + 0.04, -0.06); x0 = []
    for zz in zs:
        sel = np.abs(Sb[:, 2] - zz) < 0.06
        if sel.sum() < 200: x0.append(np.nan); continue
        xv, ev = sym_fit_x0(Sb[sel]); x0.append(xv)
    x0 = np.array(x0); ok = np.isfinite(x0); x0 = np.interp(zs, zs[ok][::-1], x0[ok][::-1])
    xs = x0.copy()
    for _ in range(6): xs[1:-1] = 0.25 * xs[:-2] + 0.5 * xs[1:-1] + 0.25 * xs[2:]
    print('trunk/tail mirror offsets (z: raw -> smooth):', ' '.join(f'{a:+.2f}:{b * 100:+.1f}/{c * 100:+.1f}' for a, b, c in zip(zs[::3], x0[::3], xs[::3])))
    shift = np.interp(P1[:, 2], zs[::-1], xs[::-1]); shift = shift * (1 - k)   # (the head already sits on x = 0)
    # limbs shift with the slab at their root (a translation keeps them rigid)
    for pre, sd in (('upperarm', 'L'), ('upperarm', 'R'), ('thigh', 'L'), ('thigh', 'R')):
        grp = ['upperarm', 'forearm', 'hand', 'finger'] if pre == 'upperarm' else ['thigh', 'shin', 'foot', 'toes', 'toe']
        cols = [i for kk, i in bi.items() if any(kk.startswith(g) for g in grp) and ('.' + sd) in kk]; wl = np.clip(W[:, cols].sum(1), 0, 1)
        root = P1[(wl > 0.3) & (wl < 0.7)].mean(0); sr = np.interp(root[2], zs[::-1], xs[::-1]); shift = shift * (1 - wl) + sr * wl
    P2 = P1.copy(); P2[:, 0] -= shift
    np.savez(O + 'crawl_sym_pre.npz', P=P2, labels=lab)
    write_view(O + 'www/rb/', 'presym', m, P2)
    # ---- 3. cut at x = 0, keep x >= 0, mirror
    Pm, Tm, src, uvw = cut_and_mirror(P2, T, m.UV[m.uidx] if hasattr(m, 'uidx') else None)
    np.savez(O + 'crawl_mirror.npz', P=Pm, T=Tm, src=src, uvw=uvw)
    class MM: pass
    mm = MM(); mm.T = Tm; write_view(O + 'www/rb/', 'mirror', mm, Pm)
    print('mirrored mesh', len(Pm), 'verts', len(Tm), 'tris')
def cut_and_mirror(P, T, UV=None, eps=1e-6):
    """keep the part of the surface with x >= 0 (triangles crossing x = 0 are clipped), mirror it, weld the cut. Returns P, T, src (for each
    new vertex: two source vertices and a blend weight, for carrying attributes), uv"""
    n = len(P); x = P[:, 0].copy(); x[np.abs(x) < eps] = 0.0
    newP = list(P); newsrc = [(i, i, 0.0) for i in range(n)]; edge_cache = {}
    def cut_vertex(a, b):
        key = (min(a, b), max(a, b))
        if key in edge_cache: return edge_cache[key]
        u = x[a] / (x[a] - x[b]); p = P[a] + u * (P[b] - P[a]); p[0] = 0.0; newP.append(p); newsrc.append((a, b, u)); edge_cache[key] = len(newP) - 1; return len(newP) - 1
    keep = []
    for t in T:
        s = [x[i] >= 0 for i in t]
        if all(s): keep.append(list(t)); continue
        if not any(s): continue
        # clip the triangle to x >= 0 (polygon clipping against one plane)
        poly = []
        for k in range(3):
            a, b = t[k], t[(k + 1) % 3]; ina, inb = x[a] >= 0, x[b] >= 0
            if ina: poly.append(a)
            if ina != inb and x[a] != 0 and x[b] != 0: poly.append(cut_vertex(a, b))
        for k in range(1, len(poly) - 1): keep.append([poly[0], poly[k], poly[k + 1]])
    P1 = np.array(newP); src = np.array(newsrc, dtype=object); K = np.array(keep)
    used = np.unique(K); remap = -np.ones(len(P1), int); remap[used] = np.arange(len(used)); P1 = P1[used]; K = remap[K]; src = src[used]
    on = np.abs(P1[:, 0]) < 1e-9; P1[on, 0] = 0
    # mirror: vertices on the plane are shared
    nm = len(P1); mir = np.where(on, np.arange(nm), nm + np.cumsum(~on) - 1); Pm = np.vstack([P1, P1[~on] * np.array([-1, 1, 1])])
    Km = mir[K][:, ::-1]; Tall = np.vstack([K, Km])
    srcall = np.concatenate([src, src[~on]])
    # drop degenerate triangles (zero area from clipping exactly through vertices)
    a = Pm[Tall[:, 0]]; b = Pm[Tall[:, 1]]; c = Pm[Tall[:, 2]]; ar = np.linalg.norm(np.cross(b - a, c - a), axis=1); Tall = Tall[ar > 1e-12]
    side = np.r_[np.ones(nm), -np.ones(len(Pm) - nm)]
    return Pm, Tall, srcall, side
if __name__ == '__main__': main()
