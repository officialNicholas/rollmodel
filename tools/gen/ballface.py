# the roller ball's recolor range: a few settings side by side, next to the everyday slime, same light
import asyncio, sys, json, base64, io
from playwright.async_api import async_playwright
from PIL import Image
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
OUT = sys.argv[1] if len(sys.argv) > 1 else 'lumab'
SETS = json.loads(sys.argv[2]) if len(sys.argv) > 2 else [[0.17, 0.83], [0.17, 0.6], [0.17, 0.52]]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 420, 'height': 420}, device_scale_factor=1)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', mode: 'solo', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300]))
        await pg.goto('file://' + SP + 'pc_t.html', timeout=240000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=240000)
        await pg.evaluate("""() => { const T = __T; window.__noLoop = true; T.mode = 'solo'; T.applyMode(); T.genWorld(91, { themes: ["blank"] }); T.mapUsed = false; T.start(); T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {};
          T.setWx('clear', 999); window.__step = (n, f) => { const dt = 1 / 60; for (let i = 0; i < n; i++) { if (f) f(i); T.step(dt); T.visuals(dt, dt); T.flushTrail(); T.matchLeft = 99; } };
          window.__shot = (cam, look) => { T.camera.position.set(cam[0], cam[1], cam[2]); T.camera.lookAt(look[0], look[1], look[2]); T.camera.updateMatrixWorld(); T.renderFrame(); return T.renderer.domElement.toDataURL('image/png'); };
          __step(90, () => { T.steerIn = 0; }); }""")
        frames = []
        # the slime itself first, then the ball at each setting (stopped, face toward the camera)
        d = await pg.evaluate("""() => { const T = __T, P = T.P; __step(30, () => { T.steerIn = 0; P.spd = 0; }); const r = 2.0, c = [P.x + Math.sin(P.yaw + 0.35) * r, P.y + 0.8, P.z + Math.cos(P.yaw + 0.35) * r]; return __shot(c, [P.x, P.y + 0.35, P.z]); }""")
        frames.append(Image.open(io.BytesIO(base64.b64decode(d.split(',')[1]))).convert('RGB'))
        await pg.evaluate("() => { __T.P.power = { type: 'roller', t: 99 }; __step(40, () => { __T.steerIn = 0; __T.P.spd = 0; if (__T.P.power) __T.P.power.t = 99; }); }")
        for st in SETS:
            d = await pg.evaluate("""(st) => { const T = __T, P = T.P, I = T.VP.slime; I.giant.spin.rotation.x = st[0]; I.giant.rollA = st[0];
              __step(2, () => { T.steerIn = 0; P.spd = 0; if (P.power) P.power.t = 99; }); I.giant.spin.rotation.x = st[0]; const r = 1.45, c = [P.x + Math.sin(P.yaw + 0.15) * r, P.y + 0.45, P.z + Math.cos(P.yaw + 0.15) * r]; return __shot(c, [P.x, P.y + 0.28, P.z]); }""", st)
            frames.append(Image.open(io.BytesIO(base64.b64decode(d.split(',')[1]))).convert('RGB'))
        W = frames[0].width; sheet = Image.new('RGB', (W * len(frames), frames[0].height), 'white')
        for i, f in enumerate(frames): sheet.paste(f, (i * W, 0))
        sheet.save(SP + OUT + '.png'); print('errors', errs[:5]); await b.close()
asyncio.run(main())
