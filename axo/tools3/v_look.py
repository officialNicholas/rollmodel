# look check: still frames of the stand and the crawl (rest-ish poses) from several cameras, optionally with a pre-js (colour, eyes...)
import asyncio, sys, json
sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo3')
from rsheet import render
def run(url, out, cells, W=420, H=420, ncol=4, pre=''):
    cl = []
    for st, settle, cam, lab in cells:
        js = f"axo.setLook(0,0); {pre}; axo.setState('{st}'); axo.step(1/60,{settle}); axo.view({cam[0]},{cam[1]},{cam[2]},{cam[3]},{cam[4]},{cam[5]},{cam[6] if len(cam) > 6 else 30});"
        cl.append((js, lab))
    return asyncio.run(render(url, cl, ncol, W, H, out, size_js=f'axo.size({W},{H})'))
if __name__ == '__main__':
    a = json.loads(sys.argv[1]); run(a['url'], a['out'], a['cells'], a.get('W', 420), a.get('H', 420), a.get('ncol', 4), a.get('pre', ''))
