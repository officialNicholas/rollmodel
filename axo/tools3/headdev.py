# where do the crawl head and the stand head (moved onto the crawl's face centre) coincide? deviation by direction about the face centre
import numpy as np, sys
sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo3')
from remesh import Surface
s = np.load('stand7_rig.npz', allow_pickle=True); c = np.load('crawl7_rig.npz', allow_pickle=True)
names = list(s['names']); gi = [i for i, n in enumerate(names) if n.startswith('gill')]
def dom(z): return z['idx'][np.arange(len(z['idx'])), z['w'].argmax(1)]
ds, dc = dom(s), dom(c)
CSs = s['C']; CCc = c['C']; t = CCc - CSs; print('stand C', CSs, 'crawl C', CCc, 't', t)
Ps = s['P'] + t; Pc = c['P']
gs = np.isin(ds, gi); gc = np.isin(dc, gi)
# stand surface without its gills
Ts = s['T'][~gs[s['T']].any(1)]; Tc = c['T'][~gc[c['T']].any(1)]
Ss = Surface(Ps, Ts); Sc = Surface(Pc, Tc)
def angles(P, C):
    d = P - C; r = np.linalg.norm(d, axis=1); u = d / r[:, None]; return np.degrees(np.arctan2(u[:, 0], u[:, 2])), np.degrees(np.arcsin(np.clip(u[:, 1], -1, 1))), r
yc, pc, rc = angles(Pc, CCc); near = (rc < 0.55) & ~gc
q = Ss.project(Pc[near]); dev = np.linalg.norm(q - Pc[near], axis=1)
Y, Pi = yc[near], pc[near]
print('crawl head verts near:', near.sum())
bins_y = np.arange(0, 181, 15); bins_p = np.arange(-90, 91, 15)
print('median |dev| (mm), crawl -> stand surface; rows pitch (top +90 .. -90), cols |yaw| 0..180')
print('      ' + ''.join(f'{b:>6d}' for b in bins_y[:-1]))
for p0 in bins_p[::-1][1:]:
    row = []
    for y0 in bins_y[:-1]:
        m = (np.abs(Y) >= y0) & (np.abs(Y) < y0 + 15) & (Pi >= p0) & (Pi < p0 + 15)
        row.append(f'{np.median(dev[m]) * 1000:6.0f}' if m.sum() > 3 else '     .')
    print(f'{p0:+4d}  ' + ''.join(row))
# gill bases: angles of the gill-dominated vertices nearest to the head
for nm, z, dd, C in (('stand', s, ds, CSs), ('crawl', c, dc, CCc)):
    P = z['P']; g = np.isin(dd, gi); y_, p_, r_ = angles(P[g], C)
    base = r_ < np.percentile(r_, 15)
    print(nm, 'gill verts', g.sum(), 'base yaw range', np.percentile(np.abs(y_[base]), [5, 50, 95]).round(0), 'pitch', np.percentile(p_[base], [5, 50, 95]).round(0), 'r', np.percentile(r_[base], [5, 50, 95]).round(3))
