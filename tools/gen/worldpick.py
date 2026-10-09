import asyncio, json
from playwright.async_api import async_playwright
U = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', stage: 'standard', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: m.type == 'error' and errs.append(m.text[:200]))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=120000); await pg.wait_for_timeout(1500)
        print('boot', await pg.evaluate("[__T.stageSel, __T.TH.id, __T.GEN.key]"))
        await pg.click('#homePlay'); await pg.wait_for_timeout(900)
        cards = await pg.evaluate("[...document.querySelectorAll('#stagePick .world')].map(b => b.dataset.s + ':' + b.querySelector('.wn').textContent)")
        print('cards', cards, await pg.evaluate("document.querySelectorAll('#gDots i').length"))
        await pg.click('.world[data-s="garden"]'); await pg.wait_for_timeout(1500)
        print('garden', await pg.evaluate("[__T.stageSel, __T.TH.id, __T.GEN.key, JSON.parse(localStorage.getItem('paint-world-red.v1')).stage]"))
        await pg.screenshot(path='ui/reorg_worlds.png')
        await pg.click('#startBtn'); await pg.wait_for_timeout(2500)
        print('play', await pg.evaluate("[__T.state, __T.TH.id]"))
        print('errors', errs[:4]); await b.close()
asyncio.run(main())
