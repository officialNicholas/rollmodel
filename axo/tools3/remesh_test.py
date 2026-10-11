import sys, time; sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo3')
import numpy as np
from remesh import remesh, quality, edges_of, compact
from mesh import mirror_map
from crawlbuild import load_old
from rig7crawl import face_cap
O = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo3/'
z = np.load(O + 'crawl_head.npz', allow_pickle=True); P = z['P'].copy(); T = z['T']; src = z['src']; Cc = z['Cc']; R = float(z['R'])
z0 = np.load(O + 'crawl_sym.npz', allow_pickle=True); mm = mirror_map(z0['P'])
P = (P + P[mm] * np.array([-1, 1, 1])) / 2; P[np.abs(z0['P'][:, 0]) < 1e-9, 0] = 0
P, wcap = face_cap(P, Cc, R)
m0, W0, names0, lab0 = load_old(); a = src[:, 0].astype(int); b = src[:, 1].astype(int); u = src[:, 2]; lab = np.where(u < 0.5, lab0[a], lab0[b])
L = P[:, 0] >= -1e-9; TL = T[L[T].all(1)]; Ph, Th, ex = compact(P, TL, {'lab': lab}); labh = ex['lab']
print('half', len(Ph), len(Th), 'quality before: p1', np.percentile(quality(Ph, Th), 1).round(3), 'median', np.median(quality(Ph, Th)).round(3))
SC = 1.15
isg = np.array([l.startswith('gill') for l in labh]); isd = np.array([l.startswith(('finger', 'toe')) and not l.startswith('toes') for l in labh]); isl = np.array([l.startswith(('arm', 'leg')) for l in labh])
Lf = np.where(isd, 0.016, np.where(isl, 0.022, 0.03)) / SC
# smooth the sizing over the mesh
from scipy.sparse import coo_matrix
E, *_ = edges_of(Th); n = len(Ph); A = coo_matrix((np.ones(2 * len(E)), (np.r_[E[:, 0], E[:, 1]], np.r_[E[:, 1], E[:, 0]])), shape=(n, n)).tocsr(); deg = np.asarray(A.sum(1)).ravel()
for _ in range(8): Lf = 0.5 * Lf + 0.5 * (A @ Lf) / np.maximum(deg, 1)
fr = isg.copy()
tip = Ph[:, 2].min(); fr |= (Ph[:, 2] < tip + 0.03)
for _ in range(1): fr = fr | (A @ fr.astype(float) > 0)
t0 = time.time()
Pr, Tr, labr = remesh(Ph, Th, Lf, frozen=fr, iters=5, labels=labh)
print('time', round(time.time() - t0, 1))
np.savez(O + 'remesh_test.npz', P=Pr, T=Tr, lab=labr)
from remesh import Surface
S_ = Surface(Ph, Th); q = S_.project(Pr); d = np.linalg.norm(q - Pr, axis=1)
print('new -> input: mean', d.mean().round(5), 'p99', np.percentile(d, 99).round(4), 'max', d.max().round(4))
S2 = Surface(Pr, Tr); q2 = S2.project(Ph); d2 = np.linalg.norm(q2 - Ph, axis=1)
print('input -> new: mean', d2.mean().round(5), 'p99', np.percentile(d2, 99).round(4), 'max', d2.max().round(4))
bi = np.argsort(-d2)[:12]
for i in bi: print('   ', Ph[i].round(3), d2[i].round(4), labh[i])
