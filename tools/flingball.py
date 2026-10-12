"""The slingshot's jelly ball timing in a match: a full-pull fling, then each frame: in the air, time to land, which body shows (the ball or
the axolotl), and the animator's state; plus frames from the play camera. usage: flingball.py [page] [tag]"""
import asyncio, sys, functools
from playwright.async_api import async_playwright
print = functools.partial(print, flush=True)
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
PAGE = sys.argv[1] if len(sys.argv) > 1 else 'pc_h.html'; TAG = sys.argv[2] if len(sys.argv) > 2 else 'a'
LOG = """(() => { window.__fb = []; const f = () => { const P = __T.P, I = __T.VP.slime, V = I && __T.lookOf ? null : null;
  __fb.push([+__T.runT.toFixed(2), P.air ? 1 : 0, +P.vy.toFixed(1), +(P.y).toFixed(2), I.root.visible ? 'axo' : 'ball', P.flung ? 1 : 0]);
  if (__fb.length < 600) requestAnimationFrame(f); }; requestAnimationFrame(f); })()"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 360, 'height': 640}, device_scale_factor=1, has_touch=True)
        await ctx.add_init_script("window.__noVote = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{}, drops: 0, runs: 5, mode: 'solo', tut: { ph: 'done' } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); ev = pg.evaluate
        await pg.goto('http://localhost:8765/' + PAGE, timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000, polling=100); await pg.wait_for_timeout(1500)
        await ev("__T.mode = 'solo'; __T.applyMode(); __T.start()"); await pg.wait_for_function("__T.state === 'play'", timeout=400000, polling=100)
        await pg.wait_for_function("!__T.P.air && __T.P.spd > 3", timeout=60000, polling=100); await pg.wait_for_timeout(1200)
        await ev("__T.startCharge(__T.P)"); await pg.wait_for_timeout(300); await ev(LOG); await ev("__T.P.charge = 1; __T.P.pullTgt = 1; __T.fling(__T.P, 1)")
        shots = []
        for k in range(8):
            await pg.wait_for_timeout(150); fn = f'{WS}/ui/fb_{TAG}_{k}.png'; await pg.screenshot(path=fn); shots.append(fn)
        await pg.wait_for_function("!__T.P.air", timeout=20000, polling=50); await pg.wait_for_timeout(400)
        lg = await ev("__fb"); prev = None
        for r in lg:
            key = (r[1], r[4]); 
            if key != prev: print(r); prev = key
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
