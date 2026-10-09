import asyncio, json, sys
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
W, H, TAG = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        mobile = W < 700
        ctx = await b.new_context(viewport={'width':W,'height':H}, device_scale_factor=2 if mobile else 1, has_touch=mobile, is_mobile=mobile)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', color: 'green', look: { eyes: 'googly', head: 'hat', back: 'wings', mouth: 'fangs' }, seen: {steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,look:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: m.type=='error' and errs.append(m.text[:200]))
        await pg.goto(U, timeout=240000); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=240000); await pg.wait_for_timeout(700)
        await pg.evaluate("document.getElementById('mWorld').hidden && document.getElementById('homePlay').click()"); await pg.wait_for_timeout(350); await pg.click('#startBtn'); await pg.wait_for_function("__T.state === 'play'", polling=100, timeout=240000); await pg.wait_for_timeout(2200)
        await pg.screenshot(path=f'ui/{TAG}_a_play.png')
        # the rival, wearing a halo and wings, right in front of you
        await pg.evaluate("""(() => { const T = __T, P = T.P, H = T.H; window.__noLoop = true; T.LH.wearing = { head: 'horns', back: 'wings', mouth: 'fangs' };
          H.ai = null; H.x = P.x + Math.sin(P.yaw) * 3.2; H.z = P.z + Math.cos(P.yaw) * 3.2; H.y = P.y; H.yaw = P.yaw + Math.PI; H.st = 'play'; H.spd = 0; H.air = false;
          for (let i = 0; i < 30; i++) { T.visuals(0.016, 0.016); } T.renderFrame(); })()""")
        await pg.screenshot(path=f'ui/{TAG}_b_rival.png')
        await pg.evaluate("""(() => { const T = __T, P = T.P; window.__noLoop = false; for (let i = 0; i < 16; i++) { const x = P.x + (i % 4 - 1.5) * 3.2, z = P.z + (i / 4 | 0) * 3.2 - 4.8; T.addSplat(x, Math.max(0, T.surfaceUnder(x, z, P.y + 3, true)), z, 0, 3, T.clock, false, true, 0); } T.flushTrail(); T.matchLeft = 0.05; })()""")
        await pg.wait_for_function("!!__T.vic", polling=200, timeout=150000); await pg.wait_for_timeout(500)
        await pg.evaluate("(()=>{ window.__noLoop = true; __T.vic.t = 2.35; for (let i = 0; i < 3; i++) __T.visuals(0.0001, 0.016); __T.renderFrame(); })()")
        await pg.screenshot(path=f'ui/{TAG}_c_vic.png')
        info = await pg.evaluate("[document.getElementById('vName').getAttribute('aria-label'), [...document.querySelectorAll('.vcn')].map(e => e.textContent)]")
        print(TAG, info, errs[:4]); await b.close()
asyncio.run(main())
