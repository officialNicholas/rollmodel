import asyncio
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__noLoop = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', mode:'duel', stage:'blank', seen:{steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,look:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(1000)
        await pg.evaluate("document.getElementById('homePlay').click()"); await pg.wait_for_function("__T.state === 'play'", timeout=30000); await pg.wait_for_timeout(500)
        r = await pg.evaluate("""(() => { const T = __T, P = T.P; T.matchLeft = 500; for (const R of T.rivals) { R.x = -20; R.z = -20; R.spd = 0; }
          P.power = { type: 'roller', left: 30, t: 30 }; for (let i = 0; i < 70; i++) T.step(1 / 60); T.flushTrail(); return [P.power && P.power.type, +P.spd.toFixed(2), T.splatN]; })()""")
        print('roller', r)
        await pg.evaluate("window.__noLoop = false"); await pg.wait_for_timeout(1500); await pg.screenshot(path=f'{WS}/ui/roller_trail.png', clip={'x': 0, 'y': 300, 'width': 390, 'height': 480})
        print('errors', errs[:2]); await b.close()
asyncio.run(main())
