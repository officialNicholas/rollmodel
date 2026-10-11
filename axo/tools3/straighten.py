# Step 1 of the crawl rebuild: unbend the user's crawl sculpt (an S-curved body, head turned) into a straight body along -z, heights kept.
# The centreline comes from geodesic rings over the body tube (trunk + tail + head, no limbs / gills); each vertex keeps its lateral and
# longitudinal offset from its closest centreline point (a 2D curve deformer in the top view). Limbs and gills ride rigidly with the frame of
# the centreline point they grow from, blended in by the old rig's limb / gill weights, so they are carried, never bent.
import sys, os, json
sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo2')
import numpy as np
from geo import M, D
O = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo3/'
SEED = dict(snout=(-0.3, 0.02, 0.95), tailtip=(0.85, 0.22, -0.95))
def unit(v): v = np.asarray(v, float); return v / (np.linalg.norm(v, axis=-1, keepdims=True) + 1e-12)
def resample(pts, step):
    seg = np.linalg.norm(np.diff(pts, axis=0), axis=1); cum = np.r_[0, np.cumsum(seg)]; s = np.arange(0, cum[-1], step); s = np.r_[s, cum[-1]]
    return np.stack([np.interp(s, cum, pts[:, k]) for k in range(pts.shape[1])], 1)
def smooth_poly(pts, it=20, lam=0.5, fix_ends=True):
    p = pts.copy()
    for _ in range(it):
        q = p.copy(); q[1:-1] = p[1:-1] + lam * ((p[:-2] + p[2:]) / 2 - p[1:-1]); p = q
    return p
def main():
    m = M('crawl'); P = m.P.copy(); r = np.load(D + 'crawl_rig.npz', allow_pickle=True); labels = np.array([str(x) for x in r['labels']]); names = list(r['names'])
    W = np.zeros((m.n, len(names)))
    for c in range(4): np.add.at(W, (np.arange(m.n), r['idx'][:, c]), r['w'][:, c])
    bi = {k: i for i, k in enumerate(names)}; ws = lambda pre: W[:, [i for k, i in bi.items() if k.startswith(pre)]].sum(1)
    tube = np.isin(labels, ['trunk', 'tail', 'head'])
    tip = m.near(SEED['tailtip']); snout = m.near(SEED['snout'])
    d = m.geo(tip, limit=4.0, mask=tube); dmax = d[np.isfinite(d)].max(); print('tube geodesic tail->front', round(float(dmax), 3), 'snout at', round(float(d[snout]), 3))
    # rings every 2 cm: the midpoint of each ring's extent (x and z by its bbox in the top view, y by its height range)
    cen = []
    for t in np.arange(0.0, d[snout] + 0.001, 0.02):
        sel = tube & np.isfinite(d) & (np.abs(d - t) < 0.012)
        if sel.sum() < 4: continue
        q = P[sel]; cen.append([(q[:, 0].min() + q[:, 0].max()) / 2, (q[:, 1].min() + q[:, 1].max()) / 2, (q[:, 2].min() + q[:, 2].max()) / 2])
    cen = np.array(cen)[::-1]   # snout -> tail tip
    cen = smooth_poly(resample(cen, 0.01), it=60, lam=0.5); cen = resample(cen, 0.01)
    C2 = cen[:, [0, 2]]; seg = np.linalg.norm(np.diff(C2, axis=0), axis=1); s_c = np.r_[0, np.cumsum(seg)]; L = s_c[-1]
    T2 = unit(np.gradient(C2, axis=0)); B2 = np.stack([-T2[:, 1], T2[:, 0]], 1)   # lateral (left of the direction of travel toward the tail)
    print('centreline', len(cen), 'pts, length (top view)', round(float(L), 3))
    # closest centreline sample for each vertex (dense samples: 1 cm)
    from scipy.spatial import cKDTree
    kd = cKDTree(C2); _, ci = kd.query(P[:, [0, 2]]); ci = np.clip(ci, 0, len(C2) - 1)
    # the straight target: the snout at z = +Zs, running toward -z; the lateral axis maps to +x (the character's left stays left)
    # (the direction of travel is from the snout toward the tail: T' = (0,-1) in (x,z); B' = (-T'z, T'x) = (1, 0))
    Zs = 0.0
    def tmap(v_xz, i):
        rel = v_xz - C2[i]; a = (rel * B2[i]).sum(-1); l = (rel * T2[i]).sum(-1)
        return np.stack([a, Zs - (s_c[i] + l)], -1)
    tube_xz = tmap(P[:, [0, 2]], ci)
    # rigid carriers: each limb (by its old rig chain) and the gills ride with the frame at their root's centreline sample
    def rigid(v_xz, i0):
        rel = v_xz - C2[i0]; a = rel @ B2[i0]; l = rel @ T2[i0]; return np.stack([a, Zs - (s_c[i0] + l)], -1)
    out_xz = tube_xz.copy(); carried = np.zeros(m.n)
    groups = {'arm.L': ['upperarm.L', 'forearm.L', 'hand.L', 'finger'], 'arm.R': ['upperarm.R', 'forearm.R', 'hand.R', 'finger'], 'leg.L': ['thigh.L', 'shin.L', 'foot.L', 'toes.L', 'toe'], 'leg.R': ['thigh.R', 'shin.R', 'foot.R', 'toes.R', 'toe']}
    for g, bones in groups.items():
        sd = g[-1]; cols = [i for k, i in bi.items() if any(k.startswith(b) for b in bones) and (k.endswith('.' + sd) or ('.' + sd + '.') in k)]
        wl = np.clip(W[:, cols].sum(1), 0, 1)
        root = P[(wl > 0.3) & (wl < 0.7)].mean(0) if ((wl > 0.3) & (wl < 0.7)).sum() > 3 else P[wl > 0.5].mean(0)
        i0 = int(kd.query(root[[0, 2]])[1]); rv = rigid(P[:, [0, 2]], i0)
        k = np.clip((wl - 0.15) / 0.55, 0, 1); k = k * k * (3 - 2 * k); out_xz = out_xz * (1 - k[:, None]) + rv * k[:, None]; carried = np.maximum(carried, k)
        print(f'  {g}: root {root.round(3)} at s={s_c[i0]:.3f}, carried verts {int((k > 0.5).sum())}')
    wg = np.clip(ws('gill'), 0, 1); gl = (wg > 0.05) | np.array([l.startswith('gill') for l in labels])
    hc = P[labels == 'head'].mean(0); ih = int(kd.query(hc[[0, 2]])[1]); rv = rigid(P[:, [0, 2]], ih)
    kg = np.where(np.array([l.startswith('gill') for l in labels]), 1.0, np.clip(wg / 0.5, 0, 1)); out_xz = out_xz * (1 - kg[:, None]) + rv * kg[:, None]
    print('  gills carried with the head frame at s=%.3f' % s_c[ih])
    Pn = np.stack([out_xz[:, 0], P[:, 1], out_xz[:, 1]], 1)
    # centreline heights after straightening (for later): y along s
    np.savez(O + 'crawl_straight.npz', P=Pn, P0=P, cen=cen, s=s_c, labels=labels)
    print('straight bbox', Pn.min(0).round(3), Pn.max(0).round(3))
    # quick symmetry report: per z-slice, the lateral centre of the tube
    tub = tube & ~gl
    for z in np.arange(Pn[tub, 2].max() - 0.05, Pn[tub, 2].min(), -0.15):
        q = Pn[tub & (np.abs(Pn[:, 2] - z) < 0.02)]
        if len(q) > 3: print(f'   z {z:+.2f}: x range {q[:, 0].min():+.3f}..{q[:, 0].max():+.3f} mid {(q[:, 0].min() + q[:, 0].max()) / 2:+.3f}  y {q[:, 1].min():+.3f}..{q[:, 1].max():+.3f}')
    # write a viewable runtime-format mesh (no skin) for inspection
    write_view(O + 'www/rb/', 'straight', m, Pn)
def write_view(dirp, nm, m, Pw, extra_meta=None):
    os.makedirs(dirp, exist_ok=True); n = len(Pw); T = m.T
    fn = np.cross(Pw[T[:, 1]] - Pw[T[:, 0]], Pw[T[:, 2]] - Pw[T[:, 0]]); vn = np.zeros((n, 3))
    for k in range(3): np.add.at(vn, T[:, k], fn)
    vn = unit(vn)
    parts = [Pw.astype(np.float32).tobytes(), vn.astype(np.float32).tobytes(), np.zeros((n, 2), np.float32).tobytes(), np.zeros((n, 4), np.uint8).tobytes(), np.tile(np.array([255, 0, 0, 0], np.uint8), (n, 1)).tobytes(), T.astype(np.uint32).ravel().tobytes()]
    off = []; o = 0
    for b in parts: off.append(o); o += len(b); o += (-o) % 4
    buf = bytearray(o)
    for b, of in zip(parts, off): buf[of:of + len(b)] = b
    meta = {'n': n, 'ni': int(T.size), 'i32': True, 'off': off, 'bones': [{'name': 'root', 'pos': [0, 0, 0], 'end': [0, 0.1, 0], 'q': [0, 0, 0, 1], 'parent': None}], 'bbox': [Pw.min(0).tolist(), Pw.max(0).tolist()]}
    if extra_meta: meta.update(extra_meta)
    open(dirp + nm + '.bin', 'wb').write(buf); json.dump(meta, open(dirp + nm + '.json', 'w'))
if __name__ == '__main__': main()
