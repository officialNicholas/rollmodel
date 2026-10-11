# render debug meshes in view.html (vertex colours)
import asyncio, sys, json
sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo3')
from rsheet import render
def run(out, cells, W=480, H=420, ncol=4, d='/dbg/'):
    url = f'http://localhost:8811/view.html?d={d}'
    cl = [(f"(async () => {{ await V.show('{nm}', '{mode}', {{joints: false}}); V.view({cam[0]},{cam[1]},{cam[2]},{cam[3]},{cam[4]},{cam[5]},{cam[6] if len(cam) > 6 else 30}); return 1; }})()", lab) for nm, mode, cam, lab in cells]
    return asyncio.run(render(url, cl, ncol, W, H, out, shot_js='V.shot()', size_js=f'V.size({W},{H})'))
if __name__ == '__main__': a = json.loads(sys.argv[1]); run(a['out'], a['cells'], a.get('W', 480), a.get('H', 420), a.get('ncol', 4), a.get('d', '/dbg/'))
