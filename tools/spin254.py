"""v254 spin probes. usage: spin254.py PAGE TAG [locker|lockfast|vic]
  locker    a drag-sized turn in the locker (shim target +2.4 rad), top and front cameras
  lockfast  a flick (target +5 rad), top camera"""
import asyncio, sys
from playwright.async_api import async_playwright
sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/tools')
from h254 import *
PAGE, TAG = sys.argv[1], sys.argv[2]; SC = sys.argv[3:] or ['locker']
async def locker(b, sc):
    for cam in (['game', 'top'] if sc == 'locker' else ['game']):
        ctx, pg, errs = await boot(b, PAGE, SAVE)
        await pg.evaluate("document.getElementById('lookBtn').click()")
        await pg.wait_for_function("__T.ev('!lookIntro && lookOpen')", timeout=60000, polling=100); await pg.wait_for_timeout(1500)
        await pg.evaluate("window.__tscale = 1e-9; window.__idleForce = 'still'"); await pg.wait_for_timeout(200)
        # a camera fixed in the world over the character (the character turns under it)
        if cam == 'top': await pg.evaluate("window.__camRel = [[0.01, 6.5, 0.5], [0, 0, 0]]")
        await pg.evaluate("__adv(1/30, 20)")
        cx, cy = await pg.evaluate("__scr(0.2)")
        W, Hh = (360, 360) if cam == 'top' else (390, 330)
        if cam == 'game': cx, cy = 195, 250
        await pg.evaluate("__T.ev('shim.tgt += %s')" % ('2.4' if sc == 'locker' else '5'))
        frames = []; t = 0
        while t < 2.4:
            v = await pg.evaluate("__T.ev('[shim.vel.toFixed(1), VP.slime.ax.A.loco ? VP.slime.ax.A.loco.bend.toFixed(0) : 0].join(\" \")')")
            frames.append((f'{t:.2f} v{v}', await grab(pg, cx, cy, W, Hh)))
            await pg.evaluate("__adv(1/30, 2)"); t += 2 / 30
        sheet(frames, f'{OUT}/{TAG}_{sc}_{cam}.png', cols=9)
        print(sc, cam, 'errors', errs[:4]); await ctx.close()
async def main():
    async with async_playwright() as p:
        b = await launch(p)
        for sc in SC: await locker(b, sc)
        await b.close()
asyncio.run(main())
