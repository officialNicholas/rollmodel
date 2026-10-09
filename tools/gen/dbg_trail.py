import asyncio, json, sys
from playwright.async_api import async_playwright
U = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        for gfx in ['perf', 'hi']:
            ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, has_touch=True, is_mobile=True)
            await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: '" + gfx + "', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
            pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
            await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=60000); await pg.wait_for_timeout(600)
            for th in ['island', 'garden']:
                r = await pg.evaluate("""(th) => { const T = __T, P = T.P; window.__noLoop = true;
                  T.genWorld(4242, { themes: [th] }); T.mapUsed = false; T.start(); window.__noStep = false;
                  for (let i = 0; i < 300; i++) { T.steerIn = 0.12; T.step(0.016); T.visuals(0.016, 0.016); T.flushTrail(); }
                  T.steerIn = 0; document.getElementById('banner').style.display = 'none'; T.renderFrame();
                  return [P.x.toFixed(1), P.z.toFixed(1), T.camera.position.toArray().map(v => v.toFixed(1)).join(','), T.paintMesh.geometry.drawRange.count]; }""", th)
                await pg.screenshot(path=f'fin/tr_{gfx}_{th}_follow.png')
                await pg.evaluate("(() => { const T = __T, P = T.P, c = T.camera; c.position.set(P.x + 2, 22, P.z + 2); c.lookAt(P.x, 0, P.z); T.renderFrame(); })()")
                await pg.screenshot(path=f'fin/tr_{gfx}_{th}_top.png')
                print(gfx, th, r)
                await pg.evaluate("(() => { document.getElementById('banner').style.display = ''; __T.state = 'menu'; __T.showMenu(); })()")
            print(errs[:3]); await ctx.close()
        await b.close()
asyncio.run(main())
