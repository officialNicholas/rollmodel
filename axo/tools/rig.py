# build a shared-skeleton rig for one axolotl mesh: joints from centered geodesic chains, fingers/toes/gill stems found automatically, skin weights by heat diffusion
import numpy as np, sys, json
from scipy.sparse import coo_matrix, diags
from scipy.sparse.linalg import splu
sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo')
from geo import M, D
CFG = {
 'stand': dict(snout=(0.2, 0.3, 0.62), tail=(-0.77, 0.32, -0.65), head=(0.2, 0.42, 0.3), headR=0.3, up=(0, 1, 0),
   spine=dict(neck=(0.2, 0.16, 0.16), chest=(0.2, -0.05, 0.15), spine=(0.2, -0.28, 0.15), hips=(0.2, -0.5, 0.12), tail1=(0.15, -0.5, -0.08)),
   arms=dict(L=dict(tip=(0.78, -0.17, 0.5), sh=(0.42, 0.0, 0.15), el=(0.55, -0.06, 0.28), wr=(0.66, -0.12, 0.4)), R=dict(tip=(-0.33, -0.17, 0.5), sh=(-0.02, 0.0, 0.15), el=(-0.15, -0.06, 0.28), wr=(-0.26, -0.12, 0.4))),
   legs=dict(L=dict(tip=(0.5, -0.94, 0.42), sh=(0.38, -0.56, 0.17), el=(0.45, -0.76, 0.18), wr=(0.48, -0.88, 0.17)), R=dict(tip=(-0.1, -0.94, 0.42), sh=(0.02, -0.56, 0.17), el=(-0.05, -0.76, 0.18), wr=(-0.08, -0.88, 0.17))),
   gillBox=dict(minY=0.12)),
 'crawl': dict(snout=(-0.3, 0.05, 0.95), tail=(0.84, 0.25, -0.95), head=(-0.3, 0.12, 0.68), headR=0.26, up=(0, 1, 0),
   spine=dict(neck=(-0.27, -0.03, 0.46), chest=(-0.22, -0.15, 0.3), spine=(-0.1, -0.18, 0.06), hips=(0.02, -0.2, -0.18), tail1=(0.12, -0.18, -0.32)),
   arms=dict(L=dict(tip=(-0.03, -0.41, 0.78), sh=(-0.1, -0.2, 0.42), el=(-0.02, -0.3, 0.56), wr=(-0.03, -0.37, 0.66)), R=dict(tip=(-0.86, -0.41, 0.62), sh=(-0.38, -0.2, 0.36), el=(-0.58, -0.3, 0.45), wr=(-0.7, -0.37, 0.55))),
   legs=dict(L=dict(tip=(0.4, -0.41, 0.15), sh=(0.12, -0.22, -0.08), el=(0.24, -0.32, 0.02), wr=(0.32, -0.38, 0.08)), R=dict(tip=(-0.33, -0.41, -0.55), sh=(-0.08, -0.22, -0.27), el=(-0.18, -0.32, -0.38), wr=(-0.26, -0.38, -0.46))),
   gillBox=dict(minZ=0.25)),
}
def nearest_on(path, p): return path[int(np.argmin(np.linalg.norm(path - np.asarray(p), axis=1)))]
def build(nm):
    c = CFG[nm]; m = M(nm); col = np.load(D + nm + '_col.npz'); hsv, rgb = col['hsv'], col['col']
    J = {}; PAR = {}; ORDER = []
    def add(name, pos, par): J[name] = np.asarray(pos, float); PAR[name] = par; ORDER.append(name)
    # ---- the spine: one centered line from the snout to the tail tip ----
    sn, tt = m.near(c['snout']), m.near(c['tail']); dst = m.geo(sn); L = dst[tt]
    line = m.centerline(sn, L, 140, rmax=0.42, step_ring=0.02)
    sp = c['spine']; hips = nearest_on(line, sp['hips']); add('hips', hips, None)
    add('spine', nearest_on(line, sp['spine']), 'hips'); add('chest', nearest_on(line, sp['chest']), 'spine'); add('neck', nearest_on(line, sp['neck']), 'chest')
    add('head', np.asarray(c['head'], float) * 0.5 + J['neck'] * 0.5, 'neck')
    i1 = int(np.argmin(np.linalg.norm(line - np.asarray(sp['tail1']), axis=1))); tail = line[i1:]; idx = np.linspace(0, len(tail) - 1, 7).astype(int)
    prev = 'hips'
    for k, ii in enumerate(idx[:-1]): add(f'tail{k + 1}', tail[ii], prev); prev = f'tail{k + 1}'
    END = {'head': np.asarray(c['head'], float) + (np.asarray(c['head']) - J['neck']) * 0.6, 'tail6': tail[-1]}
    # ---- limbs: a centered line from the hand/foot tip back to the shoulder/hip, joints where the guesses fall on it; then fingers/toes ----
    for kind, grp, par, names in (('arm', c['arms'], 'chest', ('upperarm', 'forearm', 'hand', 'finger')), ('leg', c['legs'], 'hips', ('thigh', 'shin', 'foot', 'toe'))):
        for side, g in grp.items():
            tip, root = m.near(g['tip']), m.near(g['sh']); d = m.geo(tip); Ll = d[root]
            ln = m.centerline(tip, Ll, 40, rmax=0.16, step_ring=0.015)
            ia, ib, iw = [int(np.argmin(np.linalg.norm(ln - np.asarray(g[k]), axis=1))) for k in ('sh', 'el', 'wr')]
            iw = min(iw, len(ln) - 3); ib = min(max(ib, iw + 2), ia - 2); ia = max(ia, ib + 2)  # (keep them apart and in order along the limb)
            a, b, w = ln[min(ia, len(ln) - 1)], ln[ib], ln[iw]
            add(f'{names[0]}.{side}', a, par); add(f'{names[1]}.{side}', b, f'{names[0]}.{side}'); add(f'{names[2]}.{side}', w, f'{names[1]}.{side}')
            # digits: tips of the hand/foot (geodesic maxima from the wrist, beyond it)
            wv = m.near(w); dw = m.geo(wv, limit=0.3); fwd = m.P[tip] - w if np.linalg.norm(m.P[tip] - w) > 0.03 else w - b; fwd /= np.linalg.norm(fwd)
            region = np.isfinite(dw) & (((m.P - w) @ fwd) > -0.01)
            tips = m.tips(dw, region & (dw > 0.07), r=0.028, k=7)
            tips = [t for t in tips if dw[t] > 0.6 * max(dw[tips[0]], 1e-6)][:5]
            # order digits across the hand
            side_ax = np.cross(fwd, np.array(c['up'], float)); side_ax /= np.linalg.norm(side_ax) + 1e-9
            tips.sort(key=lambda t: float((m.P[t] - w) @ side_ax))
            for k, t in enumerate(tips):
                dl = m.centerline(t, max(dw[t] - 0.02, 0.04), 8, mask=region, rmax=0.06, step_ring=0.012)
                base, mid = dl[-1], dl[3]
                add(f'{names[3]}{k}.{side}.1', base, f'{names[2]}.{side}'); add(f'{names[3]}{k}.{side}.2', mid, f'{names[3]}{k}.{side}.1'); END[f'{names[3]}{k}.{side}.2'] = m.P[t]
            END[f'{names[2]}.{side}'] = w + fwd * 0.06
            print(nm, kind, side, 'digits', len(tips), 'limb len', round(float(Ll), 2))
    # ---- gill stems: red fronds near the head, three clusters a side, each a two-bone stem from the head surface ----
    hc = np.asarray(c['head'], float); dh = np.linalg.norm(m.P - hc, axis=1)
    red = (hsv[:, 1] > 0.6) & ((hsv[:, 0] > 0.93) | (hsv[:, 0] < 0.03)) & (rgb[:, 1] < 0.42)
    gb = c['gillBox']; near = (dh < c['headR'] + 0.42) & (dh > c['headR'] * 0.95)
    if 'minY' in gb: near &= m.P[:, 1] > gb['minY']
    if 'minZ' in gb: near &= m.P[:, 2] > gb['minZ']
    gill = red & near
    # left/right by the head's side axis (perpendicular to the neck->head direction and up)
    fwd_h = (np.asarray(c['snout']) - hc); fwd_h[1] = 0; fwd_h /= np.linalg.norm(fwd_h); left = np.cross(np.array(c['up'], float), fwd_h)
    for side, sgn in (('L', 1), ('R', -1)):
        g = np.where(gill & (((m.P - hc) @ left) * sgn > 0))[0]
        if len(g) < 30: print(nm, 'gills', side, 'too few', len(g)); continue
        dirs = m.P[g] - hc; dirs /= np.linalg.norm(dirs, axis=1, keepdims=True)
        # k-means into 3 on direction (seeded high / mid / low)
        upv = np.array(c['up'], float); hs = dirs @ upv; cent = np.array([dirs[np.argmax(hs)], dirs[np.argmin(np.abs(hs - np.median(hs)))], dirs[np.argmin(hs)]])
        for it in range(25):
            lab = np.argmax(dirs @ cent.T, axis=1)
            for k in range(3):
                if (lab == k).any(): v = dirs[lab == k].mean(0); cent[k] = v / np.linalg.norm(v)
        order = np.argsort(-(cent @ upv))
        for rank, k in enumerate(order):
            q = g[lab == k]; pts = m.P[q]; far = pts[np.argmax(np.linalg.norm(pts - hc, axis=1))]
            dirk = cent[k]; root = hc + dirk * c['headR'] * 0.92; mid = root + (far - root) * 0.45
            add(f'gill{rank}.{side}.1', root, 'head'); add(f'gill{rank}.{side}.2', mid, f'gill{rank}.{side}.1'); END[f'gill{rank}.{side}.2'] = far
        print(nm, 'gills', side, len(g))
    return m, J, PAR, ORDER, END
def skin(m, J, PAR, ORDER, END):
    names = ORDER; n = len(m.P)
    kids = {k: [c for c in names if PAR[c] == k] for k in names}
    seg = []
    for k in names:
        a = J[k]; ch = kids[k]
        if k in END: b = END[k]
        elif len(ch) == 1: b = J[ch[0]]
        elif k == 'hips': b = J['spine']
        elif k == 'chest': b = J['neck']
        elif ch: b = np.mean([J[x] for x in ch], 0)
        else: b = a + 0.02
        seg.append((a, b))
    A = np.array([s[0] for s in seg]); B = np.array([s[1] for s in seg]); AB = B - A; L2 = np.maximum((AB ** 2).sum(1), 1e-9)
    t = np.clip(((m.P[:, None, :] - A[None]) * AB[None]).sum(2) / L2[None], 0, 1); C = A[None] + t[..., None] * AB[None]
    dist = np.linalg.norm(m.P[:, None, :] - C, axis=2)  # n x bones
    # the trunk bones get a slight discount so thin parts do not pull body skin
    near = np.argmin(dist, axis=1); dmin = dist[np.arange(n), near]
    # cotangent Laplacian
    T = m.T; P = m.P; I, Jx, V = [], [], []
    for a_, b_, c_ in ((0, 1, 2), (1, 2, 0), (2, 0, 1)):
        u = P[T[:, a_]] - P[T[:, c_]]; v = P[T[:, b_]] - P[T[:, c_]]
        cot = (u * v).sum(1) / np.maximum(np.linalg.norm(np.cross(u, v), axis=1), 1e-12); cot = np.clip(cot, -10, 10) * 0.5
        I += [T[:, a_], T[:, b_]]; Jx += [T[:, b_], T[:, a_]]; V += [cot, cot]
    W = coo_matrix((np.concatenate(V), (np.concatenate(I), np.concatenate(Jx))), shape=(n, n)).tocsr(); Lap = diags(np.asarray(W.sum(1)).ravel()) - W
    H = 1.0 / np.maximum(dmin, 0.01) ** 2 * 0.002
    Amat = (Lap + diags(H)).tocsc(); lu = splu(Amat)
    nb = len(names); Wt = np.zeros((n, nb), np.float32)
    for j in range(nb):
        p = (near == j).astype(float); Wt[:, j] = lu.solve(H * p)
    Wt = np.clip(Wt, 0, None)
    top = np.argsort(-Wt, axis=1)[:, :4]; tw = np.take_along_axis(Wt, top, 1); tw[tw < 0.02] = 0; s = tw.sum(1, keepdims=True); s[s == 0] = 1; tw /= s
    bad = tw.sum(1) == 0; top[bad, 0] = near[bad]; tw[bad, 0] = 1
    return top.astype(np.uint8), tw.astype(np.float32), near, seg
if __name__ == '__main__':
    for nm in sys.argv[1:] or ('stand', 'crawl'):
        m, J, PAR, ORDER, END = build(nm)
        idx, w, near, seg = skin(m, J, PAR, ORDER, END)
        np.savez(D + nm + '_rig.npz', idx=idx, w=w, near=near)
        json.dump({'bones': [{'name': k, 'parent': PAR[k], 'pos': [round(float(x), 5) for x in J[k]], 'end': [round(float(x), 5) for x in (END[k] if k in END else seg[ORDER.index(k)][1])]} for k in ORDER]}, open(D + nm + '_skel.json', 'w'), indent=0)
        print(nm, 'bones', len(ORDER))
