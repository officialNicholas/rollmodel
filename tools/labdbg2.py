import asyncio, sys
from playwright.async_api import async_playwright
SC, OPT, WARM, N = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width': 300, 'height': 200}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:400]))
        await pg.goto('http://localhost:8765/lab/index.html?d=2', timeout=120000); await pg.wait_for_function('window.LAB && LAB.ready', timeout=120000, polling=200)
        await pg.evaluate(f"LAB.set('{SC}', {OPT}); LAB.step({WARM})")
        for i in range(N):
            r = await pg.evaluate("""(() => { LAB.step(1); const A = LAB.I.ax.A, P = A.P, pos = P.fk(A.mesh, A.pose), c = A.pose.contacts['foot.L'], ch = A.pose.contacts['hand.L'];
              const M = P.m[A.mesh], w = new THREE.Vector3(); M.mesh.updateMatrixWorld(true); M.byName['foot.L'].getWorldPosition(w);
              const tw = c ? c.t.clone().applyMatrix4(M.mesh.matrixWorld) : null;
              return [+LAB.t.toFixed(3), A.mesh, A.state, c ? c.w.toFixed(2) : '-', 'tgt', c ? c.t.toArray().map(x => +x.toFixed(3)) : null, 'fk', pos[P.idx['foot.L']].toArray().map(x => +x.toFixed(3)), 'world', w.toArray().map(x => +x.toFixed(3)), 'tgtW', tw && tw.toArray().map(x => +x.toFixed(3)), 'sq', +A.squash.toFixed(3), LAB.I.root.scale.toArray().map(x => +x.toFixed(3))]; })()""")
            print(r)
        print(errs[:3]); await b.close()
asyncio.run(main())
