# Lab probes: cells on the new lab only, for close looks while fixing things.
#   python3 -I probe.py <name> '<json cells: [[label, js], ...]>' [W H ncol] [page]
import json, sys, os, subprocess
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'; HERE = os.path.dirname(os.path.abspath(__file__))
name, cells = sys.argv[1], json.loads(sys.argv[2]); W = int(sys.argv[3]) if len(sys.argv) > 3 else 520; H = int(sys.argv[4]) if len(sys.argv) > 4 else 440; ncol = int(sys.argv[5]) if len(sys.argv) > 5 else 3
pages = (sys.argv[6] if len(sys.argv) > 6 else 'lab_new').split(',')
spec = {'out': f'{S}/fable4/shots/{name}.jpg', 'W': W, 'H': H, 'ncol': ncol, 'title': name, 'pages': {p: {'url': f'http://localhost:8767/fable4/{p}/index.html', 'ready': 'window.LAB && LAB.ready && LAB.I.ax.C.mesh.material.map && LAB.I.ax.C.mesh.material.map.userData.ready', 'shot': 'screenshot', 'init': "LAB.set('idle'); LAB.step(120)"} for p in pages},
        'cells': [[c[2] if len(c) > 2 else pages[0], c[1], c[0]] for c in cells]}
json.dump(spec, open(f'{S}/fable4/shots/{name}.json', 'w')); subprocess.run(['python3', '-I', HERE + '/shoot.py', f'{S}/fable4/shots/{name}.json'], check=True, env=dict(os.environ, PLAYWRIGHT_BROWSERS_PATH='/opt/pw-browsers'))
