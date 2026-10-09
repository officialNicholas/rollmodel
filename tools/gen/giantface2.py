# every look the slime takes in a match, from the same 3/4 front camera: everyday, jumping, roller, turret, turret firing, giant sitting,
# giant rolling, rocket, bat wings, flattened, knocked out
import asyncio, sys, json, base64, io
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
GFX = sys.argv[1] if len(sys.argv) > 1 else 'hi'; OUT = sys.argv[2] if len(sys.argv) > 2 else 'forms'; THEME = sys.argv[3] if len(sys.argv) > 3 else 'blank'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 400, 'height': 400}, device_scale_factor=1)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: '" + GFX + "', mode: 'solo', look: { head: 'hat' }, seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300]))
        await pg.goto('file://' + SP + 'pc_t.html', timeout=240000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=240000)
        await pg.evaluate("""(theme) => { const T = __T; window.__noLoop = true; T.mode = 'solo'; T.applyMode(); T.genWorld(91, { themes: [theme] }); T.mapUsed = false; T.start(); T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {};
          T.setWx('clear', 999); window.__step = (n, f) => { const dt = 1 / 60; for (let i = 0; i < n; i++) { if (f) f(i); T.step(dt); T.visuals(dt, dt); T.flushTrail(); T.matchLeft = 99; } };
          window.__shot = (cam, look) => { T.camera.position.set(cam[0], cam[1], cam[2]); T.camera.lookAt(look[0], look[1], look[2]); T.camera.updateMatrixWorld(); T.renderFrame(); return T.renderer.domElement.toDataURL('image/png'); };
          window.__clear = () => { const P = T.P; P.power = null; P.turret = null; P.giantT = 0; P.rocket = null; P.batT = 0; P.flatT = 0; P.stunT = 0; };
          __step(90, () => { T.steerIn = 0; });
          let best = null; for (let i = 0; i < 400; i++) { const x = (Math.random() * 2 - 1) * 18, z = (Math.random() * 2 - 1) * 18; let ok = 0; for (let k = 0; k < 24; k++) { const a = k / 24 * 6.283, r = 1 + (k % 3) * 1.5; const h = T.surfaceUnder(x + Math.cos(a) * r, z + Math.sin(a) * r, 3, true); if (Math.abs(h) < 0.05) ok++; } if (!best || ok > best[2]) best = [x, z, ok]; }
          const P = T.P; P.x = best[0]; P.z = best[1]; P.y = 0; P.yaw = 0.3; __step(20, () => { T.steerIn = 0; P.spd = 0; }); }""", THEME)
        shots = [
          ('giant sit front', "() => { __clear(); __T.P.giantT = 30; __step(50, () => { __T.P.spd = 0; __T.steerIn = 0; }); }", 1.9, 3.6, 0.0),
          ('giant sit front close', "() => { __step(2, () => { __T.P.spd = 0; __T.steerIn = 0; }); }", 1.4, 2.6, 0.15),
          ('giant sit 3/4', "() => { __step(2, () => { __T.P.spd = 0; __T.steerIn = 0; }); }", 1.6, 3.2, 0.7),
          ('slime front', "() => { __clear(); __step(60, () => { __T.P.spd = 0; __T.steerIn = 0; }); }", 1.0, 2.0, 0.0),
          ('turret front', "() => { __clear(); __T.startTurret(__T.P); __step(50); }", 1.3, 2.4, 0.0),
          ('roller front', "() => { __clear(); __T.P.power = { type: 'roller', t: 99 }; __step(50, () => { __T.steerIn = 0; __T.P.spd = 0; if (__T.P.power) __T.P.power.t = 99; }); }", 1.0, 2.0, 0.0),
        ]
        frames = []
        for name, setup, h, r, ang in shots:
            try:
                await pg.evaluate(setup)
                d = await pg.evaluate("""([h, r, ang]) => { const P = __T.P; const c = [P.x + Math.sin(P.yaw + ang) * r, P.y + h, P.z + Math.cos(P.yaw + ang) * r]; return [__shot(c, [P.x, P.y + 0.35 + (h - 0.9) * 0.4, P.z]), { form: __T.VP.slime.form, vis: __T.VP.slime.root.visible, old: __T.VP.oldBlob.visible, ball: +__T.VP.slime.st.ball.toFixed(2) }]; }""", [h, r, ang])
                im = Image.open(io.BytesIO(base64.b64decode(d[0].split(',')[1]))).convert('RGB'); ImageDraw.Draw(im).text((8, 8), name, fill=(20, 20, 20)); frames.append(im); print(name, d[1])
            except Exception as e:
                print(name, 'ERR', str(e)[:200])
        W = frames[0].width; cols = 3; rows = (len(frames) + cols - 1) // cols; sheet = Image.new('RGB', (W * cols, frames[0].height * rows), 'white')
        for i, f in enumerate(frames): sheet.paste(f, ((i % cols) * W, (i // cols) * f.height))
        sheet.save(SP + OUT + '.png'); print('errors', errs[:5]); await b.close()
asyncio.run(main())
