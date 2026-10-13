"""Showdown matches between CPUs (you handed to the game's own AI), stepped faster than real time with drawing off: how long a match
runs, who wins and how, knock-outs and self-eliminations. usage: sdsim.py PAGE TAG MODE DIFF REPS [STAGE]"""
import asyncio, json, sys, time
from playwright.async_api import async_playwright
sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/tools')
from h254 import *
PAGE, TAG, MODE, DIFF, REPS = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], int(sys.argv[5]); STAGE = sys.argv[6] if len(sys.argv) > 6 else None
SIM = """(n => { const T = __T, dt = 1 / 60; let k = 0;
  for (; k < n && T.state === 'play'; k++) { T.step(dt / 2); T.step(dt / 2); T.visuals(dt, dt); T.flushTrail(); }
  return [T.state, __T.ev('+runT.toFixed(1)'), __T.ev('JSON.stringify(ACTIVE.map(D => [D.hearts, D.st]))')]; })"""
async def main():
    async with async_playwright() as p:
        b = await launch(p)
        ctx = await b.new_context(viewport={'width': 400, 'height': 720})
        save = dict(SAVE, mode=MODE, diff=DIFF)
        await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify(" + json.dumps(save) + ")); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8765/' + PAGE, timeout=300000)
        await pg.wait_for_function('typeof __T === "object" && !!__T.VP && !!__T.VP.slime', timeout=300000, polling=1000)
        await pg.evaluate("(() => { __T.renderer.render = () => {}; })()")
        res = []
        for rep in range(REPS):
            if STAGE: await pg.evaluate(f"__T.setStage('{STAGE}')")
            await pg.evaluate(f"(() => {{ __T.setDiff('{DIFF}'); window.__noStep = false; }})()")
            await pg.evaluate("__T.start()")
            await pg.wait_for_function("__T.state === 'play'", timeout=240000, polling=200)
            await pg.evaluate("(() => { window.__noStep = true; __T.ev('P.cpu = true; aiReset(P);'); })()")
            t0 = time.time(); last = None
            while time.time() - t0 < 900:
                r = await pg.evaluate(SIM + "(600)")
                last = r
                if r[0] != 'play': break
            info = await pg.evaluate("__T.ev(`JSON.stringify({ th: TH.id, t: +runT.toFixed(1), win: endInfo && endInfo.win, timeUp: endInfo && endInfo.timeUp, places: endInfo && endInfo.places, kos: endInfo && endInfo.kos, selfs: endInfo && endInfo.selfs, hearts: endInfo && endInfo.hearts, by: ACTIVE.map(D => D.elimBy ? nameOf(D.elimBy) : null), at: ACTIVE.map(D => +D.elimAt.toFixed(1)) })`)")
            print(rep, info, 'wall', round(time.time() - t0)); sys.stdout.flush(); res.append(json.loads(info))
            await pg.evaluate("(() => { window.__noStep = false; __T.showMenu(); })()"); await pg.wait_for_timeout(500)
        json.dump(res, open(f'{OUT}/sdsim_{TAG}_{MODE}_{DIFF}.json', 'w'))
        ts = [r['t'] for r in res]; print('mean t', sum(ts) / len(ts), 'timeUps', sum(1 for r in res if r['timeUp']), 'errors', errs[:4])
        await b.close()
asyncio.run(main())
