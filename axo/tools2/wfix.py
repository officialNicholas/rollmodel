# weight fixer: measure edge stretch over sampled frames of given states for one mesh, smooth the weights of the vertices of visibly stretched
# edges (ratio > 1.8 and growth > 1.5 cm) with their 1-ring, re-export the skin in place, iterate
import asyncio, json, sys, os
sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo2')
import numpy as np
from shot import *
from geo import M, D
from rigcore import finalize
W_ = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/axo2/'
nm = sys.argv[1]; states = sys.argv[2].split(','); iters = int(sys.argv[3]) if len(sys.argv) > 3 else 3
meta = json.load(open(W_ + f'axo_{nm}.json')); m = M(nm); r = np.load(D + f'{nm}_rig.npz', allow_pickle=True); names = list(r['names']); nb = len(names)
P0 = np.frombuffer(open(W_ + f'axo_{nm}.bin', 'rb').read(), np.float32, meta['n'] * 3, meta['off'][0]).reshape(-1, 3)
E = np.unique(np.sort(np.concatenate([m.I0[:, [0, 1]], m.I0[:, [1, 2]], m.I0[:, [2, 0]]]), axis=1), axis=0); L0 = np.linalg.norm(P0[E[:, 0]] - P0[E[:, 1]], axis=1)
nbr = m.G.tolil().rows
def dense():
    Wd = np.zeros((m.n, nb)); idx, w = r['idx'], r['w']
    for c in range(4): np.add.at(Wd, (np.arange(m.n), idx[:, c]), w[:, c])
    return Wd
def write(Wd):
    idx, w = finalize(Wd); iu = idx[m.wid]; wu = w[m.wid]; wq = np.round(wu * 255).astype(np.int32); wq[:, 0] += 255 - wq.sum(1); wq = np.clip(wq, 0, 255).astype(np.uint8)
    buf = bytearray(open(W_ + f'axo_{nm}.bin', 'rb').read()); o = meta['off']; buf[o[3]:o[3] + m.n * 0 + len(iu) * 4] = iu.astype(np.uint8).tobytes(); buf[o[4]:o[4] + len(wq) * 4] = wq.tobytes(); open(W_ + f'axo_{nm}.bin', 'wb').write(buf)
    np.savez(D + f'{nm}_rig.npz', idx=idx, w=w, labels=r['labels'], names=r['names'])
async def measure():
    worst = np.zeros(len(E))
    async with async_playwright() as p:
        b, pg, errs = await open_page(p, 'http://localhost:8765/axo2/preview.html?manual', 300, 300)
        for st in states:
            pre, s_, dur = (st.split('>') + ['1.5'])[:3] if '>' in st else (None, st, '2.5')
            if pre: await pg.evaluate(f'axo.setState("{pre}"); axo.step(1/60, 90)')
            await pg.evaluate(f'axo.setState("{s_}")'); n = int(float(dur) * 60)
            for f in range(0, n, 6):
                await pg.evaluate(f'axo.step(1/60,6); axo.showMesh("{nm}")'); sk = np.array(await pg.evaluate('axo.skinned()'), np.float32).reshape(-1, 3)
                L1 = np.linalg.norm(sk[E[:, 0]] - sk[E[:, 1]], axis=1); worst = np.maximum(worst, L1 / np.maximum(L0, 1e-4) * ((L1 - L0) > 0.03))
        await b.close()
    return worst
for it in range(iters):
    worst = asyncio.run(measure()); bad = np.where(worst > 2.5)[0]; vs = np.unique(m.wid[E[bad].ravel()])
    print(f'iter {it}: {len(bad)} visibly stretched edges, max ratio {worst.max():.2f}, {len(vs)} welded vertices')
    if len(bad) == 0: break
    Wd = dense()
    for k in range(3):
        new = Wd.copy()
        for v in vs: ring = [v] + list(nbr[v]); new[v] = Wd[ring].mean(0)
        Wd = new
    write(Wd); r = np.load(D + f'{nm}_rig.npz', allow_pickle=True)
