import asyncio, sys
sys.path.insert(0, '.')
from rsheet import render
name = sys.argv[1] if len(sys.argv) > 1 else 'straight'; d = sys.argv[2] if len(sys.argv) > 2 else '/rb/'
cells = []
for yaw, pitch, nm in ((0, 1.55, 'top'), (0, -1.55, 'bottom'), (1.57, 0.02, 'side +x (L)'), (-1.57, 0.02, 'side -x (R)'), (0.0, 0.05, 'front'), (3.14, 0.1, 'back'), (0.7, 0.4, '3/4 L'), (-0.7, 0.4, '3/4 R')):
    cells.append((f"(async()=>{{await V.show('{name}','flat',{{joints:false}}); V.view({yaw},{pitch},3.6,0,-0.1,-1.0,30);}})()", f'{name} {nm}'))
asyncio.run(render(f'http://localhost:8811/view.html?d={d}', cells, 4, 520, 520, f'{name}_view.jpg', shot_js='V.shot()', size_js='V.size(520,520)'))
