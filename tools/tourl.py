import asyncio
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 844, 'height': 390}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'land', name:'Dusk', mode:'duel', seen:{steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,look:1}, drops:420, owned:['flower'], bought:['flower'], wins:{duel:3}, bestCov:{duel:22}, xp:140 })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200])); logs = []; pg.on('console', lambda m: logs.append(m.text[:200]) if m.type == 'error' and 'CORS' not in m.text and 'ERR_FAILED' not in m.text else None)
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(2500)
        shots = []
        async def shot(name, ms=900):
            await pg.wait_for_timeout(ms); await pg.screenshot(path=f'{WS}/ui/tourl_{name}.png'); shots.append(name)
        await shot('lobby', 200)
        await pg.evaluate("document.getElementById('stageBtn').click()"); await shot('canvases')
        await pg.evaluate("__T.showMenu && 0; document.querySelector('.gnav.back, #worldBack, .mworld .ib') && 0"); await pg.keyboard.press('Escape'); await pg.wait_for_timeout(400)
        await pg.evaluate("document.getElementById('howBtn').click()"); await shot('howto'); await pg.evaluate("document.getElementById('howClose').click()"); await pg.wait_for_timeout(300)
        await pg.evaluate("document.getElementById('commBtn').click()"); await shot('commissions'); await pg.keyboard.press('Escape'); await pg.wait_for_timeout(300)
        await pg.evaluate("document.getElementById('setBtn').click()"); await shot('settings'); await pg.evaluate("document.getElementById('setDone').click()"); await pg.wait_for_timeout(300)
        await pg.evaluate("document.getElementById('homePlay').click()"); await pg.wait_for_function("__T.state === 'play'", timeout=30000); await pg.wait_for_timeout(1200); await shot('play', 200)
        await pg.evaluate("document.getElementById('pauseBtn').click()"); await shot('pause'); await pg.evaluate("document.getElementById('resumeBtn').click()"); await pg.wait_for_timeout(300)
        print('shots', shots, 'errors', errs[:4], logs[:4]); await b.close()
asyncio.run(main())
