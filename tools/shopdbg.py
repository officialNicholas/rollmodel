import asyncio
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{steer:1,look:1}, owned:['flower','hockey'], bought:[], drops:900, look:{head:null, eyes:'edgy', iris:'violet'} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(1500)
        await pg.evaluate("document.getElementById('dabsBtn').click()"); await pg.wait_for_timeout(1500)
        print(await pg.evaluate("(() => { const b = document.querySelector('#shopGrid .shitem'); const r = e => { const q = e.getBoundingClientRect(); return [Math.round(q.width), Math.round(q.height)]; }; const cs = getComputedStyle(b); return { card: r(b), display: cs.display, rows: cs.gridTemplateRows, pic: r(b.querySelector('.shpic')), picDisp: getComputedStyle(b.querySelector('.shpic')).display, ar: getComputedStyle(b.querySelector('.shpic')).aspectRatio, plate: r(b.querySelector('.shplate')), plateDisp: getComputedStyle(b.querySelector('.shplate')).display, img: b.querySelector('.shpic img') ? r(b.querySelector('.shpic img')) : null, html: b.outerHTML.slice(0, 160) }; })()"), errs[:2])
        await pg.screenshot(path=f'{WS}/ui/shop_dbg.png', clip={'x': 0, 'y': 140, 'width': 390, 'height': 260})
        await b.close()
asyncio.run(main())
