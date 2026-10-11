import asyncio, sys
sys.path.insert(0, '.')
from rsheet import render
# raw sculpt joint positions (exported crawl bind): L hind foot ~(0.13,0.08,-0.12), R hind foot (-0.45,0.04,-0.65), L hand (-0.31,0.06,0.68), R hand (-1.05,0.05,0.42)
tg = {'hindL': (0.0, 0.1, -0.2), 'hindR': (-0.35, 0.1, -0.5), 'armL': (-0.3, 0.15, 0.55), 'armR': (-0.85, 0.15, 0.4)}
cells = []
for k, (x, y, z) in tg.items():
    for yaw, pitch, nm in ((0, 1.55, 'top'), (0, -1.55, 'bottom'), (1.57, 0.1, 'side +x'), (-1.57, 0.1, 'side -x'), (0.0, 0.1, 'front'), (3.14, 0.1, 'back')):
        cells.append((f"(async()=>{{await V.show('axo_crawl','flat',{{flat:false}}); V.view({yaw},{pitch},1.5,{x},{y},{z},30);}})()", f'{k} {nm}'))
asyncio.run(render('http://localhost:8811/view.html?d=/v6/', cells, 6, 360, 360, 'crawl_limbs.jpg', shot_js='V.shot()', size_js='V.size(360,360)'))
