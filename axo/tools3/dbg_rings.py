import sys, json; sys.path.insert(0, '.')
import numpy as np, asyncio
import rig7crawl as R
from mesh import Mesh
from dbgview import write_cats
from rsheet import render
z = np.load(R.O + 'crawl7_geo.npz', allow_pickle=True); P, T, lab = z['P'], z['T'], z['lab']
m = Mesh(P, T)
cats = np.zeros(len(P), int); bones = []
for kind in ('leg', 'arm'):
    dig = np.array([l.startswith(('finger' if kind == 'arm' else 'toe')) and not l.startswith('toes') and l.endswith('.L') for l in lab])
    limb = lab == f'{kind}.L'; mask = limb | dig; d = m.geo(np.where(dig)[0], limit=1.2, mask=mask)
    sel = limb & np.isfinite(d); cats[sel] = 1 + (np.floor(d[sel] / 0.03).astype(int) % 6)
    L = R.limb_line(m, lab, 'L', kind)
    prev = None
    for i, p in enumerate(L['pts']):
        if i % 2: continue
        nm = f'{kind}{i}.L'; bones.append({'name': nm, 'pos': p.round(4).tolist(), 'end': (p + [0, 0.01, 0]).round(4).tolist(), 'q': [0, 0, 0, 1], 'parent': prev}); prev = nm
cats[dig] = 7
write_cats(R.O + 'www/rb/', 'rings', P, T, cats, [f'c{i}' for i in range(8)])
meta = json.load(open(R.O + 'www/rb/rings.json')); meta['bones'] = bones; json.dump(meta, open(R.O + 'www/rb/rings.json', 'w'))
cells = []
for yaw, pitch, nm, tgt in ((0, 1.55, 'leg top', (0.2, 0.12, -0.8)), (0, -1.5, 'leg bottom', (0.2, 0.12, -0.8)), (1.57, 0.05, 'leg side', (0.2, 0.12, -0.8)), (2.4, 0.4, 'leg 3/4 back', (0.2, 0.12, -0.8)),
                            (0, 1.55, 'arm top', (0.33, 0.15, -0.05)), (0, -1.5, 'arm bottom', (0.33, 0.15, -0.05)), (1.57, 0.05, 'arm side', (0.33, 0.15, -0.05)), (0.7, 0.3, 'arm 3/4 front', (0.33, 0.15, -0.05))):
    cells.append((f"(async()=>{{await V.show('rings','bones',{{joints:true, jr:0.006}}); V.view({yaw},{pitch},0.95,{tgt[1]},{tgt[0]},{tgt[2]},30);}})()", nm))
asyncio.run(render('http://localhost:8811/view.html?d=/rb/', cells, 4, 480, 480, R.O + 'dbg_rings.jpg', shot_js='V.shot()', size_js='V.size(480,480)'))
