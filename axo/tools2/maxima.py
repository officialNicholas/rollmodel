# all geodesic local maxima (from the wrist) per extremity, in EXPORTED coordinates, for seed picking; writes a sheet spec with numbered markers
import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo2')
import numpy as np, json
from rigcore import *
W = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/axo2/'
which = sys.argv[1]
if which == 'crawl':
    m = M('crawl'); col, hsv = vertex_colours(m, D + 'crawl_tex.png'); red = (hsv[:, 1] > 0.5) & ((hsv[:, 0] > 0.9) | (hsv[:, 0] < 0.05))
    seeds = {'hand.L': ((-0.02, -0.37, 0.66), (-0.03, -0.41, 0.80)), 'hand.R': ((-0.70, -0.36, 0.55), (-0.86, -0.41, 0.62)), 'toes.L': ((0.32, -0.38, 0.08), (0.40, -0.41, 0.15)), 'toes.R': ((-0.26, -0.38, -0.46), (-0.33, -0.41, -0.55))}
    meta = json.load(open(W + 'axo_crawl.json')); sc, sh = 1.15, None
    hips_raw = None
else:
    m = M('stand'); red = np.zeros(m.n, bool)
    seeds = {'toes.L': ((0.269, 0.067, 0.727), (0.3, 0.06, 0.78)), 'toes.R': ((-0.256, 0.069, 0.677), (-0.3, 0.09, 0.73)), 'hand.L': ((0.478, 0.705, 0.766), (0.5, 0.55, 0.82)), 'hand.R': ((-0.459, 0.69, 0.682), (-0.5, 0.55, 0.72))}
    meta = json.load(open(W + 'axo_stand.json')); sc = 1.0
# recover the export transform from the exported hips joint vs raw: compute from meta (bones pos) and raw joint positions is messy; use bbox instead
raw_min = m.P0.min(0); exp_min = np.array(meta['bbox'][0]); shift = exp_min - raw_min * sc
print('transform scale', sc, 'shift', shift.round(4))
cells = []; allm = {}
for nm, (wr, tp) in seeds.items():
    wr = np.asarray(wr); tp = np.asarray(tp); ax = unit(tp - wr)
    reg = (np.linalg.norm(m.P - (wr + ax * 0.06), axis=1) < 0.2) & ~red
    src = np.where(reg)[0]; src = src[np.argmin(np.linalg.norm(m.P[src] - wr, axis=1))]; d = m.geo(src, limit=0.6); fin = np.isfinite(d) & reg
    t = m.tips(d, fin & (d > 0.3 * d[fin].max()), r=0.012, k=24)
    pts = [(m.P[v] * sc + shift).tolist() for v in t]; allm[nm] = {'raw': [m.P[v].tolist() for v in t], 'exp': pts, 'd': [float(d[v]) for v in t]}
    print(nm, 'maxima:'); [print(f'   {i:2d} raw {np.round(m.P[v], 3).tolist()} d={d[v]:.3f}') for i, v in enumerate(t)]
    c = (np.mean(pts, 0)).tolist(); dist = 0.55
    for yaw, pitch, vl in [(0.0, 1.4, 'top'), (0.0, -1.4, 'below'), (0.0, 0.2, 'front'), (1.57, 0.3, 'side+x'), (-1.57, 0.3, 'side-x'), (3.14, 0.3, 'back')]:
        cells.append([f'{nm} {vl}', f"rv.reset(); rv.mode('flat'); rv.skel(false); rv.marks({json.dumps([[round(x, 4) for x in p] for p in pts])}); rv.view({yaw},{pitch},{dist},{c[0]},{c[1]},{c[2]},30)"])
json.dump({'mesh': 'axo_' + which, 'out': f'rv_max_{which}.jpg', 'cells': cells, 'ncol': 6, 'W': 480, 'H': 480}, open(D + f'spec_max_{which}.json', 'w')); json.dump(allm, open(D + f'maxima_{which}.json', 'w'))
