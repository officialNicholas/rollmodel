import asyncio
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 393, 'height': 852}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{steer:1,look:1}, owned:['pearls'], bought:['pearls'], drops:300, look:{head:null, eyes:'edgy', iris:'violet'} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(1500)
        await pg.evaluate("document.getElementById('lookBtn').click()"); await pg.wait_for_timeout(3000)
        await pg.evaluate("document.getElementById('lkBal').click()")
        for k, ms in enumerate([60, 160, 500]):
            await pg.wait_for_timeout(ms if k == 0 else ms - [60, 160, 500][k - 1]); await pg.screenshot(path=f'{WS}/ui/shoptr_in_{k}.png')
        st = await pg.evaluate("[getComputedStyle(document.getElementById('shop')).opacity, document.getElementById('shop').hidden, getComputedStyle(document.querySelector('.mhome')).opacity]"); print('open', st)
        await pg.evaluate("document.getElementById('shopBack').click()"); await pg.wait_for_timeout(110); await pg.screenshot(path=f'{WS}/ui/shoptr_out_0.png')
        mid = await pg.evaluate("[document.getElementById('shop').hidden, document.getElementById('shop').className]"); await pg.wait_for_timeout(400)
        print('close', mid, await pg.evaluate("[document.getElementById('shop').hidden, document.getElementById('shop').className, !document.getElementById('look').hidden]"), errs[:2]); await b.close()
asyncio.run(main())
