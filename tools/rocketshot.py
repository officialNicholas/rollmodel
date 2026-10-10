import asyncio, json, sys
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
# the paint backpack on the player: going up, hovering, and the pack from behind
async def run():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 844, 'height': 390}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'land', name:'Dusk', seen:{steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,look:1,items:1}, look:{head:null, eyes:'edgy', iris:'violet'} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200])); pg.on('console', lambda m: m.type == 'error' and 'Failed to load' not in m.text and errs.append(m.text[:200]))
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(1500)
        await pg.evaluate("document.getElementById('mWorld').hidden && document.getElementById('stageBtn').click()"); await pg.wait_for_timeout(350); await pg.tap('#startBtn'); await pg.wait_for_timeout(400)
        await pg.wait_for_function("__T.state === 'play'", timeout=40000); await pg.wait_for_function("!__T.P.air", timeout=90000, polling=300); await pg.wait_for_timeout(800)
        await pg.evaluate("__T.matchLeft = 400; for (const D of __T.ACTIVE) if (D !== __T.P) { D.ai && (D.ai.thinkT = 99); D.spd = 0; } __T.startRocket(__T.P);")
        await pg.wait_for_timeout(1500); await pg.evaluate("(o => { const P = __T.P; window.__camRel = [o, [0, 0.1, 0]]; })([1.7, 0.3, 1.7])"); await pg.wait_for_timeout(900); await pg.screenshot(path=f'{WS}/ui/rocket_up.png')
        await pg.wait_for_function("__T.P.rocket && __T.P.rocket.ph === 'hover'", timeout=120000, polling=300)
        for i, (off, name, wait) in enumerate([([1.1, 0.25, -1.5], 'back', 800), ([1.6, 0.15, 0.6], 'side', 800), ([-1.3, -0.6, -1.2], 'below', 800)]):
            await pg.wait_for_timeout(wait); await pg.evaluate("(o => { const P = __T.P; window.__camRel = [o, [0, 0.2, 0]]; })(%s)" % json.dumps(off)); await pg.wait_for_timeout(1200)
            print(name, await pg.evaluate("[__T.P.rocket && __T.P.rocket.ph, +__T.P.y.toFixed(1), __T.VP.rk && __T.VP.rk.visible, +(__T.VP.rkLv || 0).toFixed(2)]"))
            await pg.screenshot(path=f'{WS}/ui/rocket_{name}.png')
        print('errors', errs[:4]); await b.close()
asyncio.run(run())
