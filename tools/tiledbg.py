import asyncio
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{steer:1,look:1}, owned:['hat','tophat','flower','tiara'], bought:['hat','tophat','flower','tiara'], drops:500 })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(1500)
        await pg.evaluate("document.getElementById('lookBtn').click()"); await pg.wait_for_timeout(2500)
        print(await pg.evaluate("[...document.querySelectorAll('#lookRail .ltile')].map(t => t.dataset.w + ':' + t.className + ':' + t.getAttribute('aria-pressed'))"))
        ids = await pg.evaluate("[...document.querySelectorAll('#lookRail .ltile')].filter(t => !t.classList.contains('locked') && !t.classList.contains('sale')).map(t => t.dataset.w)")
        print('owned', ids)
        tgt = ids[1] if len(ids) > 1 else ids[0]
        await pg.evaluate("document.querySelector('#lookRail .ltile[data-w=\"" + tgt + "\"]').click()"); await pg.wait_for_timeout(1500)
        print(await pg.evaluate("(() => { const t = document.querySelector('#lookRail .ltile[aria-pressed=\"true\"]'); if (!t) return 'none pressed'; const c = getComputedStyle(t), r = t.getBoundingClientRect(); return { w: t.dataset.w, cls: t.className, op: c.opacity, vis: c.visibility, disp: c.display, tr: c.transform, scale: c.scale, anim: c.animationName, bg: c.backgroundColor, rect: [r.left|0, r.top|0, r.width|0, r.height|0], rail: document.getElementById('lookRail').className }; })()"))
        r = await pg.evaluate("(() => { const r = document.getElementById('lookRail').getBoundingClientRect(); return [r.left, r.top, r.width, r.height]; })()")
        await pg.screenshot(path=f'{WS}/ui/tile_dbg.png', clip={'x': 0, 'y': max(0, r[1] - 110), 'width': 390, 'height': r[3] + 130})
        print('errors', errs[:2]); await b.close()
asyncio.run(main())
