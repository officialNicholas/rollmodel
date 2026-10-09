import asyncio, sys
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
LAND = '--land' in sys.argv
VP = {'width': 780, 'height': 360} if LAND else {'width': 390, 'height': 780}
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport=VP, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ seen: {steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1}, name:'Dusk', orient:'" + ('land' if LAND else 'port') + "' })); } catch (e) {}")
        pg = await ctx.new_page()
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=240000); await pg.wait_for_timeout(1500)
        await pg.evaluate("document.getElementById('lookBtn').click()")
        for i in range(8):
            await pg.wait_for_timeout(700); await pg.screenshot(path=f'{WS}/ui/seq/look_{"l" if LAND else "p"}_{i}.png')
            print(i, await pg.evaluate("(() => { const P = __T.P; return [P.burst, P.bursting, P.shatter, P.hp, P.wet, P.state, __T.state].map(String).join(' '); })()"))
        await b.close()
asyncio.run(main())
