"""debug: the basin pointer's conditions, and a blob caught in the air at the buzzer (logic only, drawing off)"""
import asyncio, os, sys, functools, json
from playwright.async_api import async_playwright
print = functools.partial(print, flush=True)
PAGE = os.environ.get('PAGE', 'pc_h.html')
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 360, 'height': 640}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__noVote = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{ jump: 1, hold: 1, steer: 1, item: 1, orb: 1, roll: 1, pound: 1, missile: 1, burst: 1 }, drops: 0, runs: 5, stage: 'blank', mode: 'duel', tut: { ph: 'done', strokes: 1, comms: 1 } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); ev = pg.evaluate
        await pg.goto('http://localhost:8765/' + PAGE, timeout=300000); await pg.wait_for_function('typeof __T === "object"', timeout=300000, polling=100)
        await ev("(() => { const r = __T.renderer; r.render = () => {}; })(); 0")
        await ev("__T.start()"); await pg.wait_for_function("__T.state === 'play'", timeout=300000, polling=100); await pg.wait_for_timeout(2000)
        await ev("__T.wxLeft = 999")
        C = "__T.ev(`[state, P.st, !!tut, !!P.rocket, !!P.turret, P.giantT, !!kcam, tutArrowEl.hidden, P.dry, +P.paint.toFixed(3), wxPhase, P.exposed, typeof potCueTick, potCueTo ? +Math.hypot(potCueTo.x - P.x, potCueTo.z - P.z).toFixed(1) : null, +potCueK.toFixed(2), potCue.visible, pots.filter(p => potUp(p) && !p.occ && p.cool <= 0 && p.ink > 0.05).length, +clock.toFixed(2), +potCueAt.toFixed(2), P.turf]`)"
        for i in range(6):
            await ev("__T.P.paint = 0.05; __T.P.turf = 0"); await pg.wait_for_timeout(300); print('low', await ev(C))
        # caught in the air at the buzzer
        await ev("(() => { const P = __T.P; P.air = true; P.y += 2.4; P.vy = 3; P.slam = false; __T.matchLeft = 0.03; })()")
        await pg.wait_for_function("__T.state === 'dead'", timeout=60000, polling=20)
        D = "__T.ev(`[state, P.st, P.air, +P.y.toFixed(2), +P.vy.toFixed(2), surfaceUnder(P.x, P.z, P.y + STEP, true), typeof endSettle, !!vic, ACTIVE.length, !!P.pot, +clock.toFixed(2)]`)"
        for i in range(6): print('dead', await ev(D)); await pg.wait_for_timeout(250)
        print('errors', errs[:4]); await b.close()
asyncio.run(main())
