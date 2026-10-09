import asyncio
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__instant = false; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Juliana', mode:'duel', seen:{steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,look:1}, owned:['flower'], bought:['flower'], look:{head:'flower'} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(2500)
        # mid-bounce and a tap-hop right as Play is pressed
        await pg.evaluate("window.__idleForce = 'bounce'"); await pg.wait_for_timeout(1500)
        await pg.evaluate("document.getElementById('lookBtn').click()"); await pg.wait_for_timeout(2500); await pg.evaluate("document.getElementById('lookDone').click()"); await pg.wait_for_timeout(200)
        await pg.evaluate("document.getElementById('homePlay').click()"); await pg.wait_for_timeout(1400); await pg.screenshot(path=f'{WS}/ui/vsb_card.png')
        await pg.wait_for_function("__T.state === 'play'", timeout=40000); await pg.wait_for_timeout(4000)
        # the weather chip steps aside for the banner
        await pg.evaluate("__T.setWx('warn', 9); __T.banner('Heat wave in 9', 'Hide in a paint tub or the shade', true)"); await pg.wait_for_timeout(1500)
        a = await pg.evaluate("[__T.wxOnChip, document.getElementById('banner').className]"); await pg.screenshot(path=f'{WS}/ui/vsb_banner.png', clip={'x': 0, 'y': 0, 'width': 390, 'height': 260})
        await pg.wait_for_timeout(3400); bb = await pg.evaluate("[__T.wxOnChip, __T.wx]"); await pg.screenshot(path=f'{WS}/ui/vsb_after.png', clip={'x': 0, 'y': 0, 'width': 390, 'height': 260})
        print('chip during banner', a, 'after', bb, 'errors', errs[:3]); await b.close()
asyncio.run(main())
