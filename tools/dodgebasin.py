"""v197: the basin rises just ahead of you two seconds after the fling, and the dodge lesson locks the pound and always lets an on-time swipe through."""
import asyncio, sys
from playwright.async_api import async_playwright
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
MODE = sys.argv[1] if len(sys.argv) > 1 else 'basin'; EARLY = MODE == 'early'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{}, drops: 0 })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        async def wait(js, t=300000): await pg.wait_for_function(js, timeout=t, polling=50)
        async def shot(name): await pg.evaluate("__T.renderer.render = window.__o; 0"); await pg.wait_for_timeout(200); await pg.screenshot(path=S + '/ws/ui/' + name); await pg.evaluate("__T.renderer.render = () => {}; 0")
        step = "__T.TUT_STEPS[__T.tut.step].id"
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await wait('typeof __T === "object"'); await pg.wait_for_timeout(1500)
        await pg.evaluate("(() => { const r = __T.renderer; window.__o = r.render.bind(r); r.render = () => {}; })(); 0")
        await pg.tap('#homePlay'); await wait("__T.tut && __T.tut.step === 0")
        if MODE == 'basin':
            await pg.evaluate("(() => { let n = 0; while (__T.TUT_STEPS[__T.tut.step].id !== 'free1' && n++ < 20) __T.tutNext(); })(); 0")
            t0 = await pg.evaluate("performance.now()"); await wait(step + " === 'basin'")
            print('free1 lasted (real ms, sim)', round(await pg.evaluate("performance.now()") - t0))
            print('basin start', await pg.evaluate("(() => { const q = __T.tut.potQ, P = __T.P; if (!q) return 'no potQ'; const n = q.next; const d = Math.hypot(n[0] - P.x, n[2] - P.z), a = Math.atan2(n[0] - P.x, n[2] - P.z) - P.yaw; return [q.st, +d.toFixed(2), +(Math.atan2(Math.sin(a), Math.cos(a))).toFixed(2), +P.paint.toFixed(2)]; })()"))
            await wait("__T.tutTip && __T.tutTip.key === 'basin'", 60000)
            print('basin tip', await pg.evaluate("[__T.tut.potQ.st, +__T.tut.st.toFixed(2), +__T.P.paint.toFixed(2), document.getElementById('tutArrow').hidden]"))
            await shot('basin_mark.png')
            await wait("__T.tut.potQ && __T.tut.potQ.st === 'up'", 60000); await pg.wait_for_timeout(300)
            print('basin up', await pg.evaluate("(() => { const q = __T.tut.potQ, h = document.querySelector('.tuthand:not(#tutHand)'); return [q.st, +Math.hypot(q.x - __T.P.x, q.z - __T.P.z).toFixed(2), h && !h.hidden, h && h.style.left + ',' + h.style.top]; })()"))
            await shot('basin_up.png')
        if MODE == 'basin': print('errors', errs); await b.close(); return
        await pg.evaluate("(() => { let n = 0; while (__T.TUT_STEPS[__T.tut.step].id !== 'dodge' && n++ < 20) __T.tutNext(); })(); 0"); await pg.wait_for_timeout(300)
        print('dodge start', await pg.evaluate("(() => { const b = document.getElementById('slamBtn'); return [b.className, getComputedStyle(b).pointerEvents, getComputedStyle(b).opacity, __T.useSlam(__T.P), __T.P.slam]; })()"))
        await pg.evaluate("setInterval(() => { const id = __T.TUT_STEPS[__T.tut.step].id; if ((id === 'dodge' || id === 'rocketdodge') && __T.P.st === 'hide') __T.exitPot(__T.P, true); }, 100); 0")
        if MODE == 'shot': await pg.evaluate("(() => { const P = __T.P, x0 = P.x, z0 = P.z; const L = () => { if (P.st === 'play' && !P.air) { P.x = x0; P.z = z0; } requestAnimationFrame(L); }; requestAnimationFrame(L); })(); 0")
        else: await pg.keyboard.down('ArrowLeft')
        if EARLY: await pg.evaluate("__T.dodgeRoll(__T.P); 0"); print('early swipe', await pg.evaluate("[+__T.P.rollT.toFixed(2), +__T.P.rollCD.toFixed(2)]"))
        for i in range(60):
            try: await wait("__T.tut.sub === 'now'", 3000); break
            except Exception: print('  waiting', await pg.evaluate("(() => { const P = __T.P, H = __T.H, t = __T.tut; return [+t.st.toFixed(1), +Math.hypot(H.x - P.x, H.z - P.z).toFixed(1), H.st, H.slam, +H.slamCD.toFixed(2), H.air, P.st, P.air, t.sub]; })()"))
        g = await pg.evaluate("(() => { const g = document.querySelector('.tutgest'); const r = g && g.getBoundingClientRect(), s = document.getElementById('slamBtn').getBoundingClientRect(); return [g && g.dataset.g, r && Math.round(r.top), Math.round(s.top), +__T.P.rollCD.toFixed(2), +(__T.H.slamEta - __T.H.slamT).toFixed(2)]; })()")
        print('NOW: gesture, gest top, pound top, rollCD, eta', g)
        await shot('dodge_now.png')
        await pg.evaluate("window.__sw = performance.now(); setTimeout(() => { window.__swr = [__T.dodgeRoll(__T.P), +__T.P.rollT.toFixed(2), +(__T.H.slamEta - __T.H.slamT).toFixed(2), __T.canAct(__T.P), __T.P.air]; }, 350); 0")
        await wait("window.__swr"); print('swipe 350ms later: ok, rollT, eta, canAct, air', await pg.evaluate("window.__swr"))
        await wait("!__T.H.slam", 60000); await pg.wait_for_timeout(500)
        print('after landing', await pg.evaluate("[__T.P.st, __T.tut.rolled, __T.tut.hits, " + step + "]"))
        await wait(step + " !== 'dodge'", 60000); print('next step', await pg.evaluate(step + " + ' ' + document.getElementById('slamBtn').className"))
        print('errors', errs); await b.close()
asyncio.run(main())
