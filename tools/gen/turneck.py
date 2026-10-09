# the turret's neck up close: body + head and body + firing head, turned 0 / 20 / 45 degrees, before and after tucking in the body's stump
import asyncio, sys
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
TUCK = sys.argv[1] if len(sys.argv) > 1 else '0'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width': 1200, 'height': 800}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('file://' + SP + 'pc_t.html', timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.SLIME && __T.SLIME.S.ready', polling=200, timeout=300000)
        await pg.evaluate("""(tuck) => { const T = __T, THREE = T.THREE, G = T.SLIME.S.geo; window.__noLoop = true; const cv = document.createElement('canvas'); cv.style.cssText = 'position:fixed;left:0;top:0;width:1200px;height:800px;z-index:99999'; document.body.appendChild(cv); const R = new THREE.WebGLRenderer({ canvas: cv, antialias: true }); R.setSize(1200, 800, false);
          const tm = T.SLIME.S.meta.turret, nk = tm.neck; let body = G.turBody;
          if (tuck === '1') { body = body.clone(); const P = body.attributes.position, cz = nk[2], ss = (a, b, x) => { const t = Math.min(1, Math.max(0, (x - a) / (b - a))); return t * t * (3 - 2 * t); };
            for (let i = 0; i < P.count; i++) { const y = P.getY(i); if (y < -0.21) continue; const t = ss(-0.21, -0.15, y), x = P.getX(i), dz = P.getZ(i) - cz, r = Math.hypot(x, dz), Rr = 0.14; if (r > Rr) { const k = 1 + (Rr / r - 1) * t; P.setX(i, x * k); P.setZ(i, cz + dz * k); } P.setY(i, y - 0.04 * t); } P.needsUpdate = true; }
          const sc = new THREE.Scene(); sc.background = new THREE.Color(0xdde6ee); sc.add(new THREE.HemisphereLight(0xffffff, 0x887766, 1.6)); const dl = new THREE.DirectionalLight(0xffffff, 2.4); dl.position.set(2, 4, 3); sc.add(dl);
          const mat = new THREE.MeshStandardMaterial({ color: 0xE04848, roughness: 0.45 }), mat2 = new THREE.MeshStandardMaterial({ color: 0xF0A0A0, roughness: 0.45 });
          const rig = (hg, x, z, ang) => { const g = new THREE.Group(); g.position.set(x, 0, z); sc.add(g); g.add(new THREE.Mesh(body, mat)); const piv = new THREE.Group(); piv.position.set(nk[0], nk[1], nk[2]); piv.rotation.y = ang; g.add(piv); const hm = new THREE.Mesh(hg, mat2); hm.position.set(-nk[0], -nk[1], -nk[2]); piv.add(hm); };
          [0, 0.35, 0.8].forEach((a, i) => { rig(G.turHead, (i - 1) * 2.2, 0, a); rig(G.turFire, (i - 1) * 2.2, -2.6, a); });
          const W = 1200, H = 800; R.setScissorTest(true); const views = [[-1.8, 1.4, 3.6], [1.8, 1.4, -4.6]];
          views.forEach((v, i) => { const cam = new THREE.PerspectiveCamera(42, W / (H / 2), 0.1, 50); cam.position.set(v[0], v[1], v[2]); cam.lookAt(0, -0.1, -1.3); R.setViewport(0, (1 - i) * H / 2, W, H / 2); R.setScissor(0, (1 - i) * H / 2, W, H / 2); R.render(sc, cam); });
          R.setScissorTest(false); }""", TUCK)
        await pg.screenshot(path=SP + 'st/turneck_' + TUCK + '.png'); print(errs[:3]); await b.close()
asyncio.run(main())
