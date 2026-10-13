"""v250 lesson finale: after Ol' Bloop's 'Now win it!' card, no rollers; a few seconds to roll, then the orb, timed so the rocket comes
down on the buzzer and the blast ends the match. Logs the clock at each beat (orb out, taken, hover, dive, landing, match over).
usage: tut250.py [auto|boost]  (auto: never touch boost; boost: boost the moment the hover starts)"""
import asyncio, os, sys, functools, json
from playwright.async_api import async_playwright
print = functools.partial(print, flush=True)
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'; HOW = sys.argv[1] if len(sys.argv) > 1 else 'auto'; PAGE = os.environ.get('PAGE', 'pc_h.html')
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 300, 'height': 560}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__tut = true; window.__skipIntro = false; window.__noReveal = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{}, drops: 0 })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); ev = pg.evaluate
        async def wait(js, t=400000): await pg.wait_for_function(js, timeout=t, polling=60)
        async def shot(n): await pg.screenshot(path=f'{WS}/ui/t250_{HOW}_{n}.png')
        await pg.goto('http://localhost:8765/' + PAGE, timeout=240000); await wait('typeof __T === "object"'); await pg.wait_for_timeout(800)
        await ev("document.getElementById('homePlay').click()"); await wait("__T.state === 'play'"); await wait("__T.tut && __T.tut.step === 0"); await wait("__T.H.st === 'play' && !__T.H.air")
        await ev("(() => { __T.tut.gap = 0; let n = 0; while (__T.TUT_STEPS[__T.tut.step].id !== 'rest' && n++ < 20) __T.tutNext(); })()")
        await ev("if (__T.P.st === 'hide') __T.useSlam(__T.P)"); await wait("__T.P.st === 'play' && !__T.P.air")
        # (beats logged from inside: the orb put out, taken, the dive (by itself or boosted), the landing, the match's end)
        await ev("""__T.ev(`(() => { window.__log = []; const L = (k, x) => window.__log.push(Object.assign({ k, ml: +matchLeft.toFixed(3), t: +runT.toFixed(3), st: state }, x || {}));
          const o1 = tutFinOrb; tutFinOrb = function (sp) { L('orb', { d: +Math.hypot(sp[0] - P.x, sp[2] - P.z).toFixed(2) }); return o1(sp); };
          const o2 = takeOrb; takeOrb = function (D) { L('take', { who: D === P ? 'P' : 'H' }); return o2(D); };
          const o3 = rocketDive; rocketDive = function (D, auto) { const r = o3(D, auto); if (r && D === P) L('dive', { auto: !!auto, h: +(D.y - (D.rocket.gy > -Infinity ? D.rocket.gy : 0)).toFixed(2) }); return r; };
          const o4 = rocketLand; rocketLand = function (D) { L('land', { Hst: H.st, dH: +Math.hypot(H.x - D.x, H.z - D.z).toFixed(2) }); const r = o4(D); L('landed', { Hst: H.st, kc: !!kcam }); return r; };
          const o5 = endMatch; endMatch = function () { L('end'); return o5(); };
          const o6 = tutFinStart; tutFinStart = function () { L('finStart'); const r = o6(); L('finStart2', { rollers: powers.filter(q => q.type === 'roller').length }); return r; };
        })()`)""")
        await wait("!document.getElementById('tutGo').hidden"); print('card: clock', await ev("+__T.matchLeft.toFixed(2)"))
        await ev("document.getElementById('tgGo').click()"); await pg.wait_for_timeout(300)
        print('rollers right after:', await ev("__T.powers.filter(q => q.type === 'roller').length"))
        hov = False; last = None
        for i in range(4000):
            r = await ev("[+__T.matchLeft.toFixed(2), __T.state, __T.P.st, __T.orb.on, __T.P.rocket ? __T.P.rocket.ph : null, __T.tutTip && __T.tutTip.key, __T.powers.filter(q => q.type === 'roller').length]")
            if r[4] == 'hover' and not hov:
                hov = True; await shot('hover')
                if HOW == 'boost': await ev("__T.rocketDive(__T.P, false)")
            k = (r[1], r[2], r[3], r[4], r[5], r[6])
            if k != last: print('  ', r); last = k
            if r[1] != 'play': break
            await pg.wait_for_timeout(40)
        await pg.wait_for_timeout(300); await shot('end')
        for e in await ev("window.__log"): print('  LOG', json.dumps(e))
        print('errors', errs[:4]); await b.close()
asyncio.run(main())
