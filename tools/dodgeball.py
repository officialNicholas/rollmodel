"""The dodge roll's jelly ball in a match: roll, then each frame which body shows (the ball or the axolotl) against the roll timer, plus
frames from the play camera. usage: dodgeball.py [page] [tag]"""
import asyncio, sys, functools
from playwright.async_api import async_playwright
from PIL import Image
print = functools.partial(print, flush=True)
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
PAGE = sys.argv[1] if len(sys.argv) > 1 else 'pc_h.html'; TAG = sys.argv[2] if len(sys.argv) > 2 else 'a'
LOG = """(() => { window.__db = []; const f = () => { const P = __T.P, I = __T.VP.slime; __db.push([+__T.runT.toFixed(2), +P.rollT.toFixed(2), I.root.visible ? 'axo' : 'ball']); if (__db.length < 240) requestAnimationFrame(f); }; requestAnimationFrame(f); })()"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 360, 'height': 640}, device_scale_factor=1, has_touch=True)
        await ctx.add_init_script("window.__noVote = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{}, drops: 0, runs: 5, mode: 'solo', tut: { ph: 'done' } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); ev = pg.evaluate
        await pg.goto('http://localhost:8765/' + PAGE, timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000, polling=100); await pg.wait_for_timeout(1500)
        await ev("__T.mode = 'solo'; __T.applyMode(); __T.start()"); await pg.wait_for_function("__T.state === 'play'", timeout=400000, polling=100)
        await pg.wait_for_function("!__T.P.air && __T.P.spd > 3", timeout=60000, polling=100); await pg.wait_for_timeout(1200)
        await ev(LOG); print('rolled', await ev("__T.dodgeRoll(__T.P)"))
        shots = []
        for k in range(8):
            await pg.wait_for_timeout(90); fn = f'{WS}/ui/db_{TAG}_{k}.png'; await pg.screenshot(path=fn); shots.append(fn)
        await pg.wait_for_timeout(600); lg = await ev("__db"); prev = None
        for r in lg:
            if r[2] != prev: print(r); prev = r[2]
        print('errors', errs[:3]); await b.close()
    ims = [Image.open(f).crop((40, 150, 320, 470)) for f in shots]; w, h = ims[0].size; sh = Image.new('RGB', (w * 4, h * 2), 'white')
    for i, im in enumerate(ims): sh.paste(im, ((i % 4) * w, (i // 4) * h))
    sh.save(f'{WS}/ui/db_{TAG}_sheet.png'); print(sh.size)
asyncio.run(main())
