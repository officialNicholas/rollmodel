import asyncio, sys
sys.path.insert(0, '.')
from rsheet import render
name = sys.argv[1]; d = sys.argv[2]; mode = sys.argv[3] if len(sys.argv) > 3 else 'flat'; tz = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0; ty = float(sys.argv[5]) if len(sys.argv) > 5 else 0.05
cells = []
for yaw, pitch, nm in ((0, 1.55, 'top'), (0, -1.55, 'bottom'), (0.0, 0.05, 'front'), (1.57, 0.05, 'side +x'), (-1.57, 0.05, 'side -x'), (0.7, 0.35, '3/4 +x'), (-0.7, 0.35, '3/4 -x'), (3.14, 0.3, 'back')):
    cells.append((f"(async()=>{{await V.show('{name}','{mode}',{{joints:false}}); V.view({yaw},{pitch},1.9,0,{ty},{tz},30);}})()", f'{name} {nm}'))
asyncio.run(render(f'http://localhost:8811/view.html?d={d}', cells, 4, 460, 460, f'{name}_head.jpg', shot_js='V.shot()', size_js='V.size(460,460)'))
