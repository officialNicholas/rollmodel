# a sheet of cells, each: [pre_js, state, settle_frames, cam, label]
#   cam = [yaw, pitch, dist, joint (or null: absolute target), ox, oy, oz, fov]   target = joint world position + (ox, oy, oz)
#   state = null keeps the current state (settle frames are still stepped); pre_js runs first (colour, eyes, expression, speed ...)
#   usage: python3 -I v_cells.py spec.json     spec: {url, out, cells, W, H, ncol, title, init}
import asyncio, sys, json
sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo3')
from rsheet import render
def cell_js(pre, state, settle, cam, mesh=None):
    js = f"{pre or ''};"
    if state: js += f"axo.setState('{state}');"
    if settle: js += f"axo.step(1/60,{settle});"
    yaw, pitch, dist, joint, ox, oy, oz = cam[:7]; fov = cam[7] if len(cam) > 7 else 30
    if state: js = "window.__fix = {};" + js
    if joint and joint.startswith('@'):   # a fixed camera: the joint's position the first time it is used (after the last state change)
        jn = joint[1:]; js += f"(() => {{ window.__fix = window.__fix || {{}}; const p = window.__fix['{jn}'] || (window.__fix['{jn}'] = axo.joint(axo.A.mesh, '{jn}')); axo.view({yaw},{pitch},{dist},p[1]+({oy}),p[0]+({ox}),p[2]+({oz}),{fov}); }})();"
    elif joint == 'HC': js += f"(() => {{ const p = axo.hc(axo.A.mesh); axo.view({yaw},{pitch},{dist},p[1]+({oy}),p[0]+({ox}),p[2]+({oz}),{fov}); }})();"   # the head (face sphere) centre
    elif joint: js += f"(() => {{ const p = axo.joint(axo.A.mesh, '{joint}'); axo.view({yaw},{pitch},{dist},p[1]+({oy}),p[0]+({ox}),p[2]+({oz}),{fov}); }})();"
    else: js += f"axo.view({yaw},{pitch},{dist},{oy},{ox},{oz},{fov});"
    return js
def run(spec):
    cells = [(cell_js(*c[:4]), c[4]) for c in spec['cells']]
    W, H = spec.get('W', 400), spec.get('H', 400)
    return asyncio.run(render(spec['url'], cells, spec.get('ncol', 4), W, H, spec['out'], size_js=f'axo.size({W},{H})', init_js=spec.get('init'), title=spec.get('title')))
if __name__ == '__main__': run(json.load(open(sys.argv[1])))
