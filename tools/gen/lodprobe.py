# how big each blob is on screen (radius in device pixels) and which detail level it picked: menu, customize, play
import asyncio, json
from playwright.async_api import async_playwright
SP = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        for vw, vh in [(390, 844), (844, 390)]:
            ctx = await b.new_context(viewport={'width': vw, 'height': vh}, device_scale_factor=2, has_touch=True, is_mobile=True)
            await ctx.add_init_script('window.__NATIVE = {"platform":"ios","model":"iPhone16,1","tier":3,"memGB":7.5,"lowPower":false,"thermal":0,"maxFPS":120,"scale":3};')
            await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
            pg = await ctx.new_page(); await pg.goto(SP + 'pc_t.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=240000)
            r = await pg.evaluate("""() => { const T = __T, out = {}; window.__noLoop = true; const rd = () => [T.body.userData.rpx | 0, T.body.userData.lodL];
              for (let i = 0; i < 60; i++) T.visuals(0.016, 0.016); T.renderFrame(); out.menu = rd();
              T.openLook(); for (let i = 0; i < 90; i++) T.visuals(0.016, 0.016); T.renderFrame(); out.look = rd(); T.closeLook();
              T.genWorld(77, { themes: ['cathedral'] }); T.mapUsed = false; T.start(); for (let i = 0; i < 200; i++) { T.step(0.016); T.visuals(0.016, 0.016); } T.renderFrame(); out.play = rd(); out.dbh = T.renderer.domElement.height; return out; }""")
            print(vw, vh, json.dumps(r))
            await ctx.close()
        await b.close()
asyncio.run(main())
