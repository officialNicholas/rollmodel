import asyncio
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        for w, h, t in [(390, 780, 'p'), (780, 360, 'l')]:
            ctx = await b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=2, has_touch=True, is_mobile=True)
            await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'" + ('land' if w > h else 'port') + "', name:'Dusk', mode:'duel', stage:'crypt', seen:{steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,look:1} })); } catch (e) {}")
            pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
            await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(1500)
            await pg.evaluate("document.getElementById('homePlay').click()"); await pg.wait_for_function("__T.state === 'play'", timeout=30000); await pg.wait_for_timeout(1500)
            await pg.evaluate("window.__noLoop = true; document.getElementById('bannerBig').textContent = 'Paint it red!'; document.getElementById('bannerSmall').textContent = 'The Crypt'; document.getElementById('bannerEm').dataset.k = 'stroke'; document.getElementById('banner').classList.add('on'); document.getElementById('hintText').textContent = 'Out of paint: your own color speeds you back up. Reach a coffin or your color in 4 seconds'; document.getElementById('hint').classList.add('on')")
            await pg.wait_for_timeout(700); await pg.screenshot(path=f'{WS}/ui/plate_{t}_0.png')
            await pg.evaluate("document.getElementById('banner').classList.remove('on'); void document.getElementById('banner').offsetWidth; document.getElementById('bannerBig').textContent = 'Heat wave in 5'; document.getElementById('bannerSmall').textContent = 'Hard paint cracks'; document.getElementById('bannerEm').dataset.k = 'heat'; document.getElementById('banner').classList.add('on'); document.getElementById('hint').classList.remove('on')")
            await pg.wait_for_timeout(700); await pg.screenshot(path=f'{WS}/ui/plate_{t}_1.png')
            print(t, 'errors', errs[:3]); await ctx.close()
        await b.close()
asyncio.run(main())
