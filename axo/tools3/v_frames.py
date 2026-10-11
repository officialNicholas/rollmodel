# specific frames of one state from specific cameras (each cell: frame offset after settle, camera yaw/pitch/dist, target joint + offset)
import asyncio, sys, json
sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo3')
from rsheet import render
def run(url, out, state, settle, cells_spec, W=600, H=600, ncol=3, pre=''):
    cells = []; last = None
    for (f, yaw, pitch, dist, joint, off, lab) in cells_spec:
        js = f"axo.setLook(0,0); {pre}; axo.setState('{state}'); axo.step(1/60,{settle}); axo.step(1/60,{f});" if (last is None or f < last) else f"axo.step(1/60,{f - last});"
        last = f
        js += f"(()=>{{const p=axo.joint(axo.A.mesh,'{joint}'); axo.view({yaw},{pitch},{dist},p[1]+{off[1]},p[0]+{off[0]},p[2]+{off[2]},30);}})();"
        cells.append((js, lab or f'{state} +{f}f'))
    # cells must be in increasing frame order per state reset; reset when frame goes back
    return asyncio.run(render(url, cells, ncol, W, H, out, size_js=f'axo.size({W},{H})'))
if __name__ == '__main__':
    a = json.loads(sys.argv[1]); run(a['url'], a['out'], a['state'], a['settle'], a['cells'], a.get('W', 600), a.get('H', 600), a.get('ncol', 3), a.get('pre', ''))
