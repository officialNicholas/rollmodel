import numpy as np, sys
sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo')
from geo import M
for nm, core in (('stand', (0.2, -0.3, 0.2)), ('crawl', (-0.15, -0.22, 0.2))):
    m = M(nm); c = m.near(core); d = m.geo(c)
    T = m.tips(d, np.ones(len(m.P), bool), r=0.045, k=60)
    print('==', nm, 'core', m.P[c].round(2), 'tips', len(T))
    for v in T[:60]: print('  ', m.P[v].round(2), 'd', round(float(d[v]), 2))
