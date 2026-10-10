import numpy as np
D = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo2/'
s = np.load(D + 'stand_src.npz', allow_pickle=True); P, JN, WT, names = s['P'], s['JN'], s['WT'], list(s['names'])
W = np.zeros((len(P), len(names)))
for c in range(4): np.add.at(W, (np.arange(len(P)), JN[:, c]), WT[:, c])
dom = W.argmax(1)
for k, n in enumerate(names):
    sel = dom == k
    if sel.sum(): print(f'{n:28s} dominant {sel.sum():5d}  bbox {P[sel].min(0).round(2)} {P[sel].max(0).round(2)}  mean {P[sel].mean(0).round(2)}')
# joint world positions from rest TRS
T, Rq, par = s['T'], s['Rq'], s['par']
def qm(q):
    x, y, z, w = q; return np.array([[1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)], [2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)], [2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)]])
Wm = [None]*len(names)
for i in range(len(names)):
    L = np.eye(4); L[:3, :3] = qm(Rq[i]); L[:3, 3] = T[i]
    Wm[i] = L if par[i] < 0 else Wm[par[i]] @ L
pos = np.array([(0.01 * m[:3, 3]) for m in Wm])
print('joint positions (x0.01):'); [print(f'  {n:28s} {pos[i].round(3)}') for i, n in enumerate(names)]
# check inverse bind consistency: ibm should equal inverse(0.01*world)
ibm = s['ibm']; Sm = np.diag([0.01, 0.01, 0.01, 1])
err = max(np.abs(np.linalg.inv(Sm @ Wm[i]) - ibm[i]).max() for i in range(len(names))); print('ibm vs rest world inverse max err', err)
