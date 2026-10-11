# automated stretch QA: step every state and transition, sample skinned positions, max edge stretch (posed / rest length) per body region
import asyncio, json, sys, os
sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo2')
import numpy as np
from shot import *
from geo import M, D
W = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/axo2/'
URL = os.environ.get('URL', 'http://localhost:8765/axo2/preview.html?manual')
REGION = lambda l: 'gills' if l.startswith('gill') else 'fingers' if l.startswith('finger') else 'toes' if l.startswith('toe') else 'tail' if l == 'tail' else 'head' if l == 'head' else 'arms' if l.startswith('arm') else 'legs' if l.startswith('leg') else 'body'
def mesh_data(nm):
    meta = json.load(open(W + f'axo_{nm}.json')); m = M(nm); r = np.load(D + f'{nm}_rig.npz', allow_pickle=True); labels = np.array([REGION(str(x)) for x in r['labels']])[m.wid]; labels = np.concatenate([labels, np.full(meta['n'] - len(labels), 'web')])
    P0 = np.frombuffer(open(W + f'axo_{nm}.bin', 'rb').read(), np.float32, meta['n'] * 3, meta['off'][0]).reshape(-1, 3)
    E = np.unique(np.sort(np.concatenate([m.I0[:, [0, 1]], m.I0[:, [1, 2]], m.I0[:, [2, 0]]]), axis=1), axis=0); L0 = np.linalg.norm(P0[E[:, 0]] - P0[E[:, 1]], axis=1)
    return dict(E=E, L0=np.maximum(L0, 1e-4), labels=labels, P0=P0, n=meta['n'], wid=m.wid)
SCHED = [('stand', 3.0, 10), ('crawl', 3.0, 14), ('power', 1.5, 4), ('victory', 1.5, 8), ('pound', 1.0, 3), ('jetpack', 1.5, 4), ('crouch', 0.6, 2), ('armsfwd', 0.3, 1), ('armsside', 0.3, 1), ('armsup', 0.3, 1),
         ('crawl', 0.2, 1), ('stand', 1.2, 16), ('crawl', 1.2, 16), ('stand', 0.3, 1)]   # last four: the transitions (crawl->stand, stand->crawl)
async def main():
    md = {nm: mesh_data(nm) for nm in ('stand', 'crawl')}; worst = {nm: {} for nm in md}; vworst = {nm: np.zeros(md[nm]['n']) for nm in md}; per = []
    async with async_playwright() as p:
        b, pg, errs = await open_page(p, URL, 300, 300)
        for st, dur, ns in SCHED:
            await pg.evaluate(f'axo.setState("{st}")'); n = int(dur * 60); step = max(1, n // ns)
            for f in range(0, n, step):
                await pg.evaluate(f'axo.step(1/60,{step})')
                for which in ('cur', 'oth'):
                    info = json.loads(await pg.evaluate('JSON.stringify({m: axo.A.mesh, f: axo.A.fade, s: axo.A.state})'))
                    if which == 'oth' and info['f'] >= 1: continue
                    nm = info['m'] if which == 'cur' else ('crawl' if info['m'] == 'stand' else 'stand')
                    if which == 'oth': await pg.evaluate(f'axo.showMesh("{nm}")')
                    sk = np.array(await pg.evaluate('axo.skinned()'), np.float32).reshape(-1, 3)
                    if which == 'oth': await pg.evaluate(f'axo.showMesh("{info["m"]}"); axo.A.fade={info["f"]}')
                    d = md[nm]; L1 = np.linalg.norm(sk[d['E'][:, 0]] - sk[d['E'][:, 1]], axis=1); r = L1 / d['L0']
                    r[d['L0'] < 0.004] = 1   # ignore sub-4mm edges (noise)
                    r = np.where((L1 - d['L0']) > 0.02, r, np.minimum(r, 1.0))   # only edges that grew by more than 2 cm count as visible stretch
                    vr = np.zeros(d['n']); np.maximum.at(vr, d['E'][:, 0], r); np.maximum.at(vr, d['E'][:, 1], r); vworst[nm] = np.maximum(vworst[nm], vr)
                    for reg in np.unique(d['labels']):
                        mx = float(vr[d['labels'] == reg].max()); k = (nm, reg); worst[nm][reg] = max(worst[nm].get(reg, 0), mx)
                    per.append((info['s'], nm, round(float(r.max()), 2)))
        await b.close()
    print('max edge stretch per region (posed / rest):')
    for nm in worst: print(' ', nm, {k: round(v, 2) for k, v in sorted(worst[nm].items())})
    bad = [(s, n, r) for s, n, r in per if r > 1.8]; print('frames with any edge > 1.8x:', len(bad), 'of', len(per), bad[:12])
    np.savez(D + 'qa_vworst.npz', stand=vworst['stand'], crawl=vworst['crawl'])
    print('errors', errs[:3])
asyncio.run(main())
