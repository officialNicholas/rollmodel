import asyncio, sys
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        for GFX in ['hi']:
            ctx = await b.new_context(viewport={'width':1280,'height':760})
            await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: '" + GFX + "', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
            pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
            await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=60000); await pg.wait_for_timeout(600)
            for th in ['studio','crypt']:
                r = await pg.evaluate("""(th) => { const T = __T; window.__noLoop = true; if (th === 'studio') T.loadStd(); else T.genWorld(4242, { themes: [th] }); T.mapUsed = false; T.start(); window.__noStep = false;
                  for (let i = 0; i < 70; i++) T.step(0.016);
                  const P = T.P; const o = { st: T.state, P: [P.x.toFixed(2), P.y.toFixed(2), P.z.toFixed(2), P.air] };
                  for (let i = 0; i < 40; i++) T.visuals(0.016, 0.016);
                  o.fade = T.moverMeshes.map(g => +g.userData.fade.toFixed(2)); o.hull = T.moverMeshes.map(g => g.children[1].visible); o.op = T.moverMeshes.map(g => [g.children[0].material.opacity.toFixed(2), g.children[0].material.transparent, g.children[0].material.depthWrite]); T.renderFrame(); return o; }""", th)
                print(GFX, th, r); await pg.screenshot(path=f'gfx/dbg2_{GFX}_{th}.png')
                await pg.evaluate("(() => { __T.state = 'menu'; __T.showMenu(); })()")
            print(errs[:3]); await ctx.close()
        await b.close()
asyncio.run(main())
