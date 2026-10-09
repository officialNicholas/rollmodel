import asyncio, sys
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 360, 'height': 640}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ seen: {steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1}, name:'Dusk', orient:'port', mode:'trio' })); } catch (e) {}")
        pg = await ctx.new_page()
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=240000); await pg.wait_for_timeout(1500)
        await pg.evaluate("(() => { const e = document.getElementById('end'); window.__log = []; const ro = new ResizeObserver(() => __log.push([performance.now()|0, e.offsetTop, e.offsetHeight, e.scrollHeight])); ro.observe(e); })()")
        await pg.evaluate("document.getElementById('homePlay').click()"); await pg.wait_for_function("__T.state === 'play'", timeout=20000); await pg.wait_for_timeout(1500)
        await pg.evaluate("(() => { const P = __T.P; for (let i = 0; i < 16; i++) { const x = P.x + (i % 4 - 1.5) * 3.2, z = P.z + (i / 4 | 0) * 3.2 - 4.8; __T.addSplat(x, Math.max(0, __T.surfaceUnder(x, z, P.y + 3, true)), z, 0, 3, __T.clock, false, true, 0); } __T.flushTrail(); __T.matchLeft = 0.4; })()")
        await pg.wait_for_function("!!__T.vic", timeout=40000, polling=200); await pg.wait_for_timeout(1500)
        await pg.tap('#victory'); await pg.wait_for_function("!document.getElementById('end').hidden", timeout=10000); await pg.wait_for_timeout(2500)
        print(await pg.evaluate("[__log, document.getElementById('gframe').style.cssText, document.getElementById('end').offsetTop]"))
        await b.close()
asyncio.run(main())
