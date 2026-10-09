import asyncio, json
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'+(__import__('sys').argv[1] if len(__import__('sys').argv)>1 else 'pc_t.html')
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ seen: {steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
        await ctx.add_init_script("""(() => { const raf = window.requestAnimationFrame.bind(window); window.__fr = []; window.requestAnimationFrame = cb => raf(t => { const t0 = performance.now(); cb(t); window.__fr.push([+(t0).toFixed(0), +(performance.now() - t0).toFixed(1)]); if (window.__fr.length > 400) window.__fr.shift(); }); })();""")
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)[:400]))
        await pg.goto(U, timeout=240000); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=240000); await pg.wait_for_timeout(500)
        await pg.evaluate("""()=>{ const T=__T; window.__noLoop = true; T.mode='duo'; T.applyMode(); T.start(); const P=T.P;
              for (let i = 0; i < 12; i++) { const x = P.x + (i % 4 - 1.5) * 3.2, z = P.z + (i / 4 | 0) * 3.2 - 4.8; T.addSplat(x, Math.max(0, T.surfaceUnder(x, z, P.y + 3, true)), z, 0, 3, T.clock, false, true, 0); } T.flushTrail();
              T.matchLeft = 0.01; for (let k=0;k<400 && T.state==='play';k++) T.step(0.012); window.__noLoop = false; window.__fr.length = 0; }""")
        for k in range(4):
            await pg.wait_for_timeout(3000)
            fr = await pg.evaluate("window.__fr.slice(-12)"); st = await pg.evaluate("({ st: __T.state, vic: __T.vic ? +__T.vic.t.toFixed(2) : null })")
            gaps = [fr[i+1][0]-fr[i][0] for i in range(len(fr)-1)]
            print(k, st, 'cb ms', [f[1] for f in fr], 'gaps', gaps)
        print(errs[:3]); await b.close()
asyncio.run(main())
