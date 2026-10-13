# Stage 2 (after repose.py): the final skeleton and the skin weights on the reposed model, in the game's frame. Writes
# fable4/work/rig.npz (positions, the welded mesh, the bones, weights) for build.py.
#   python3 -I stage_rig.py [--views]
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, json, time
import finalrig as fr, weights as wt, meshkit as mk
S = fr.S; MIR = np.array([-1.0, 1, 1])
def run():
    z = np.load(S + '/fable4/work/reposed.npz'); JT = {k: np.array(v) for k, v in json.loads(str(z['JT'])).items()}; dig = json.load(open(S + '/fable4/work/digits_rep.json'))
    Tw = z['Tw']; R0 = fr.Rig(JT, dig, z['Pw']); ears = fr.find_ears(R0.P, Tw, R0.J)
    E2 = {k: 0.5 * (ears['L'][k] + ears['R'][k] * MIR) for k in ('hinge', 'mid', 'tip')}
    ears2 = {'L': dict(ears['L'], **E2), 'R': dict(ears['R'], **{k: v * MIR for k, v in E2.items()})}
    R = fr.Rig(JT, dig, z['Pw'], ears=ears2); Pw = R.P
    t0 = time.time(); W, names, near = wt.compute(R, Pw, Tw, ears=ears2); print(f'  weights: bone heat {time.time() - t0:.1f}s')
    return R, Pw, Tw, z, W, names, ears2
if __name__ == '__main__':
    R, Pw, Tw, z, W, names, ears = run()
    np.savez(S + '/fable4/work/rig.npz', Pw=Pw, Tw=Tw, W=W, names=json.dumps(names), wid=z['wid'], rep=z['rep'], UV=z['UV'], T=z['T'],
             B=json.dumps({k: [a.tolist(), b.tolist()] for k, (a, b) in R.B.items()}), J=json.dumps({k: v.tolist() for k, v in R.J.items()}),
             ears=json.dumps({s: {'verts': ears[s]['verts'].tolist(), 'd': ears[s]['d'].tolist(), 'droot': float(ears[s]['droot'])} for s in 'LR'}))
    print('  rig.npz written')
