import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width': 300, 'height': 200}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:400]))
        await pg.goto('http://localhost:8765/lab/index.html?s=1', timeout=120000); await pg.wait_for_function('window.LAB && LAB.ready', timeout=120000, polling=200)
        await pg.evaluate("LAB.set('fling', { c: 1, at: 0.3, every: 5 }); LAB.step(20)")
        for i in range(48):
            r = await pg.evaluate("(() => { LAB.step(1); const X = LAB.I.ax, A = X.A; return [+LAB.t.toFixed(3), LAB.D.air, +(A.motion.ball || 0).toFixed(2), +(A.ballOn || 0).toFixed(2), +(X.spin || 0).toFixed(2), +((((X.spin || 0) % 6.2832) + 6.2832) % 6.2832).toFixed(2), +(X.spinV || 0).toFixed(1), !!X.ballHold, +(X.lastWant || 0).toFixed(2)]; })()")
            print(r)
        print(errs[:3]); await b.close()
asyncio.run(main())
