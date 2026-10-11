import asyncio, sys
sys.path.insert(0, '.')
from rsheet import render
cells = []
for mode, lab in (('flat', 'flat'), ('bones', 'bones')):
    for yaw, pitch, nm in ((0, 1.55, 'top'), (0, -1.55, 'bottom'), (1.57, 0.02, 'side L(+x)'), (-1.57, 0.02, 'side R(-x)')):
        cells.append((f"(async()=>{{await V.show('axo_crawl','{mode}'); V.view({yaw},{pitch},4.6,-0.25,0.15,-0.25,30);}})()", f'crawl bind {lab} {nm}'))
asyncio.run(render('http://localhost:8811/view.html?d=/v6/', cells, 4, 600, 600, 'crawl_raw.jpg', shot_js='V.shot()', size_js='V.size(600,600)'))
