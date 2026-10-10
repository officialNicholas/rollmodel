# stand rig: the user's Mixamo skeleton + weights as the base; tail chain, gill stalks, fingers and toes added from geometric segmentation
import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo2')
import numpy as np, json
from rigcore import *
OUT = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/axo2/'
SHORT = {'mixamorig:Hips': 'hips', 'mixamorig:Spine': 'spine', 'mixamorig:Spine1': 'spine1', 'mixamorig:Spine2': 'chest', 'mixamorig:Neck': 'neck', 'mixamorig:Head': 'head', 'headfront': 'headfront',
         'mixamorig:LeftShoulder': 'shoulder.L', 'mixamorig:LeftArm': 'upperarm.L', 'mixamorig:LeftForeArm': 'forearm.L', 'mixamorig:LeftHand': 'hand.L', 'mixamorig:LeftUpLeg': 'thigh.L', 'mixamorig:LeftLeg': 'shin.L', 'mixamorig:LeftFoot': 'foot.L', 'mixamorig:LeftToeBase': 'toes.L',
         'mixamorig:RightShoulder': 'shoulder.R', 'mixamorig:RightArm': 'upperarm.R', 'mixamorig:RightForeArm': 'forearm.R', 'mixamorig:RightHand': 'hand.R', 'mixamorig:RightUpLeg': 'thigh.R', 'mixamorig:RightLeg': 'shin.R', 'mixamorig:RightFoot': 'foot.R', 'mixamorig:RightToeBase': 'toes.R'}
ORDER = ['hips', 'spine', 'spine1', 'chest', 'neck', 'head', 'headfront', 'shoulder.L', 'upperarm.L', 'forearm.L', 'hand.L', 'shoulder.R', 'upperarm.R', 'forearm.R', 'hand.R', 'thigh.L', 'shin.L', 'foot.L', 'toes.L', 'thigh.R', 'shin.R', 'foot.R', 'toes.R']
NF, NT = 4, 4   # bone slots per hand / foot (shared list; the stand feet only fill 3)
# digit tips authored from the close-up inspection (mesh coordinates): 4 fingers (3 long + a short inner one) per hand, 3 stubby toes per foot
TIPS = {'hand.L': [(0.467, 0.535, 0.836), (0.379, 0.584, 0.839), (0.59, 0.56, 0.77), (0.62, 0.69, 0.79)],
        'hand.R': [(-0.6, 0.57, 0.64), (-0.5, 0.52, 0.74), (-0.62, 0.71, 0.65), (-0.42, 0.58, 0.76)],
        'foot.L': [(0.147, 0.065, 0.794), (0.24, 0.07, 0.79), (0.4, 0.06, 0.71)],
        'foot.R': [(-0.145, 0.076, 0.757), (-0.3, 0.09, 0.73), (-0.352, 0.097, 0.616)]}

def qmat(q):
    x, y, z, w = q; return np.array([[1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)], [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)], [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]])

def pad_digits(gl, n, joint, fwd, what):
    if len(gl) < n: print(f'  !!! {what}: only {len(gl)} digits found, padding to {n}')
    while len(gl) < n:
        g = dict(gl[-1]) if gl else {'verts': np.zeros(0, int), 'tip': 0, 'base': joint + fwd * 0.05, 'axis': fwd, 'L': 0.08}; g['verts'] = np.zeros(0, int); g['base'] = g['base'] + np.array([0.01, 0, 0]); gl.append(g)
    return gl

def build():
    m = M('stand'); src = m.src; names = [str(n) for n in src['names']]; par = list(src['par']); T, Rq = src['T'], src['Rq']
    # rest joint world positions (root node scale 0.01)
    Wm = [None] * len(names)
    for i in range(len(names)):
        L = np.eye(4); L[:3, :3] = qmat(Rq[i]); L[:3, 3] = T[i]; Wm[i] = L if par[i] < 0 else Wm[par[i]] @ L
    jp = {SHORT[n]: 0.01 * Wm[i][:3, 3] for i, n in enumerate(names)}; jpar = {SHORT[n]: (SHORT[names[par[i]]] if par[i] >= 0 else None) for i, n in enumerate(names)}
    R = Rig()
    for k in ORDER: R.add(k, jp[k], jpar[k])
    R.END['head'] = jp['head'] + np.array([0, 0.3, 0]); R.END['headfront'] = jp['headfront'] + np.array([0, 0, 0.05])
    R.END['chest'] = jp['neck']; R.END['hips'] = jp['spine']
    # Mixamo weights on welded vertices
    JN, WT = src['JN'], src['WT']; nm = len(names); Wmx = np.zeros((m.n, nm)); cnt = np.zeros(m.n)
    for c in range(4): np.add.at(Wmx, (m.wid, JN[:, c]), WT[:, c])
    np.add.at(cnt, m.wid, 1); Wmx /= cnt[:, None]
    col, hsv = vertex_colours(m, D + 'stand_tex.png')
    # ---- tail: fin behind the body (z < 0.2, thin in x); base ring at the body
    dom = np.array([SHORT[names[k]] for k in Wmx.argmax(1)])
    tailmask = (m.P[:, 2] < 0.22) & (m.P[:, 0] > -0.1) & (m.P[:, 0] < 0.3) & (m.P[:, 1] < 0.9)
    nc, lab = m.comps(tailmask); sizes = np.bincount(lab[lab >= 0]); tailmask = lab == sizes.argmax()
    # centerline: per-z-slice midpoints of the fin's extent (the fin is a thin vertical blade, too coarse for ring centroids)
    tz = m.P[tailmask][:, 2]; zs = np.linspace(0.2, tz.min(), 40); mids = []
    for z in zs:
        q = m.P[tailmask & (np.abs(m.P[:, 2] - z) < 0.045)]
        mids.append([(q[:, 0].min() + q[:, 0].max()) / 2, (q[:, 1].min() + q[:, 1].max()) / 2, z] if len(q) >= 2 else mids[-1])
    sm = np.array(mids)
    for i in range(len(sm)): sm[i] = np.array(mids)[max(0, i - 3):i + 4].mean(0)
    cum = np.r_[0, np.cumsum(np.linalg.norm(np.diff(sm, axis=0), axis=1))]
    tp = np.array([sm[np.argmin(np.abs(cum - f * cum[-1]))] for f in np.linspace(0, 1, 7)]); tp[0][2] = 0.2
    print(' tail verts', int(tailmask.sum()), 'length', round(float(cum[-1]), 3), 'joints', tp.round(2).tolist())
    prev = 'hips'
    for k in range(6): R.add(f'tail{k + 1}', tp[k], prev); prev = f'tail{k + 1}'
    R.END['tail6'] = tp[6]
    # ---- gills: red skin on the head (both sides), 3 stalks a side
    head_c = jp['head'] + np.array([0, 0.33, 0.0]); head_r = 0.33
    # gill skin = red frills OR thin stems, beside / behind the head (the stems are pale pink, so colour alone misses them)
    dh_ = np.linalg.norm(m.P - head_c, axis=1); near = (m.P[:, 1] > 1.05) & (dh_ > 0.33) & (dh_ < 0.75)
    redv = (hsv[:, 1] > 0.42) & ((hsv[:, 0] > 0.9) | (hsv[:, 0] < 0.05)); thin = thin_mask(m, near, red=redv)
    gill = near & (redv | thin); nc_, lab_ = m.comps(gill); sz_ = np.bincount(lab_[lab_ >= 0]); gill = np.isin(lab_, np.where(sz_ >= 40)[0])
    print('  gills: near', int(near.sum()), 'red', int((near & redv).sum()), 'thin', int(thin.sum()), 'gill', int(gill.sum()), 'components', sorted(sz_[sz_ >= 40].tolist(), reverse=True))
    nonred_d = m.geo(np.where(~gill)[0], limit=1.0)   # geodesic distance to the nearest non-gill vertex
    up = np.array([0, 1.0, 0]); fwd = np.array([0, 0, 1.0]); left = np.array([1.0, 0, 0]); stalks = {}
    for side, sg in (('L', 1), ('R', -1)):
        groups = split_stalks(m, gill, head_c, up, left, sg, 3, nonred_d)
        for k, vs in enumerate(groups):
            root, mid, tip, axis, L = stalk_chain(m, vs, head_c, nonred_d)
            R.add(f'gill{k}.{side}.1', root, 'head'); R.add(f'gill{k}.{side}.2', mid, f'gill{k}.{side}.1'); R.END[f'gill{k}.{side}.2'] = tip
            stalks[f'gill{k}.{side}'] = (vs, root, axis, L); print(f'  gill{k}.{side}: {len(vs)} verts, root {root.round(2)}, len {L:.2f}')
    # ---- digits
    digs = {}
    for side in ('L', 'R'):
        hand = jp['hand.' + side]; fa = jp['forearm.' + side]; fwdh = unit(hand - fa)
        region = (Wmx[:, names.index(f'mixamorig:{"Left" if side == "L" else "Right"}Hand')] > 0.25)
        region &= ~gill
        gl, t, hax = segment_digits(m, hand, region, nmax=NF, verbose='hand.' + side, min_verts=6, seeds=TIPS['hand.' + side]); gl = pad_digits(gl, NF, hand, hax, 'hand.' + side); fwdh = hax
        # order the digits across the hand: thumb side = toward the body (-x for L)
        sideax = np.array([-1.0 if side == 'L' else 1.0, 0, 0])
        wid = unit(np.cross(hax, np.array([0, 0, 1.0]))); gl.sort(key=lambda g: float((g['base'] - hand) @ wid) * (1 if side == 'L' else -1))
        for k, g in enumerate(gl):
            b, mi, tp_ = digit_chain(g) if len(g['verts']) else (g['base'], g['base'] + fwdh * 0.04, g['base'] + fwdh * 0.08); n1, n2 = f'finger{k}.{side}.1', f'finger{k}.{side}.2'
            R.add(n1, b, 'hand.' + side); R.add(n2, mi, n1); R.END[n2] = tp_; digs[n1[:-2]] = (g, 'hand.' + side)
        R.END['hand.' + side] = np.mean([g['base'] for g in gl], 0)
        foot = jp['foot.' + side]; toes = jp['toes.' + side]; fwdf = unit(np.array([0.25 * (1 if side == 'L' else -1), -0.1, 1.0]))
        region = (Wmx[:, names.index(f'mixamorig:{"Left" if side == "L" else "Right"}ToeBase')] + Wmx[:, names.index(f'mixamorig:{"Left" if side == "L" else "Right"}Foot')] > 0.25)
        gl, t, fax = segment_digits(m, toes, region, axis=fwdf, nmax=NT, verbose='foot.' + side, min_verts=6, seeds=TIPS['foot.' + side]); gl = pad_digits(gl, NT, toes, fwdf, 'foot.' + side)
        gl.sort(key=lambda g: float((g['base'] - toes)[0]) * (-1 if side == 'L' else 1))
        for k, g in enumerate(gl):
            b, mi, tp_ = digit_chain(g) if len(g['verts']) else (g['base'], g['base'] + fwdf * 0.04, g['base'] + fwdf * 0.08); n1, n2 = f'toe{k}.{side}.1', f'toe{k}.{side}.2'
            R.add(n1, b, 'toes.' + side); R.add(n2, mi, n1); R.END[n2] = tp_; digs[n1[:-2]] = (g, 'toes.' + side)
        R.END['toes.' + side] = np.mean([g['base'] for g in gl], 0)
    assert len(R.ORDER) == 23 + 6 + 12 + 16 + 16, len(R.ORDER)
    # ---- weights: start from the user's Mixamo weights remapped onto the shared bone list
    names_out = R.ORDER; bi = {k: i for i, k in enumerate(names_out)}; W = np.zeros((m.n, len(names_out)))
    for i, n in enumerate(names): W[:, bi[SHORT[n]]] += Wmx[:, i]
    headzone = (m.P[:, 1] > 1.05) & (np.linalg.norm(m.P - head_c, axis=1) < 0.8)
    for sh in ('shoulder.L', 'shoulder.R'):
        mv = headzone & (W[:, bi[sh]] > 0); print(f'  defect fix: {int(mv.sum())} head-zone vertices carried {sh} weight -> head'); W[mv, bi['head']] += W[mv, bi[sh]]; W[mv, bi[sh]] = 0
    labels = np.full(m.n, 'body', dtype=object)
    # tail: chain weights along the 6 bones, blending into the hips at the base
    chain_weights(m.P, np.where(tailmask)[0], tp, [bi[f'tail{k + 1}'] for k in range(6)], W, band=0.08, base_bone=bi['hips'], base_blend=0.12); labels[tailmask] = 'tail'
    # gills: per stalk
    for key, (vs, root, axis, L) in stalks.items():
        stalk_weights(m, vs, root, axis, L, [bi[key + '.1'], bi[key + '.2']], bi['head'], W); labels[vs] = key
    # digits
    for key, (g, parent) in digs.items():
        if not len(g['verts']): continue
        digit_weights(m, g, [bi[key + '.1'], bi[key + '.2']], bi[parent], W); labels[g['verts']] = key
    knuckle_smooth(m, W, np.concatenate([g['verts'] for g, _ in digs.values() if len(g['verts'])]))
    idx, w = finalize(W, P=m.P, joints=np.array([R.J[k] for k in R.ORDER]))
    # ---- frames (Y along the bone, Z = flexion / ventral side)
    F = {}; fwdz = np.array([0, 0, 1.0]); downy = np.array([0, -1.0, 0])
    for k in R.ORDER:
        y = R.dirn(k)
        if k in ('hips', 'spine', 'spine1', 'chest', 'neck'): F[k] = mkframe(y, fwdz)
        elif k == 'head': F[k] = mkframe(up, fwdz)
        elif k == 'headfront': F[k] = mkframe(fwdz, up)
        elif k.startswith('shoulder'): F[k] = mkframe(y, fwdz)
        elif k.startswith('upperarm'): F[k] = mkframe(y, fwdz)
        elif k.startswith('forearm'):
            yu = R.dirn(R.PAR[k]); flex = y - (y @ yu) * yu
            F[k] = mkframe(y, flex if np.linalg.norm(flex) > np.sin(np.radians(10)) else F[R.PAR[k]][:, 2])
        elif k.startswith('hand'):
            side = k[-1]; fb = np.array([R.J[f'finger{i}.{side}.1'] for i in range(NF)]); pts = np.r_[fb, [R.J[k]]]; c = pts.mean(0); u, s_, vt = np.linalg.svd(pts - c); nrm = vt[2]
            # ventral side of the palm: faces the body's midline and forward (hands hang at the sides)
            ref = np.array([-1.0 if side == 'L' else 1.0, 0, 0.4]); nrm = nrm if nrm @ ref > 0 else -nrm; F[k] = mkframe(y, nrm); R.UP[k] = nrm
        elif k.startswith('finger') or k.startswith('toe'): F[k] = F[R.PAR[k]].copy()   # every digit of a hand curls about the hand's hinge, so neighbours stay parallel and webs do not stretch
        elif k.startswith('thigh'): F[k] = mkframe(y, fwdz)
        elif k.startswith('shin'): F[k] = mkframe(y, -fwdz)
        elif k.startswith('foot') or k.startswith('toes'): F[k] = mkframe(y, downy)
        elif k.startswith('tail'): F[k] = mkframe(y, downy)
        elif k.startswith('gill'): F[k] = mkframe(y, fwdz)
        else: raise Exception(k)
    # debug info
    dbg = {'labels': {k: int((labels == k).sum()) for k in set(labels)}}
    export(m, R, F, idx, w, OUT + 'axo_stand', extra={'palm': {k: R.UP[k].round(4).tolist() for k in R.UP}, 'headc': (np.array([0.004, 1.371, 0.638]) - jp['head']).round(4).tolist(), 'headr': 0.38}, shift=(-jp['hips'][0], -0.023, -jp['hips'][2]))
    np.savez(D + 'stand_rig.npz', idx=idx, w=w, labels=labels.astype(str), names=np.array(names_out))
    json.dump({'bones': [{'name': k, 'parent': R.PAR[k], 'pos': R.J[k].tolist(), 'end': R.endp(k).tolist()} for k in R.ORDER]}, open(D + 'stand_skel.json', 'w'), indent=0)
    print(' labels', dbg)
    return R

if __name__ == '__main__': build()
