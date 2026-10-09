import asyncio, sys
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
LAND = '--land' in sys.argv; T = 'l' if LAND else 'p'
VP = {'width': 780, 'height': 360} if LAND else {'width': 390, 'height': 780}
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport=VP, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'" + ('land' if LAND else 'port') + "', name:'Dusk', seen:{steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,look:1}, owned:['hat','glasses','bowtie','pirate'], bought:['hat','glasses','bowtie'], drops: 40, look:{head:'hat',eye:'glasses',neck:'bowtie'} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); logs = []; pg.on('console', lambda m: logs.append(m.text[:200]) if m.type == 'error' and 'CORS' not in m.text and 'ERR_FAILED' not in m.text else None)
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(2000)
        await pg.evaluate("document.getElementById('lookBtn').click()"); await pg.wait_for_timeout(3500); await pg.screenshot(path=f'{WS}/ui/lk_{T}_0.png')
        sw = await pg.evaluate("[...document.querySelectorAll('#swatches .sw')].map(b => b.dataset.c)"); print('swatches', sw)
        await pg.evaluate("document.querySelectorAll('#swatches .sw')[3].click()"); await pg.wait_for_timeout(350); await pg.screenshot(path=f'{WS}/ui/lk_{T}_1.png')
        await pg.wait_for_timeout(2500); await pg.screenshot(path=f'{WS}/ui/lk_{T}_2.png')
        await pg.evaluate("document.querySelectorAll('#lookCats .lcat')[1].click()"); await pg.wait_for_timeout(600); await pg.screenshot(path=f'{WS}/ui/lk_{T}_3.png')
        print(T, 'errors', errs[:3], logs[:3]); await b.close()
asyncio.run(main())
