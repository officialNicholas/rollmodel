import asyncio
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        for W, H, tag in [(844, 390, 'land'), (390, 844, 'port')]:
            ctx = await b.new_context(viewport={'width': W, 'height': H}, device_scale_factor=2, has_touch=True, is_mobile=True)
            await ctx.add_init_script('window.__NATIVE = {"platform":"ios","model":"iPhone16,1","tier":3,"memGB":7.5,"lowPower":false,"thermal":0,"maxFPS":120,"scale":3};')
            await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
            pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
            await pg.goto('file://' + SP + 'pc_t.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=240000)
            await pg.evaluate("window.__noLoop = true")
            await pg.evaluate("""() => { const T = __T, P = T.P; T.genWorld(5151, { themes: ['cathedral'] }); T.mapUsed = false; T.start(); T.setWx('clear', 99); P.cpu = true; T.aiReset(P);
              for (let i = 0; i < 300; i++) { T.steerIn = P.steer || 0; T.step(0.016); if (i % 3 === 2) { T.visuals(0.048, 0.048); T.flushTrail(); } } P.cpu = false; T.steerIn = 0;
              const sb = document.getElementById('slamBtn'); sb.hidden = false; document.getElementById('banner').style.display = 'none'; for (let i = 0; i < 20; i++) T.visuals(0.016, 0.016); T.renderFrame(); }""")
            await pg.screenshot(path=f'{SP}st/hud_{tag}.png'); print(tag, errs[:2]); await ctx.close()
        await b.close()
asyncio.run(main())
