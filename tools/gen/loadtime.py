import asyncio, time
from playwright.async_api import async_playwright
SP = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 400, 'height': 400}, device_scale_factor=1)
        await ctx.add_init_script('window.__NATIVE = {"platform":"ios","model":"iPhone16,1","tier":3,"memGB":7.5,"lowPower":false,"thermal":0,"maxFPS":120,"scale":3};')
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', mode: 'duo', seen: {look:1} })); } catch (e) {}")
        pg = await ctx.new_page(); t0 = time.time()
        await pg.goto(SP + 'pc_t.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=240000)
        print('ready', round(time.time() - t0, 1))
        t1 = time.time(); await pg.evaluate("() => { window.__noLoop = true; __T.renderFrame(); }"); print('frame', round(time.time() - t1, 2))
        t1 = time.time(); await pg.screenshot(path='st/lt.png'); print('shot', round(time.time() - t1, 2))
        await b.close()
asyncio.run(main())
