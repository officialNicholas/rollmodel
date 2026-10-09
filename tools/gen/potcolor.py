# a refill's paint: off-white when fresh, a rival's color once it jumps in, yours once you splat right by it
import asyncio, sys, json, base64, io
from playwright.async_api import async_playwright
from PIL import Image
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
OUT = sys.argv[1] if len(sys.argv) > 1 else 'potcolor'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        frames = []
        for stage in ['blank', 'island', 'crypt']:
            ctx = await b.new_context(viewport={'width': 320, 'height': 320}, device_scale_factor=1)
            await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', mode: 'duel', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1} })); } catch (e) {}")
            pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300]))
            await pg.goto('file://' + SP + 'pc_t.html', timeout=240000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=240000)
            r = await pg.evaluate("""(stage) => { const T = __T; window.__noLoop = true; T.mode = 'duel'; T.applyMode(); T.genWorld(91, { themes: [stage] }); T.mapUsed = false; T.start(); T.AU.init(); for (const k in T.AU) if (typeof T.AU[k] === 'function' && k !== 'init') T.AU[k] = () => {};
              T.setWx('clear', 999); window.__step = (n, f) => { const dt = 1 / 60; for (let i = 0; i < n; i++) { if (f) f(i); T.step(dt); T.visuals(dt, dt); T.flushTrail(); T.matchLeft = 99; } };
              window.__shot = (cam, look) => { T.camera.position.set(cam[0], cam[1], cam[2]); T.camera.lookAt(look[0], look[1], look[2]); T.camera.updateMatrixWorld(); T.renderFrame(); return T.renderer.domElement.toDataURL('image/png'); };
              __step(20); const P = T.P, H = T.H; H.ai = null;
              // the refill furthest from everyone (so nobody wanders in), the players parked well away
              const pot = T.pots3.filter(q => q.st === 'up').sort((a, b) => Math.hypot(b.x - P.x, b.z - P.z) - Math.hypot(a.x - P.x, a.z - P.z))[0]; window.__pot = pot;
              return { n: T.pots3.length, team: pot.paintTeam }; }""", stage)
            for what in ['fresh', 'rival jumps in', 'you splat by it']:
                d = await pg.evaluate("""(what) => { const T = __T, P = T.P, H = T.H, pot = window.__pot;
                  if (what === 'rival jumps in') { T.enterPot2(H, pot); __step(30); T.knockOut && 0; H.st = 'play'; pot.occ = null; H.pot = null; H.x = pot.x + 6; H.z = pot.z; __step(40); }
                  if (what === 'you splat by it') { T.addSplat(pot.x + 1.0, pot.y, pot.z, 0, 1.4, T.clock, false, true, 0); __step(40); }
                  if (what === 'fresh') __step(5);
                  const c = [pot.x + 1.4, pot.y + 2.2, pot.z + 1.4]; return [__shot(c, [pot.x, pot.y + 0.3, pot.z]), { team: pot.paintTeam, col: pot.paintC.getHexString() }]; }""", what)
                frames.append(Image.open(io.BytesIO(base64.b64decode(d[0].split(',')[1]))).convert('RGB')); print(stage, what, d[1])
            print(stage, 'errors', errs[:3]); await ctx.close()
        W = frames[0].width; cols = 3; rows = (len(frames) + 2) // 3; sheet = Image.new('RGB', (W * cols, frames[0].height * rows), 'white')
        for i, f in enumerate(frames): sheet.paste(f, ((i % cols) * W, (i // cols) * f.height))
        sheet.save(SP + OUT + '.png'); await b.close()
asyncio.run(main())
