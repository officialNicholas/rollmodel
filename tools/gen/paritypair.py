import asyncio, sys
from playwright.async_api import async_playwright
SP = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
SEED = "(() => { let s = 4242; Math.random = () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; })();"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        for page, tag in [('pc_old.html', 'old'), ('pc_t.html', 'new')]:
            for gfx in ['hi', 'perf']:
                ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, has_touch=True, is_mobile=True)
                await ctx.add_init_script(SEED)
                await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: '" + gfx + "', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
                pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
                await pg.goto(SP + page); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=120000); await pg.wait_for_timeout(600)
                for th in ['garden', 'cathedral', 'island']:
                    await pg.evaluate("""(th) => { const T = __T, P = T.P; window.__noLoop = true; T.genWorld(5151, { themes: [th] }); T.mapUsed = false; T.start(); window.__noStep = false;
                      P.cpu = true; T.aiReset(P); for (let i = 0; i < 520; i++) { T.steerIn = P.steer || 0; T.step(0.016); if (i % 3 === 2) { T.visuals(0.048, 0.048); T.flushTrail(); } }
                      P.cpu = false; T.steerIn = 0; for (let i = 0; i < 20; i++) T.visuals(0.016, 0.016); T.flushTrail(); document.getElementById('banner').style.display = 'none'; T.renderFrame(); }""", th)
                    await pg.screenshot(path=f'par/{tag}_{gfx}_{th}.png')
                    await pg.evaluate("(() => { document.getElementById('banner').style.display = ''; __T.state = 'menu'; __T.showMenu(); })()")
                print(tag, gfx, errs[:3]); await ctx.close()
        await b.close()
asyncio.run(main())
