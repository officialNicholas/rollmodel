import asyncio, json, sys
sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo2')
import numpy as np
from shot import *
from geo import M, D
W = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/axo2/'
which = sys.argv[1] if len(sys.argv) > 1 else 'crawl'; state = sys.argv[2] if len(sys.argv) > 2 else 'crawl'; settle = float(sys.argv[3]) if len(sys.argv) > 3 else 2.0; pre = sys.argv[4] if len(sys.argv) > 4 else None
async def main():
    async with async_playwright() as p:
        b, pg, errs = await open_page(p, 'http://localhost:8765/axo2/preview.html?manual', 300, 300)
        if pre: await pg.evaluate(f'axo.setState("{pre}"); axo.step(1/60, 90)')
        await pg.evaluate(f'axo.setState("{state}"); axo.step(1/60, {int(settle * 60)}); axo.showMesh("{which}")')
        sk = np.array(await pg.evaluate('axo.skinned()'), np.float32).reshape(-1, 3); await b.close()
    meta = json.load(open(W + f'axo_{which}.json')); names = [b_['name'] for b_ in meta['bones']]
    m = M(which); I = m.I0; r = np.load(D + f'{which}_rig.npz', allow_pickle=True); idx, w, labels = r['idx'], r['w'], r['labels']
    P0 = np.frombuffer(open(W + f'axo_{which}.bin', 'rb').read(), np.float32, meta['n'] * 3, meta['off'][0]).reshape(-1, 3)
    E = np.concatenate([I[:, [0, 1]], I[:, [1, 2]], I[:, [2, 0]]]); L0 = np.linalg.norm(P0[E[:, 0]] - P0[E[:, 1]], axis=1); L1 = np.linalg.norm(sk[E[:, 0]] - sk[E[:, 1]], axis=1)
    bad = np.where((L1 > 1.8 * L0) & (L0 > 0.004) & (L1 - L0 > 0.02))[0]; print('stretched edges', len(bad), 'of', len(E))
    verts = np.unique(E[bad]); print('vertices involved', len(verts))
    from collections import Counter; c = Counter(); cp = Counter()
    for e in bad:
        a_, b_ = E[e]; wa, wb = m.wid[a_], m.wid[b_]; ka = (str(labels[wa]), names[idx[wa, 0]]); kb = (str(labels[wb]), names[idx[wb, 0]]); cp[tuple(sorted([ka, kb]))] += 1
    print('torn pairs (label,dominant bone):'); [print('  ', n_, k_) for k_, n_ in cp.most_common(12)]
    for v in verts:
        wv = m.wid[v]; c[(str(labels[wv]), tuple(f'{names[idx[wv, k]]}:{w[wv, k]:.2f}' for k in range(4) if w[wv, k] > 0.02))] += 1
    for k_, n_ in c.most_common(25): print(n_, k_)
    # the two ends of the worst edges: where do they sit at rest and which bones
    o = np.argsort(-(L1 - L0))[:12]
    for e in o:
        a_, b_ = E[e]; wa, wb = m.wid[a_], m.wid[b_]
        print(f'edge rest {L0[e]:.3f} -> {L1[e]:.3f}: A {np.round(P0[a_], 2).tolist()} {labels[wa]} {[names[idx[wa,k]]+":%.2f"%w[wa,k] for k in range(4) if w[wa,k]>0.02]} | B {np.round(P0[b_], 2).tolist()} {labels[wb]} {[names[idx[wb,k]]+":%.2f"%w[wb,k] for k in range(4) if w[wb,k]>0.02]}')
asyncio.run(main())
