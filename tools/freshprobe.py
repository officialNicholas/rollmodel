"""v187: buying an item marks it new; the locker tab and tile glow with a NEW tag until you pick it."""
import asyncio
from playwright.async_api import async_playwright
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 844, 'height': 390}, device_scale_factor=2)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'land', name:'Pixel', seen:{look:1}, drops: 900, tut: { ph: 'done' } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(2500)
        await pg.evaluate("document.getElementById('dabsBtn').click()"); await pg.wait_for_timeout(1500)
        ids = await pg.evaluate("[...document.querySelectorAll('#shopGrid .shitem:not(.locked):not(.broke)')].map(e => e.dataset.w)"); print('buyable', ids)
        pick = [i for i in ids if i in ('tophat', 'pirate', 'bowtie', 'glasses', 'tiara', 'pearls', 'patch')][:1] or ids[:1]
        await pg.evaluate("document.querySelector('#shopGrid .shitem[data-w=\"" + pick[0] + "\"]').click()"); await pg.wait_for_timeout(1500)
        print('bought', pick[0], await pg.evaluate("[JSON.stringify(__T.store.fresh), __T.store.drops]"))
        await pg.evaluate("document.getElementById('shopBack').click()"); await pg.wait_for_timeout(1200)
        await pg.evaluate("document.getElementById('lookBtn').click()"); await pg.wait_for_timeout(2500)
        print('tabs', await pg.evaluate("[...document.querySelectorAll('#lookCats .lcat')].map(b => b.dataset.cat + (b.classList.contains('fresh') ? '*' : ''))"))
        await pg.screenshot(path=S + '/ws/ui/fresh_tabs.png')
        cat = await pg.evaluate("[...document.querySelectorAll('#lookCats .lcat.fresh')].map(b => b.dataset.cat)[0]")
        await pg.evaluate("document.querySelector('#lookCats .lcat[data-cat=\"" + cat + "\"]').click()"); await pg.wait_for_timeout(1500)
        print('tiles', await pg.evaluate("[...document.querySelectorAll('#lookRail .ltile.fresh')].map(t => t.dataset.w)")); await pg.screenshot(path=S + '/ws/ui/fresh_tiles.png')
        await pg.evaluate("document.querySelector('#lookRail .ltile[data-w=\"" + pick[0] + "\"]').click()"); await pg.wait_for_timeout(1500)
        print('after pick', await pg.evaluate("[JSON.stringify(__T.store.fresh), [...document.querySelectorAll('#lookCats .lcat.fresh, #lookRail .ltile.fresh')].length]"))
        print('errors', errs); await b.close()
asyncio.run(main())
