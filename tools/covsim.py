"""How much of the canvas a painter covers per mode: the game's own AI drives you (and the CPUs as usual), the loop is frozen and the
probe steps the game itself with drawing off, to the buzzer. Prints each painter's coverage per match.
usage: covsim.py <modes comma list> <difficulty> [reps]"""
import asyncio, os, sys, time
from playwright.async_api import async_playwright
MODES, DF = sys.argv[1].split(','), sys.argv[2]; REPS = int(sys.argv[3]) if len(sys.argv) > 3 else 2
SIM = """(n => { const T = __T, dt = 1 / 60; for (let i = 0; i < n && T.state === 'play'; i++) { T.step(dt / 2); T.step(dt / 2); T.visuals(dt, dt); T.flushTrail(); } return T.state; })"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 430, 'height': 754})
        await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{look:1}, runs: 9, flings: 99, tut: { ph: 'done' } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8765/pc_perf.html', timeout=300000)
        for i in range(200):
            if await pg.evaluate("typeof __T === 'object' && !!window.__pf"): break
            await pg.wait_for_timeout(2500)
        await pg.evaluate("(() => { __T.renderer.render = () => {}; })()")
        for rep in range(REPS):
            for md in MODES:
                await pg.evaluate(f"(() => {{ window.__noStep = false; __T.mode = '{md}'; __T.applyMode(); __T.setDiff('{DF}'); __T.setAI('{DF}'); }})()")
                await pg.evaluate("__T.start()")
                t0 = time.time()
                while time.time() - t0 < 240:
                    if await pg.evaluate("__T.state") == 'play': break
                    await pg.wait_for_timeout(500)
                await pg.evaluate(f"(() => {{ window.__noStep = true; window.__perfAI(); __T.setAI('{DF}'); }})()")
                t1 = time.time()
                while await pg.evaluate(SIM + "(600)") == 'play': pass
                r = await pg.evaluate("(() => ({ th: __T.TH.id, mode: __T.mode, t: __T.runT, cov: __T.ACTIVE.map(D => +__T.teamCov(D.team).toFixed(1)), you: __T.endInfo && +(+__T.endInfo.you).toFixed(1) }))()")
                print(f"{r['mode']:5} {r['th']:10} {r['t']:.0f}s  you {r['cov'][0]}%  others {r['cov'][1:]}  ({time.time()-t1:.0f}s wall)", flush=True)
                await pg.evaluate("window.__noStep = false")
                for i in range(40):
                    if await pg.evaluate("__T.state === 'dead' || __T.state === 'menu'"): break
                    await pg.wait_for_timeout(500)
                await pg.evaluate("(() => { try { __T.toMenu(); } catch (e) {} })()"); await pg.wait_for_timeout(3000)
        print('errors', errs[:5])
        await b.close()
asyncio.run(main())
