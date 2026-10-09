import asyncio, sys
from playwright.async_api import async_playwright
U='http://localhost:8765/pc_h.html'; OUT=sys.argv[1]; LAND='--land' in sys.argv
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width':780,'height':360} if LAND else {'width':390,'height':780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__instant = false; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'" + ('land' if LAND else 'port') + "', name:'Dusk', xp: 180, seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.goto(U, timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(3000)
        await pg.screenshot(path=OUT+'/lobby_say.png')
        await pg.evaluate("document.getElementById('commBtn').click()"); await pg.wait_for_timeout(500); await pg.screenshot(path=OUT+'/comms.png'); await pg.evaluate("document.getElementById('commClose').click()"); await pg.wait_for_timeout(300)
        await pg.evaluate("document.getElementById('homePlay').click()"); await pg.wait_for_timeout(1500); await pg.screenshot(path=OUT+'/vs.png')
        await pg.wait_for_timeout(900); await pg.screenshot(path=OUT+'/vs_slash.png')
        await pg.wait_for_function("__T.state === 'play'", timeout=30000); await pg.wait_for_timeout(2500); await pg.screenshot(path=OUT+'/hud_tank.png')
        await pg.evaluate("(() => { const P = __T.P; P.paint = 0.3; for (let i = 0; i < 16; i++) { const x = P.x + (i % 4 - 1.5) * 3.2, z = P.z + (i / 4 | 0) * 3.2 - 4.8; __T.addSplat(x, Math.max(0, __T.surfaceUnder(x, z, P.y + 3, true)), z, 0, 3, __T.clock, false, true, 0); } __T.flushTrail(); __T.matchLeft = 0.4; })()")
        await pg.wait_for_timeout(600); await pg.screenshot(path=OUT+'/hud_tank2.png')
        await pg.wait_for_function("!!__T.vic", timeout=30000, polling=200); await pg.wait_for_timeout(1800); await pg.screenshot(path=OUT+'/victory.png')
        await pg.tap('#victory'); await pg.wait_for_function("!document.getElementById('end').hidden", timeout=10000); await pg.wait_for_timeout(3200); await pg.screenshot(path=OUT+'/end.png')
        print('errors', errs[:4]); await b.close()
asyncio.run(main())
