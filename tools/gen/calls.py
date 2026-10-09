import asyncio, sys, json
from playwright.async_api import async_playwright
PAGE = sys.argv[1]
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/' + PAGE
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':390,'height':844}); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=30000)
        out = []
        for sd in [1,2,5,9,11,16]:
            r = await pg.evaluate(f"""(() => {{ window.__noLoop = true; const T = __T, R = T.renderer; T.genWorld({sd}); T.mapUsed = false; T.showMenu();
              T.camera.position.set(0, 30, 44); T.camera.lookAt(0, -2, 2); T.camera.updateMatrixWorld();
              const fr = () => {{ R.info.reset(); R.render(T.scene, T.camera); return R.info.render.calls; }};
              fr(); const t0 = performance.now(); let c = 0; for (let i = 0; i < 5; i++) c = fr(); const ms = (performance.now() - t0) / 5;
              let stage = 0; T.scene.traverse(o => {{ }}); return [{sd}, c, +ms.toFixed(1), R.info.render.triangles]; }})()""")
            out.append(r)
        print(PAGE, out, errs[:2]); await b.close()
asyncio.run(main())
