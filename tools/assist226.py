"""The pound assist: roll into the rival with the pound ready. Case 'press': press pound during the hop (the rival should be knocked out).
Case 'leave': don't (you just land; the rival stays in). Logs the hop frame by frame and shoots it at the top. usage: assist226.py [press|leave]"""
import asyncio, sys, functools, json
from playwright.async_api import async_playwright
print = functools.partial(print, flush=True)
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
CASE = sys.argv[1] if len(sys.argv) > 1 else 'press'
LOG = """(() => { const P = __T.P, H = __T.H; window.__lg = []; const f = () => { const b = document.getElementById('slamBtn');
  window.__lg.push({ t: +__T.clock.toFixed(3), air: P.air, y: +P.y.toFixed(2), vy: +P.vy.toFixed(2), spd: +P.spd.toFixed(2), roll: +P.rollT.toFixed(2), as: +(P.assistT || 0).toFixed(2), slam: P.slam, hst: H.st, hstun: +(H.stunT || 0).toFixed(2), d: +Math.hypot(H.x - P.x, H.z - P.z).toFixed(2), btn: b.classList.contains('assist') });
  if (window.__lg.length < 3000) requestAnimationFrame(f); }; requestAnimationFrame(f); })()"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 300, 'height': 560}, device_scale_factor=1, has_touch=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{}, drops: 0, runs: 5, mode: 'duel', tut: { ph: 'done' } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); ev = pg.evaluate
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000, polling=100); await pg.wait_for_timeout(1500)
        await ev("window.__noVote = true; __T.mode = 'duel'; __T.applyMode(); __T.start()")
        await pg.wait_for_function("__T.state === 'play' && __T.P.st === 'play' && !__T.P.air", timeout=400000, polling=100); await pg.wait_for_timeout(1500)
        # the rival right ahead of you on open ground; you, the pound ready, roll into it
        await ev("""(() => { const P = __T.P, H = __T.H; P.paint = 1; P.slamCD = 0; P.rollCD = 0; const fx = Math.sin(P.yaw), fz = Math.cos(P.yaw);
          H.x = P.x + fx * 1.9; H.z = P.z + fz * 1.9; H.y = P.y; H.vy = 0; H.air = false; H.spd = 0; H.stunGuard = 0; H.immuneT = 0; H.flatT = 0; H.stunT = 0; })()""")
        await ev(LOG); await ev("__T.dodgeRoll(__T.P)")
        pressed = False
        for i in range(400):
            r = await ev("window.__lg[window.__lg.length - 1]")
            if CASE == 'press' and not pressed and r['as'] > 0 and r['vy'] < 1.2:
                await ev("__T.useSlam(__T.P)"); pressed = True; print('pressed at', r)
                await pg.screenshot(path=f'{WS}/ui/assist_{CASE}_top.png')
            if CASE == 'leave' and r['as'] > 0 and r['vy'] < 0.6 and not pressed: pressed = True; await pg.screenshot(path=f'{WS}/ui/assist_{CASE}_top.png')
            if len(await ev("window.__lg")) > 40 and r['as'] == 0 and not r['air'] and not r['slam'] and (pressed or i > 60): break
            await pg.wait_for_timeout(60)
        lg = await ev("window.__lg"); keep = [x for x in lg if x['as'] > 0 or x['slam'] or x['roll'] > 0 or x['air']]
        for x in keep[::max(1, len(keep) // 22)]: print(x)
        print('end', lg[-1]); await pg.screenshot(path=f'{WS}/ui/assist_{CASE}_end.png'); print('errors', errs[:3]); await b.close()
asyncio.run(main())
