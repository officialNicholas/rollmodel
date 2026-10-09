# beauty shots of one theme under fixed conditions: python3 gen/beauty.py TAG theme [seed=5151] [dsf=2] [gfx=hi] [views=chase,high,low]
# chase: the real game camera behind the player, placed in an open spot looking into the stage; high: a steep 3/4 look over the stage;
# low: a closer look at the nearest block (trims, strips, ivy). Clear weather, paint trails from a short AI run.
import asyncio, sys
from playwright.async_api import async_playwright
from PIL import Image
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
TAG, TH = sys.argv[1], sys.argv[2]
arg = lambda k, d: next((a[len(k) + 1:] for a in sys.argv[3:] if a.startswith(k + '=')), d)
SEED, DSF, GFX, VIEWS = int(arg('seed', '5151')), int(arg('dsf', '2')), arg('gfx', 'hi'), arg('views', 'chase,high,low').split(',')
STEPS = int(arg('steps', '700')); YAW = arg('yaw', '')
RND = "(() => { let s = 777; Math.random = () => { s = (s * 1664525 + 1013904223) >>> 0; return s / 4294967296; }; })();"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=DSF, has_touch=True, is_mobile=True)
        await ctx.add_init_script(RND)
        await ctx.add_init_script('window.__NATIVE = {"platform":"ios","model":"iPhone16,1","tier":3,"memGB":7.5,"lowPower":false,"thermal":0,"maxFPS":120,"scale":3};')
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: '" + GFX + "', look: { back: 'wings' }, seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: m.type == 'error' and 'ERR_' not in m.text and errs.append(m.text[:300]))
        await pg.goto('file://' + SP + 'pc_t.html'); await pg.wait_for_function('typeof __T === "object"', polling=200, timeout=120000); await pg.wait_for_timeout(500)
        await pg.evaluate("window.__noLoop = true")
        info = await pg.evaluate("""([th, seed, steps, yawO]) => { const T = __T, P = T.P; T.genWorld(seed, { themes: [th] }); T.mapUsed = false; T.start(); window.__noStep = false;
          P.cpu = true; T.aiReset(P);
          const run = n => { for (let i = 0; i < n; i++) { T.setWx('clear', 99); T.steerIn = P.steer || 0; T.step(0.016); if (i % 3 === 2) { T.visuals(0.048, 0.048); T.flushTrail(); } } };
          run(steps); P.cpu = false; T.steerIn = 0;
          // an open spot with room in front, looking toward the middle
          const A = T.ARENA; let best = null, bs = -1;
          for (let k = 0; k < 400; k++) { const x = (Math.sin(k * 12.9898) * 0.5) * A * 1.3, z = (Math.cos(k * 78.233) * 0.5) * A * 1.3; if (T.surfaceUnder(x, z, 40) !== 0) continue;
            const yaw = Math.atan2(-x, -z); let free = 0; for (let t = 0.5; t < 7; t += 0.5) { const px = x + Math.sin(yaw) * t, pz = z + Math.cos(yaw) * t; if (T.surfaceUnder(px, pz, 40) !== 0) break; free = t; }
            const sc = free + Math.hypot(x, z) * 0.15; if (sc > bs) { bs = sc; best = [x, z, yaw]; } }
          if (yawO !== '') best[2] = +yawO;
          P.x = best[0]; P.z = best[1]; P.y = 0; P.yaw = best[2]; P.vx = 0; P.vz = 0; P.spd = 0; T.camYaw = best[2];
          for (let i = 0; i < 60; i++) T.visuals(0.016, 0.016); T.flushTrail(); document.getElementById('banner').style.display = 'none'; document.getElementById('hud').classList.add('off'); T.renderFrame();
          return [T.TH.id, best.map(v => +v.toFixed(2))]; }""", [TH, SEED, STEPS, YAW])
        print('spot', info)
        shots = []
        for v in VIEWS:
            if v.startswith('chase'):
                yv = v.split('@')[1] if '@' in v else ''
                await pg.evaluate("""(yv) => { const T = __T, P = T.P; if (yv !== '') { P.yaw = +yv; T.camYaw = +yv; for (let i = 0; i < 60; i++) T.visuals(0.016, 0.016); } T.renderFrame(); }""", yv)
            elif v == 'high':
                await pg.evaluate("(() => { const T = __T, c = T.camera, P = T.P; c.position.set(P.x - Math.sin(P.yaw) * 9, 15.5, P.z - Math.cos(P.yaw) * 9); c.lookAt(P.x + Math.sin(P.yaw) * 6, 0, P.z + Math.cos(P.yaw) * 6); T.renderFrame(); })()")
            elif v == 'low':
                await pg.evaluate("""(() => { const T = __T, c = T.camera, P = T.P; let bb = null, bd = 1e9; for (const b of T.BOXES) { if (b[4] > 0 || b[6] === 'c' || b[6] === 'g' || b[5] - b[4] < 0.7) continue; const cx = (b[0] + b[1]) / 2, cz = (b[2] + b[3]) / 2, d = Math.hypot(cx - P.x, cz - P.z); if (d < bd) { bd = d; bb = b; } }
                  if (!bb) return; const cx = (bb[0] + bb[1]) / 2, cz = (bb[2] + bb[3]) / 2, a = Math.atan2(P.x - cx, P.z - cz), r = Math.max(bb[1] - bb[0], bb[3] - bb[2]) * 0.5 + 3.2;
                  c.position.set(cx + Math.sin(a + 0.5) * r, 3.4, cz + Math.cos(a + 0.5) * r); c.lookAt(cx, bb[5] * 0.45, cz); T.renderFrame(); })()""")
            elif v == 'ivy':
                await pg.evaluate("""(() => { const T = __T, c = T.camera, P = T.P, L = T.IVY.L; if (!L.length) return; let best = null, bd = 1e9; for (let i = 0; i < L.length; i += 7) { const q = L[i], d = Math.hypot(q[0] - P.x, q[2] - P.z) + (q[1] < 0.3 ? 3 : 0); if (d < bd) { bd = d; best = q; } }
                  const a = Math.atan2(P.x - best[0], P.z - best[2]); c.position.set(best[0] + Math.sin(a) * 2.6, best[1] + 1.4, best[2] + Math.cos(a) * 2.6); c.lookAt(best[0], best[1] - 0.2, best[2]); T.renderFrame(); })()""")
            elif v == 'menu':
                await pg.evaluate("(() => { const T = __T; T.state = 'menu'; T.showMenu(); document.getElementById('hud').classList.remove('off'); for (let i = 0; i < 40; i++) T.visuals(0.016, 0.05); T.renderFrame(); })()")
            f = f'{SP}st/{TAG}_{v.replace("@", "_")}.png'; await pg.screenshot(path=f); shots.append(f)
        print(TAG, errs[:4]); await b.close()
    W, H = 390, 844; ims = [Image.open(f).convert('RGB').resize((W, H)) for f in shots]
    o = Image.new('RGB', (len(ims) * W + (len(ims) - 1) * 6, H), (16, 16, 16))
    for i, im in enumerate(ims): o.paste(im, (i * (W + 6), 0))
    o.save(f'{SP}st/{TAG}_sheet.png'); print('sheet', o.size)
asyncio.run(main())
