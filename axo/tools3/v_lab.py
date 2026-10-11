import asyncio, sys
sys.path.insert(0, '.')
from rsheet import render
cells = []
for yaw, pitch, nm in ((0, 1.55, 'top (+x right, head down)'), (0, -1.55, 'bottom'), (1.57, 0.02, 'side +x (L)'), (-1.57, 0.02, 'side -x (R)')):
    cells.append((f"(async()=>{{await V.show('straight_lab','bones',{{joints:false}}); V.view({yaw},{pitch},3.4,0,-0.1,-0.9,32);}})()", nm))
asyncio.run(render('http://localhost:8811/view.html?d=/rb/', cells, 4, 600, 600, 'straight_lab.jpg', shot_js='V.shot()', size_js='V.size(600,600)'))
