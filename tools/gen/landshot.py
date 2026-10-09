import asyncio, json, sys
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
W,H,TAG = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
async def settle(pg, n=120):
    await pg.evaluate(f"(()=>{{ for (let i=0;i<{n};i++) __T.visuals(0.0001, 0.05); __T.renderFrame(); }})()")
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width':W,'height':H}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ seen: {steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=60000); await pg.wait_for_timeout(800)
        await settle(pg); await pg.screenshot(path=f'ui/{TAG}_a_menu.png')
        await pg.evaluate("document.getElementById('mWorld').hidden && document.getElementById('homePlay').click()"); await pg.wait_for_timeout(350); await pg.tap('#startBtn'); await pg.wait_for_timeout(500); await pg.screenshot(path=f'ui/{TAG}_b_name.png')
        await pg.fill('#nameInput', 'Count Drip'); await pg.tap('#nameOk')
        await pg.wait_for_function("__T.state === 'play'", polling=100, timeout=20000); await pg.wait_for_timeout(1500)
        await pg.screenshot(path=f'ui/{TAG}_c_play.png')
        await pg.tap('#pauseBtn'); await pg.wait_for_timeout(400); await pg.screenshot(path=f'ui/{TAG}_d_pause.png'); await pg.tap('#resumeBtn'); await pg.wait_for_timeout(300)
        await pg.evaluate("(()=>{ const T=__T, P=T.P; for (let i = 0; i < 16; i++) { const x = P.x + (i % 4 - 1.5) * 3.2, z = P.z + (i / 4 | 0) * 3.2 - 4.8; T.addSplat(x, Math.max(0, T.surfaceUnder(x, z, P.y + 3, true)), z, 0, 3, T.clock, false, true, 0); } T.flushTrail(); T.matchLeft = 0.05; })()")
        await pg.wait_for_function("!!__T.vic", polling=200, timeout=150000); await pg.wait_for_timeout(600); await pg.evaluate("(()=>{ window.__noLoop = true; __T.vic.t = 2.35; for (let i = 0; i < 3; i++) __T.visuals(0.0001, 0.016); __T.renderFrame(); window.__noLoop = false; })()")
        await pg.screenshot(path=f'ui/{TAG}_e_vic.png')
        await pg.tap('#victory'); await pg.wait_for_function("!document.getElementById('end').hidden", polling=200, timeout=60000); await pg.wait_for_timeout(300)
        await pg.evaluate("(()=>{ window.__noLoop = true; const T = __T; for (let i = 0; i < 90; i++) T.visuals(0.0001, 0.05); T.renderFrame(); })()")
        await pg.screenshot(path=f'ui/{TAG}_f_end.png')
        sc = await pg.evaluate("(() => { const e = document.getElementById('end'); return [e.scrollHeight, e.clientHeight, e.offsetLeft, e.offsetTop, __T.outroSc.toFixed(2)]; })()")
        print(TAG, sc, errs[:3]); await b.close()
asyncio.run(main())
