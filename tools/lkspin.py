"""Locker turn probe: open the locker, drag the character round, log the turn (shim) and the body's bend frame by frame, and shoot it
mid-turn. usage: lkspin.py [tag] [dx px] [hold ms]"""
import asyncio, sys, json, functools
from playwright.async_api import async_playwright
print = functools.partial(print, flush=True)
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
TAG = sys.argv[1] if len(sys.argv) > 1 else 'a'; DX = float(sys.argv[2]) if len(sys.argv) > 2 else 160; HOLD = int(sys.argv[3]) if len(sys.argv) > 3 else 0
LOG = """(() => { const AX = __T.AXOC, P = __T.P, I = AX && AX.S.list[0], A = I && I.ax.A; window.__lg = []; const f = () => { const L = A && A.loco;
  window.__lg.push({ t: +__T.clock.toFixed(3), sh: +__T.shim.vel.toFixed(2), yaw: +(P.yaw || 0).toFixed(3), bend: L ? +L.bend.toFixed(1) : null, yr: L ? +L.yr.toFixed(2) : null, act: L ? +L.act.toFixed(2) : null, st: A && A.state, tl: A ? +(A.tailLat || 0).toFixed(1) : null });
  if (window.__lg.length < 4000) requestAnimationFrame(f); }; requestAnimationFrame(f); })()"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 360, 'height': 640}, device_scale_factor=1, has_touch=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{}, drops: 40, runs: 3, tut: { done: true } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); ev = pg.evaluate
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000, polling=100)
        await pg.wait_for_timeout(2500); await ev("__T.openLook()"); await pg.wait_for_timeout(9000)
        await ev(LOG)
        x0, y0 = 120, 200
        await pg.mouse.move(x0, y0); await pg.mouse.down()
        for i in range(12): await pg.mouse.move(x0 + DX * (i + 1) / 12, y0); await pg.wait_for_timeout(40)
        await pg.mouse.up(); await pg.wait_for_timeout(700); await pg.screenshot(path=f'{WS}/ui/lkspin_{TAG}_1.png')
        await pg.wait_for_timeout(1500); await pg.screenshot(path=f'{WS}/ui/lkspin_{TAG}_2.png')
        await pg.wait_for_timeout(4000)
        lg = await ev("window.__lg"); print('frames', len(lg))
        for r in lg[::max(1, len(lg) // 40)]: print(r)
        json.dump(lg, open(f'{WS}/ui/lkspin_{TAG}.json', 'w'))
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
