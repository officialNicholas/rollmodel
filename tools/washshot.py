import asyncio
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 393, 'height': 852}, device_scale_factor=2, has_touch=True, is_mobile=True, reduced_motion='no-preference')
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{steer:1,look:1}, owned:[], bought:[], drops:300, look:{head:null, eyes:'edgy', iris:'violet'}, colorId:'orange' })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(1500)
        await pg.evaluate("document.getElementById('setBtn').click()"); await pg.wait_for_timeout(800)
        t1 = await pg.evaluate("getComputedStyle(document.querySelector('#setModal .swash i')).transform"); await pg.screenshot(path=f'{WS}/ui/wash_a.png')
        await pg.wait_for_timeout(3000); t2 = await pg.evaluate("getComputedStyle(document.querySelector('#setModal .swash i')).transform"); await pg.screenshot(path=f'{WS}/ui/wash_b.png')
        print('drift', t1, '->', t2, errs[:2]); await b.close()
asyncio.run(main())
