"""The win screen: the winner lands on all fours, rises for its jumps, settles back down between rounds. Samples the animator's state over
time in the page and films a strip. usage: winmorph.py [tag]"""
import asyncio, json, sys
from playwright.async_api import async_playwright
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
TAG = sys.argv[1] if len(sys.argv) > 1 else 'a'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 700}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', mode:'solo', stage:'manor', seen:{steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,look:1,items:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object" && !!__T.VP && !!__T.VP.slime', timeout=240000, polling=1000); await pg.wait_for_timeout(1500)
        await pg.evaluate("__T.start()"); await pg.wait_for_function("__T.state === 'play'", timeout=60000, polling=500); await pg.wait_for_timeout(1500)
        await pg.evaluate("(() => { const P = __T.P; for (let i = 0; i < 16; i++) { const x = P.x + (i % 4 - 1.5) * 3.2, z = P.z + (i / 4 | 0) * 3.2 - 4.8; __T.addSplat(x, Math.max(0, __T.surfaceUnder(x, z, P.y + 3, true)), z, 0, 3, __T.clock, false, true, 0); } __T.flushTrail(); __T.matchLeft = 0.4; })()")
        await pg.wait_for_function("!!__T.vic", timeout=60000, polling=100)
        await pg.evaluate("""window.__log = []; window.__iv = setInterval(() => { const v = __T.vic; if (!v) return; const D = v.feat[0], A = __T.VP.slime.ax.A; __log.push([+v.t.toFixed(2), D.vicPose && D.vicPose.stand, A.state, A.mesh, +(D.vicPose ? D.vicPose.hop : 0).toFixed(2)]); }, 100);""")
        for k in range(16):
            await pg.wait_for_timeout(750); await pg.screenshot(path=f'{S}/ws/ui/win_{TAG}_{k:02d}.png')
        log = await pg.evaluate("__log"); prev = None
        for r in log:
            key = (r[1], r[2], r[3])
            if key != prev: print(r); prev = key
        print('happy', await pg.evaluate("__T.vic && __T.vic.happy"), 'errors', errs[:3]); await b.close()
asyncio.run(main())
