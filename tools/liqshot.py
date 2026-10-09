import asyncio
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
SPL = "(() => { const P = __T.P, H = __T.H; for (let i = 0; i < 16; i++) { const x = P.x + (i % 4 - 1.5) * 3.2, z = P.z + (i / 4 | 0) * 3.2 - 4.8; __T.addSplat(x, Math.max(0, __T.surfaceUnder(x, z, P.y + 3, true)), z, 0, 3, __T.clock, false, true, 0); } for (let i = 0; i < 8; i++) { const x = H.x + (i % 4 - 1.5) * 3.2, z = H.z + (i / 4 | 0) * 3.2 - 2.4; __T.addSplat(x, Math.max(0, __T.surfaceUnder(x, z, H.y + 3, true)), z, 0, 3, __T.clock, false, true, 1); } __T.flushTrail(); })()"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        for w, h, t in [(390, 780, 'p'), (780, 360, 'l')]:
            ctx = await b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=2, has_touch=True, is_mobile=True)
            await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'" + ('land' if w > h else 'port') + "', name:'Dusk', mode:'duel', stage:'crypt', seen:{steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,look:1} })); } catch (e) {}")
            pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
            await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(1500)
            await pg.evaluate("document.getElementById('homePlay').click()"); await pg.wait_for_function("__T.state === 'play'", timeout=30000); await pg.wait_for_timeout(1500)
            await pg.evaluate(SPL); await pg.wait_for_timeout(400); await pg.screenshot(path=f'{WS}/ui/liq_{t}_hud.png', clip={'x': 0, 'y': 0, 'width': w, 'height': 120})
            await pg.evaluate("__T.matchLeft = 0.4"); await pg.wait_for_function("!!__T.vic", timeout=40000, polling=200); await pg.wait_for_timeout(1200)
            await pg.evaluate('window.__instant = false'); await pg.tap('#victory'); await pg.wait_for_function("!document.getElementById('end').hidden", timeout=10000); await pg.wait_for_timeout(650); await pg.screenshot(path=f'{WS}/ui/liq_{t}_end0.png')
            await pg.wait_for_timeout(2500); await pg.screenshot(path=f'{WS}/ui/liq_{t}_end1.png')
            print(t, 'errors', errs[:3]); await ctx.close()
        await b.close()
asyncio.run(main())
