# Quick looks at a raw mesh (viewer page fable4/view/index.html, served on 8767): a sheet of named views.
#   python3 -I viewsheet.py <mesh base name in fable4/view> <out.jpg> [mode tex|grey|wire] [views json]
import json, subprocess, sys, os
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'; HERE = os.path.dirname(os.path.abspath(__file__))
base, out = sys.argv[1], sys.argv[2]; mode = sys.argv[3] if len(sys.argv) > 3 else 'tex'
D = 3.4
views = json.loads(sys.argv[4]) if len(sys.argv) > 4 else [
    ['+x side', [D, 0, 0], [0, 0, 0]], ['-x side', [-D, 0, 0], [0, 0, 0]], ['+y top', [0, D, 0.001], [0, 0, 0]], ['-y bottom', [0, -D, 0.001], [0, 0, 0]],
    ['+z', [0, 0, D], [0, 0, 0]], ['-z', [0, 0, -D], [0, 0, 0]], ['3/4 (+x+y+z)', [2, 1.6, 2], [0, 0, 0]], ['3/4 (-x+y-z)', [-2, 1.6, -2], [0, 0, 0]]]
cells = [['v', f"V.mode('{mode}'); V.cam({json.dumps(p)}, {json.dumps(a)})", lab] for lab, p, a in views]
spec = {'out': out, 'W': 520, 'H': 520, 'ncol': 4, 'title': f'{base} ({mode})', 'pages': {'v': {'url': f'http://localhost:8767/fable4/view/index.html?m={base}', 'ready': 'window.ready', 'shot': 'screenshot'}}, 'cells': cells}
json.dump(spec, open(out + '.json', 'w')); subprocess.run(['python3', '-I', HERE + '/shoot.py', out + '.json'], check=True)
