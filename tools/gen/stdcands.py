import asyncio, json, sys
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
MODE = sys.argv[1]; SEEDS = [int(x) for x in sys.argv[2].split(',')]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width':640,'height':640}); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=120000); await pg.wait_for_timeout(300)
        await pg.add_style_tag(content="#stage > :not(canvas){visibility:hidden !important}")
        await pg.evaluate(f"(()=>{{ const T=__T; window.__noLoop = true; T.mode = '{MODE}'; T.applyMode(); }})()")
        out = []
        for sd in SEEDS:
            r = await pg.evaluate("""(sd) => { const T = __T; T.genWorld(sd, { easy: true, themes: ['studio'] }); T.resetRun(); T.state = 'menu';
              const A = T.ARENA; for (let i = 0; i < 3; i++) T.visuals(0.016, 0.016); const c = T.camera; c.clearViewOffset(); c.fov = 50; c.aspect = 1; c.updateProjectionMatrix(); c.position.set(0, A * 2.3, A * 0.9); c.up.set(0, 1, 0); c.lookAt(0, 0, 0.5); T.renderFrame();
              return { sd, arch: T.GEN.arch, sym: T.GEN.sym, boxes: T.BOXES.length, floating: T.BOXES.filter(b => b[4] > 0.5).length, ramps: T.RAMPS.length, holes: T.HOLES.length, pots: T.POTS.length }; }""", sd)
            await pg.screenshot(path=f'std/{MODE}_{sd}.png'); out.append(r)
        print(json.dumps(out), errs[:3]); await b.close()
asyncio.run(main())
