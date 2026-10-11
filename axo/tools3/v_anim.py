# animated preview sheet: url, state, settle steps, then capture times (in frames) x cameras (yaw, pitch, dist, ty, tx, tz)
import asyncio, sys, json
sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo3')
from rsheet import render
def sheet(url, out, state, settle, frames, cams, W=420, H=420, pre=''):
    cells = []; first = True
    for ci, cam in enumerate(cams):
        last = 0
        for fi, f in enumerate(frames):
            js = ''
            if fi == 0: js += f"axo.setLook(0,0); {pre}; axo.setState('{state}'); axo.step(1/60,{settle});"
            if f - last > 0: js += f"axo.step(1/60,{f - last});"
            last = f; js += f"axo.view({cam[0]},{cam[1]},{cam[2]},{cam[3]},{cam[4]},{cam[5]},{cam[6] if len(cam) > 6 else 30});"
            cells.append((js, f'{state} f{f} cam{ci}'))
    return asyncio.run(render(url, cells, len(frames), W, H, out, size_js=f'axo.size({W},{H})'))
if __name__ == '__main__':
    a = json.loads(sys.argv[1]); sheet(a['url'], a['out'], a['state'], a['settle'], a['frames'], a['cams'], a.get('W', 420), a.get('H', 420), a.get('pre', ''))
