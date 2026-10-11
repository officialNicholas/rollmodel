import asyncio, sys
sys.path.insert(0, '.')
from rsheet import render
# usage: v_close.py name dir tx ty tz dist out [mode]
name, d = sys.argv[1], sys.argv[2]; tx, ty, tz, dist = map(float, sys.argv[3:7]); out = sys.argv[7]; mode = sys.argv[8] if len(sys.argv) > 8 else 'flat'
views = [(0, 1.3, 'top-ish'), (3.14, 0.6, 'back high'), (2.4, 0.4, 'back 3/4'), (1.57, 0.3, 'side')]
cells = [(f"(async()=>{{await V.show('{name}','{mode}',{{joints:false}}); V.view({y},{p},{dist},{tx},{ty},{tz},30);}})()", f'{name} {nm}') for y, p, nm in views]
asyncio.run(render(f'http://localhost:8811/view.html?d={d}', cells, 4, 460, 460, out, shot_js='V.shot()', size_js='V.size(460,460)'))
