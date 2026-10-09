# close-up of the paint bursting off a slime as it leaps out of a refill: frames through the burst
import asyncio, sys, json, base64, io
from playwright.async_api import async_playwright
from PIL import Image
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
GFX = sys.argv[1] if len(sys.argv) > 1 else 'hi'; OUT = sys.argv[2] if len(sys.argv) > 2 else 'burst'; THEME = sys.argv[3] if len(sys.argv) > 3 else 'blank'; ANG = float(sys.argv[4]) if len(sys.argv) > 4 else 0.7
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 420, 'height': 420}, device_scale_factor=1)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: '" + GFX + "', mode: 'solo', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300]))
        await pg.goto('file://' + SP + 'pc_t.html', timeout=240000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=240000)
        await pg.evaluate("""(theme) => { const T = __T; window.__noLoop = true; T.mode = 'solo'; T.applyMode(); T.genWorld(91, { themes: [theme] }); T.mapUsed = false; T.start(); T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {};
          T.setWx('clear', 999); window.__step = (n, f) => { const dt = 1 / 60; for (let i = 0; i < n; i++) { if (f) f(i); T.step(dt); T.visuals(dt, dt); T.flushTrail(); T.matchLeft = 99; } };
          window.__shot = (cam, look) => { T.camera.position.set(cam[0], cam[1], cam[2]); T.camera.lookAt(look[0], look[1], look[2]); T.camera.updateMatrixWorld(); T.renderFrame(); return T.renderer.domElement.toDataURL('image/png'); };
          __step(60, () => { T.steerIn = 0; });
          const pot = T.pots3.find(p => p.st === 'up' || p.st === undefined) || T.pots3[0]; window.__pot = pot; T.enterPot2(T.P, pot); __step(40); }""", THEME)
        frames = []
        # 0: in the refill; then the leap: step until just before the burst, then frame by frame through it
        seq = [('hide', 0), ('leap', 8), ('leap', 8)] + [('burst', 3)] * 9
        for k, (what, n) in enumerate(seq):
            d = await pg.evaluate("""([k, what, n, ang]) => { const T = __T, P = T.P, I = T.VP.slime;
              if (what === 'leap' && P.st === 'hide') T.jump(P);
              if (what === 'burst' && !window.__bursting) { let g = 0; while (!(I.coat.melt) && g++ < 120) __step(1, () => { T.steerIn = 0; }); window.__bursting = true; } else __step(n, () => { T.steerIn = 0; });
              if (!window.__cam0) window.__cam0 = { a: P.yaw + ang }; const a = window.__cam0.a, r = 2.3, c = [P.x + Math.sin(a) * r, P.y + 0.9, P.z + Math.cos(a) * r];
              return [__shot(c, [P.x, P.y + 0.3, P.z]), { st: P.st, y: +P.y.toFixed(2), c: +I.coat.c.toFixed(2), b: +I.coat.b.toFixed(2), melt: I.coat.melt }]; }""", [k, what, n, ANG])
            im = Image.open(io.BytesIO(base64.b64decode(d[0].split(',')[1]))).convert('RGB'); frames.append(im); print(k, what, d[1])
        W = frames[0].width; cols = 6; rows = (len(frames) + cols - 1) // cols; sheet = Image.new('RGB', (W * cols, frames[0].height * rows), 'white')
        for i, f in enumerate(frames): sheet.paste(f, ((i % cols) * W, (i // cols) * f.height))
        sheet.save(SP + OUT + '.png'); print('errors', errs[:5]); await b.close()
asyncio.run(main())
