# camera candidates on one seeded garden moment: python3 gen/camproto.py TAG theme
import asyncio, json, sys
from playwright.async_api import async_playwright
U = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
TAG = sys.argv[1]; TH = sys.argv[2] if len(sys.argv) > 2 else 'garden'
SEED = "(() => { let s = 777; Math.random = () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; })();"
CANDS = [('a_now', 7.0, 6.0, 80), ('b', 10.4, 5.4, 62), ('c', 9.0, 5.0, 66), ('d', 11.5, 6.2, 56)]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script('window.__NATIVE = {"platform":"ios","model":"iPhone16,1","tier":3,"memGB":7.5,"lowPower":false,"thermal":0,"maxFPS":120,"scale":3};')
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', look: { back: 'wings' }, seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=60000); await pg.wait_for_timeout(800)
        r = await pg.evaluate("""([seed, th]) => { const T = __T, P = T.P; window.__noLoop = true; eval(seed);
          T.genWorld(5151, { themes: [th] }); T.mapUsed = false; T.start(); window.__noStep = false;
          P.cpu = true; T.aiReset(P);
          const run = n => { for (let i = 0; i < n; i++) { T.steerIn = P.steer || 0; T.step(0.016); if (i % 3 === 2) { T.visuals(0.048, 0.048); T.flushTrail(); } } };
          const clean = () => P.st === 'play' && !P.air && !P.power && !(P.giantT > 0) && T.wx === 'clear' && P.paint > 0.2 && !T.POTS.slice(0, 8).some(q => Math.hypot(q[0] - P.x, q[2] - P.z) < 6.5);
          run(700); let extra = 0; while (!clean() && extra < 400) { run(10); extra += 10; }
          P.cpu = false; T.steerIn = 0; for (let i = 0; i < 24; i++) T.visuals(0.016, 0.016); T.flushTrail();
          document.getElementById('banner').style.display = 'none';
          return [P.x.toFixed(1), P.z.toFixed(1), T.camYaw.toFixed(2), extra]; }""", [SEED, TH])
        print(r)
        for name, h, back, fov in CANDS:
            await pg.evaluate("""([h, back, fov]) => { const T = __T, P = T.P, c = T.camera, a = T.camYaw, fx = Math.sin(a), fz = Math.cos(a);
              c.position.set(P.x - fx * back, P.y + h, P.z - fz * back); c.up.set(0, 1, 0); c.lookAt(P.x + fx * 2.4, P.y - 0.4, P.z + fz * 2.4); c.fov = fov; c.updateProjectionMatrix(); T.renderFrame(); }""", [h, back, fov])
            await pg.screenshot(path=f'fin/cam_{TAG}_{name}.png')
        print(errs[:3]); await b.close()
asyncio.run(main())
