# frame-by-frame close-up of one joint region of the drawn mesh: url, out, state, settle, nframes, step, joint name, camera (yaw, pitch, dist, off)
import asyncio, sys, json
sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo3')
from rsheet import render
def run(url, out, state, settle, n, step, joint, cams, W=340, H=340, pre='', ncol=None, wire=False):
    cells = []
    for ci, (yaw, pitch, dist, off) in enumerate(cams):
        for i in range(n):
            js = (f"axo.setLook(0,0); {pre}; axo.setState('{state}'); axo.step(1/60,{settle});" if i == 0 else f"axo.step(1/60,{step});")
            js += f"(()=>{{const p=axo.joint(axo.A.mesh,'{joint}'); axo.view({yaw},{pitch},{dist},p[1]+{off[1]},p[0]+{off[0]},p[2]+{off[2]},30);}})();"
            cells.append((js, f'{state} {joint} +{i * step}f cam{ci}'))
    return asyncio.run(render(url, cells, ncol or n, W, H, out, size_js=f'axo.size({W},{H})'))
if __name__ == '__main__':
    a = json.loads(sys.argv[1]); run(a['url'], a['out'], a['state'], a['settle'], a['n'], a['step'], a['joint'], a['cams'], a.get('W', 340), a.get('H', 340), a.get('pre', ''), a.get('ncol'))
