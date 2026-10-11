import numpy as np, sys, json
sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo2'); sys.path.insert(0, '.')
from geo import M
from crawlbuild import load_old
from headmap import radial_map, fit_sphere, dir_of
D = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo2/'
def heads():
    ms = M('stand'); r = np.load(D + 'stand_rig.npz', allow_pickle=True); ls = np.array([str(x) for x in r['labels']])
    Ps = ms.P + np.array([0.0091, -0.023, -0.6231]); gs = np.array([l.startswith('gill') for l in ls]); Ts = ms.T[~gs[ms.T].any(1)]
    z = np.load('crawl_sym.npz', allow_pickle=True); Pc = z['P']; Tc = z['T']; src = z['src']; m, W, names, lab = load_old()
    a = src[:, 0].astype(int); b = src[:, 1].astype(int); u = src[:, 2]; labc = np.where(u < 0.5, lab[a], lab[b]); gc = np.array([l.startswith('gill') for l in labc]); Tc2 = Tc[~gc[Tc].any(1)]
    return dict(stand=(Ps, Ts, np.array([0.013, 1.348, 0.015])), crawl=(Pc, Tc2, np.array([0.0, 0.06, -0.30])))
if __name__ == '__main__':
    H = heads(); yaws = np.radians(np.arange(-90, 91, 6)); pitches = np.radians(np.arange(-70, 81, 6))
    for nm, (P, T, c0) in H.items():
        c = c0.copy()
        for it in range(3):
            r, Dd = radial_map(P, T, c, yaws, pitches); Q = (c + Dd * r[..., None]).reshape(-1, 3); YY, XX = np.meshgrid(pitches, yaws, indexing='ij')
            cone = (np.abs(XX) < np.radians(45)) & (YY > np.radians(-30)) & (YY < np.radians(40)) & np.isfinite(r); cs, Rs = fit_sphere(Q[cone.ravel()])
            res = np.linalg.norm(Q[cone.ravel()] - cs, axis=1) - Rs; print(f'{nm} it{it}: centre {c.round(3)} -> sphere {cs.round(3)} R {Rs:.3f}  resid rms {np.sqrt((res ** 2).mean()) * 1000:.1f} mm max {np.abs(res).max() * 1000:.1f}')
            c = cs
        # print the radial map relative to the sphere (mm), rows = pitch
        r, Dd = radial_map(P, T, c, yaws, pitches)
        print('   pitch \\ yaw', ' '.join(f'{int(round(np.degrees(y))):5d}' for y in yaws[::2]))
        for i in range(len(pitches) - 1, -1, -2):
            print(f'   {int(round(np.degrees(pitches[i]))):5d}     ', ' '.join(('  ---' if not np.isfinite(r[i, j]) else f'{(r[i, j] - Rs) * 1000:5.0f}') for j in range(0, len(yaws), 2)))
        np.save(f'headmap_{nm}.npy', dict(c=c, R=Rs, r=r, yaws=yaws, pitches=pitches), allow_pickle=True)
