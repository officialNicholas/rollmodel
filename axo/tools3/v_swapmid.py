# the swap's midpoint: the same moment rendered with only the stand mesh, only the crawl mesh, and the real dither mix, from several cameras
import asyncio, sys, json
sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo3')
from rsheet import render
def run(url, out, frames, cams, W=420, H=380, kind='crawl'):
    cells = []
    first = True
    for cam in cams:
        for mode in ('stand', 'crawl', 'mix'):
            pre = (f"axo.setLook(0,0); axo.setState('{'stand' if kind == 'crawl' else 'crawl'}'); axo.step(1/60,90); axo.setState('{kind}'); axo.step(1/60,{frames});") if first else ''
            first = False
            vis = {'stand': "axo.S.mesh.visible = true; axo.C.mesh.visible = false; axo.look.meshU.stand.uFadeK.value = 1;",
                   'crawl': "axo.S.mesh.visible = false; axo.C.mesh.visible = true; axo.look.meshU.crawl.uFadeK.value = 1;",
                   'mix': "axo.S.mesh.visible = true; axo.C.mesh.visible = true; axo.look.setSwap('crawl','stand',0.5);"}[mode]
            js = pre + vis + f"axo.view({cam[0]},{cam[1]},{cam[2]},{cam[3]},{cam[4]},{cam[5]},30);"
            cells.append((js, f'{mode} only' if mode != 'mix' else 'dither 50/50'))
    return asyncio.run(render(url, cells, 3, W, H, out, size_js=f'axo.size({W},{H})'))
if __name__ == '__main__':
    a = json.loads(sys.argv[1]); run(a['url'], a['out'], a['frames'], a['cams'], a.get('W', 420), a.get('H', 380), a.get('kind', 'crawl'))
