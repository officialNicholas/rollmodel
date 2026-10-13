# The source model in the rig's work frame: Meshy's mesh turned about the vertical so its hind body (hips, hind legs, tail root) faces +z
# with its mirror plane at x = 0, the ground (its lowest point) at y = 0; the welded topology (the mesh is split along its UV seams).
#   python3 -I prep.py      (reads fable4/work/src_mesh.npz from glbread.py, writes fable4/work/work.npz)
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import meshkit as mk
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'; W = S + '/fable5/work'
def ry(a): c, s = np.cos(a), np.sin(a); return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
YAW1 = -np.arctan2(-0.757, 0.654)     # the mesh's long axis (its xz principal axis) onto +z
YAW2 = np.radians(3.92)               # then the hind body's mirror plane square to x (the fitted symmetry of the hips and hind legs)
X0 = 0.162                            # and onto x = 0
if __name__ == '__main__':
    z = np.load(W + '/src_mesh.npz'); P, N, UV, T = z['P'], z['N'], z['UV'], z['T']
    R = ry(YAW2) @ ry(YAW1); P = P @ R.T; N = N @ R.T; y0 = P[:, 1].min(); P[:, 1] -= y0; P[:, 0] += X0
    wid, rep = mk.weld(P, 1e-5)
    # (a few of Meshy's triangles face inward: the runtime draws front faces only, so each showed as a hole onto the dark ink hull behind;
    # turned round)
    Pw = P[rep]; Tw = wid[T]; Nw = mk.vertex_normals(Pw, Tw); fn = np.cross(Pw[Tw[:, 1]] - Pw[Tw[:, 0]], Pw[Tw[:, 2]] - Pw[Tw[:, 0]])
    fn /= np.maximum(np.linalg.norm(fn, axis=1, keepdims=True), 1e-15); agree = (fn * Nw[Tw].mean(1)).sum(1); bad = agree < -0.5
    T = T.copy(); T[bad] = T[bad][:, [0, 2, 1]]; print('  inward-facing triangles turned round:', int(bad.sum()))
    np.savez(W + '/work.npz', P=P, N=N, UV=UV, T=T, wid=wid, rep=rep, R=R, y0=y0, x0=X0)
    print('work frame: bbox', P.min(0).round(3), P.max(0).round(3), 'welded', len(rep))
