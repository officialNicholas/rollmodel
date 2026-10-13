"""v254 dodge probes. usage: dodge254.py PAGE TAG [scenario...]
  rollout   swipe up in a basin: the roll out over the rim (side camera)
  dashfwd   hop out of a basin, then the forward dash (side camera)
  dashback  hop out of a basin, then the backward dash
  rules     which dashes a hop allows and which a basin exit allows (printed)"""
import asyncio, sys
from playwright.async_api import async_playwright
sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/tools')
from h254 import *
PAGE, TAG = sys.argv[1], sys.argv[2]; SC = sys.argv[3:] or ['rollout', 'dashfwd', 'dashback', 'rules']
INPOT = """__T.ev(`(() => { let best = null, bd = 1e9; for (const p of pots) { if (!potUp(p) || p.occ) continue; const d = Math.hypot(p.x - P.x, p.z - P.z); if (d < bd) { bd = d; best = p; } } P.paint = 1; P.slamCD = 0; enterPot(P, best); P.yaw = potRun(best, 9).yaw; P.immuneT = 0; return [best.x, best.z]; })()`)"""
async def run(b, sc):
    ctx, pg, errs = await match(b, PAGE)
    if sc == 'rules':
        out = []
        for how in ['hop', 'pothop', 'potroll', 'burst']:
            for d in [1, -1]:
                if how == 'hop': await pg.evaluate("__T.ev('P.paint = 1; jump(P)')")
                else:
                    await pg.evaluate(INPOT); await pg.evaluate("__adv(1/30, 4)")
                    await pg.evaluate("__T.ev('%s')" % {'pothop': 'exitPot(P)', 'potroll': 'dodgeRoll(P)', 'burst': 'burstCoffin(P)'}[how])
                await pg.evaluate("__adv(1/60, 8)")
                r = await pg.evaluate("__T.ev('[P.air, P.airSling, !!P.airBack, airDash(P, %d), P.dashT > 0]')" % d)
                out.append((how, d, r))
                for _ in range(80):
                    if not await pg.evaluate("__T.P.air"): break
                    await pg.evaluate("__adv(1/30, 3)")
                await pg.evaluate("__adv(1/30, 20)")
        for o in out: print('rules', o)
        print('errors', errs[:4]); await ctx.close(); return
    await pg.evaluate(CAMF); await pg.evaluate("__camAx([3.4, 1.0, 0.6], [0, 0.4, 0.6])")
    await pg.evaluate(INPOT); await pg.evaluate("__adv(1/30, 6)"); cx, cy = await pg.evaluate("__scr(0.5)")
    if sc == 'rollout': await pg.evaluate("__T.ev('dodgeRoll(P)')")
    else: await pg.evaluate("__T.ev('exitPot(P)')")
    frames = []; t = 0; dashed = False
    while t < 1.3:
        if sc != 'rollout' and not dashed and t >= 0.25:
            dashed = True; ok = await pg.evaluate("__T.ev('airDash(P, %d)')" % (1 if sc == 'dashfwd' else -1)); print(sc, 'dash ok', ok)
        info = await pg.evaluate("__T.ev(`[P.air ? 'A' : 'G', P.rollOutT.toFixed(2), P.dashT.toFixed(2), vOf(P).balled ? 'B' : '-'].join(' ')`)")
        frames.append((f'{t:.2f} {info}', await grab(pg, cx, cy - 40, 300, 260)))
        await pg.evaluate("__adv(1/60, 3)"); t += 3 / 60
    sheet(frames, f'{OUT}/{TAG}_{sc}.png', cols=9)
    print(sc, 'errors', errs[:4]); await ctx.close()
async def main():
    async with async_playwright() as p:
        b = await launch(p)
        for sc in SC: await run(b, sc)
        await b.close()
asyncio.run(main())
