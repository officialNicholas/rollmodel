"""The paint's start: from the match's Go, logs the player's air state, the clean-crawl timer (flowT) and the stream's swell (flowK), and
films the stream coming in; then, swimming, runs the player out of paint and checks the swim lets go (crawl only). usage: flowstart.py [page] [tag]"""
import asyncio, sys, functools
from playwright.async_api import async_playwright
print = functools.partial(print, flush=True)
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
PAGE = sys.argv[1] if len(sys.argv) > 1 else 'pc_h.html'; TAG = sys.argv[2] if len(sys.argv) > 2 else 'a'
LOG = """(() => { window.__fl = []; const t0 = performance.now(); const f = () => { const P = __T.P, A = __T.VP && __T.VP.slime && __T.VP.slime.ax ? __T.VP.slime.ax.A : null, L = A && A.loco;
  if (__T.state === 'play') __fl.push({ t: +((performance.now() - t0) / 1000).toFixed(2), air: P.air, flowT: P.flowT === undefined ? null : +P.flowT.toFixed(2), flowK: P.flowK === undefined ? null : +P.flowK.toFixed(2), spd: +P.spd.toFixed(1), dry: !!P.dry, sl: L ? +(L.slK || 0).toFixed(2) : null, mdry: A ? !!A.motion.dry : null });
  if (__fl.length < 3000) requestAnimationFrame(f); }; requestAnimationFrame(f); })()"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 360, 'height': 640}, device_scale_factor=1, has_touch=True)
        await ctx.add_init_script("window.__noVote = true; window.__skipIntro = false; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{}, drops: 0, runs: 5, mode: 'solo', tut: { ph: 'done' } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); ev = pg.evaluate
        await pg.goto('http://localhost:8765/' + PAGE, timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000, polling=100); await pg.wait_for_timeout(1500)
        await ev("__T.mode = 'solo'; __T.applyMode(); __T.start()"); await pg.wait_for_function("__T.state === 'play'", timeout=400000, polling=50)
        await ev(LOG)
        for k, w in enumerate([900, 700, 700, 900]):
            await pg.wait_for_timeout(w); await pg.screenshot(path=f'{WS}/ui/flow_{TAG}_{k}.png')
        log = await ev("__fl"); prev = None
        for r in log:
            key = (r['air'], r['flowT'] is not None and r['flowT'] > 0, r['flowK'] is not None and r['flowK'] >= 1)
            if key != prev: print(r); prev = key
        await pg.wait_for_function("(() => { const A = __T.VP.slime.ax.A; return A.loco && A.loco.slK > 0.9; })()", timeout=60000, polling=100); print('swimming, sl', await ev("__T.VP.slime.ax.A.loco.slK.toFixed(2)"))
        await ev("__T.P.paint = 0"); await pg.wait_for_timeout(600)
        print('dry after 0.6s', await ev("(() => { const A = __T.VP.slime.ax.A; return { dry: __T.P.dry, mdry: A.motion.dry, sl: +A.loco.slK.toFixed(2), vc: +A.loco.vc.toFixed(1) }; })()"))
        await pg.wait_for_timeout(1500); print('dry after 2.1s', await ev("(() => { const A = __T.VP.slime.ax.A; return { dry: __T.P.dry, sl: +A.loco.slK.toFixed(2), vc: +A.loco.vc.toFixed(1) }; })()"))
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
