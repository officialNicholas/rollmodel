# the roller's handle: running, a jump (up, floating, the landing slap and bounce), then pulling up to a stop and sitting still
import asyncio, sys, json, base64, io
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
GFX = sys.argv[1] if len(sys.argv) > 1 else 'hi'; OUT = sys.argv[2] if len(sys.argv) > 2 else 'handle'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 340, 'height': 340}, device_scale_factor=1)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: '" + GFX + "', mode: 'solo', look: { head: 'hat' }, seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300]))
        await pg.goto('file://' + SP + 'pc_t.html', timeout=240000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=240000)
        await pg.evaluate("""() => { const T = __T; window.__noLoop = true; T.mode = 'solo'; T.applyMode(); T.genWorld(91, { themes: ['island'] }); T.mapUsed = false; T.start(); T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {};
          T.setWx('clear', 999); window.__step = (n, f) => { const dt = 1 / 60; for (let i = 0; i < n; i++) { if (f) f(i); T.step(dt); T.visuals(dt, dt); T.flushTrail(); T.matchLeft = 99; } };
          window.__shot = (cam, look) => { T.camera.position.set(cam[0], cam[1], cam[2]); T.camera.lookAt(look[0], look[1], look[2]); T.camera.updateMatrixWorld(); T.renderFrame(); return T.renderer.domElement.toDataURL('image/png'); };
          __step(60);
          let best = null; for (let i = 0; i < 500; i++) { const x = (Math.random() * 2 - 1) * 20, z = (Math.random() * 2 - 1) * 20, a = Math.random() * 6.283; let ok = 0;
            for (let st = 0; st < 30; st++) { const px = x + Math.sin(a) * st * 0.5, pz = z + Math.cos(a) * st * 0.5, h = T.surfaceUnder(px, pz, 3, true); if (Math.abs(h) > 0.05 || T.blockedAt(px, pz, 0)) break; ok++; } if (!best || ok > best[3]) best = [x, z, a, ok]; }
          const P = T.P; P.x = best[0]; P.z = best[1]; P.y = 0; P.yaw = best[2]; P.power = { type: 'roller', t: 99 }; __step(40, () => { T.steerIn = 0; if (P.power) P.power.t = 99; }); }""")
        plan = [('run', 4, None)] * 2 + [('jump', 1, 'jump')] + [('air', 4, None)] * 7 + [('land', 4, None)] * 3 + [('brake', 3, 'stop')] + [('stopping', 4, 'hold')] * 4 + [('still', 12, 'hold')] * 2
        frames = []
        for name, n, act in plan:
            d = await pg.evaluate("""([n, act]) => { const T = __T, P = T.P; if (act === 'jump') T.jump(P);
              __step(n, () => { T.steerIn = 0; if (P.power) P.power.t = 99; if (act === 'stop' || act === 'hold') { P.spd = Math.max(0, P.spd - 0.6); P.charging = false; } });
              if (!window.__ca) window.__ca = P.yaw; const a = window.__ca + 1.35, r = 3.0, c = [P.x + Math.sin(a) * r, Math.max(P.y, 0) + 1.0, P.z + Math.cos(a) * r];
              return [__shot(c, [P.x, P.y + 0.35, P.z]), { air: P.air, y: +P.y.toFixed(2), spd: +P.spd.toFixed(2), hdl: +(T.VP.hdl ? T.VP.hdl.a : 0).toFixed(2), old: T.VP.oldBlob.visible }]; }""", [n, act])
            im = Image.open(io.BytesIO(base64.b64decode(d[0].split(',')[1]))).convert('RGB'); ImageDraw.Draw(im).text((6, 6), name + ' ' + str(d[1]['hdl']), fill=(20, 20, 20)); frames.append(im); print(name, d[1])
        W = frames[0].width; cols = 6; rows = (len(frames) + cols - 1) // cols; sheet = Image.new('RGB', (W * cols, frames[0].height * rows), 'white')
        for i, f in enumerate(frames): sheet.paste(f, ((i % cols) * W, (i // cols) * f.height))
        sheet.save(SP + OUT + '.png'); print('errors', errs[:5]); await b.close()
asyncio.run(main())
