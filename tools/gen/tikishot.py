import asyncio, sys
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
PAGE = sys.argv[1]; OUT = sys.argv[2]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 600}, device_scale_factor=2)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', mode: 'solo', seen: {look:1} })); } catch (e) {}")
        pg = await ctx.new_page(); await pg.goto('file://' + SP + PAGE, timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000); await pg.wait_for_timeout(2500)
        await pg.evaluate("""() => { const T = __T; window.__noLoop = true; T.mode = 'solo'; T.applyMode(); T.setStage('island'); T.genWorld(2468, { themes: ['island'] }); T.mapUsed = false; T.start(); T.setWx('clear', 999);
          for (let i = 0; i < 60; i++) { T.step(1 / 60); T.visuals(1 / 60, 1 / 60); } const p = T.pots3[0], c = T.camera; c.position.set(p.x + 1.9, p.y + 1.7, p.z + 2.1); c.lookAt(p.x, p.y + 0.35, p.z); c.updateMatrixWorld(); T.sun.shadow.needsUpdate = true; T.renderFrame(); }""")
        await pg.screenshot(path=SP + OUT); await b.close()
asyncio.run(main())
