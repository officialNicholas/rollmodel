import asyncio, json
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_base.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width':360,'height':720}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ seen: {steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: m.type=='error' and errs.append(m.text[:200]))
        await pg.goto(U, timeout=240000); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=240000)
        await pg.wait_for_timeout(1500)
        boot = await pg.evaluate("document.getElementById('boot').className")
        await pg.evaluate("document.getElementById('mWorld').hidden && document.getElementById('homePlay').click()"); await pg.wait_for_timeout(350); await pg.tap('#startBtn'); await pg.wait_for_timeout(400)
        modal = await pg.evaluate("!document.getElementById('nameModal').hidden")
        await pg.fill('#nameInput', 'Dusk'); await pg.tap('#nameOk')
        await pg.wait_for_function("__T.state === 'play'", timeout=10000)
        await pg.wait_for_timeout(1500)
        await pg.evaluate("(() => { const P = __T.P; P.power = { type: 'roller', t: 9 }; for (let i = 0; i < 16; i++) { const x = P.x + (i % 4 - 1.5) * 3.2, z = P.z + (i / 4 | 0) * 3.2 - 4.8; __T.addSplat(x, Math.max(0, __T.surfaceUnder(x, z, P.y + 3, true)), z, 0, 3, __T.clock, false, true, 0); } __T.flushTrail(); __T.matchLeft = 0.4; })()")
        for i in range(40):
            st = await pg.evaluate("[__T.state, +__T.matchLeft.toFixed(2), +__T.teamCov(0).toFixed(2), +__T.teamCov(1).toFixed(2), +__T.runT.toFixed(2)]")
            if i % 4 == 0: print('t', i, st)
            if st[0] == 'dead': break
            await pg.wait_for_timeout(500)
        await pg.wait_for_function("!!__T.vic", timeout=20000, polling=200)
        await pg.wait_for_timeout(1800)
        vis = await pg.evaluate("[!document.getElementById('victory').hidden, document.getElementById('vName').getAttribute('aria-label'), __T.vic && +__T.vic.t.toFixed(2)]")
        await pg.screenshot(path='ui/e2e_vic.png')
        await pg.tap('#victory'); await pg.wait_for_timeout(300)
        await pg.wait_for_function("!document.getElementById('end').hidden", timeout=10000)
        await pg.wait_for_timeout(1500)
        await pg.screenshot(path='ui/e2e_end.png')
        res = await pg.evaluate("[document.getElementById('endTitle').textContent, document.getElementById('chipYouName').textContent, document.getElementById('victory').hidden]")
        fr = await pg.evaluate("new Promise(r => { let n = 0; const t0 = performance.now(); const f = () => { n++; if (performance.now() - t0 < 3000) requestAnimationFrame(f); else r([n, JSON.stringify(__T.shadowCache), __T.state]); }; requestAnimationFrame(f); })")
        print('end-screen frames in 3s', fr, 'errs so far', errs[:4])
        await pg.evaluate("document.getElementById('replayBtn').click()"); await pg.wait_for_function("__T.state === 'play'", timeout=60000); await pg.wait_for_timeout(800)
        after = await pg.evaluate("[__T.state, document.getElementById('victory').hidden, document.getElementById('end').hidden, !!__T.vic]")
        print(json.dumps({'boot': boot, 'nameModal': modal, 'victory': vis, 'results': res, 'afterReplay': after}))
        print('errors', errs[:5]); await b.close()
asyncio.run(main())
