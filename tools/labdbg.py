import asyncio, json, sys
from playwright.async_api import async_playwright
SC, OPT, WARM, N = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width': 300, 'height': 200}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:400]))
        await pg.goto('http://localhost:8765/lab/index.html?d=1', timeout=120000); await pg.wait_for_function('window.LAB && LAB.ready', timeout=120000, polling=200)
        await pg.evaluate(f"LAB.set('{SC}', {OPT}); LAB.step({WARM})")
        for i in range(N):
            r = await pg.evaluate("""(() => { LAB.step(1); const A = LAB.I.ax.A, L = A.loco, C = A.motion.carry, f = LAB.feet();
              return [+LAB.t.toFixed(3), LAB.D.air, L.land ? +L.land.t.toFixed(3) : null, +L.f.toFixed(2), C ? [C.elements[12], C.elements[13], C.elements[14]].map(x => +x.toFixed(4)) : null,
                L.limbs.map(l => l.en + ':' + l.st + ':' + l.p.toArray().map(x => +x.toFixed(3)).join(',')).join(' | '), f['foot.L'].map(x => +x.toFixed(3)).join(',')]; })()""")
            print(r)
        print(errs[:3]); await b.close()
asyncio.run(main())
