import sys; sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo2')
import numpy as np, json
from geo import M, D
def unit(v): v = np.asarray(v, float); return v / np.linalg.norm(v)
out = {}
JJ = {'stand': {'handL': ((0.331, 0.87, 0.666), (0.478, 0.705, 0.766)), 'handR': ((-0.316, 0.859, 0.609), (-0.459, 0.69, 0.682)), 'footL': ((0.248, 0.223, 0.571), (0.23, 0.055, 0.639)), 'footR': ((-0.2, 0.244, 0.56), (-0.193, 0.067, 0.603))},
      'crawl': {'handL': ((-0.02, -0.3, 0.56), (-0.03, -0.37, 0.66)), 'handR': ((-0.58, -0.3, 0.45), (-0.7, -0.37, 0.55)), 'footL': ((0.24, -0.32, 0.02), (0.32, -0.38, 0.08)), 'footR': ((-0.18, -0.32, -0.38), (-0.26, -0.38, -0.46))}}
for nm, J in JJ.items():
    m = M(nm)
    for k, (el, wr) in J.items():
        wr = np.asarray(wr); fwd = unit(np.asarray(wr) - el)
        if k.startswith('foot') and nm == 'stand': fwd = unit([fwd[0] * 0.3, -0.2, 1.0])   # feet point forward (+z), ankle is above
        half = ((m.P - wr) @ fwd) > 0.0
        v = m.near(wr); d = m.geo(v, limit=0.5, mask=half); t = m.tips(d, d > 0.06, r=0.03, k=8)
        print(nm, k, 'wrist', m.P[v].round(3).tolist(), 'tips', [(round(float(d[x]), 3), m.P[x].round(3).tolist()) for x in t])
        out[nm + '_' + k] = {'wrist': m.P[v].tolist(), 'tips': [m.P[x].tolist() for x in t], 'd': [float(d[x]) for x in t]}
json.dump(out, open(D + 'tips.json', 'w'))
