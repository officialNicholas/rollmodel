import json
cells = []
body = [('top', "rv.view(0,1.5,3.2,0,-0.2,0,30)"), ('side+x', "rv.view(1.57,0.15,3.2,0,-0.2,0,30)"), ('front', "rv.view(0,0.2,3.2,0,-0.2,0,30)"), ('3/4', "rv.view(0.8,0.5,3.2,0,-0.2,0,30)")]
for lab, js in body: cells.append([f'crawl {lab} bones', f"rv.reset(); rv.mode('bones'); rv.skel(true); {js}"])
spots = {'handL': (-0.1, -0.39, 0.75), 'handR': (-0.78, -0.39, 0.6), 'footL': (0.37, -0.4, 0.12), 'footR': (-0.25, -0.4, -0.55), 'gillsL': (-0.1, 0.12, 0.5), 'gillsR': (-0.6, 0.12, 0.5)}
for sp, c in spots.items():
    for yaw, pitch, vl in [(0.0, 1.4, 'top'), (0.0, 0.2, 'front'), (1.57, 0.3, 'side+x'), (-1.57, 0.3, 'side-x')]:
        cells.append([f'{sp} {vl}', f"rv.reset(); rv.mode('bones'); rv.skel(true); rv.view({yaw},{pitch},{0.6 if 'gill' not in sp else 1.0},{c[0]},{c[1]},{c[2]},30)"])
json.dump({'mesh': 'axo_crawl', 'out': 'rv_crawl.jpg', 'cells': cells, 'ncol': 4, 'W': 480, 'H': 480}, open('/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo2/spec_crawl.json', 'w'))
