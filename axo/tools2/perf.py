# CPU cost of the procedural animation (pose evaluation + secondary motion + bone writes + skeleton matrix update) per character per frame
import asyncio, json
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width': 300, 'height': 300}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8765/axo2/preview.html?manual', timeout=600000); await pg.wait_for_function('window.ready', timeout=600000)
        r = await pg.evaluate('''() => { const A = axo.A, P = axo.P; const out = {};
          for (const st of ['stand', 'crawl', 'jetpack']) { axo.setState(st); for (let i = 0; i < 150; i++) A.update(1 / 60);
            const t0 = performance.now(); const N = 1500; for (let i = 0; i < N; i++) { A.update(1 / 60); P.m[A.mesh].mesh.skeleton.update(); } out[st] = ((performance.now() - t0) / N).toFixed(3) + ' ms'; }
          return out; }''')
        print('animation cost per character per frame (incl. skeleton matrix update):', r, errs)
        await b.close()
asyncio.run(main())
