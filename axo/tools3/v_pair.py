# a pose on both meshes side by side (stand mesh at x = 0, crawl mesh shifted by dx), from several cameras.
# cells: [js that fills pose `p` for mesh `w` (A = animator), cam [yaw, pitch, dist, ty, tx, tz, fov], label]
import asyncio, sys, json
sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo3')
from rsheet import render
INIT = """(() => { window.posePair = (fill, dx, only) => { const A = axo.A, P = axo.P; const mk = () => new A.pose.constructor(P.nb);
  for (const w of ['stand', 'crawl']) { const p = mk(); fill(A, p, w); A.ground(w, p); P.apply(w, p); }
  axo.S.mesh.visible = only !== 'crawl'; axo.C.mesh.visible = only !== 'stand'; axo.C.mesh.position.x = dx; axo.look.meshU.stand.uFadeK.value = 1; axo.look.meshU.crawl.uFadeK.value = 1; }; return 1; })()"""
def run(url, out, cells, W=520, H=420, ncol=3, dx=1.1, title=None):
    cl = []
    for c in cells:
        fill, cam, lab = c[:3]; only = c[3] if len(c) > 3 else ''
        js = f"posePair((A, p, w) => {{ {fill} }}, {dx}, '{only}'); axo.view({cam[0]},{cam[1]},{cam[2]},{cam[3]},{cam[4]},{cam[5]},{cam[6] if len(cam) > 6 else 30});"
        cl.append((js, lab))
    return asyncio.run(render(url, cl, ncol, W, H, out, size_js=f'axo.size({W},{H})', init_js=INIT, title=title))
if __name__ == '__main__':
    a = json.loads(open(sys.argv[1]).read()); run(a['url'], a['out'], a['cells'], a.get('W', 520), a.get('H', 420), a.get('ncol', 3), a.get('dx', 1.1), a.get('title'))
