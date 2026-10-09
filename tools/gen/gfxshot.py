# in-match screenshots per theme: python3 gen/gfxshot.py TAG [gfx=hi|perf] [themes...]
import asyncio, sys, json
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
TAG = sys.argv[1]; GFX = sys.argv[2] if len(sys.argv) > 2 else 'hi'; THEMES = sys.argv[3:] or ['studio', 'crypt', 'garden']
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        for W, H, dev in [(390, 844, 'phone'), (1280, 760, 'desk')]:
            mobile = dev == 'phone'
            ctx = await b.new_context(viewport={'width':W,'height':H}, device_scale_factor=2 if mobile else 1, has_touch=mobile, is_mobile=mobile)
            await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: '" + GFX + "', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
            pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: m.type == 'error' and 'ERR_' not in m.text and errs.append(m.text))
            await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=60000); await pg.wait_for_timeout(600)
            for th in THEMES:
                r = await pg.evaluate(f"""(() => {{ const T = __T; window.__noLoop = true;
                  if ('{th}' === 'studio') {{ T.loadStd ? T.loadStd() : 0; }} else T.genWorld(4242, {{ themes: ['{th}'] }});
                  T.mapUsed = false; T.start(); window.__noStep = false;
                  for (let i = 0; i < 70; i++) T.step(0.016);
                  const P = T.P; for (let i = 0; i < 18; i++) {{ const a = i * 0.7, d = 2 + i * 0.5, x = P.x + Math.sin(a) * d, z = P.z + Math.cos(a) * d + 3; const y = T.surfaceUnder(x, z, 4, true); if (y > -1) T.addSplat(x, y, z, a, 1.2 + (i % 3) * 0.4, T.clock, false, true, i % 4 === 0 ? 1 : 0); }}
                  T.flushTrail(); for (let i = 0; i < 40; i++) T.visuals(0.016, 0.016); T.renderFrame(); return [T.TH.id, T.moverMeshes.map(g => +g.userData.fade.toFixed(2)).join(","), T.P.y.toFixed(2), T.P.air]; }})()""")
                print(dev, r); await pg.screenshot(path=f'gfx/{TAG}_{dev}_{th}.png')
                await pg.evaluate("(() => { __T.state = 'menu'; __T.showMenu(); })()")
            print(dev, errs[:3]); await ctx.close()
        await b.close()
asyncio.run(main())
