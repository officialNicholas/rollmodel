# crawl rig: the user's crawling sculpt rigged to the same bone list as the stand rig, joints and weights from geometric segmentation
import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo2')
import numpy as np, json
from rigcore import *
OUT = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/axo2/'
NF = NT = 4
# seeds in the sculpt's own coordinates (head toward +z, up +y, character's left = +x): refined from the geometry below
SEED = dict(head=(-0.3, 0.1, 0.66), snout=(-0.3, 0.02, 0.95), tailtip=(0.85, 0.22, -0.95),
            arms={'L': dict(wrist=(-0.02, -0.37, 0.66), tip=(-0.03, -0.41, 0.80)), 'R': dict(wrist=(-0.70, -0.36, 0.55), tip=(-0.86, -0.41, 0.62))},
            legs={'L': dict(wrist=(0.32, -0.38, 0.08), tip=(0.40, -0.41, 0.15)), 'R': dict(wrist=(-0.26, -0.38, -0.46), tip=(-0.33, -0.41, -0.55))})
# digit tips authored from the close-up inspection (sculpt coordinates): 4 fingers and 4 toes per limb
TIPS = {'hand.L': [(-0.142, -0.406, 0.835), (-0.04, -0.4, 0.80), (-0.201, -0.403, 0.807), (-0.221, -0.394, 0.705)],
        'hand.R': [(-0.853, -0.403, 0.59), (-0.782, -0.412, 0.657), (-0.68, -0.42, 0.67), (-0.57, -0.41, 0.59)],
        'toes.L': [(0.224, -0.417, 0.146), (0.33, -0.42, 0.19), (0.429, -0.417, 0.121), (0.181, -0.414, 0.039)],
        'toes.R': [(-0.191, -0.406, -0.639), (-0.26, -0.4, -0.58), (-0.117, -0.37, -0.547), (-0.099, -0.389, -0.502)]}
ORDER = json.load(open(OUT + 'axo_stand.json'))['bones']; ORDER = [b['name'] for b in ORDER]

def limb_from_hand(m, hand_verts, mask, step=0.025, maxlen=1.0):
    """ring centroids of geodesic distance from the hand verts up the limb; stops where the rings widen into the body. returns pts, radii, d"""
    d = m.geo(np.where(hand_verts)[0], limit=maxlen + 0.1, mask=mask); pts = []; rads = []; last = None
    for t in np.arange(0.0, maxlen, step):
        sel = np.isfinite(d) & (np.abs(d - t) < step * 0.6) & mask
        if sel.sum() < 3: break
        q = m.P[sel]; cen = q.mean(0); r = np.percentile(np.linalg.norm(q - cen, axis=1), 85)
        if len(rads) > 6 and r > 1.7 * np.median(rads[-6:]) and r > 0.09: break
        pts.append(cen); rads.append(r); last = t
    return np.array(pts), np.array(rads), d, last

def build():
    m = M('crawl'); col, hsv = vertex_colours(m, D + 'crawl_tex.png'); R = Rig(); P = m.P
    up = np.array([0, 1.0, 0]); fwd = np.array([0, 0, 1.0]); left = np.array([1.0, 0, 0])
    # ---- head & gills
    head_c = np.asarray(SEED['head'], float); red = (hsv[:, 1] > 0.5) & ((hsv[:, 0] > 0.9) | (hsv[:, 0] < 0.05))
    headmask = (np.linalg.norm(P - head_c, axis=1) < 0.36) & ~red & (P[:, 2] > 0.33)
    head_c = P[headmask].mean(0); headmask = (np.linalg.norm(P - head_c, axis=1) < 0.36) & ~red & (P[:, 2] > 0.33); print(' head centre', head_c.round(3), 'verts', int(headmask.sum()))
    # gill skin = red skin near the head that is THIN (frills and stems have an opposite-facing neighbour within 3.5 cm); the red flank
    # stripes on the smooth body are not thin. One dilation step over the mesh keeps stem bases that sit on the head.
    from scipy.spatial import cKDTree
    near = (np.linalg.norm(P - head_c, axis=1) < 0.55) & (P[:, 2] > 0.2) & (P[:, 1] > head_c[1] - 0.15) & (np.linalg.norm(P - head_c, axis=1) > 0.3 * 0.6)
    thin = thin_mask(m, near) & ~headmask   # (the colour-consistent variant makes sails on this sculpt: frills merge into the shoulders)
    nb_rows = m.G.tolil().rows; dil = thin.copy()
    for v in np.where(near & ~thin)[0]:
        if any(thin[u] for u in nb_rows[v]): dil[v] = True
    gill = near & (dil | red); nc_, lab_ = m.comps(gill); sz_ = np.bincount(lab_[lab_ >= 0]); gill = np.isin(lab_, np.where(sz_ >= 40)[0])
    print('  gills: near-red', int(near.sum()), 'thin', int(thin.sum()), 'gill', int(gill.sum()), 'components', sorted(sz_[sz_ >= 40].tolist(), reverse=True))
    nonred_d = m.geo(np.where(~gill)[0], limit=1.0); stalks = {}
    for side, sg in (('L', 1), ('R', -1)):
        groups = split_stalks(m, gill, head_c, up, left, sg, 3, nonred_d)
        for k, vs in enumerate(groups):
            root, mid, tip, axis, L = stalk_chain(m, vs, head_c, nonred_d)
            rel = P[vs] - root; perp = np.linalg.norm(rel - (rel @ axis)[:, None] * axis[None], axis=1); far = perp > 0.16
            if far.any(): print(f'    gill{k}.{side}: {int(far.sum())} verts far from the stalk -> body'); gill[vs[far]] = False; vs = vs[~far]
            stalks[f'gill{k}.{side}'] = (vs, root, axis, L, mid, tip); print(f'  gill{k}.{side}: {len(vs)} verts root {root.round(2)} len {L:.2f}')
    # ---- digits and limbs
    limbs = {}; digs = {}; limbmask = np.zeros(m.n, bool)
    for kind, grp in (('arm', SEED['arms']), ('leg', SEED['legs'])):
        for side, g in grp.items():
            wrist = np.asarray(g['wrist'], float); tip = np.asarray(g['tip'], float); ax = unit(tip - wrist)
            # the hand: verts within a ball around the hand seed, excluding the gills; axis = toward the tip
            handreg = (np.linalg.norm(P - (wrist + ax * 0.06), axis=1) < 0.2) & ~gill & (P[:, 1] < -0.15)
            nm = ('hand' if kind == 'arm' else 'toes') + '.' + side
            gl, t, hax = segment_digits(m, wrist, handreg, axis=ax, nmax=NF, verbose=nm, min_verts=6, seeds=TIPS[nm])
            while len(gl) < NF: print(f'  !!! {nm}: only {len(gl)} digits'); g0 = dict(gl[-1]); g0['verts'] = np.zeros(0, int); g0['base'] = g0['base'] + np.array([0.01, 0, 0]); gl.append(g0)
            wid = unit(np.cross(hax, up)); gl.sort(key=lambda q: float((q['base'] - wrist) @ wid) * (1 if side == 'L' else -1))
            handverts = np.zeros(m.n, bool)
            for q in gl: handverts[q['verts']] = True
            # the limb: ring centroids from the digit bases up to the body
            notlimb = ~gill & ~headmask
            pts, rads, dl, last = limb_from_hand(m, handverts, notlimb, maxlen=0.55 if kind == 'arm' else 0.5)
            knuck = np.mean([q['base'] for q in gl], 0)
            # wrist = the first ring after the palm (palm length ~0.07), root = the last ring, elbow = the polyline point farthest from the chord
            wr = pts[min(len(pts) - 1, 3)]; root = pts[-1]; chord = unit(root - wr); rel = pts[3:] - wr; perp = np.linalg.norm(rel - (rel @ chord)[:, None] * chord[None], axis=1)
            lo, hi = 3 + int(0.3 * (len(pts) - 3)), 3 + int(0.75 * (len(pts) - 3)); k_ = lo + int(np.argmax(perp[lo - 3:hi - 3])) if hi > lo else (len(pts) + 3) // 2   # the knee / elbow sits in the middle part of the limb
            el = pts[k_] if perp[k_ - 3] > 0.025 else 0.5 * (wr + root)
            lm = np.isfinite(dl) & (dl < (last if last else 0.5) + 0.02) & notlimb; limbmask |= lm
            limbs[(kind, side)] = dict(root=root, elbow=el, wrist=wr, knuck=knuck, mask=lm, gl=gl, hax=hax)
            print(f'  {kind}.{side}: rings {len(pts)} root {root.round(2)} elbow {el.round(2)} wrist {wr.round(2)} knuckles {knuck.round(2)} limb verts {int(lm.sum())}')
    # ---- tail: rings from the tip until the rings widen into the rump
    legz = np.mean([limbs[('leg', s_)]['root'][2] for s_ in ('L', 'R')]); tipv = m.near(SEED['tailtip']); tailmask0 = ~gill & ~headmask & ~limbmask
    dtail = m.geo(tipv, limit=2.0, mask=tailmask0); tpts = []; trad = []
    for t in np.arange(0.0, 1.6, 0.03):
        sel = np.isfinite(dtail) & (np.abs(dtail - t) < 0.02)
        if sel.sum() < 2: break
        q = P[sel]; cen = np.array([(q[:, 0].min() + q[:, 0].max()) / 2, (q[:, 1].min() + q[:, 1].max()) / 2, (q[:, 2].min() + q[:, 2].max()) / 2]); r = np.linalg.norm(q - cen, axis=1).max()
        if len(trad) > 8 and r > 1.5 * np.median(trad[-8:]) and r > 0.2: break
        if cen[2] > legz - 0.2: break   # the tail ends behind the hind legs
        tpts.append(cen); trad.append(r)
    tpts = np.array(tpts)[::-1]   # from the rump to the tip
    tailmask = np.isfinite(dtail) & (dtail < (len(tpts) - 1) * 0.03 + 0.02) & tailmask0
    print(' tail rings', len(tpts), 'root', tpts[0].round(2), 'tip', tpts[-1].round(2), 'verts', int(tailmask.sum()))
    # ---- trunk centerline: the dorsal ridge of the trunk (no limbs / tail / head) per z-slice, dropped to 55% of the section height
    trunkmask = ~gill & ~headmask & ~limbmask & ~tailmask
    zs = np.linspace(tpts[0][2] + 0.05, 0.33, 14); tr = []
    for z in zs:
        q = P[trunkmask & (np.abs(P[:, 2] - z) < 0.04)]
        if len(q) < 6: continue
        top = q[np.argsort(-q[:, 1])[:5]].mean(0); lo = np.percentile(q[:, 1], 5); tr.append([top[0], top[1] - 0.5 * (top[1] - lo), z])
    tr = np.array(tr); sm = tr.copy()
    for i in range(len(tr)): sm[i] = tr[max(0, i - 1):i + 2].mean(0)
    tr = sm; cum = np.r_[0, np.cumsum(np.linalg.norm(np.diff(tr, axis=0), axis=1))]
    at = lambda f: tr[int(np.argmin(np.abs(cum - f * cum[-1])))]
    hips, spine, spine1, chest, neck = at(0.0), at(0.3), at(0.55), at(0.8), at(1.0)
    headj = neck * 0.45 + head_c * 0.55; headj[1] = neck[1] + 0.03
    print(' trunk', tr.round(2).tolist())
    # ---- assemble the rig in the shared order
    R.add('hips', hips, None); R.add('spine', spine, 'hips'); R.add('spine1', spine1, 'spine'); R.add('chest', chest, 'spine1'); R.add('neck', neck, 'chest'); R.add('head', headj, 'neck')
    R.END['head'] = headj + up * 0.3; R.add('headfront', head_c + np.array([0, 0, 0.25]), 'head'); R.END['headfront'] = head_c + np.array([0, 0, 0.3]); R.END['chest'] = neck; R.END['hips'] = spine
    for side in ('L', 'R'):
        a = limbs[('arm', side)]; sh = chest * 0.6 + a['root'] * 0.4
        R.add('shoulder.' + side, sh, 'chest'); R.add('upperarm.' + side, a['root'], 'shoulder.' + side); R.add('forearm.' + side, a['elbow'], 'upperarm.' + side); R.add('hand.' + side, a['wrist'], 'forearm.' + side); R.END['hand.' + side] = a['knuck']
    for side in ('L', 'R'):
        l = limbs[('leg', side)]; R.add('thigh.' + side, l['root'], 'hips'); R.add('shin.' + side, l['elbow'], 'thigh.' + side); R.add('foot.' + side, l['wrist'], 'shin.' + side)
        tb = l['wrist'] * 0.5 + l['knuck'] * 0.5; R.add('toes.' + side, tb, 'foot.' + side); R.END['toes.' + side] = l['knuck']
    idx6 = np.linspace(0, len(tpts) - 1, 7).astype(int); prev = 'hips'
    for k in range(6): R.add(f'tail{k + 1}', tpts[idx6[k]], prev); prev = f'tail{k + 1}'
    R.END['tail6'] = tpts[-1]
    for side in ('L', 'R'):
        for k, q in enumerate(limbs[('arm', side)]['gl']):
            b, mi, tp_ = digit_chain(q) if len(q['verts']) else (q['base'], q['base'] + limbs[('arm', side)]['hax'] * 0.04, q['base'] + limbs[('arm', side)]['hax'] * 0.08)
            R.add(f'finger{k}.{side}.1', b, 'hand.' + side); R.add(f'finger{k}.{side}.2', mi, f'finger{k}.{side}.1'); R.END[f'finger{k}.{side}.2'] = tp_; digs[f'finger{k}.{side}'] = (q, 'hand.' + side)
        for k, q in enumerate(limbs[('leg', side)]['gl']):
            b, mi, tp_ = digit_chain(q) if len(q['verts']) else (q['base'], q['base'] + limbs[('leg', side)]['hax'] * 0.04, q['base'] + limbs[('leg', side)]['hax'] * 0.08)
            R.add(f'toe{k}.{side}.1', b, 'toes.' + side); R.add(f'toe{k}.{side}.2', mi, f'toe{k}.{side}.1'); R.END[f'toe{k}.{side}.2'] = tp_; digs[f'toe{k}.{side}'] = (q, 'toes.' + side)
    for side in ('L', 'R'):
        for k in range(3):
            vs, root, axis, L, mid, tip = stalks[f'gill{k}.{side}']; R.add(f'gill{k}.{side}.1', root, 'head'); R.add(f'gill{k}.{side}.2', mid, f'gill{k}.{side}.1'); R.END[f'gill{k}.{side}.2'] = tip
    assert set(R.ORDER) == set(ORDER), set(R.ORDER) ^ set(ORDER); R.ORDER = list(ORDER); bi = {k: i for i, k in enumerate(R.ORDER)}
    # ---- weights, part by part
    W = np.zeros((m.n, len(R.ORDER))); labels = np.full(m.n, 'trunk', dtype=object)
    # trunk along the spine chain (hips .. neck .. head joint)
    tv = np.where(trunkmask)[0]; chain_weights(P, tv, np.array([tpts[0], hips, spine, spine1, chest, neck, headj]), [bi['hips'], bi['hips'], bi['spine'], bi['spine1'], bi['chest'], bi['neck']], W, band=0.12)
    # head: rigid, fading into the neck at the back
    hv = np.where(headmask | (trunkmask & (P[:, 2] > neck[2] - 0.06)))[0]; u = np.clip((P[hv, 2] - neck[2] + 0.04) / 0.16, 0, 1); W[hv, :] = 0; W[hv, bi['head']] = smooth(u); W[hv, bi['neck']] = 1 - smooth(u); labels[np.where(headmask)[0]] = 'head'
    # tail
    tv = np.where(tailmask)[0]; chain_weights(P, tv, tpts[idx6], [bi[f'tail{k + 1}'] for k in range(6)], W, band=0.08, base_bone=bi['hips'], base_blend=0.1); labels[tv] = 'tail'
    # limbs
    for (kind, side), l in limbs.items():
        names = ('upperarm', 'forearm', 'hand') if kind == 'arm' else ('thigh', 'shin', 'foot')
        pts = np.array([l['root'], l['elbow'], l['wrist'], l['knuck']]); vs = np.where(l['mask'])[0]
        chain_weights(P, vs, pts, [bi[f'{n}.{side}'] for n in names], W, band=0.06, base_bone=bi['chest' if kind == 'arm' else 'hips'], base_blend=0.1); labels[vs] = f'{kind}.{side}'
        if kind == 'leg':   # the toes bone takes the front half of the foot
            fv = vs[(P[vs] - l['wrist']) @ unit(l['knuck'] - l['wrist']) > 0.5 * np.linalg.norm(l['knuck'] - l['wrist'])]; wf = W[fv, bi['foot.' + side]].copy(); W[fv, bi['foot.' + side]] = wf * 0.4; W[fv, bi['toes.' + side]] = wf * 0.6
    for key, (q, parent) in digs.items():
        if len(q['verts']): digit_weights(m, q, [bi[key + '.1'], bi[key + '.2']], bi[parent], W); labels[q['verts']] = key
    for key, (vs, root, axis, L, mid, tip) in stalks.items():
        stalk_weights(m, vs, root, axis, L, [bi[key + '.1'], bi[key + '.2']], bi['head'], W, blend=0.3 if key.startswith('gill2') else 0.2); labels[vs] = key
    # gill skin that lies on the body (shoulders): pin it to the body's own weights so nothing bridges between a stalk and the trunk
    from scipy.spatial import cKDTree
    bodyv = np.where(np.isin(labels, ['trunk', 'head']))[0]; bt = cKDTree(P[bodyv]); gv = np.where(gill)[0]
    dd, ii = bt.query(P[gv]); pin = gv[dd < 0.05]; W[pin] = W[bodyv[ii[dd < 0.05]]]; labels[pin] = 'trunk'
    print('  pinned', len(pin), 'gill vertices lying on the body to the body weights')
    for key, (vs, root, axis, L, mid, tip) in stalks.items(): laplacian_smooth_weights(m, W, vs, iters=3, lam=0.5)
    knuckle_smooth(m, W, np.concatenate([q['verts'] for q, _ in digs.values() if len(q['verts'])]))
    # soften seams between parts (trunk / limbs / tail only; digits and gills stay crisp)
    soft = np.where(np.isin(labels, ['trunk', 'tail', 'arm.L', 'arm.R', 'leg.L', 'leg.R', 'head']))[0]; laplacian_smooth_weights(m, W, soft, iters=4, lam=0.5)
    idx, w = finalize(W, P=m.P, joints=np.array([R.J[k] for k in R.ORDER]))
    # ---- frames: same conventions as the stand rig
    F = {}; downy = -up
    for k in R.ORDER:
        y = R.dirn(k)
        if k in ('hips', 'spine', 'spine1', 'chest', 'neck'): F[k] = mkframe(y, downy)   # horizontal spine: ventral = down
        elif k == 'head': F[k] = mkframe(up, fwd)
        elif k == 'headfront': F[k] = mkframe(fwd, up)
        elif k.startswith('shoulder') or k.startswith('upperarm') or k.startswith('thigh'): F[k] = mkframe(y, fwd if not k.startswith('thigh') else fwd)
        elif k.startswith('forearm') or k.startswith('shin'):
            yu = R.dirn(R.PAR[k]); X = np.cross(yu, y)
            if np.linalg.norm(X) > np.sin(np.radians(10)): X = unit(X); F[k] = mkframe(y, np.cross(X, y))
            else: F[k] = mkframe(y, fwd if k.startswith('forearm') else -fwd)
        elif k.startswith('hand') or k.startswith('foot') or k.startswith('toes'): F[k] = mkframe(y, downy)   # palms / soles on the ground: ventral = down
        elif k.startswith('finger') or k.startswith('toe'): F[k] = F[R.PAR[k]].copy()   # every digit of a hand curls about the hand's hinge, so neighbours stay parallel and webs do not stretch
        elif k.startswith('tail'): F[k] = mkframe(y, downy)
        elif k.startswith('gill'): F[k] = mkframe(y, fwd)
        else: raise Exception(k)
    export(m, R, F, idx, w, OUT + 'axo_crawl', extra={'headc': ((head_c - headj) * 1.15).round(4).tolist(), 'headr': 0.34 * 1.15}, scale=1.15, shift=(-hips[0] * 1.15, 0.418 * 1.15, 0.45 - headj[2] * 1.15))
    np.savez(D + 'crawl_rig.npz', idx=idx, w=w, labels=labels.astype(str), names=np.array(R.ORDER))
    print(' labels', {k: int((labels == k).sum()) for k in sorted(set(labels))})

if __name__ == '__main__': build()
