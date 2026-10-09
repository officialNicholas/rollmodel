# the slime moving in the game, as contact sheets: a jump from the side, a turn from above, and an idle moment from the front
import asyncio, sys, json, base64, io
from playwright.async_api import async_playwright
from PIL import Image
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
GFX = sys.argv[1] if len(sys.argv) > 1 else 'hi'; OUT = sys.argv[2] if len(sys.argv) > 2 else 'seq'; WHICH = sys.argv[3] if len(sys.argv) > 3 else 'jump,turn,idle'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 360, 'height': 360}, device_scale_factor=1)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: '" + GFX + "', mode: 'solo', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300]))
        await pg.goto('file://' + SP + 'pc_t.html', timeout=240000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=240000)
        await pg.evaluate("""() => { const T = __T; window.__noLoop = true; T.mode = 'solo'; T.applyMode(); T.genWorld(91, { themes: ["blank"] }); T.mapUsed = false; T.start(); T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {};
          T.setWx('clear', 999); const P = T.P; window.__step = (n, f) => { const dt = 1 / 60; for (let i = 0; i < n; i++) { if (f) f(i); T.step(dt); T.visuals(dt, dt); T.flushTrail(); T.matchLeft = 99; } };
          window.__shot = (cam, look) => { T.camera.position.set(cam[0], cam[1], cam[2]); T.camera.lookAt(look[0], look[1], look[2]); T.camera.updateMatrixWorld(); T.renderFrame(); return T.renderer.domElement.toDataURL('image/png'); };
          __step(120); }""")
        sheets = {}
        async def seq(name, setup, n, every, cam):
            await pg.evaluate(setup)
            frames = []
            for k in range(n):
                d = await pg.evaluate("([every, cam]) => { __step(every, window.__drive); const P = __T.P; const c = cam(P); return [__shot(c[0], c[1]), { air: P.air, vy: +P.vy.toFixed(2), y: +P.y.toFixed(2), ball: +__T.VP.slime.st.ball.toFixed(2), bend: +__T.VP.slime.st.bend.toFixed(2), ears: __T.VP.slime.st.earL.map(v => +v.toFixed(2)) }]; }".replace('cam(P)', cam), [every, 0])
                frames.append(Image.open(io.BytesIO(base64.b64decode(d[0].split(',')[1]))).convert('RGB')); print(name, k, d[1])
            W = frames[0].width; sheet = Image.new('RGB', (W * min(6, n), frames[0].height * ((n + 5) // 6)), 'white')
            for i, f in enumerate(frames): sheet.paste(f, ((i % 6) * W, (i // 6) * f.height))
            sheet.save(SP + OUT + '_' + name + '.png')
        side = "((P) => { const r = 3.2; return [[P.x + Math.cos(P.yaw) * r, P.y + 0.9, P.z - Math.sin(P.yaw) * r], [P.x, P.y + 0.35, P.z]]; })(P)"
        top = "((P) => [[P.x - Math.sin(P.yaw) * 1.2, P.y + 4.2, P.z - Math.cos(P.yaw) * 1.2], [P.x, P.y, P.z]])(P)"
        front = "((P) => { const r = 1.25; return [[P.x + Math.sin(P.yaw + 0.5) * r, P.y + 0.42, P.z + Math.cos(P.yaw + 0.5) * r], [P.x, P.y + 0.22, P.z]]; })(P)"
        if 'jump' in WHICH:
            await seq('jump', "() => { const T = __T; window.__drive = null; T.steerIn = 0; __step(30); T.jump(T.P); }", 12, 4, side)
        if 'run' in WHICH:
            await seq('run', "() => { const T = __T; window.__drive = () => { T.steerIn = 0; }; }", 12, 3, "((P) => [[P.x - Math.sin(P.yaw) * 0.6, P.y + 3.4, P.z - Math.cos(P.yaw) * 0.6], [P.x + Math.sin(P.yaw) * 0.1, P.y, P.z + Math.cos(P.yaw) * 0.1]])(P)")
        if 'swerve' in WHICH:
            await seq('swerve', "() => { const T = __T; let n = 0; window.__drive = () => { n++; T.steerIn = Math.sin(n / 18) > 0 ? 1 : -1; }; }", 12, 4, "((P) => [[P.x - Math.sin(P.yaw) * 0.6, P.y + 3.4, P.z - Math.cos(P.yaw) * 0.6], [P.x, P.y, P.z]])(P)")
        if 'turn' in WHICH:
            await seq('turn', "() => { const T = __T; window.__drive = () => { T.steerIn = 1; }; }", 12, 6, top)
        if 'tur' in WHICH:
            await seq('tur', "() => { const T = __T; window.__drive = null; T.steerIn = 0; T.startTurret(T.P); __step(40); let k = 0; window.__drive = (i) => { T.P.yaw += 0.02; if (i === 0 && (k++ % 2 === 0)) T.fireShot(T.P); }; }", 12, 8, "((P) => [[P.x + 0.4, P.y + 2.4, P.z + 1.5], [P.x, P.y + 0.3, P.z]])(P)")
        if 'giant' in WHICH:
            await seq('giant', "() => { const T = __T; window.__drive = null; T.P.giantT = 6; T.P.spd = 0; __step(40); let n = 0; window.__drive = (i) => { n++; T.steerIn = n > 120 ? 0.6 : 0; if (n < 120) T.P.spd = 0; }; }", 12, 20, "((P) => { const r = 4.5; return [[P.x + 3.0, P.y + 2.6, P.z + 3.2], [P.x, P.y + 0.6, P.z]]; })(P)")
        if 'idle' in WHICH:
            await seq('idle', "() => { const T = __T; window.__drive = () => { T.steerIn = 0; T.P.spd = 0; }; __step(40); }", 12, 14, front)
        print('errors', errs[:5]); await b.close()
asyncio.run(main())
