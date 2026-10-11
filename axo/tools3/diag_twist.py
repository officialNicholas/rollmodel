import json, numpy as np, sys
def qmat(q):
    x, y, z, w = q
    return np.array([[1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)], [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)], [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]])
def unit(v): return v / np.linalg.norm(v)
meta = json.load(open(sys.argv[1])); B = {b['name']: b for b in meta['bones']}
for up, lo, en, sU in (('upperarm', 'forearm', 'hand', -1), ('thigh', 'shin', 'foot', 1)):
    for sd in 'LR':
        r = np.array(B[f'{up}.{sd}']['pos']); k = np.array(B[f'{lo}.{sd}']['pos']); e = np.array(B[f'{en}.{sd}']['pos'])
        n = unit(e - r); p = k - r; p = p - n * (p @ n); p = unit(p); Xh = unit(np.cross(n, p))
        for bone, Xexp, a, b in ((up, sU * Xh, r, k), (lo, -Xh, k, e)):
            F = qmat(B[f'{bone}.{sd}']['q']); yb = unit(b - a); Xe = unit(Xexp - yb * (Xexp @ yb))
            print(f'  {bone}.{sd}: twist vs IK {np.degrees(np.arctan2(np.cross(F[:, 0], Xe) @ F[:, 1], F[:, 0] @ Xe)):7.2f} deg')
