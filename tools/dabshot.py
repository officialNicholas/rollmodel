import asyncio
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 780}, device_scale_factor=3, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{steer:1,look:1}, owned:['tiara'], drops:240 })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(1500)
        await pg.screenshot(path=f'{WS}/ui/dab_lobby.png', clip={'x': 296, 'y': 210, 'width': 90, 'height': 60})
        await pg.evaluate("document.getElementById('lookBtn').click()"); await pg.wait_for_timeout(2500)
        r = await pg.evaluate("(() => { const r = document.getElementById('lkBal').getBoundingClientRect(); return [r.left|0, r.top|0, r.width|0, r.height|0]; })()")
        await pg.screenshot(path=f'{WS}/ui/dab_chip.png', clip={'x': r[0] - 6, 'y': r[1] - 6, 'width': r[2] + 12, 'height': r[3] + 12})
        t = await pg.evaluate("(() => { const t = document.querySelector('#lookRail .ltile.sale'); if (!t) return null; const r = t.getBoundingClientRect(); return [r.left|0, r.top|0, r.width|0, r.height|0, t.getAttribute('aria-label')]; })()")
        print('tag', t)
        if t: await pg.screenshot(path=f'{WS}/ui/dab_tag.png', clip={'x': t[0] - 4, 'y': t[1] - 14, 'width': t[2] + 8, 'height': t[3] + 18})
        print('errors', errs[:2]); await b.close()
asyncio.run(main())
