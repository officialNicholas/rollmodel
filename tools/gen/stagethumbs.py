# thumbnails of the three Halloween canvases for the stage grid: an aerial three-quarter view of a generated stage, no UI
import asyncio, sys, json
from playwright.async_api import async_playwright
SP = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
SEEDS = {'crypt': 7712, 'cathedral': 5151, 'manor': 2424}
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 960, 'height': 660}, device_scale_factor=1)
        await ctx.add_init_script('window.__NATIVE = {"platform":"ios","model":"iPhone16,1","tier":3,"memGB":7.5,"lowPower":false,"thermal":0,"maxFPS":120,"scale":3};')
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', mode: 'duo', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
        pg = await ctx.new_page(); await pg.goto(SP + 'pc_t.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=240000)
        await pg.add_style_tag(content='#menu,.hud,.corner,#banner,#hint,.pop,#vig{display:none !important}')
        for th, seed in SEEDS.items():
            await pg.evaluate("""([th, seed]) => { const T = __T; window.__noLoop = true; T.genWorld(seed, { themes: [th] }); T.mapUsed = false; T.resetRun(); T.decorate();
              for (let i = 0; i < 30; i++) T.visuals(0.016, 0.016); const c = T.camera, A = T.ARENA; c.fov = 42; c.position.set(A * 0.62, A * 1.02, A * 1.18); c.lookAt(0, -2, -A * 0.08); c.updateProjectionMatrix(); c.updateMatrixWorld(); T.renderFrame(); }""", [th, seed])
            await pg.wait_for_timeout(200)
            await pg.screenshot(path=f'st/thumb_{th}.png')
            print('ok', th)
        await b.close()
asyncio.run(main())
