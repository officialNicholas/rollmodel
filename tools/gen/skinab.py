# close-ups of the slime's skin (scales, sheen) from a few sides, standing still and then moving through paint
import asyncio, sys, json, base64, io
from playwright.async_api import async_playwright
from PIL import Image
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
GFX = sys.argv[1] if len(sys.argv) > 1 else 'hi'; OUT = sys.argv[2] if len(sys.argv) > 2 else 'skin'; THEME = sys.argv[3] if len(sys.argv) > 3 else 'island'
K = json.loads(sys.argv[4]) if len(sys.argv) > 4 else None
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 480, 'height': 480}, device_scale_factor=1)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: '" + GFX + "', mode: 'solo', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300])); pg.on('console', lambda m: errs.append('CONSOLE ' + m.text[:300]) if m.type == 'error' else None)
        await pg.goto('file://' + SP + 'pc_t.html', timeout=240000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=240000)
        await pg.evaluate("""([theme, K]) => { const T = __T; window.__noLoop = true; T.mode = 'solo'; T.applyMode(); T.genWorld(91, { themes: [theme] }); T.mapUsed = false; T.start(); T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {};
          T.setWx('clear', 999); window.__step = (n, f) => { const dt = 1 / 60; for (let i = 0; i < n; i++) { if (f) f(i); T.step(dt); T.visuals(dt, dt); T.flushTrail(); T.matchLeft = 99; } };
          window.__shot = (cam, look) => { T.camera.position.set(cam[0], cam[1], cam[2]); T.camera.lookAt(look[0], look[1], look[2]); T.camera.updateMatrixWorld(); T.renderFrame(); return T.renderer.domElement.toDataURL('image/png'); };
          __step(60, () => { T.steerIn = 0; });
          let best = null; for (let i = 0; i < 400; i++) { const x = (Math.random() * 2 - 1) * 18, z = (Math.random() * 2 - 1) * 18; let ok = 0; for (let k = 0; k < 24; k++) { const a = k / 24 * 6.283, r = 1 + (k % 3) * 1.5; const h = T.surfaceUnder(x + Math.cos(a) * r, z + Math.sin(a) * r, 3, true); if (Math.abs(h) < 0.05) ok++; } if (!best || ok > best[2]) best = [x, z, ok]; }
          const P = T.P; P.x = best[0]; P.z = best[1]; P.y = 0; P.yaw = 0.3; __step(30, () => { T.steerIn = 0; P.spd = 0; }); if (K) T.SLIME.SCALE_K.value.set(...K); }""", [THEME, K])
        shots = []
        for kk in json.loads(sys.argv[5]): shots += [('k', 2.6, 1.0, 0.75, kk), ('k', 0.75, 1.05, 0.72, kk)]
        frames = []
        for name, ang, r, h, mode in shots:
            d = await pg.evaluate("""([ang, r, h, mode]) => { const T = __T, P = T.P;
              T.SLIME.SCALE_K.value.set(...mode); __step(2, () => { T.steerIn = 0; P.spd = 0; });
              const c = [P.x + Math.sin(P.yaw + ang) * r, P.y + h, P.z + Math.cos(P.yaw + ang) * r]; return [__shot(c, [P.x, P.y + 0.32, P.z]), { wade: +(T.VP.wade || 0).toFixed(2), spd: +P.spd.toFixed(2) }]; }""", [ang, r, h, mode])
            frames.append(Image.open(io.BytesIO(base64.b64decode(d[0].split(',')[1]))).convert('RGB')); print(name, d[1])
        W = frames[0].width; cols = 4; rows = (len(frames) + cols - 1) // cols; sheet = Image.new('RGB', (W * cols, frames[0].height * rows), 'white')
        for i, f in enumerate(frames): sheet.paste(f, ((i % cols) * W, (i // cols) * f.height))
        sheet.save(SP + OUT + '.png'); print('errors', errs[:5]); await b.close()
asyncio.run(main())
