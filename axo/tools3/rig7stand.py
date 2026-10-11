# v7 stand rig: the v6 standing sculpt made mirror-symmetric from its right half (the side whose arm the review called perfect), the tail
# straightened onto the midline first, the face cap exactly spherical, isotropically remeshed like the crawl (same triangle sizes per region),
# the v6 right-side skin weights and joints carried over and mirrored bone for bone. Limb frames follow the crawl's conventions.
import sys, os, json, time
sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo2'); sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo3')
import numpy as np
from scipy.spatial import cKDTree
from mesh import Mesh, mirror_map
O = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo3/'
A2 = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo2/'
OFF = np.array([0.0091, -0.023, -0.6231])          # stand source -> export coordinates
CS = np.array([0.021, 1.19, 0.041]); RS = 0.329    # the stand's face sphere (export, before symmetrizing)
def ss(t): t = np.clip(t, 0, 1); return t * t * (3 - 2 * t)
def unit(v): v = np.asarray(v, float); return v / (np.linalg.norm(v, axis=-1, keepdims=True) + 1e-12)
def mirror_name(k): return k.replace('.L', '.#').replace('.R', '.L').replace('.#', '.R')
def source():
    """the v6 stand: welded mesh (export coordinates), dense skin weights, labels, bones"""
    from geo import M
    ms = M('stand'); P = ms.P + OFF; T = ms.T
    r = np.load(A2 + 'stand_rig.npz', allow_pickle=True); names = [str(x) for x in r['names']]; lab = np.array([str(x) for x in r['labels']])
    W = np.zeros((len(P), len(names)))
    for c in range(4): np.add.at(W, (np.arange(len(P)), r['idx'][:, c].astype(int)), r['w'][:, c])
    meta = json.load(open(A2 + 'stand_export.json')); B = {b['name']: b for b in meta['bones']}
    return P, T, W, lab, names, B
def dominant_region(W, names):
    bi = np.argmax(W, 1); nm = np.array(names)[bi]
    def reg(n):
        if n.startswith('gill'): return 'gill'
        if n.startswith(('finger', 'toe')) and not n.startswith('toes'): return 'digit'
        if n.startswith(('upperarm', 'forearm', 'hand', 'thigh', 'shin', 'foot', 'toes', 'shoulder')): return 'limb'
        if n.startswith('tail'): return 'tail'
        if n in ('head', 'headfront'): return 'head'
        return 'trunk'
    return np.array([reg(n) for n in nm])
# ======================== symmetric from the right half ========================
def symmetrize(save=True):
    """the head (+ gills) turned and moved onto x = 0 as one rigid piece, the trunk and the tail moved slab by slab onto the midline, each
    limb carried rigidly with its root; then the right half (x < 0) cut at x = 0 and mirrored. Weights ride along (mirrored with .L/.R
    swapped); joints are moved with the same field and the right side's mirrored to the left"""
    from mirror import surf_samples, sym_fit_x0, sym_fit_plane, cut_and_mirror
    P, T, W, lab, names, B = source(); bi = {k: i for i, k in enumerate(names)}; reg = dominant_region(W, names)
    ws = lambda pre: np.clip(W[:, [i for k, i in bi.items() if k.startswith(pre)]].sum(1), 0, 1)
    # 1. head + gills: the front's mirror plane (yaw, offset), turned onto the y-z plane
    hd = reg == 'head'; Sh = surf_samples(P, T[hd[T].all(1)], 20000); hc = P[hd].mean(0)
    fr = Sh[:, 2] > hc[2]; e, th, off = sym_fit_plane(Sh[fr], hc); nrm = np.array([np.cos(th), 0, -np.sin(th)]); p0 = hc + nrm * off
    c_, s_ = np.cos(-th), np.sin(-th); Ry = np.array([[c_, 0, s_], [0, 1, 0], [-s_, 0, c_]])
    headT = lambda X: (np.asarray(X) - p0) @ Ry.T + np.array([0, p0[1], p0[2]])
    print(f'  head plane: yaw {np.degrees(th):+.2f} deg, x at the head centre {p0[0]:+.3f}; normal after turn {(Ry @ nrm).round(3)}')
    hk = np.clip(ws('head') + ws('headfront') + ws('gill'), 0, 1); hk = np.maximum(hk, np.isin(reg, ['head', 'gill']).astype(float)); hk = hk * hk * (3 - 2 * hk)
    # 2. trunk: the mirror plane per height; 3. tail: per slab along it
    tr = reg == 'trunk'; Sb = surf_samples(P, T[tr[T].all(1)], 30000); ys = np.arange(Sb[:, 1].min() + 0.04, Sb[:, 1].max() - 0.02, 0.06); xy = []
    for y in ys:
        sel = np.abs(Sb[:, 1] - y) < 0.05; xy.append(sym_fit_x0(Sb[sel], (-0.1, 0.12), 45)[0] if sel.sum() > 300 else np.nan)
    xy = np.array(xy); ok = np.isfinite(xy); xy = np.interp(ys, ys[ok], xy[ok])
    for _ in range(4): xy[1:-1] = 0.25 * xy[:-2] + 0.5 * xy[1:-1] + 0.25 * xy[2:]
    tl = reg == 'tail'; St = surf_samples(P, T[tl[T].all(1)], 30000); zs = np.arange(St[:, 2].max() - 0.04, St[:, 2].min() + 0.03, -0.08); xz = []
    for z in zs:
        sel = np.abs(St[:, 2] - z) < 0.06; xz.append(sym_fit_x0(St[sel], (-0.35, 0.35), 71)[0] if sel.sum() > 200 else np.nan)
    xz = np.array(xz); ok = np.isfinite(xz); xz = np.interp(zs, zs[ok][::-1], xz[ok][::-1])
    for _ in range(3): xz[1:-1] = 0.25 * xz[:-2] + 0.5 * xz[1:-1] + 0.25 * xz[2:]
    print('  trunk offsets (y: cm):', ' '.join(f'{a:.2f}:{b * 100:+.1f}' for a, b in zip(ys[::2], xy[::2])))
    print('  tail offsets (z: cm):', ' '.join(f'{a:+.2f}:{b * 100:+.1f}' for a, b in zip(zs[::2], xz[::2])))
    sh_tr = lambda X: np.interp(np.asarray(X)[..., 1], ys, xy)
    sh_tl = lambda X: np.interp(np.asarray(X)[..., 2], zs[::-1], xz[::-1])
    # the tail's share: its weight, easing into the trunk's over the tail's base
    tk = np.clip(ws('tail'), 0, 1); tk = np.maximum(tk, tl.astype(float)); zb = zs[0]
    shift = sh_tr(P) * (1 - tk) + sh_tl(P) * tk
    # limbs: the slab shift at their root, as a rigid translation
    limbs = {}
    for sd in ('L', 'R'):
        for grp, root in ((('shoulder', 'upperarm', 'forearm', 'hand', 'finger'), 'upperarm'), (('thigh', 'shin', 'foot', 'toes', 'toe'), 'thigh')):
            cols = [i for k, i in bi.items() if k.startswith(grp) and ('.' + sd) in k]; wl = np.clip(W[:, cols].sum(1), 0, 1)
            rs = float(sh_tr(np.array(B[f'{root}.{sd}']['pos']))); shift = shift * (1 - wl) + rs * wl; limbs[(root, sd)] = rs
    P1 = P.copy(); P1[:, 0] -= shift
    P1 = P1 * (1 - hk[:, None]) + headT(P) * hk[:, None]
    # joints: the same field (limb joints with their limb's translation, midline joints onto x = 0, the head's with the head's turn)
    J = {k: np.array(b['pos'], float) for k, b in B.items()}; END = {k: np.array(b['end'], float) for k, b in B.items()}
    Jn = {}
    for k in J:
        p = J[k].copy()
        if k.startswith(('head', 'gill')): p = headT(p)
        elif k.startswith(('shoulder', 'upperarm', 'forearm', 'hand', 'finger')): p[0] -= limbs[('upperarm', k.split('.')[1])]
        elif k.startswith(('thigh', 'shin', 'foot', 'toes', 'toe')): p[0] -= limbs[('thigh', k.split('.')[1])]
        elif k.startswith('tail'): p[0] -= float(sh_tl(p))
        else: p[0] -= float(sh_tr(p))
        Jn[k] = p
    # 4. keep the right half (x <= 0): flip x, cut, mirror (the result is symmetric, its +x half = the old right side)
    Pf = P1 * np.array([-1, 1, 1]); Tf = T[:, ::-1]
    Pm, Tm, src, side = cut_and_mirror(Pf, Tf)
    a = np.array([s_[0] for s_ in src], int); b = np.array([s_[1] for s_ in src], int); u = np.array([s_[2] for s_ in src], float)
    Wm = W[a] * (1 - u[:, None]) + W[b] * u[:, None]
    # the kept half carries the old right side's weights: on the +x side now, so its .R bones become .L; the mirrored half keeps .R
    swap = np.array([bi[mirror_name(k)] for k in names]); Wl = np.zeros_like(Wm); Wl[:, swap] = Wm   # Wl[:, swap[i]] = Wm[:, i]: bone i -> its mirror
    Wfinal = np.where((side > 0)[:, None], Wl, Wm)
    labm = np.where(u < 0.5, lab[a], lab[b])
    # joints: the old right side's, flipped to +x as .L; the mirror as .R; midline x = 0
    Jsym = {}
    for k, p in Jn.items():
        if '.R' in k: q = p * np.array([-1, 1, 1]); Jsym[mirror_name(k)] = q; Jsym[k] = q * np.array([-1, 1, 1])
        elif '.L' in k: continue
        else: q = p.copy(); q[0] = 0.0; Jsym[k] = q
    CSs = headT(CS); CSs[0] = 0.0
    print(f'  symmetric stand: {len(Pm)} verts {len(Tm)} tris; face sphere {CSs.round(3)} R {RS}')
    if save: np.savez(O + 'stand_sym.npz', P=Pm, T=Tm, W=Wfinal, lab=labm, names=np.array(names), side=side, CS=CSs, J=np.array([Jsym[k] for k in names]), Ry=Ry)
    return Pm, Tm, Wfinal, labm, names, Jsym, CSs
# ======================== remesh, weights, joints, frames, export ========================
def qmat(q):
    x, y, z, w = q
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)], [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)], [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])
def build(remesh_iters=5):
    from rig7crawl import face_cap, export_runtime, ORDER
    from remesh import remesh, compact, edges_of, Surface
    from rigcore import finalize, quat, mkframe
    from scipy.sparse import coo_matrix
    global HEADROT
    t0 = time.time(); z = np.load(O + 'stand_sym.npz', allow_pickle=True); HEADROT = z['Ry'] if 'Ry' in z.files else np.eye(3)
    P, T, W, names, CSs, Jarr = z['P'], z['T'], z['W'], [str(x) for x in z['names']], z['CS'], z['J']
    assert names == ORDER, 'bone order differs from the crawl'
    J = {k: Jarr[i] for i, k in enumerate(names)}
    # the face exactly on its sphere (the crawl's face cap: the same projection region)
    P, wcap = face_cap(P, CSs, RS)
    reg = dominant_region(W, names)
    # the left half, remeshed like the crawl (region sizes in export units), mirrored
    Lh = P[:, 0] >= -1e-9; Ph, Th, ex = compact(P, T[Lh[T].all(1)], {'W': W, 'reg': reg}); Wh = ex['W']; regh = ex['reg']
    Lf = np.select([regh == 'digit', regh == 'limb', regh == 'head', regh == 'gill'], [0.016, 0.022, 0.025, 0.02], 0.03)
    E_, *_ = edges_of(Th); nh = len(Ph); A_ = coo_matrix((np.ones(2 * len(E_)), (np.r_[E_[:, 0], E_[:, 1]], np.r_[E_[:, 1], E_[:, 0]])), shape=(nh, nh)).tocsr(); dg = np.asarray(A_.sum(1)).ravel()
    for _ in range(8): Lf = 0.5 * Lf + 0.5 * (A_ @ Lf) / np.maximum(dg, 1)
    isg = regh == 'gill'; fr = isg | (A_ @ isg.astype(float) > 0); tl = regh == 'tail'
    if tl.any(): fr |= tl & (Ph[:, 2] < Ph[tl, 2].min() + 0.03)
    Pr, Tr, regr = remesh(Ph, Th, Lf, frozen=fr, iters=remesh_iters, labels=regh, verbose=True)
    # weights: interpolated at each new vertex's closest point on the pre-remesh half
    bt, bc, dist = Surface(Ph, Th).project_bary(Pr); Wr = (Wh[Th[bt]] * bc[:, :, None]).sum(1)
    print(f'  weight transfer: max projection distance {dist.max() * 1000:.1f} mm')
    seam = np.abs(Pr[:, 0]) < 1e-9; nr = len(Pr); ns = np.where(~seam)[0]; mir = np.arange(nr); mir[ns] = nr + np.arange(len(ns))
    P2 = np.vstack([Pr, Pr[ns] * np.array([-1, 1, 1])]); T2 = np.vstack([Tr, mir[Tr][:, ::-1]]); reg2 = np.r_[regr, regr[ns]]
    bi = {k: i for i, k in enumerate(names)}; swap = np.array([bi[mirror_name(k)] for k in names])
    Wm = np.zeros_like(Wr); Wm[:, swap] = Wr; W2 = np.vstack([Wr, Wm[ns]])
    # the seam: average with its own mirror (exactly symmetric)
    W2[np.where(seam)[0]] = 0.5 * (Wr[seam] + Wm[seam])
    idx, w = finalize(W2, P=P2, joints=np.array([J[k] for k in names]))
    # bones: parents and ends from v6, moved like the joints (the head's with its turn); frames: the old right side's (turned with the head
    # where it rides the head), mirrored onto the left; the midline's made exactly symmetric
    B = source()[5]; PAR = {k: B[k]['parent'] for k in names}
    END = {}
    for k in names:
        if k in ('hand.L', 'hand.R', 'foot.L', 'foot.R', 'toes.L', 'toes.R', 'tail6', 'head', 'headfront', 'chest') or k.endswith('.2'):
            # keep the end's offset from the joint as in v6 (turned with the head for head-carried bones; mirrored for the left side)
            src = mirror_name(k) if '.L' in k else k; d = np.array(B[src]['end']) - np.array(B[src]['pos'])
            if '.L' in k: d = d * np.array([-1, 1, 1])
            if k.startswith(('head', 'gill')): d = HEADROT @ d if '.L' not in k else (HEADROT @ (d * np.array([-1, 1, 1]))) * np.array([-1, 1, 1])
            if k in ('head', 'headfront', 'chest', 'tail6'): d[0] = 0.0
            END[k] = J[k] + d
    F = {}
    for k in names:
        src = mirror_name(k) if '.L' in k else k; R0 = qmat(B[src]['q'])
        if k.startswith(('head', 'gill')): R0 = HEADROT @ R0
        if '.L' in k: Mx = np.diag([-1, 1, 1]); y = Mx @ R0[:, 1]; zz = Mx @ R0[:, 2]; F[k] = np.stack([np.cross(y, zz), y, zz], 1)
        elif '.R' in k: F[k] = R0
        else:
            y = R0[:, 1].copy(); y[0] = 0; zz = R0[:, 2].copy(); zz[0] = 0; F[k] = mkframe(y, zz)
    hb = J['head']; Rf = RS
    extra = {'headc': (CSs - hb).round(4).tolist(), 'headr': round(float(Rf), 4), 'face': {'c': CSs.round(4).tolist(), 'r': round(float(Rf), 4)}}
    export_runtime(P2, T2, idx, w, J, END, PAR, F, O + 'www/s7/axo_stand', extra)
    np.savez(O + 'stand7_rig.npz', P=P2, T=T2, idx=idx, w=w, labels=reg2.astype(str), names=np.array(names), C=CSs, R=Rf)
    print(f'stand built: {len(P2)} verts {len(T2)} tris in {time.time() - t0:.1f}s')

if __name__ == '__main__':
    if 'sym' in sys.argv: t0 = time.time(); symmetrize(); print(f'{time.time() - t0:.1f}s')
    if 'build' in sys.argv: build()
