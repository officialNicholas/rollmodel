import json, sys
mesh = sys.argv[1] if len(sys.argv) > 1 else 'axo_stand'
spots = {'handL': ((0.5, 0.63, 0.81), 0.55), 'handR': ((-0.5, 0.62, 0.72), 0.55), 'footL': ((0.3, 0.07, 0.73), 0.5), 'footR': ((-0.28, 0.07, 0.68), 0.5)}
views = [(0.0, 1.4, 'top'), (0.0, -1.4, 'below'), (0.0, 0.1, 'front'), (1.57, 0.1, 'side+x'), (-1.57, 0.1, 'side-x'), (3.1, 0.1, 'back')]
cells = []
for sp, (c, dist) in spots.items():
    for yaw, pitch, vl in views:
        cells.append([f'{sp} {vl} bones', f"rv.reset(); rv.mode('bones'); rv.skel(true); rv.view({yaw},{pitch},{dist},{c[0]},{c[1]},{c[2]},30)"])
json.dump({'mesh': mesh, 'out': 'rv_hands.jpg', 'cells': cells, 'ncol': 6, 'W': 420, 'H': 420}, open('/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo2/spec_hands.json', 'w'))
