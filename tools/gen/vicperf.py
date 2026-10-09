import asyncio, json
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ seen: {steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)[:400]))
        await pg.goto(U, timeout=240000); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=240000); await pg.wait_for_timeout(500)
        r = await pg.evaluate("""()=>{ const T=__T; window.__noLoop = true; T.mode='duo'; T.applyMode(); T.start(); const P=T.P;
              const tm = (fn, n) => { const t0 = performance.now(); for (let i = 0; i < n; i++) fn(); return +((performance.now() - t0) / n).toFixed(1); };
              const play = { vis: tm(() => T.visuals(0.016, 0.016), 5), render: tm(() => T.renderFrame(), 3) };
              for (let i = 0; i < 12; i++) { const x = P.x + (i % 4 - 1.5) * 3.2, z = P.z + (i / 4 | 0) * 3.2 - 4.8; T.addSplat(x, Math.max(0, T.surfaceUnder(x, z, P.y + 3, true)), z, 0, 3, T.clock, false, true, 0); } T.flushTrail();
              T.matchLeft = 0.01; for (let k=0;k<400 && T.state==='play';k++) T.step(0.012);
              return { play, st: T.state, gfx: T.GFX }; }""")
        await pg.wait_for_timeout(2500)
        r2 = await pg.evaluate("""()=>{ const T=__T; if (!T.vic && T.state === 'dead') T.startVictory(); for (let i = 0; i < 30; i++) T.visuals(0.016, 0.016); const tm = (fn, n) => { const t0 = performance.now(); for (let i = 0; i < n; i++) fn(); return +((performance.now() - t0) / n).toFixed(1); };
              const f = { st: T.state, vic: !!T.vic, vis: tm(() => T.visuals(0.016, 0.016), 3), render: tm(() => T.renderFrame(), 2) }; f.plain = []; for (let k = 0; k < 4; k++) { const p0 = T.renderer.info.programs.length, t0 = performance.now(); T.visuals(0.016, 0.016); T.renderFrame(); T.renderer.getContext().finish(); f.plain.push([+(performance.now() - t0).toFixed(0), T.renderer.info.programs.length - p0]); } f.calls = T.renderer.info.render.calls; f.tris = T.renderer.info.render.triangles; f.progs = T.renderer.info.programs.length; return f; }""")
        print('vic', r2)
        print(r, errs[:3]); await b.close()
asyncio.run(main())
