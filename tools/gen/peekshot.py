# a slime down in a refill: a blob with its eyes over the rim, watching a rival as it moves round (close 3/4 view, and the game's view)
import asyncio, sys, json, base64, io
from playwright.async_api import async_playwright
from PIL import Image
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
OUT = sys.argv[1] if len(sys.argv) > 1 else 'peek'; THEME = sys.argv[2] if len(sys.argv) > 2 else 'blank'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 360, 'height': 360}, device_scale_factor=1)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', mode: 'duel', look: { head: 'halo' }, seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300]))
        await pg.goto('file://' + SP + 'pc_t.html', timeout=240000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=240000)
        await pg.evaluate("""(theme) => { const T = __T; window.__noLoop = true; T.mode = 'duel'; T.applyMode(); T.genWorld(91, { themes: [theme] }); T.mapUsed = false; T.start(); T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {};
          T.setWx('clear', 999); window.__step = (n, f) => { const dt = 1 / 60; for (let i = 0; i < n; i++) { if (f) f(i); T.step(dt); T.visuals(dt, dt); T.flushTrail(); T.matchLeft = 99; } };
          window.__shot = (cam, look) => { T.camera.position.set(cam[0], cam[1], cam[2]); T.camera.lookAt(look[0], look[1], look[2]); T.camera.updateMatrixWorld(); T.renderFrame(); return T.renderer.domElement.toDataURL('image/png'); };
          __step(40);
          const pot = T.pots3.find(q => q.st === 'up' || q.st === undefined) || T.pots3[0]; window.__pot = pot; T.enterPot2(T.P, pot); T.P.yaw = 0; __step(30);
          const H = T.H; H.ai = null; }""", THEME)
        frames = []
        # the rival walks a circle round the refill; frames from a close 3/4 view (top row) and from behind-above like the game (bottom row)
        angs = [0.0, 1.2, 2.4, -1.2, -2.4, 0.6]
        for view in ['close', 'game']:
            for a in angs:
                d = await pg.evaluate("""([a, view]) => { const T = __T, P = T.P, H = T.H, pot = window.__pot; const r = 3.2;
                  __step(20, () => { H.x = pot.x + Math.sin(a) * r; H.z = pot.z + Math.cos(a) * r; H.y = pot.y; H.spd = 0; H.st = 'play'; });
                  const c = view === 'close' ? [pot.x + 0.9, pot.y + 2.0, pot.z + 1.2] : [pot.x - Math.sin(P.yaw) * 1.7, pot.y + 2.6, pot.z - Math.cos(P.yaw) * 1.7];
                  const S = T.VP.slime.st; return [__shot(c, [pot.x, pot.y + 0.45, pot.z]), { st: P.st, head: S.head.map(v => +v.toFixed(2)), look: S.look.map(v => +v.toFixed(2)), coat: +T.VP.slime.coat.b.toFixed(2), sink: +(T.VP.sink || 0).toFixed(2), expr: S.exprB }]; }""", [a, view])
                frames.append(Image.open(io.BytesIO(base64.b64decode(d[0].split(',')[1]))).convert('RGB')); print(view, a, d[1])
        W = frames[0].width; cols = 6; sheet = Image.new('RGB', (W * cols, frames[0].height * 2), 'white')
        for i, f in enumerate(frames): sheet.paste(f, ((i % cols) * W, (i // cols) * f.height))
        sheet.save(SP + OUT + '.png'); print('errors', errs[:5]); await b.close()
asyncio.run(main())
