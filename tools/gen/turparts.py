# the turret's three pieces from the pack, on their own: the body, the head, the firing head (front, side, back, above)
import asyncio, sys
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width': 1200, 'height': 900}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('file://' + SP + 'pc_t.html', timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.SLIME && __T.SLIME.S.ready', polling=200, timeout=300000)
        await pg.evaluate("""() => { const T = __T, THREE = T.THREE, G = T.SLIME.S.geo; window.__noLoop = true; const cv = document.createElement('canvas'); cv.style.cssText = 'position:fixed;left:0;top:0;width:1200px;height:900px;z-index:99999'; document.body.appendChild(cv); const R = new THREE.WebGLRenderer({ canvas: cv, antialias: true }); R.setSize(1200, 900, false);
          const sc = new THREE.Scene(); sc.background = new THREE.Color(0xdde6ee); sc.add(new THREE.HemisphereLight(0xffffff, 0x887766, 1.6)); const dl = new THREE.DirectionalLight(0xffffff, 2.4); dl.position.set(2, 4, 3); sc.add(dl);
          const mk = (g, col, x) => { const m = new THREE.Mesh(g, new THREE.MeshStandardMaterial({ color: col, roughness: 0.5, side: THREE.DoubleSide })); m.position.x = x; sc.add(m); return m; };
          const meta = T.SLIME.S.meta.turret, nk = meta.neck;
          // body and head together (as built), the head alone, the firing head alone
          mk(G.turBody, 0xE04040, -3); mk(G.turHead, 0xF08080, -3); mk(G.turHead, 0xF08080, 0); mk(G.turFire, 0x80A0F0, 3);
          const piv = new THREE.Mesh(new THREE.SphereGeometry(0.03), new THREE.MeshBasicMaterial({ color: 0x000000 })); piv.position.set(-3 + nk[0], nk[1], nk[2]); sc.add(piv);
          const W = 1200, H = 900; R.setRenderTarget(null); R.setScissorTest(true); const views = [[0, 0.6, 9], [9, 0.6, 0.01], [0, 0.6, -9], [0.01, 10, 1.2]];
          views.forEach((v, i) => { const cam = new THREE.PerspectiveCamera(40, (W / 2) / (H / 2), 0.1, 50); cam.position.set(v[0], v[1], v[2]); cam.lookAt(0, 0.1, 0.3); const vx = (i % 2) * W / 2, vy = (1 - (i >> 1)) * H / 2;
            R.setViewport(vx, vy, W / 2, H / 2); R.setScissor(vx, vy, W / 2, H / 2); const s0 = cam.position.clone(); cam.position.x += 0; R.render(sc, cam); });
          R.setScissorTest(false); }""")
        await pg.screenshot(path=SP + 'st/turparts.png'); print(errs[:3]); await b.close()
asyncio.run(main())
