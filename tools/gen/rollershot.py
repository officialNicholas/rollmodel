# the roller power-up on the player: close-ups from the side and front while it rolls
import asyncio, sys, json, base64, io
from playwright.async_api import async_playwright
from PIL import Image
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
GFX = sys.argv[1] if len(sys.argv) > 1 else 'hi'; OUT = sys.argv[2] if len(sys.argv) > 2 else 'roller'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 360, 'height': 360}, device_scale_factor=1)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: '" + GFX + "', mode: 'solo', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300]))
        await pg.goto('file://' + SP + 'pc_t.html', timeout=240000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=240000)
        await pg.evaluate("""() => { const T = __T; window.__noLoop = true; T.mode = 'solo'; T.applyMode(); T.genWorld(91, { themes: ["blank"] }); T.mapUsed = false; T.start(); T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {};
          T.setWx('clear', 999); window.__step = (n, f) => { const dt = 1 / 60; for (let i = 0; i < n; i++) { if (f) f(i); T.step(dt); T.visuals(dt, dt); T.flushTrail(); T.matchLeft = 99; } };
          window.__shot = (cam, look) => { T.camera.position.set(cam[0], cam[1], cam[2]); T.camera.lookAt(look[0], look[1], look[2]); T.camera.updateMatrixWorld(); T.renderFrame(); return T.renderer.domElement.toDataURL('image/png'); };
          __step(120); T.P.power = { type: 'roller', t: 99 }; }""")
        frames = []
        for k in range(12):
            d = await pg.evaluate("""(k) => { const T = __T, P = T.P; __step(8, () => { T.steerIn = k < 6 ? 0 : 0.5; if (P.power) P.power.t = 99; });
              const side = k % 2 === 0, r = 2.6, c = side ? [P.x + Math.cos(P.yaw) * r, P.y + 1.0, P.z - Math.sin(P.yaw) * r] : [P.x + Math.sin(P.yaw + 0.4) * r, P.y + 1.0, P.z + Math.cos(P.yaw + 0.4) * r];
              return [__shot(c, [P.x, P.y + 0.4, P.z]), { roll: +T.VP.look.roll.toFixed(2), slimeVis: T.VP.slime.root.visible, old: T.VP.oldBlob.visible, rig: T.VP.rig && T.VP.rig.visible }]; }""", k)
            frames.append(Image.open(io.BytesIO(base64.b64decode(d[0].split(',')[1]))).convert('RGB')); print(k, d[1])
        W = frames[0].width; sheet = Image.new('RGB', (W * 6, frames[0].height * 2), 'white')
        for i, f in enumerate(frames): sheet.paste(f, ((i % 6) * W, (i // 6) * f.height))
        sheet.save(SP + OUT + '.png'); print('errors', errs[:5]); await b.close()
asyncio.run(main())
