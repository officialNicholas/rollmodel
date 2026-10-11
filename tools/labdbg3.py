import asyncio, sys
from playwright.async_api import async_playwright
SC, OPT, WARM, N, LIMB = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4]), sys.argv[5]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width': 300, 'height': 200}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:400]))
        await pg.goto('http://localhost:8765/lab/index.html?d=3', timeout=120000); await pg.wait_for_function('window.LAB && LAB.ready', timeout=120000, polling=200)
        await pg.evaluate(f"LAB.set('{SC}', {OPT}); LAB.step({WARM})")
        prev = None
        for i in range(N):
            r = await pg.evaluate("""(n => { LAB.step(1); const A = LAB.I.ax.A, P = A.P, L = A.loco, l = L.limbs.find(x => x.en === n), pos = P.fk(A.mesh, A.pose), c = A.pose.contacts[n];
              const M = P.m[A.mesh], w = new THREE.Vector3(); M.mesh.updateMatrixWorld(true); M.byName[n].getWorldPosition(w);
              return [+LAB.t.toFixed(3), LAB.D.air, L.land ? +L.land.t.toFixed(3) : '-', +L.f.toFixed(2), +L.ph.toFixed(3), l.st, 'tgt', c.t.toArray().map(x => +x.toFixed(3)), 'fk', pos[P.idx[n]].toArray().map(x => +x.toFixed(3)), 'w', w.x, w.z]; })""" + f"('{LIMB}')")
            if prev: r.append(round(((r[-2] - prev[0]) ** 2 + (r[-1] - prev[1]) ** 2) ** 0.5 * 60, 2))
            prev = (r[-2] if not prev else r[-3], r[-1] if not prev else r[-2]) if False else (r[11], r[12])
            print(r[:11], 'wspd', r[13] if len(r) > 13 else '-')
        print(errs[:3]); await b.close()
asyncio.run(main())
