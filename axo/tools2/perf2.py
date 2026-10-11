import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width': 400, 'height': 400}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8765/axo2/preview.html?manual', timeout=600000); await pg.wait_for_function('window.ready', timeout=600000)
        r = await pg.evaluate('''() => { const A = axo.A, P = axo.P; const out = {};
          for (const st of ['stand', 'crawl']) { axo.setState(st); for (let i = 0; i < 150; i++) A.update(1 / 60);
            const t0 = performance.now(); const N = 1500; for (let i = 0; i < N; i++) { A.update(1 / 60); P.m[A.mesh].mesh.skeleton.update(); } out[st] = ((performance.now() - t0) / N).toFixed(3) + ' ms'; }
          return out; }''')
        print('anim cost per character per frame incl. look / jelly / face updates:', r, errs[:3]); await b.close()
asyncio.run(main())
