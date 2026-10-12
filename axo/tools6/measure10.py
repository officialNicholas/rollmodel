# The v10b body measured against the v9b one (fable2/rt3, the body v239 shipped with): the neck and trunk profile by height along the
# neck axis (front, side and back radius), the width across the shoulders and the trunk's depth at its top, the limbs' radii, the hands',
# feet's and head's sizes, and the throat's front at the bow tie's height (bodyPoint). usage: measure10.py
import json
import numpy as np
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
WORK = S + '/fable3'
def load(d, nm):
    meta = json.load(open(f'{d}/axo_{nm}.json')); b = open(f'{d}/axo_{nm}.bin', 'rb').read(); o = meta['off7']; n = meta['n']
    P = np.frombuffer(b, np.float32, n * 3, o['position']).reshape(n, 3).astype(float)
    si = np.frombuffer(b, np.uint8, n * 4, o['skinIndex']).reshape(n, 4); sw = np.frombuffer(b, np.uint8, n * 4, o['skinWeight']).reshape(n, 4)
    names = [x['name'] for x in meta['bones']]; W = np.zeros((n, len(names)))
    for c in range(4): np.add.at(W, (np.arange(n), si[:, c].astype(int)), sw[:, c] / 255)
    bi = {k: i for i, k in enumerate(names)}
    w = lambda *ks: sum(W[:, bi[k]] for k in ks); wl = lambda pre: sum(W[:, i] for i, k in enumerate(names) if k.startswith(pre))
    return dict(P=P, W=W, bi=bi, bones={x['name']: x for x in meta['bones']}, meta=meta, w=w, wl=wl, n=n)
def profile(M, ax, al0, half=0.02):
    P, w, wl = M['P'], M['w'], M['wl']; o, nx = np.array(ax['o']), np.array(ax['n']); fwd = np.array([0, 0, 1.0]) - nx * nx[2]; fwd /= np.linalg.norm(fwd); side = np.cross(nx, fwd)
    rel = P - o; al = rel @ nx; rad = rel - np.outer(al, nx); rr = np.linalg.norm(rad, axis=1); ph = np.degrees(np.arctan2(rad @ side, rad @ fwd))
    body = (wl('gill') < 0.02) & ((w('head', 'headfront', 'neck', 'chest', 'spine1') > 0.02)) & (wl('shoulder') + wl('upperarm') + wl('forearm') + wl('hand') + wl('finger') < 0.3)
    band = body & (np.abs(al - al0) < half)
    def mx(m): return rr[m].max() if m.any() else float('nan')
    return mx(band & (np.abs(ph) < 20)), mx(band & (np.abs(np.abs(ph) - 90) < 20)), mx(band & (np.abs(ph) > 160))
def limb_r(M, bone, thr=0.6):
    b = M['bones'][bone]; p0, p1 = np.array(b['pos']), np.array(b['end']); d = p1 - p0; L = np.linalg.norm(d); d /= L
    m = M['W'][:, M['bi'][bone]] > thr; rel = M['P'][m] - p0; al = rel @ d; r = np.linalg.norm(rel - np.outer(al, d), axis=1)
    mid = (al > 0.25 * L) & (al < 0.75 * L); return r[mid].mean() if mid.any() else float('nan'), L
def extent(M, m, axis=None):
    Q = M['P'][m]
    if axis is None: return Q.max(0) - Q.min(0)
    a = Q @ axis; return a.max() - a.min()
for nm in ('stand', 'crawl'):
    A = load(S + '/fable2/rt3', nm); B = load(WORK + '/rt4', nm); ax = json.load(open(f'{WORK}/rt4/axo_{nm}_caps.json'))['neck_axis']
    print(f'== {nm}: neck axis o {np.round(ax["o"], 3).tolist()}; profile radius (m) front / side / back, v9b body -> v10b, by height along the axis (0 = the head joint)')
    for al0 in np.arange(-0.60, 0.13, 0.04):
        fa, sa, ba = profile(A, ax, al0); fb, sb, bb = profile(B, ax, al0)
        print(f'  al {al0:+.2f}: {fa:.3f} {sa:.3f} {ba:.3f} -> {fb:.3f} {sb:.3f} {bb:.3f}   ({fb - fa:+.3f} {sb - sa:+.3f} {bb - ba:+.3f})')
    for M, lab in ((A, 'v9b'), (B, 'v10b')):
        w, wl, P = M['w'], M['wl'], M['P']; o, nx = np.array(ax['o']), np.array(ax['n']); al = (P - o) @ nx
        sh = (w('chest', 'spine1') + wl('shoulder') > 0.3) & (wl('upperarm') < 0.5) & (wl('gill') < 0.02)
        band = sh & (al > -0.50) & (al < -0.26); width = np.abs(P[band, 0]).max() * 2 if band.any() else float('nan'); depth = extent(M, band)[2] if band.any() else float('nan')
        hip = (w('hips') > 0.5); hipw = np.abs(P[hip, 0]).max() * 2
        skull = (w('head', 'headfront') > 0.5) & (wl('gill') < 0.02); hw_ = extent(M, skull)
        hand = (w('hand.L') + sum(M['W'][:, i] for i, k in enumerate(M['bones']) if k.startswith('finger') and k.endswith('.L.1') or k.startswith('finger') and k.endswith('.L.2'))) > 0.5
        foot = (w('foot.L', 'toes.L') + sum(M['W'][:, i] for i, k in enumerate(M['bones']) if k.startswith('toe') and '.L.' in k)) > 0.5
        hb = M['bones']['hand.L']; hd = np.array(hb['end']) - np.array(hb['pos']); hd /= np.linalg.norm(hd)
        fb_ = M['bones']['foot.L']; fd = np.array(fb_['end']) - np.array(fb_['pos']); fd /= np.linalg.norm(fd)
        ua, uL = limb_r(M, 'upperarm.L'); th, tL = limb_r(M, 'thigh.L'); fa_, _ = limb_r(M, 'forearm.L'); sn, _ = limb_r(M, 'shin.L')
        hgt = M['meta']['bbox'][1][1] - M['meta']['bbox'][0][1]
        print(f'  {lab}: shoulders width {width:.3f}, trunk-top depth {depth:.3f}, hips width {hipw:.3f}; upper arm r {ua:.3f} (L {uL:.3f}), forearm r {fa_:.3f}, thigh r {th:.3f} (L {tL:.3f}), shin r {sn:.3f}; '
              f'hand {extent(M, hand, hd):.3f} long x {extent(M, hand)[0]:.3f} wide, foot {extent(M, foot, fd):.3f} long x {extent(M, foot)[0]:.3f} wide; skull {hw_[0]:.3f} wide x {hw_[1]:.3f} tall, height {hgt:.3f}, head/height {hw_[1] / hgt:.2f}, head/hips {hw_[0] / hipw:.2f}')
    if nm == 'stand':
        fc, r = B['meta']['face']['c'], B['meta']['face']['r']; anchor = np.array([fc[0], fc[1] - 0.84 * r, fc[2] + 0.5 * r])
        for M, lab in ((A, 'v9b'), (B, 'v10b')):
            P, w, wl = M['P'], M['w'], M['wl']; body = (wl('gill') < 0.02) & (wl('upperarm') + wl('shoulder') < 0.3)
            band = body & (np.abs(P[:, 1] - anchor[1]) < 0.02) & (np.abs(P[:, 0]) < 0.06); zf = P[band, 2].max()
            print(f'  bodyPoint (bow tie) at {np.round(anchor, 3).tolist()} = face.c + (0, -0.84 r, 0.5 r): the throat front there is at z {zf:.3f} in {lab} ({(zf - fc[2]) / r:.2f} r in front of face.c)')
