import asyncio
from playwright.async_api import async_playwright
SP = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script('window.__NATIVE = {"platform":"ios","model":"iPhone16,1","tier":3,"memGB":7.5,"lowPower":false,"thermal":0,"maxFPS":120,"scale":3};')
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', seen: {look:1} })); } catch (e) {}")
        pg = await ctx.new_page(); await pg.goto(SP + 'pc_t.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=240000)
        r = await pg.evaluate("""() => { const T = __T; window.__noLoop = true; T.genWorld(77, { themes: ['cathedral'] }); T.mapUsed = false; T.start(); T.renderFrame(); T.renderFrame();
          const R = T.renderer; R.info.autoReset = false; R.info.reset(); T.renderFrame(); const c1 = R.info.render.calls; T.post.mirror = false; R.info.reset(); T.renderFrame(); const c2 = R.info.render.calls;
          return { mirror: T.post.mirror, th: T.TH.id, thm: T.TH.mirror, map: !!T.sun.shadow.map, c1, c2 }; }""")
        print(r); await b.close()
asyncio.run(main())
