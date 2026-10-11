import asyncio, json
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width': 400, 'height': 300})
        await pg.goto('http://localhost:8765/lab/index.html', timeout=120000); await pg.wait_for_function('window.LAB && LAB.ready', timeout=120000, polling=200)
        print(await pg.evaluate("""(() => { const A = LAB.I.ax.A, P = A.P, pos = P.fk('crawl', A.LS), o = {};
          for (const n of ['hips', 'spine', 'spine1', 'chest', 'neck', 'head', 'shoulder.L', 'upperarm.L', 'forearm.L', 'hand.L', 'thigh.L', 'shin.L', 'foot.L', 'toes.L', 'tail1', 'tail3', 'tail6', 'gill0.L.1']) o[n] = pos[P.idx[n]].toArray().map(v => +v.toFixed(3));
          const M = P.m.crawl; o.faceC = M.meta.face && M.meta.face.c.map(v => +v.toFixed(3)); o.faceR = M.meta.face && M.meta.face.r; return JSON.stringify(o); })()"""))
        await b.close()
asyncio.run(main())
