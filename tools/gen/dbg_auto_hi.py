import asyncio, json
from playwright.async_api import async_playwright
U = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=60000); await pg.wait_for_timeout(600)
        r = await pg.evaluate("""() => { const T = __T, P = T.P, H = T.H; window.__noLoop = true; const out = [];
          T.genWorld(4242, { themes: ['island'] }); T.mapUsed = false; T.start(); window.__noStep = false;
          P.cpu = true; T.aiReset(P);
          for (let i = 0; i < 640; i++) { T.steerIn = P.steer || 0; T.step(0.016); if (i % 3 === 2) { T.visuals(0.048, 0.048); T.flushTrail(); }
            if (i % 80 === 0) out.push([i, T.state, P.st, P.x.toFixed(1), P.z.toFixed(1), (P.spd||0).toFixed(2), (P.steer||0).toFixed(2), P.paint.toFixed(2), !!P.dry, T.splatN, H.x.toFixed(1), H.z.toFixed(1), P.ai && P.ai.mode]); }
          out.push(['nV', T.chunkN, 'cam', T.camera.position.x.toFixed(1), T.camera.position.z.toFixed(1), 'P', P.x.toFixed(1), P.z.toFixed(1), P.yaw.toFixed(2)]);
          for (let i = 0; i < 20; i++) T.visuals(0.016, 0.016); T.flushTrail(); T.renderFrame();
          return out; }""")
        await pg.screenshot(path='fin/dbg_follow_hi.png')
        await pg.evaluate("(() => { const T = __T, c = T.camera; document.getElementById('hud').classList.add('off'); c.position.set(0, 70, 0.01); c.lookAt(0, 0, 0); T.renderFrame(); })()")
        await pg.screenshot(path='fin/dbg_top_hi.png')
        for row in r: print(row)
        print(errs[:3]); await b.close()
asyncio.run(main())
