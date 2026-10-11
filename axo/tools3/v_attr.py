# per-vertex attribute views of both v7 meshes (vertex colours), several cameras per attribute
import sys, asyncio, json; sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo3')
import numpy as np
from straighten import write_view
from rsheet import render
O = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo3/'
def heat(x):
    x = np.clip(x, 0, 1)[:, None]; a = np.array([0.1, 0.1, 0.45]); b = np.array([0.95, 0.3, 0.2]); c = np.array([1.0, 0.95, 0.6])
    return np.where(x < 0.5, a + (b - a) * (x * 2), b + (c - b) * (x * 2 - 1))
def write(nm, attrs):
    d = np.load(O + f'{nm}7_extras.npz', allow_pickle=True); P, T = d['P'], d['T']
    class MM: pass
    mm = MM(); mm.T = T; write_view(O + 'www/rb/', f'x_{nm}', mm, P)
    for k, f in attrs.items():
        col = f(d); open(O + f'www/rb/x_{nm}.{k}', 'wb').write(np.clip(np.round(col * 255), 0, 255).astype(np.uint8).tobytes())
ATTR = {'belly': lambda d: heat(d['jelly'][:, 0]), 'thin': lambda d: heat(d['jelly'][:, 2]), 'head': lambda d: heat(d['jelly'][:, 3]), 'ao': lambda d: heat(d['fill'][:, 2]),
        'edge': lambda d: heat(d['fill'][:, 3]), 'finh': lambda d: heat(d['mat'][:, 0]), 'gill': lambda d: heat(d['mat'][:, 1]), 'wrinkle': lambda d: heat(d['mat'][:, 2]),
        'spots': lambda d: heat(d['mat'][:, 3]), 'cpos': lambda d: np.clip((d['cp'] - np.array([-0.65, 0, -1.75])) / np.array([1.3, 1.8, 2.3]), 0, 1),
        'along': lambda d: heat((np.sin(d['along'] * 2 * np.pi / 0.05) + 1) / 2)}
if __name__ == '__main__':
    keys = sys.argv[1].split(','); out = sys.argv[2]
    for nm in ('stand', 'crawl'): write(nm, {k: ATTR[k] for k in keys})
    cams = {'stand': [((0, 0.0), (0, 0.9, -0.2), 4.4), ((2.5, 0.25), (0, 0.8, -0.4), 4.6), ((0.9, -0.5), (0, 0.6, 0), 4.2)],
            'crawl': [((0.6, 0.4), (0, 0.3, -0.6), 4.8), ((2.6, 0.55), (0, 0.3, -0.6), 4.8), ((1.2, -0.5), (0, 0.2, -0.5), 4.4)]}
    cells = []
    for k in keys:
        for nm in ('stand', 'crawl'):
            for (yaw, pitch), t, dd in cams[nm]:
                cells.append((f"(async()=>{{await V.show('x_{nm}','vcol',{{joints:false, col:'{k}'}}); V.view({yaw},{pitch},{dd},{t[0]},{t[1]},{t[2]},30);}})()", f'{k} {nm}'))
    asyncio.run(render('http://localhost:8811/view.html?d=/rb/', cells, 6, 330, 330, out, shot_js='V.shot()', size_js='V.size(330,330)'))
