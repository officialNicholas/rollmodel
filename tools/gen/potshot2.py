# the slime in a refill and jumping out of it: a sequence from a 3/4 front camera
import asyncio, sys, json, base64, io
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
GFX = sys.argv[1] if len(sys.argv) > 1 else 'hi'; OUT = sys.argv[2] if len(sys.argv) > 2 else 'pot'; THEME = sys.argv[3] if len(sys.argv) > 3 else 'island'; N = int(sys.argv[4]) if len(sys.argv) > 4 else 12; EVERY = int(sys.argv[5]) if len(sys.argv) > 5 else 3
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 400, 'height': 400}, device_scale_factor=1)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: '" + GFX + "', mode: 'solo', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300]))
        await pg.goto('file://' + SP + 'pc_t.html', timeout=240000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=240000)
        await pg.evaluate("""(theme) => { const T = __T; window.__noLoop = true; T.mode = 'solo'; T.applyMode(); T.genWorld(91, { themes: [theme] }); T.mapUsed = false; T.start(); T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {};
          T.setWx('clear', 999); window.__step = (n, f) => { const dt = 1 / 60; for (let i = 0; i < n; i++) { if (f) f(i); T.step(dt); T.visuals(dt, dt); T.flushTrail(); T.matchLeft = 99; } };
          window.__shot = (cam, look) => { T.camera.position.set(cam[0], cam[1], cam[2]); T.camera.lookAt(look[0], look[1], look[2]); T.camera.updateMatrixWorld(); T.renderFrame(); return T.renderer.domElement.toDataURL('image/png'); };
          __step(60, () => { T.steerIn = 0; });
          const pot = T.pots3.find(p => p.st === 'up' || p.st === undefined) || T.pots3[0]; window.__pot = pot; T.enterPot2(T.P, pot); __step(40); }""", THEME)
        frames = []
        for k in range(N):
            d = await pg.evaluate("""([k, every]) => { const T = __T, P = T.P, pot = window.__pot; if (k === 3) { T.jump(P); } __step(k < 3 ? 10 : every, () => { T.steerIn = 0; });
              if (!window.__cam0) window.__cam0 = { a: P.yaw + 0.9 }; const a = window.__cam0.a, r = 4.2, c = [P.x + Math.sin(a) * r, P.y + 1.1, P.z + Math.cos(a) * r];
              return [__shot(c, [P.x, P.y + 0.35, P.z]), { st: P.st, air: P.air, y: +P.y.toFixed(2), vis: T.VP.slime.root.visible, coat: T.VP.slime.coat ? +T.VP.slime.coat.c.toFixed(2) : null }]; }""", [k, EVERY])
            im = Image.open(io.BytesIO(base64.b64decode(d[0].split(',')[1]))).convert('RGB'); frames.append(im); print(k, d[1])
        W = frames[0].width; cols = 6; rows = (len(frames) + cols - 1) // cols; sheet = Image.new('RGB', (W * cols, frames[0].height * rows), 'white')
        for i, f in enumerate(frames): sheet.paste(f, ((i % cols) * W, (i // cols) * f.height))
        sheet.save(SP + OUT + '.png'); print('errors', errs[:5]); await b.close()
asyncio.run(main())
