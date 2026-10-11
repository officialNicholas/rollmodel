# the stand / crawl swap pair at fixed skeleton mixes u, each mesh alone, for an anchor mode
import asyncio, sys, json
sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axo3')
from rsheet import render
def run(url, out, us, cams, mode_js, W=400, H=340):
    init = "(() => { const A = axo.A, P = axo.P; window.SK = 1; window.mixAt = (u, which) => { const pS = new A.pose.constructor(P.nb), pC = new A.pose.constructor(P.nb); A.swapPose('stand', pS); A.ground('stand', pS); A.swapPose('crawl', pC); A.ground('crawl', pC); P.applyMorph(pS, pC, u); axo.S.mesh.visible = which !== 'crawl'; axo.C.mesh.visible = which !== 'stand'; axo.look.meshU.stand.uFadeK.value = 1; axo.look.meshU.crawl.uFadeK.value = 1; if (which === 'mix') axo.look.setSwap('crawl', 'stand', 0.5); }; " + mode_js + " return 1; })()"
    cells = []
    for cam in cams:
        for u in us:
            for w in ('stand', 'crawl'):
                cells.append((f"mixAt({u}, '{w}'); axo.view({cam[0]},{cam[1]},{cam[2]},{cam[3]},{cam[4]},{cam[5]},30);", f'{w} at u={u}'))
    return asyncio.run(render(url, cells, len(us) * 2, W, H, out, size_js=f'axo.size({W},{H})', init_js=init))
if __name__ == '__main__':
    a = json.loads(sys.argv[1]); run(a['url'], a['out'], a['us'], a['cams'], a.get('mode', ''), a.get('W', 400), a.get('H', 340))
