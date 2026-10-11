"""The axolotl's slither: start a match and log the body's speed and the slither's weight from the start (a crawl up to speed, then the
slither), then stop it (load a fling) and see it go back to the crawl. Shots from overhead and from the play camera. usage: slither226.py [tag]"""
import asyncio, sys, functools
from playwright.async_api import async_playwright
print = functools.partial(print, flush=True)
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
TAG = sys.argv[1] if len(sys.argv) > 1 else 'a'
LOG = """(() => { const P = __T.P; window.__lg = []; const f = () => { const I = __T.AXOC && __T.AXOC.S.list.find(x => x.root.parent && x.root.parent.parent && P.look && (P.look.root || {}).uuid), A = (__T.VP && __T.VP.slime && __T.VP.slime.ax) ? __T.VP.slime.ax.A : null, L = A && A.loco;
  if (L) window.__lg.push({ t: +__T.clock.toFixed(2), spd: +P.spd.toFixed(2), v: +L.v.toFixed(2), vc: +L.vc.toFixed(2), act: +L.act.toFixed(2), sl: +(L.slK || 0).toFixed(2), air: P.air, chg: !!P.charging });
  if (window.__lg.length < 4000) requestAnimationFrame(f); }; requestAnimationFrame(f); })()"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 360, 'height': 640}, device_scale_factor=1, has_touch=True)
        await ctx.add_init_script("window.__noVote = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{}, drops: 0, runs: 5, mode: 'solo', tut: { ph: 'done' } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); ev = pg.evaluate
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000, polling=100); await pg.wait_for_timeout(1500)
        await ev("__T.mode = 'solo'; __T.applyMode(); __T.start()")
        await pg.wait_for_function("__T.state === 'play'", timeout=400000, polling=100)
        await ev(LOG)
        for i in range(10):
            await pg.wait_for_timeout(700); r = await ev("window.__lg[window.__lg.length - 1]"); print(i, r)
            if i in (3, 6): await pg.screenshot(path=f'{WS}/ui/slither_{TAG}_play{i}.png')
        await ev("(() => { const P = __T.P; window.__cam = [[P.x + 0.01, P.y + 5.2, P.z + 0.3], [P.x, P.y, P.z]]; window.__camFollow = true; })()")
        for k in range(4):
            await ev("(() => { const P = __T.P; window.__cam = [[P.x + 0.01, P.y + 5.2, P.z + 0.3], [P.x, P.y, P.z]]; })()"); await pg.wait_for_timeout(250)
            await pg.screenshot(path=f'{WS}/ui/slither_{TAG}_top{k}.png')
        await ev("window.__cam = null"); await ev("__T.startCharge(__T.P)")
        for i in range(5):
            await pg.wait_for_timeout(600); print('stop', i, await ev("window.__lg[window.__lg.length - 1]"))
        await pg.screenshot(path=f'{WS}/ui/slither_{TAG}_stopped.png')
        lg = await ev("window.__lg"); print('max vc', max(x['vc'] for x in lg), 'max sl', max(x['sl'] for x in lg), 'n', len(lg)); print('errors', errs[:3]); await b.close()
asyncio.run(main())
