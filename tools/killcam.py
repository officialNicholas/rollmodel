"""The first pound knockout in a 1v1: the rival's ragdoll blast and the slow-motion kill cam. Puts the rival just ahead, pounds, then logs
each frame (real ms, the clock, the cam's time, the rival's state and height) and shoots frames. usage: killcam.py [page] [tag]"""
import asyncio, sys, functools
from playwright.async_api import async_playwright
from PIL import Image
print = functools.partial(print, flush=True)
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
PAGE = sys.argv[1] if len(sys.argv) > 1 else 'pc_h.html'; TAG = sys.argv[2] if len(sys.argv) > 2 else 'a'
LOG = """(() => { window.__kc = []; const t0 = performance.now(); const f = () => { const P = __T.P, H = __T.H, K = __T.kcam; __kc.push([Math.round(performance.now() - t0), +__T.matchLeft.toFixed(3), K ? +K.t.toFixed(2) : null, H.st, H.rag ? +H.rag.t.toFixed(2) : null, +H.y.toFixed(2), H.look.drop.visible]); if (__kc.length < 400) requestAnimationFrame(f); }; requestAnimationFrame(f); })()"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__noVote = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{}, drops: 0, runs: 5, mode: 'duel', tut: { ph: 'done' } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); ev = pg.evaluate
        await pg.goto('http://localhost:8765/' + PAGE, timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000, polling=100); await pg.wait_for_timeout(1500)
        await ev("__T.mode = 'duel'; __T.applyMode(); __T.start()"); await pg.wait_for_function("__T.state === 'play' && __T.H.st === 'play'", timeout=400000, polling=100)
        await pg.wait_for_timeout(2500); await pg.wait_for_function("!__T.P.air && __T.P.st === 'play'", timeout=60000, polling=100)
        r = await ev("""(() => { const P = __T.P, H = __T.H; H.ai.thinkT = 9; H.x = P.x + Math.sin(P.yaw) * 1.4; H.z = P.z + Math.cos(P.yaw) * 1.4; H.y = P.y; H.air = false; H.vy = 0; H.spd = 0; H.immuneT = 0;
          P.slamCD = 0; P.paint = 1; const ok = __T.slamReady(P); __T.useSlam(P); return [ok, P.slam, +__T.matchLeft.toFixed(2)]; })()""")
        print('pound', r); await ev(LOG)
        shots = []
        for k in range(10):
            await pg.wait_for_timeout(260); fn = f'{WS}/ui/kc_{TAG}_{k}.png'; await pg.screenshot(path=fn); shots.append(fn)
        await pg.wait_for_timeout(1500); lg = await ev("__kc"); prev = None
        for i, r in enumerate(lg):
            key = (r[2] is None, r[3], r[4] is None, r[6])
            if key != prev or i % 15 == 0: print(r); prev = key
        print("kcam after", await ev("__T.kcam ? __T.kcam.t : null"), "errors", errs[:3]); await b.close()
    ims = [Image.open(f).resize((195, 422)) for f in shots]; w, h = ims[0].size; sh = Image.new('RGB', (w * 5, h * 2), 'white')
    for i, im in enumerate(ims): sh.paste(im, ((i % 5) * w, (i // 5) * h))
    sh.save(f'{WS}/ui/kc_{TAG}_sheet.png'); print(sh.size)
asyncio.run(main())
