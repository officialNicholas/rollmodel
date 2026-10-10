import asyncio, sys
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
W, H, tag = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': W, 'height': H}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'%s', name:'Dusk', seen:{steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,look:1,items:1}, owned:['pearls'], bought:['pearls'], drops:300, wins:3, look:{head:null, neck:'pearls', eyes:'edgy', iris:'violet'} })); } catch (e) {}" % ('land' if W > H else 'port'))
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(2500)
        await pg.screenshot(path=f'{WS}/ui/sv_{tag}_lobby.png')
        await pg.evaluate("document.getElementById('stageBtn') && document.getElementById('stageBtn').click()"); await pg.wait_for_timeout(1200); await pg.screenshot(path=f'{WS}/ui/sv_{tag}_world.png')
        await pg.evaluate("const b = document.querySelector('#mWorld .back, #worldBack, #mWorld button[data-back]'); b && b.click()"); await pg.wait_for_timeout(600)
        for sel, name in [('#setBtn', 'settings'), ('#howBtn', 'how')]:
            ok = await pg.evaluate("(s => { const e = document.querySelector(s); if (!e) return false; e.click(); return true; })('%s')" % sel); await pg.wait_for_timeout(900); await pg.screenshot(path=f'{WS}/ui/sv_{tag}_{name}.png'); print(name, ok)
            await pg.keyboard.press('Escape'); await pg.wait_for_timeout(500)
        await pg.evaluate("document.getElementById('mWorld').hidden && document.getElementById('stageBtn').click()"); await pg.wait_for_timeout(350); await pg.tap('#startBtn')
        await pg.wait_for_function("__T.state === 'play'", timeout=40000); await pg.wait_for_function("!__T.P.air", timeout=90000, polling=300); await pg.wait_for_timeout(2500)
        await pg.screenshot(path=f'{WS}/ui/sv_{tag}_play.png')
        await pg.evaluate("const e = document.getElementById('pauseBtn'); e && e.click()"); await pg.wait_for_timeout(800); await pg.screenshot(path=f'{WS}/ui/sv_{tag}_pause.png')
        print(tag, 'errors', errs[:3]); await b.close()
asyncio.run(main())
