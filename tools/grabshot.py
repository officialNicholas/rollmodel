"""v206: the blob with and without the see-through copy (the tuning's 'refraction off' notch), same moment, and errors"""
import asyncio
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 430, 'height': 754}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{look:1}, runs: 5, tut: { ph: 'done' } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8765/pc_h.html', timeout=300000)
        for i in range(120):
            if await pg.evaluate("typeof __T === 'object'"): break
            await pg.wait_for_timeout(2500)
        await pg.evaluate("document.getElementById('homePlay').click()")
        for i in range(120):
            if await pg.evaluate("__T.state === 'play'"): break
            await pg.wait_for_timeout(2500)
        await pg.wait_for_timeout(3000)
        await pg.evaluate("window.__noStep = true")  # (hold the moment still)
        await pg.wait_for_timeout(1500); await pg.screenshot(path=f'{WS}/ui/grab_on.png')
        print('post', await pg.evaluate("({ grab: __T.post.grab, bloom: __T.post.bloom, dof: __T.post.dof })"))
        await pg.evaluate("__T.post.grab = false"); await pg.wait_for_timeout(2500); await pg.screenshot(path=f'{WS}/ui/grab_off.png')
        print('errors', errs)
        await b.close()
asyncio.run(main())
