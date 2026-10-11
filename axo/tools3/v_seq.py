# a frame sequence of one transition (or any state change) from a fixed camera: settle in `from`, switch to `to`, capture every `every` frames
# usage: v_seq.py '{"url":..., "out":..., "from":"stand", "to":"crawl", "settle":90, "n":16, "every":4, "cam":[yaw,pitch,dist,ty,tx,tz,fov], "W":360, "H":300, "ncol":4, "slow":1, "pre":""}'
import asyncio, sys, json
sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo3')
from rsheet import render
def run(a):
    cam = a['cam']; camjs = f"axo.view({cam[0]},{cam[1]},{cam[2]},{cam[3]},{cam[4]},{cam[5]},{cam[6] if len(cam) > 6 else 30});"
    dt = 1 / 60 / a.get('slow', 1); cells = []
    cells.append((f"axo.setLook(0,0); {a.get('pre', '')}; axo.setState('{a['from']}'); axo.step(1/60,{a['settle']}); {camjs}", f"{a['from']} (before)"))
    for i in range(a['n']):
        first = (i == 0)
        js = (f"axo.setState('{a['to']}');" if first else '') + f"axo.step({dt},{a['every'] if not first else a.get('first', a['every'])}); {camjs} (() => {{ const A = axo.A; return [A.state, A.mesh, A.mixU, A.fade]; }})()"
        cells.append((js, None))
    labs = []; f = 0
    for i in range(a['n']):
        f += a.get('first', a['every']) if i == 0 else a['every']; t = f * dt
        labs.append(f"+{f} f{' (slowed x' + str(a['slow']) + ')' if a.get('slow', 1) != 1 else ''}  t={t:.3f}s")
    cells = [cells[0]] + [(c[0], labs[i]) for i, c in enumerate(cells[1:])]
    return asyncio.run(render(a['url'], cells, a.get('ncol', 4), a.get('W', 360), a.get('H', 300), a['out'], size_js=f"axo.size({a.get('W', 360)},{a.get('H', 300)})", title=a.get('title')))
if __name__ == '__main__': run(json.loads(sys.argv[1]))
