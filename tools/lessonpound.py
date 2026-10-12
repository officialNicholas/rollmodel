"""The lesson's pound step with the kill cam: jump to the step, pound the rival from close, log the cam, the step and the tip.
usage: lessonpound.py [page] [tag]"""
import asyncio, sys, functools
from playwright.async_api import async_playwright
print = functools.partial(print, flush=True)
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
PAGE = sys.argv[1] if len(sys.argv) > 1 else 'pc_h.html'; TAG = sys.argv[2] if len(sys.argv) > 2 else 'a'
ST = "[+__T.runT.toFixed(2), __T.TUT_STEPS[__T.tut.step].id, __T.tutTip && __T.tutTip.key, __T.kcam ? +__T.kcam.t.toFixed(2) : null, __T.H.st, __T.H.rag ? +__T.H.rag.t.toFixed(2) : null, +__T.matchLeft.toFixed(2), __T.tut.slowK]"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__tut = true; window.__noVote = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{}, drops: 0, runs: 0, tut: { ph: 'match' } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); ev = pg.evaluate
        wait = lambda f, t=400000: pg.wait_for_function(f, timeout=t, polling=100)
        await pg.goto('http://localhost:8765/' + PAGE, timeout=240000); await wait('typeof __T === "object"'); await pg.wait_for_timeout(1500)
        await ev("__T.start()"); await wait("__T.state === 'play' && __T.tut && __T.tut.step !== undefined")
        await wait("__T.tut && __T.tut.outAt !== undefined"); await wait("__T.tut.step === 0"); await pg.wait_for_timeout(500)
        await ev("(() => { __T.tut.gap = 0; let n = 0; while (__T.tut && __T.TUT_STEPS[__T.tut.step].id !== 'pound' && n++ < 20) __T.tutNext(); })()"); print('at', await ev(ST))
        await wait("__T.P.st === 'play' && !__T.P.air && __T.H.st === 'play'")
        r = await ev("""(() => { const P = __T.P, H = __T.H; H.x = P.x + Math.sin(P.yaw) * 1.4; H.z = P.z + Math.cos(P.yaw) * 1.4; H.y = P.y; H.air = false; H.vy = 0; H.spd = 0; H.immuneT = 0;
          P.slamCD = 0; P.paint = 1; const ok = __T.slamReady(P); __T.useSlam(P); return ok; })()"""); print('pounded', r)
        shot = False
        for i in range(60):
            s = await ev(ST)
            if i % 4 == 0: print(s)
            if not shot and s[3] is not None and s[3] > 0.9: shot = True; await pg.screenshot(path=f'{WS}/ui/lp_{TAG}.png'); print('shot at', s)
            if s[3] is None and i > 10 and s[1] != 'pound': print('after', s); break
            await pg.wait_for_timeout(700)
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
