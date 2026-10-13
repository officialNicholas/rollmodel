"""v250 checks in one match: the rain waters your paint down (and for a moment after); the floor pointer to the nearest basin when
you're low or the heat's coming; caught in the air at the buzzer you come down to the floor (and stay down after the winner screen).
usage: misc250.py [stage]"""
import asyncio, os, sys, functools, json
from playwright.async_api import async_playwright
print = functools.partial(print, flush=True)
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'; SID = sys.argv[1] if len(sys.argv) > 1 else 'blank'; PAGE = os.environ.get('PAGE', 'pc_h.html')
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 360, 'height': 640}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__noVote = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{ jump: 1, hold: 1, steer: 1, item: 1, orb: 1, roll: 1, pound: 1, missile: 1, burst: 1 }, drops: 0, runs: 5, stage: '" + SID + "', mode: 'duel', tut: { ph: 'done', strokes: 1, comms: 1 } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); ev = pg.evaluate
        await pg.goto('http://localhost:8765/' + PAGE, timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000, polling=100); await pg.wait_for_timeout(1000)
        if os.environ.get('FAST'): await ev("(() => { const r = __T.renderer; window.__rr = r.render.bind(r); r.render = () => {}; })(); 0")  # (logic only: 3D drawing off, so the game runs at full speed)
        await ev("__T.start()"); await pg.wait_for_function("__T.state === 'play'", timeout=400000, polling=100); await pg.wait_for_timeout(2500)
        await ev("__T.wxLeft = 999")  # (no weather of its own while we look)
        # ---- the rain
        await ev("__T.ev('setWx(\"rain\", 2.0)')"); await pg.wait_for_timeout(700)
        print('rain: dilT P/H', await ev("[+__T.P.dilT.toFixed(2), +__T.H.dilT.toFixed(2), __T.wxPhase, document.getElementById('pop').textContent]"))
        await pg.wait_for_function("__T.wxPhase !== 'rain'", timeout=60000, polling=50); t0 = await ev("__T.runT"); print('rain over: dilT', await ev("+__T.P.dilT.toFixed(2)"))
        await pg.wait_for_function("__T.P.dilT <= 0", timeout=60000, polling=50); print('  watered down for', round(await ev("__T.runT") - t0, 2), 's after the rain')
        await ev("__T.wxLeft = 999; __T.ev('setWx(\"clear\", 999)')")
        # ---- the basin pointer
        await ev("__T.P.paint = 0.05"); await pg.wait_for_timeout(1200)
        print('low paint: cue', await ev("__T.ev('[potCue.visible, +potCueK.toFixed(2), potCueTo && +Math.hypot(potCueTo.x - P.x, potCueTo.z - P.z).toFixed(1), +potCueYaw.toFixed(2)]')"))
        await pg.screenshot(path=f'{WS}/ui/m250_{SID}_cue.png')
        await ev("__T.P.paint = 1"); await pg.wait_for_timeout(900); print('full: cue', await ev("__T.ev('[potCue.visible, +potCueK.toFixed(2)]')"))
        await ev("__T.ev('setWx(\"warn\", 999)')"); await pg.wait_for_timeout(900); print('heat warning: cue', await ev("__T.ev('[potCue.visible, +potCueK.toFixed(2)]')")); await pg.screenshot(path=f'{WS}/ui/m250_{SID}_cuewarn.png')
        await ev("__T.ev('setWx(\"clear\", 999)')"); await pg.wait_for_timeout(600)
        # ---- caught in the air at the buzzer
        await ev("(() => { const P = __T.P; P.air = true; P.y += 2.4; P.vy = 3; P.slam = false; __T.matchLeft = 0.03; })()")
        await pg.wait_for_function("__T.state === 'dead'", timeout=60000, polling=30)
        for i in range(8):
            print('  after the buzzer', await ev("(() => { const P = __T.P, g = __T.surfaceUnder(P.x, P.z, P.y + 0.4, true); return [+__T.runT.toFixed(2), +P.y.toFixed(2), +g.toFixed(2), P.air]; })()")); await pg.wait_for_timeout(250)
        await pg.wait_for_function("!!__T.vic", timeout=120000, polling=100); await ev("__T.endVictory()")
        await pg.wait_for_timeout(1200)
        print('after the winner screen', await ev("(() => { const P = __T.P, g = __T.surfaceUnder(P.x, P.z, P.y + 0.4, true); return [+P.y.toFixed(2), +g.toFixed(2), P.air, __T.state]; })()"))
        print('errors', errs[:4]); await b.close()
asyncio.run(main())
