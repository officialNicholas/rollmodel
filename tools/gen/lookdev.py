# look-dev renders of the slime: a few angles in a day stage and a night stage (stills, no wading), optionally with material overrides
#   python3 gen/lookdev.py out '{"stages":["island","crypt"], "mat": {...}, "K": [..]}'
import asyncio, sys, json, base64, io
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
OUT = sys.argv[1] if len(sys.argv) > 1 else 'lookdev'; CFG = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
STAGES = CFG.get('stages', ['island', 'crypt']); GFX = CFG.get('gfx', 'hi'); SIZE = CFG.get('size', 420)
ANGLES = CFG.get('angles', [[0.55, 1.25, 0.62], [1.7, 1.35, 0.7], [2.7, 1.3, 0.8]])
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        frames = []
        for stage in STAGES:
            ctx = await b.new_context(viewport={'width': SIZE, 'height': SIZE}, device_scale_factor=1)
            await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: '" + GFX + "', mode: 'solo', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1} })); } catch (e) {}")
            pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300]))
            await pg.goto('file://' + SP + (CFG.get('page') or 'pc_t.html'), timeout=240000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=240000)
            await pg.evaluate("""([stage, cfg]) => { const T = __T; window.__noLoop = true; T.mode = 'solo'; T.applyMode(); T.genWorld(91, { themes: [stage] }); T.mapUsed = false; T.start(); T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {};
              T.setWx('clear', 999); window.__step = (n, f) => { const dt = 1 / 60; for (let i = 0; i < n; i++) { if (f) f(i); T.step(dt); T.visuals(dt, dt); T.flushTrail(); T.matchLeft = 99; } };
              window.__shot = (cam, look) => { T.camera.position.set(cam[0], cam[1], cam[2]); T.camera.lookAt(look[0], look[1], look[2]); T.camera.updateMatrixWorld(); T.renderFrame(); return T.renderer.domElement.toDataURL('image/png'); };
              __step(40, () => { T.steerIn = 0; });
              let best = null; for (let i = 0; i < 500; i++) { const x = (Math.random() * 2 - 1) * 16, z = (Math.random() * 2 - 1) * 16; let ok = 0; for (let k = 0; k < 24; k++) { const a = k / 24 * 6.283, r = 0.8 + (k % 3) * 1.2; const h = T.surfaceUnder(x + Math.cos(a) * r, z + Math.sin(a) * r, 3, true); if (Math.abs(h) < 0.05 && !T.blockedAt(x + Math.cos(a) * r, z + Math.sin(a) * r, 0)) ok++; } if (!best || ok > best[2]) best = [x, z, ok]; if (ok >= 24) break; }
              const P = T.P; P.x = best[0]; P.z = best[1]; P.y = 0; P.yaw = 0.3; window.__wadeOff = true;
              __step(20, () => { T.steerIn = 0; P.spd = 0; });
              if (cfg.K) T.SLIME.SCALE_K.value.set(...cfg.K);
              const I = T.VP.slime; if (cfg.mat) for (const k in I.mats) { const m = I.mats[k].body; for (const [a, v] of Object.entries(cfg.mat)) { if (a in m) { if (m[a] && m[a].isColor) m[a].set(v); else m[a] = v; } } m.needsUpdate = !!cfg.recompile; }
              if (cfg.expr) I.setExpression(cfg.expr); }""", [stage, CFG])
            for ang, r, h in ANGLES:
                d = await pg.evaluate("""([ang, r, h]) => { const T = __T, P = T.P; __step(3, () => { T.steerIn = 0; P.spd = 0; T.VP.wade = 0; });
                  T.VP.slime.U.sWade.value.x = 0; const c = [P.x + Math.sin(P.yaw + ang) * r, P.y + h, P.z + Math.cos(P.yaw + ang) * r]; return __shot(c, [P.x, P.y + 0.3, P.z]); }""", [ang, r, h])
                im = Image.open(io.BytesIO(base64.b64decode(d.split(',')[1]))).convert('RGB'); frames.append(im)
            print(stage, 'errors', errs[:3]); await ctx.close()
        W = frames[0].width; cols = len(ANGLES); rows = (len(frames) + cols - 1) // cols; sheet = Image.new('RGB', (W * cols, frames[0].height * rows), 'white')
        for i, f in enumerate(frames): sheet.paste(f, ((i % cols) * W, (i // cols) * f.height))
        sheet.save(SP + OUT + '.png'); await b.close()
asyncio.run(main())
