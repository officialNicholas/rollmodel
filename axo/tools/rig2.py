# shared-skeleton rig for both axolotl meshes (normalized 'sn' = rigged standing model, 'cn' = crawling sculpt)
# stand: Mixamo joints + weights kept for the body; tail / gill stems / fingers / toes added and re-skinned by heat diffusion, blended at the borders
# crawl: everything from geometry (centered geodesic chains), same bone names and hierarchy
# every bone also gets an orthonormal rest frame (Y = along the bone, Z = ventral / flexion side, X = Y x Z = hinge) so one pose drives both meshes
import numpy as np, sys, json
from scipy.sparse import coo_matrix, diags
from scipy.sparse.linalg import splu
from scipy.sparse.csgraph import dijkstra
sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo')
from geo import M, D
CS = 1.25; CT = np.array([-0.02, 0.418, 0.18])
def cn(p): return tuple(((np.asarray(p, float) + CT) * CS).tolist())   # old crawl config coords -> normalized
CFG = {
 'sn': dict(snout=(0, 1.3, 0.37), tail=(0.05, 0.4, -1.7), head=(0, 1.4, -0.02), headR=0.3, belly=(0, 0, 1), palm=(0, 0, -1), armFlex=(0, 0, 1), legFlex=(0, 0, -1),
            tail1=(0, 0.56, -0.3), gillBox=dict(minY=1.15), gillSat=0.4, headUp=(0, 1, 0)),
 'cn': dict(snout=cn((-0.3, 0.05, 0.95)), tail=cn((0.84, 0.25, -0.95)), head=cn((-0.3, 0.12, 0.68)), headR=0.26 * CS, belly=(0, -1, 0), palm=(0, -1, 0), armFlex=(0, -1, 0), legFlex=(0, -1, 0),
            spine=dict(neck=cn((-0.27, -0.03, 0.46)), chest=cn((-0.22, -0.15, 0.3)), spine=cn((-0.1, -0.18, 0.06)), hips=cn((0.02, -0.2, -0.18)), tail1=cn((0.12, -0.18, -0.32))),
            arms=dict(L=dict(tip=cn((-0.03, -0.41, 0.78)), sh=cn((-0.1, -0.2, 0.42)), el=cn((-0.02, -0.3, 0.56)), wr=cn((-0.03, -0.37, 0.66))), R=dict(tip=cn((-0.86, -0.41, 0.62)), sh=cn((-0.38, -0.2, 0.36)), el=cn((-0.58, -0.3, 0.45)), wr=cn((-0.7, -0.37, 0.55)))),
            legs=dict(L=dict(tip=cn((0.4, -0.41, 0.15)), sh=cn((0.12, -0.22, -0.08)), el=cn((0.24, -0.32, 0.02)), wr=cn((0.32, -0.38, 0.08))), R=dict(tip=cn((-0.33, -0.41, -0.55)), sh=cn((-0.08, -0.22, -0.27)), el=cn((-0.18, -0.32, -0.38)), wr=cn((-0.26, -0.38, -0.46)))),
            gillBox=dict(minZ=cn((0, 0, 0.25))[2], minY=cn((0, -0.12, 0))[1]), gillSat=0.6, headUp=(0, 1, 0)),
}
NFING, NTOE = 4, 4   # digits per hand / foot (shared bone list)
MIX = {'mixamorig:Hips': 'hips', 'mixamorig:Spine': 'spine', 'mixamorig:Spine1': 'spine1', 'mixamorig:Spine2': 'chest', 'mixamorig:Neck': 'neck', 'mixamorig:Head': 'head',
       'mixamorig:LeftShoulder': 'chest', 'mixamorig:LeftArm': 'upperarm.L', 'mixamorig:LeftForeArm': 'forearm.L', 'mixamorig:LeftHand': 'hand.L',
       'mixamorig:RightShoulder': 'chest', 'mixamorig:RightArm': 'upperarm.R', 'mixamorig:RightForeArm': 'forearm.R', 'mixamorig:RightHand': 'hand.R',
       'mixamorig:LeftUpLeg': 'thigh.L', 'mixamorig:LeftLeg': 'shin.L', 'mixamorig:LeftFoot': 'foot.L', 'mixamorig:LeftToeBase': 'foot.L',
       'mixamorig:RightUpLeg': 'thigh.R', 'mixamorig:RightLeg': 'shin.R', 'mixamorig:RightFoot': 'foot.R', 'mixamorig:RightToeBase': 'foot.R', 'headfront': 'head'}
def unit(v): v = np.asarray(v, float); return v / (np.linalg.norm(v) + 1e-12)
def nearest_on(path, p): return path[int(np.argmin(np.linalg.norm(path - np.asarray(p), axis=1)))]

class Rig:
    def __init__(s): s.J = {}; s.PAR = {}; s.ORDER = []; s.END = {}
    def add(s, name, pos, par): s.J[name] = np.asarray(pos, float); s.PAR[name] = par; s.ORDER.append(name)
    def kids(s, k): return [c for c in s.ORDER if s.PAR[c] == k]
    def dirn(s, k):
        if k in s.END: return unit(s.END[k] - s.J[k])
        ch = s.kids(k)
        if k == 'hips': return unit(s.J['spine'] - s.J['hips'])
        if k == 'chest': return unit(s.J['neck'] - s.J['chest'])
        if k.startswith('hand') or k.startswith('foot'): return unit(np.mean([s.J[c] for c in ch], 0) - s.J[k])
        return unit(s.J[ch[0]] - s.J[k]) if ch else np.array([0, 1.0, 0])
    def endp(s, k):
        if k in s.END: return s.END[k]
        ch = s.kids(k)
        if k == 'hips': return s.J['spine']
        if k == 'chest': return s.J['neck']
        if ch: return np.mean([s.J[c] for c in ch], 0)
        return s.J[k] + 0.02

def digits(m, R, c, w_name, w, b, tip, fwd_hint, names, count, region_mask=None):
    # digit chains from a wrist/ankle joint: geodesic maxima beyond the joint, ordered across the hand
    wv = m.near(w); dw = m.geo(wv, limit=0.45); fwd = unit(fwd_hint)
    region = np.isfinite(dw) & (((m.P - w) @ fwd) > -0.01)
    tips = m.tips(dw, region & (dw > 0.07), r=0.028, k=8)
    tips = [t for t in tips if dw[t] > 0.55 * max(dw[tips[0]], 1e-6)][:count]
    side_ax = unit(np.cross(fwd, np.array(c['headUp'], float)))
    tips.sort(key=lambda t: float((m.P[t] - w) @ side_ax))
    out = []
    for k, t in enumerate(tips):
        dl = m.centerline(t, max(dw[t] - 0.02, 0.04), 8, mask=region, rmax=0.08, step_ring=0.012)
        base, mid = dl[-1], dl[3]; tp = m.P[t]
        if np.linalg.norm(tp - base) < 0.03 or np.linalg.norm(mid - base) < 0.012 or np.linalg.norm(tp - mid) < 0.012:   # (collapsed ring chain: straight digit from the wrist)
            base = w + (tp - w) * 0.35; mid = w + (tp - w) * 0.68
        n1, n2 = f'{names}{k}.{w_name}.1', f'{names}{k}.{w_name}.2'
        R.add(n1, base, f'{"hand" if names == "finger" else "foot"}.{w_name}'); R.add(n2, mid, n1); R.END[n2] = m.P[t]; out.append(t)
    while len(out) < count:  # (missing digit: duplicate the last chain slightly offset, so the bone list stays shared)
        k = len(out); src = f'{names}{k - 1}.{w_name}'; off = side_ax * 0.02
        R.add(f'{names}{k}.{w_name}.1', R.J[src + '.1'] + off, R.PAR[src + '.1']); R.add(f'{names}{k}.{w_name}.2', R.J[src + '.2'] + off, f'{names}{k}.{w_name}.1'); R.END[f'{names}{k}.{w_name}.2'] = R.END[src + '.2'] + off; out.append(None)
    return tips

def gills(m, R, c, hsv, rgb):
    hc = np.asarray(c['head'], float); dh = np.linalg.norm(m.P - hc, axis=1)
    red = (hsv[:, 1] > c['gillSat']) & ((hsv[:, 0] > 0.93) | (hsv[:, 0] < 0.03)) & (rgb[:, 1] < 0.45)
    gb = c['gillBox']; near = (dh < c['headR'] + 0.5) & (dh > c['headR'] * 0.9)
    if 'minY' in gb: near &= m.P[:, 1] > gb['minY']
    if 'minZ' in gb: near &= m.P[:, 2] > gb['minZ']
    gill = red & near
    fwd_h = (np.asarray(c['snout']) - hc); fwd_h[1] = 0; fwd_h = unit(fwd_h); left = np.cross(np.array(c['headUp'], float), fwd_h)
    for side, sgn in (('L', 1), ('R', -1)):
        g = np.where(gill & (((m.P - hc) @ left) * sgn > 0))[0]
        print(' gills', side, len(g))
        dirs = m.P[g] - hc; dirs /= np.linalg.norm(dirs, axis=1, keepdims=True)
        upv = np.array(c['headUp'], float); hs = dirs @ upv; cent = np.array([dirs[np.argmax(hs)], dirs[np.argmin(np.abs(hs - np.median(hs)))], dirs[np.argmin(hs)]])
        for it in range(30):
            lab = np.argmax(dirs @ cent.T, axis=1)
            for k in range(3):
                if (lab == k).any(): cent[k] = unit(dirs[lab == k].mean(0))
        order = np.argsort(-(cent @ upv))
        for rank, k in enumerate(order):
            q = g[lab == k]; pts = m.P[q]; dd = np.linalg.norm(pts - hc, axis=1); far = pts[np.argmax(dd)]
            root = pts[dd <= np.percentile(dd, 12)].mean(0); mid = root + (far - root) * 0.45
            R.add(f'gill{rank}.{side}.1', root, 'head'); R.add(f'gill{rank}.{side}.2', mid, f'gill{rank}.{side}.1'); R.END[f'gill{rank}.{side}.2'] = far
    R.gillmask = gill
    return gill, red

def build_sn():
    c = CFG['sn']; m = M('sn'); col = np.load(D + 'sn_col.npz'); mx = np.load(D + 'sn_mixamo.npz'); jp = {str(n): p for n, p in zip(mx['names'], mx['pos'])}
    R = Rig()
    R.add('hips', jp['mixamorig:Hips'], None); R.add('spine', jp['mixamorig:Spine'], 'hips'); R.add('spine1', jp['mixamorig:Spine1'], 'spine'); R.add('chest', jp['mixamorig:Spine2'], 'spine1')
    R.add('neck', jp['mixamorig:Neck'], 'chest'); R.add('head', jp['mixamorig:Head'], 'neck'); R.END['head'] = jp['mixamorig:Head'] + np.array([0, 0.32, 0])
    # tail: centered rings from the tip back to the body
    tt = m.near(c['tail']); d = m.geo(tt); hv = m.near(c['tail1']); L = d[hv]
    line = m.centerline(tt, L, 60, rmax=0.3, step_ring=0.02)[::-1]   # from body to tip
    sm = line.copy()
    for i in range(len(line)): sm[i] = line[max(0, i - 6):i + 7].mean(0)
    sm[-1] = line[-1]; line = sm
    i0 = int(np.argmin(np.linalg.norm(line - np.asarray(c['tail1']), axis=1))); tail = line[i0:]; idx = np.linspace(0, len(tail) - 1, 7).astype(int); prev = 'hips'
    for k, ii in enumerate(idx[:-1]): R.add(f'tail{k + 1}', tail[ii], prev); prev = f'tail{k + 1}'
    R.END['tail6'] = m.P[tt]
    for side, sd in (('L', 'Left'), ('R', 'Right')):
        R.add(f'upperarm.{side}', jp[f'mixamorig:{sd}Arm'], 'chest'); R.add(f'forearm.{side}', jp[f'mixamorig:{sd}ForeArm'], f'upperarm.{side}'); R.add(f'hand.{side}', jp[f'mixamorig:{sd}Hand'], f'forearm.{side}')
        R.add(f'thigh.{side}', jp[f'mixamorig:{sd}UpLeg'], 'hips'); R.add(f'shin.{side}', jp[f'mixamorig:{sd}Leg'], f'thigh.{side}'); R.add(f'foot.{side}', jp[f'mixamorig:{sd}Foot'], f'shin.{side}')
    for side, sd in (('L', 'Left'), ('R', 'Right')):
        w = jp[f'mixamorig:{sd}Hand']; fwd = unit(w - jp[f'mixamorig:{sd}ForeArm'])
        tips = digits(m, R, c, side, w, None, None, fwd, 'finger', NFING); print(' fingers', side, len(tips))
        a = jp[f'mixamorig:{sd}Foot']; fwd = unit(jp[f'mixamorig:{sd}ToeBase'] - a + np.array([0, -0.02, 0.0]))
        tips = digits(m, R, c, side, a, None, None, fwd, 'toe', NTOE); print(' toes', side, len(tips))
    gill, red = gills(m, R, c, col['hsv'], col['col']); R.red = red
    return m, R, mx

def slab_centerline(m, guesses, R, mask, iters=3):
    # refine a guessed polyline: each point becomes the centroid of the (masked) vertices in a thin slab perpendicular to the local tangent, within radius R
    pts = np.array(guesses, float)
    for it in range(iters):
        out = pts.copy()
        for i in range(len(pts)):
            a = pts[max(i - 1, 0)]; b = pts[min(i + 1, len(pts) - 1)]; tdir = unit(b - a); rel = m.P - pts[i]
            along = rel @ tdir; perp = np.linalg.norm(rel - along[:, None] * tdir[None], axis=1)
            sel = mask & (np.abs(along) < 0.03) & (perp < R)
            if sel.sum() > 8:
                q = m.P[sel]; ridge = q[q[:, 1] >= np.percentile(q[:, 1], 94)].mean(0); lo = np.percentile(q[:, 1], 4)
                out[i] = ridge; out[i][1] = ridge[1] - 0.45 * (ridge[1] - lo)
        pts = out
    return pts

def limb_from_tip(m, tip, mask, step=0.02, maxlen=1.2):
    # ring centroids from a hand/foot tip up the limb; the limb ends where the ring spreads out into the body
    d = m.geo(tip, limit=maxlen + 0.1); pts = []; rads = []
    for t in np.arange(0.04, maxlen, step):
        sel = np.isfinite(d) & (np.abs(d - t) < step) & mask
        if sel.sum() < 4: break
        q = m.P[sel]; cen = q.mean(0); r = np.percentile(np.linalg.norm(q - cen, axis=1), 90)
        if t > 0.3 and len(rads) > 8 and r > 1.8 * np.median(rads[-8:]) and r > 0.12: break
        if pts and np.linalg.norm(cen - pts[-1]) > 0.12: break
        pts.append(cen); rads.append(r)
    return np.array(pts), np.array(rads)

def build_cn():
    c = CFG['cn']; m = M('cn'); col = np.load(D + 'cn_col.npz'); R = Rig()
    hsv, rgb = col['hsv'], col['col']; red = (hsv[:, 1] > c['gillSat']) & ((hsv[:, 0] > 0.93) | (hsv[:, 0] < 0.03)) & (rgb[:, 1] < 0.45)
    sp = c['spine']
    # tail: centered rings from the tip forward to the tail root
    tt = m.near(c['tail']); d = m.geo(tt); hv = m.near(sp['tail1']); L = d[hv]
    tl = m.centerline(tt, L, 60, rmax=0.35, step_ring=0.02)[::-1]
    i0 = int(np.argmin(np.linalg.norm(tl - np.asarray(sp['tail1']), axis=1))); tail = tl[i0:]
    # trunk: slab-refined guesses neck -> hips, resampled by arc length
    hc0 = np.asarray(c['head'], float); gz = (np.linalg.norm(m.P - hc0, axis=1) < c['headR'] + 0.6) & (np.abs(m.P[:, 0] - hc0[0]) > 0.22) & (m.P[:, 1] > hc0[1] - 0.1)
    # trunk: the dorsal ridge per z-bin (the back's midline), dropped 45% of the body height; the belly lies on the ground
    ok = ~gz & (np.abs(m.P[:, 0]) < 0.7); z0, z1 = sp['hips'][2], sp['neck'][2]; trunk = []
    for zc in np.linspace(z0, z1, 12):
        sel = ok & (np.abs(m.P[:, 2] - zc) < 0.035); q = m.P[sel]; top = q[np.argsort(-q[:, 1])[:4]].mean(0); lo = np.percentile(q[:, 1], 3)
        trunk.append([top[0], top[1] - 0.45 * (top[1] - lo), zc])
    trunk = np.array(trunk)[::-1]; sm = trunk.copy()
    for i in range(len(trunk)): sm[i] = trunk[max(0, i - 1):i + 2].mean(0)
    trunk = sm
    fine = np.concatenate([np.linspace(trunk[i], trunk[i + 1], 8, endpoint=False) for i in range(len(trunk) - 1)] + [trunk[-1:]])
    seg = fine[::-1]; cum = np.r_[0, np.cumsum(np.linalg.norm(np.diff(seg, axis=0), axis=1))]; cum /= cum[-1]
    at = lambda f: seg[int(np.argmin(np.abs(cum - f)))]
    R.add('hips', at(0), None); R.add('spine', at(0.25), 'hips'); R.add('spine1', at(0.5), 'spine'); R.add('chest', at(0.75), 'spine1'); R.add('neck', at(1.0), 'chest')
    hc = np.asarray(c['head'], float); R.add('head', hc * 0.5 + R.J['neck'] * 0.5, 'neck'); R.END['head'] = R.J['head'] + np.array(c['headUp']) * 0.32
    idx = np.linspace(0, len(tail) - 1, 7).astype(int); prev = 'hips'
    for k, ii in enumerate(idx[:-1]): R.add(f'tail{k + 1}', tail[ii], prev); prev = f'tail{k + 1}'
    R.END['tail6'] = tail[-1]
    print(' trunk', np.round(trunk, 2).tolist(), 'tail1', np.round(tail[0], 2), 'tail6', np.round(tail[idx[-2]], 2))
    for kind, grp, par, names, dn, cnt in (('arm', c['arms'], 'chest', ('upperarm', 'forearm', 'hand'), 'finger', NFING), ('leg', c['legs'], 'hips', ('thigh', 'shin', 'foot'), 'toe', NTOE)):
        for side, g in grp.items():
            tip = m.near(g['tip'])
            def refine(p, r=0.13):
                sel = (np.linalg.norm(m.P - np.asarray(p), axis=1) < r) & ~red; return m.P[sel].mean(0) if sel.sum() > 5 else np.asarray(p, float)
            a, b, w = refine(g['sh'], 0.16), refine(g['el']), refine(g['wr'], 0.1)
            R.add(f'{names[0]}.{side}', a, par); R.add(f'{names[1]}.{side}', b, f'{names[0]}.{side}'); R.add(f'{names[2]}.{side}', w, f'{names[1]}.{side}')
            fwd = m.P[tip] - w
            tips = digits(m, R, c, side, w, b, tip, fwd, dn, cnt); print(' ', kind, side, 'digits', len(tips), 'root', np.round(a, 2), 'elbow', np.round(b, 2), 'wrist', np.round(w, 2))
    gill, red = gills(m, R, c, col['hsv'], col['col']); R.red = red
    return m, R, None

def frames(R, c):
    # rest frames: columns [X, Y, Z]; Y along the bone, Z the ventral / flexion side (projected), X = Y x Z
    F = {}
    def mk(y, zref):
        assert np.linalg.norm(y) > 1e-6, 'degenerate bone direction'
        y = unit(y); z = np.asarray(zref, float); z = z - (z @ y) * y
        if np.linalg.norm(z) < 1e-6: z = np.cross(y, [1, 0, 0])
        z = unit(z); x = np.cross(y, z); return np.stack([x, y, z], 1)
    belly = np.array(c['belly'], float); up = np.array(c['headUp'], float)
    for k in R.ORDER:
        if k in ('hips', 'spine', 'spine1', 'chest', 'neck'): F[k] = mk(R.dirn(k), belly)
        elif k.startswith('tail'): F[k] = mk(R.dirn(k), (0, -1, 0))   # the tail runs back horizontally in both sculpts: ventral = down
        elif k == 'head': F[k] = mk(up, np.asarray(c['snout']) - R.J['head'])
        elif k.startswith('upperarm') or k.startswith('thigh'):
            y = R.dirn(k); ch = R.kids(k)[0]; y2 = R.dirn(ch); flex = y2 - (y2 @ y) * y
            if np.linalg.norm(flex) < np.sin(np.radians(12)): flex = np.array(c['armFlex' if k.startswith('upperarm') else 'legFlex'], float)
            F[k] = mk(y, flex)
        elif k.startswith('forearm') or k.startswith('shin'): F[k] = mk(R.dirn(k), F[R.PAR[k]][:, 2])
        elif k.startswith('hand'): F[k] = mk(R.dirn(k), c['palm'])
        elif k.startswith('foot'): F[k] = mk(R.dirn(k), (0, -1, 0))
        elif k.startswith('finger') or k.startswith('toe'): F[k] = mk(R.dirn(k), F[R.PAR[k]][:, 2])
        elif k.startswith('gill'): F[k] = mk(R.dirn(k), -up)
        else: raise Exception(k)
    return F

def quat(Mx):
    # rotation matrix -> quaternion (x, y, z, w)
    t = np.trace(Mx)
    if t > 0: s_ = np.sqrt(t + 1) * 2; return np.array([(Mx[2, 1] - Mx[1, 2]) / s_, (Mx[0, 2] - Mx[2, 0]) / s_, (Mx[1, 0] - Mx[0, 1]) / s_, 0.25 * s_])
    i = int(np.argmax(np.diag(Mx))); j, k = (i + 1) % 3, (i + 2) % 3
    s_ = np.sqrt(1 + Mx[i, i] - Mx[j, j] - Mx[k, k]) * 2; q = np.zeros(4); q[i] = 0.25 * s_; q[j] = (Mx[j, i] + Mx[i, j]) / s_; q[k] = (Mx[k, i] + Mx[i, k]) / s_; q[3] = (Mx[k, j] - Mx[j, k]) / s_
    return q

def cot_laplacian(m):
    T = m.T; P = m.P; n = len(P); I, Jx, V = [], [], []
    for a_, b_, c_ in ((0, 1, 2), (1, 2, 0), (2, 0, 1)):
        u = P[T[:, a_]] - P[T[:, c_]]; v = P[T[:, b_]] - P[T[:, c_]]
        cot = (u * v).sum(1) / np.maximum(np.linalg.norm(np.cross(u, v), axis=1), 1e-12); cot = np.clip(cot, -10, 10) * 0.5
        I += [T[:, a_], T[:, b_]]; Jx += [T[:, b_], T[:, a_]]; V += [cot, cot]
    W = coo_matrix((np.concatenate(V), (np.concatenate(I), np.concatenate(Jx))), shape=(n, n)).tocsr(); return diags(np.asarray(W.sum(1)).ravel()) - W

def heat_skin(m, R, thin_boost=None):
    names = R.ORDER; n = len(m.P)
    A = np.array([R.J[k] for k in names]); B = np.array([R.endp(k) for k in names]); AB = B - A; L2 = np.maximum((AB ** 2).sum(1), 1e-9)
    t = np.clip(((m.P[:, None, :] - A[None]) * AB[None]).sum(2) / L2[None], 0, 1); C = A[None] + t[..., None] * AB[None]
    dist = np.linalg.norm(m.P[:, None, :] - C, axis=2)
    if thin_boost is not None: dist = dist * thin_boost[None, :]
    isg = np.array([k.startswith('gill') for k in names]); dist[np.ix_(~R.gillmask, isg)] = 1e9   # gill bones only own the detected gill skin
    # a bone may only claim skin that is geodesically near it (a hand resting against the chin must not take head skin, and vice versa)
    for j, k in enumerate(names):
        mid = 0.5 * (A[j] + B[j]); L = np.linalg.norm(AB[j])
        if isg[j]: gi = np.where(R.gillmask)[0]; anchor = int(gi[np.argmin(np.linalg.norm(m.P[gi] - mid, axis=1))])
        else: anchor = m.near(mid)
        lim = L * 1.6 + 0.22 if k.startswith(('finger', 'toe', 'gill')) else L * 1.6 + 0.5 if k in ('head', 'neck', 'hand.L', 'hand.R', 'foot.L', 'foot.R') else L * 3 + 1.0 if k.startswith('tail') else L * 2 + 0.6
        gd = dijkstra(m.G, indices=anchor, limit=lim); dist[~np.isfinite(gd), j] = 1e9
    near = np.argmin(dist, axis=1); dmin = dist[np.arange(n), near]
    Lap = cot_laplacian(m); H = 1.0 / np.maximum(dmin, 0.01) ** 2 * 0.03
    lu = splu((Lap + diags(H)).tocsc()); Wt = np.zeros((n, len(names)), np.float32)
    for j in range(len(names)):
        p = (near == j).astype(float); Wt[:, j] = lu.solve(H * p)
    return np.clip(Wt, 0, None), near, Lap

def top4(Wt, near):
    top = np.argsort(-Wt, axis=1)[:, :4]; tw = np.take_along_axis(Wt, top, 1); tw[tw < 0.04] = 0; s_ = tw.sum(1, keepdims=True); s_[s_ == 0] = 1; tw /= s_
    bad = tw.sum(1) == 0; top[bad, 0] = near[bad]; tw[bad, 0] = 1
    return top.astype(np.uint8), tw.astype(np.float32)

def skin_sn(m, R, mx, pure=False):
    names = R.ORDER; n = len(m.P); nb = len(names)
    # the thin new parts (gills, digits) get a discount so they win their own skin, the trunk bones a penalty near them
    boost = np.ones(nb)
    for i, k in enumerate(names):
        if k.startswith('gill') or k.startswith('finger') or k.startswith('toe'): boost[i] = 0.8
    Wt, near, Lap = heat_skin(m, R, boost)
    # Mixamo weights remapped onto the shared bones (welded vertices: average)
    JN, WT = mx['JN'], mx['WT']; mnames = [str(x) for x in mx['names']]; remap = np.array([names.index(MIX[k]) for k in mnames])
    Wm = np.zeros((n, nb)); cnt = np.zeros(n)
    for col in range(4):
        np.add.at(Wm, (m.wid, remap[JN[:, col]]), WT[:, col])
    np.add.at(cnt, m.wid, 1); Wm /= cnt[:, None]; Wm /= np.maximum(Wm.sum(1, keepdims=True), 1e-9)
    # region owned by the new bones: nearest bone is new, grown a little along the tail so the hips do not hold the tail root
    new = np.array([k.startswith(('tail', 'gill', 'finger', 'toe')) for k in names])
    inside = new[near]
    d = dijkstra(m.G, indices=np.where(inside)[0], min_only=True, limit=0.12)
    alpha = 1 - np.clip(d / 0.10, 0, 1); alpha = alpha * alpha * (3 - 2 * alpha); alpha[inside] = 1
    if pure: alpha[:] = 1
    Wh = Wt / np.maximum(Wt.sum(1, keepdims=True), 1e-9)
    W = alpha[:, None] * Wh + (1 - alpha[:, None]) * Wm
    idx, w = top4(W.astype(np.float32), near)
    print(' re-skinned verts', int(inside.sum()), 'blend band', int(((alpha > 0) & (alpha < 1)).sum()))
    return idx, w, near

def skin_cn(m, R):
    Wt, near, _ = heat_skin(m, R); return (*top4(Wt, near), near)

def export(nm, m, R, idx, w, F, out):
    names = R.ORDER
    bones = [{'name': k, 'parent': R.PAR[k], 'pos': [round(float(x), 5) for x in R.J[k]], 'end': [round(float(x), 5) for x in R.endp(k)], 'q': [round(float(x), 6) for x in quat(F[k])]} for k in names]
    json.dump({'bones': bones}, open(D + nm + '_skel.json', 'w'), indent=0); np.savez(D + nm + '_rig.npz', idx=idx, w=w)
    idx = idx[m.wid]; w = w[m.wid]; wq = np.round(w * 255).astype(np.int32); wq[:, 0] += 255 - wq.sum(1); wq = np.clip(wq, 0, 255).astype(np.uint8)
    P = m.P0.astype(np.float32); N = m.N0.astype(np.float32); UV = m.UV.astype(np.float32); I = m.I0.reshape(-1).astype(np.uint16 if len(P) < 65536 else np.uint32)
    parts = [P.tobytes(), N.tobytes(), UV.tobytes(), idx.astype(np.uint8).tobytes(), wq.tobytes(), I.tobytes()]; off = []; o = 0
    for b in parts: off.append(o); o += len(b); o += (-o) % 4
    buf = bytearray(o)
    for b, of in zip(parts, off): buf[of:of + len(b)] = b
    open(out + '.bin', 'wb').write(buf)
    json.dump({'n': len(P), 'ni': len(I), 'i32': len(P) >= 65536, 'off': off, 'bones': bones, 'bbox': [P.min(0).round(4).tolist(), P.max(0).round(4).tolist()]}, open(out + '.json', 'w'))
    print(nm, 'exported', len(buf), 'bytes', len(P), 'verts', len(names), 'bones')

if __name__ == '__main__':
    OUT = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/axo/'
    which = sys.argv[1:] or ['sn', 'cn']; order = None
    for nm in which:
        print('==', nm)
        m, R, mx = build_sn() if nm == 'sn' else build_cn()
        if nm == 'sn': json.dump(R.ORDER, open(D + 'bone_order.json', 'w'))
        else:
            ref = json.load(open(D + 'bone_order.json')); assert set(ref) == set(R.ORDER), set(ref) ^ set(R.ORDER); R.ORDER = list(ref)
        F = frames(R, CFG[nm])
        if nm == 'sn':
            idx, w, near = skin_sn(m, R, mx); export(nm, m, R, idx, w, F, OUT + 'axo_stand')
            idx, w, near = skin_sn(m, R, mx, pure=True); export('snh', m, R, idx, w, F, OUT + 'axo_stand_h')
        else: idx, w, near = skin_cn(m, R); export(nm, m, R, idx, w, F, OUT + 'axo_crawl')
        print(' bones:', len(R.ORDER))
