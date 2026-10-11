# The v7 crawl mesh, from the user's crawl sculpt:
#   1. straighten: unbend the S-curved trunk + tail (a lateral curve deformer along a measured centreline), the head + gills carried as ONE rigid
#      piece turned onto the body axis by its own mirror plane, the limbs carried rigidly by the frame they grow from
#   2. symmetrize: per-slab mirror-plane drift removed, cut at x = 0, the character's left half (+x: the four-toed hind foot) mirrored
# Output: crawl_sym.npz (welded positions P, triangles T, per-vertex source map for attributes) + a viewable runtime mesh in www/rb/
import sys, os, json, time
sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo2'); sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo3')
import numpy as np
from scipy.spatial import cKDTree
from geo import M, D
from straighten import write_view, resample, smooth_poly
from mirror import surf_samples, sym_fit_x0, cut_and_mirror
from arap import arap
O = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo3/'
SEED = dict(snout=(-0.3, 0.02, 0.95), tailtip=(0.85, 0.22, -0.95))
def unit(v): v = np.asarray(v, float); return v / (np.linalg.norm(v, axis=-1, keepdims=True) + 1e-12)
def ss(t): t = np.clip(t, 0, 1); return t * t * (3 - 2 * t)
def sym_plane(S, c, yaws, offs):
    kd = cKDTree(S); best = None
    for th in yaws:
        nrm = np.array([np.cos(th), 0, -np.sin(th)])
        for off in offs:
            p0 = c + nrm * off; d0 = (S - p0) @ nrm; R = S - 2 * d0[:, None] * nrm[None]; d, _ = kd.query(R); e = np.mean(np.minimum(d, 0.04) ** 2)
            if best is None or e < best[0]: best = (e, th, off)
    return best
def load_old():
    m = M('crawl'); r = np.load(D + 'crawl_rig.npz', allow_pickle=True); names = list(r['names']); W = np.zeros((m.n, len(names)))
    for c in range(4): np.add.at(W, (np.arange(m.n), r['idx'][:, c]), r['w'][:, c])
    labels = np.array([str(x) for x in r['labels']]); return m, W, names, labels
def stage1():
    t0 = time.time(); m, W, names, lab = load_old(); P = m.P.copy(); T = m.T; bi = {k: i for i, k in enumerate(names)}
    wsum = lambda pred: np.clip(W[:, [i for k, i in bi.items() if pred(k)]].sum(1), 0, 1)
    isg = np.array([l.startswith('gill') for l in lab]); head = lab == 'head'
    # ---- the head's own mirror plane (original sculpt): yaw and offset, coarse then fine, on 9k samples of the skull (no gills)
    Sh = surf_samples(P, T[head[T].all(1)], 9000); hc = P[head].mean(0)
    e, th, off = sym_plane(Sh, hc, np.radians(np.arange(-40, 41, 2.5)), np.linspace(-0.12, 0.12, 25))
    e, th, off = sym_plane(Sh, hc, np.linspace(th - np.radians(2.5), th + np.radians(2.5), 11), np.linspace(off - 0.01, off + 0.01, 11))
    print(f'head mirror plane: yaw {np.degrees(th):+.2f} deg, offset {off:+.3f} m, rms {np.sqrt(e) * 1000:.1f} mm  ({time.time() - t0:.0f}s)')
    nrm = np.array([np.cos(th), 0, -np.sin(th)]); p0 = hc + nrm * off; fwd_h = np.array([np.sin(th), 0, np.cos(th)])   # in the plane, horizontal: the head's forward
    # ---- trunk + tail centreline (top view), from the neck to the tail tip; the head's forward axis continues it.
    # The body runs monotonic in z, so z-slices of dense surface samples of the clean tube (no limb roots, nothing within 4 cm of a gill: the old
    # rig pinned fused frill skin to the shoulders) give the midline as each slice's mid extent, smoothed along z.
    limbw = wsum(lambda k: k.startswith(('upperarm', 'forearm', 'hand', 'finger', 'thigh', 'shin', 'foot', 'toes', 'toe')))
    gd, _ = cKDTree(P[isg]).query(P); clean = np.isin(lab, ['trunk', 'tail']) & (limbw < 0.12) & (gd > 0.04)
    Sc = surf_samples(P, T[clean[T].all(1)], 60000); zt = P[m.near(SEED['tailtip']), 2]
    zz = np.arange(Sc[:, 2].max() - 0.01, zt + 0.005, -0.01); mid = []
    for z_ in zz:
        q = Sc[np.abs(Sc[:, 2] - z_) < 0.015]
        mid.append([(q[:, 0].min() + q[:, 0].max()) / 2, (q[:, 1].min() + q[:, 1].max()) / 2, z_] if len(q) > 20 else [np.nan] * 3)
    mid = np.array(mid); ok = np.isfinite(mid[:, 0]); mid = mid[ok]
    gk = lambda a, s: np.array([np.sum(a * np.exp(-0.5 * ((mid[:, 2] - z_) / s) ** 2)) / np.sum(np.exp(-0.5 * ((mid[:, 2] - z_) / s) ** 2)) for z_ in mid[:, 2]])
    mid[:, 0] = gk(mid[:, 0], 0.05); mid[:, 1] = gk(mid[:, 1], 0.05)
    tipp = P[m.near(SEED['tailtip'])]; mid = np.vstack([mid, tipp[None]])
    print(f'  tube midline: {len(mid)} slices, z {mid[0, 2]:+.2f} .. {mid[-1, 2]:+.2f}, x {mid[:, 0].min():+.2f} .. {mid[:, 0].max():+.2f}')
    # the neck: from the head's plane point straight back along the head axis, eased into the tube's front end
    zf = mid[0]; hx = []
    for s_ in np.arange(0.35, -0.001, -0.02): hx.append(p0 + fwd_h * s_)
    gap = np.linalg.norm((p0 - zf)[[0, 2]]); nb = max(2, int(gap / 0.02))
    for k_ in range(1, nb): u = k_ / nb; hx.append(p0 * (1 - u) + zf * u - fwd_h * 0.0)
    cen = np.vstack([np.array(hx), mid]); cen = smooth_poly(resample(cen, 0.01), it=30, lam=0.5); cen = resample(cen, 0.01)
    np.save(O + 'cen_dbg.npy', cen)
    C2 = cen[:, [0, 2]]; s_c = np.r_[0, np.cumsum(np.linalg.norm(np.diff(C2, axis=0), axis=1))]
    T2 = unit(np.gradient(C2, axis=0)); B2 = np.stack([-T2[:, 1], T2[:, 0]], 1)
    kd = cKDTree(C2); _, ci = kd.query(P[:, [0, 2]])
    def mp(v_xz, i): rel = v_xz - C2[i]; a = (rel * B2[i]).sum(-1); l = (rel * T2[i]).sum(-1); return np.stack([a, -(s_c[i] + l)], -1)
    out = mp(P[:, [0, 2]], ci); klimb = np.zeros(m.n)
    # limbs: rigid with the frame at their root
    for chain in (('upperarm', 'forearm', 'hand', 'finger'), ('thigh', 'shin', 'foot', 'toes', 'toe')):
        for sd in 'LR':
            wl = wsum(lambda k: any(k.startswith(c) for c in chain) and (k.endswith('.' + sd) or ('.' + sd + '.') in k))
            band = (wl > 0.3) & (wl < 0.7); root = P[band].mean(0) if band.sum() > 3 else P[wl > 0.5].mean(0)
            i0 = int(kd.query(root[[0, 2]])[1]); rv = mp(P[:, [0, 2]], np.full(m.n, i0)); k = ss((wl - 0.15) / 0.55); out = out * (1 - k[:, None]) + rv * k[:, None]; klimb = np.maximum(klimb, k)
    # the head + gills: one rigid piece. Its rotation turns its mirror plane square to x; its position follows the tube map of the head centre
    ih = int(kd.query(p0[[0, 2]])[1]); c_, s_ = np.cos(-th), np.sin(-th); Ry = np.array([[c_, 0, s_], [0, 1, 0], [-s_, 0, c_]])
    tgt = mp(p0[None, [0, 2]], np.array([ih]))[0]   # where the head's plane point lands (x lateral, z)
    Ph = (P - p0) @ Ry.T; Ph[:, 0] += 0.0; Ph[:, 2] += tgt[1]; Ph[:, 1] += p0[1]   # x: plane at 0
    kh = np.maximum(wsum(lambda k: k in ('head', 'headfront') or k.startswith('gill')), (head | isg).astype(float))
    kh = np.maximum(kh, ss((P - hc) @ fwd_h / 0.0 if False else np.zeros(m.n)))
    nk = wsum(lambda k: k == 'neck'); kh = np.clip(kh + 0.6 * nk, 0, 1); kh = ss(kh)
    Pn = np.stack([out[:, 0], P[:, 1], out[:, 1]], 1); Pn = Pn * (1 - kh[:, None]) + Ph * kh[:, None]
    # the blend bands (limb roots, the neck) are re-solved as-rigid-as-possible against the sculpt: the mapped cores stay put
    blend = ~(((klimb < 0.02) & (kh < 0.02)) | (klimb > 0.98) | (kh > 0.98))
    gb = m.geo(np.where(blend)[0], limit=0.09); fixed = ~(np.isfinite(gb) & (gb < 0.08))
    fixed |= isg & (gb > 0.03)   # the gill frills keep their carried shape
    print(f'  ARAP: {int((~fixed).sum())} free verts in the blend bands')
    Pn = arap(P, T, Pn, fixed, iters=25, verbose=True)
    print(f'straightened ({time.time() - t0:.0f}s): bbox', Pn.min(0).round(3), Pn.max(0).round(3))
    # ---- per-slab drift of the trunk + tail mirror plane, removed by a smooth lateral shift (the head is already on x = 0)
    body = np.isin(lab, ['trunk', 'tail']); Sb = surf_samples(Pn, T[body[T].all(1)], 40000)
    zs = np.arange(Sb[:, 2].max() - 0.04, Sb[:, 2].min() + 0.04, -0.06); x0 = []
    for zz in zs:
        sel = np.abs(Sb[:, 2] - zz) < 0.06
        x0.append(sym_fit_x0(Sb[sel], (-0.12, 0.12), 49)[0] if sel.sum() > 150 else np.nan)
    x0 = np.array(x0); ok = np.isfinite(x0); x0 = np.interp(zs, zs[ok][::-1], x0[ok][::-1]); xs = x0.copy()
    for _ in range(6): xs[1:-1] = 0.25 * xs[:-2] + 0.5 * xs[1:-1] + 0.25 * xs[2:]
    print('slab drift (cm):', ' '.join(f'{a:+.2f}:{c * 100:+.1f}' for a, c in zip(zs[::3], xs[::3])))
    zh = Pn[head, 2].min()   # the drift fades out toward the head (already square)
    sh = np.interp(Pn[:, 2], zs[::-1], xs[::-1]) * (1 - kh) * ss((zh - Pn[:, 2]) / 0.15 + 0.0)
    for chain in (('upperarm', 'forearm', 'hand', 'finger'), ('thigh', 'shin', 'foot', 'toes', 'toe')):
        for sd in 'LR':
            wl = wsum(lambda k: any(k.startswith(c) for c in chain) and (k.endswith('.' + sd) or ('.' + sd + '.') in k))
            root = Pn[(wl > 0.3) & (wl < 0.7)].mean(0); sr = np.interp(root[2], zs[::-1], xs[::-1]) * ss((zh - root[2]) / 0.15); sh = sh * (1 - wl) + sr * wl
    Pn[:, 0] -= sh
    np.savez(O + 'crawl_straight2.npz', P=Pn, labels=lab, head_yaw=th)
    write_view(O + 'www/rb/', 'straight2', m, Pn)
    # ---- cut at x = 0 and mirror the +x half
    Pm, Tm, src, side = cut_and_mirror(Pn, T)
    np.savez(O + 'crawl_sym.npz', P=Pm, T=Tm, src=np.array([list(s) for s in src], dtype=float), side=side)
    class MM: pass
    mm = MM(); mm.T = Tm; write_view(O + 'www/rb/', 'sym', mm, Pm)
    print(f'mirrored: {len(Pm)} verts, {len(Tm)} tris ({time.time() - t0:.0f}s)')
if __name__ == '__main__':
    stage1()
