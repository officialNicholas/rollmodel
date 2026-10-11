"""v200: in the lesson's rocket step the rival walks into your crosshair; in a real match with no flinging, Ol' Bloop's slingshot pro tip with
the slow pull finger (gone when you fling); and the score screen's song starting as the dabs fly up"""
import asyncio, sys
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
async def run(part):
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        if part == 'rocket': await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{}, drops: 0 })); } catch (e) {}")
        else: await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', runs: 4, drops: 50, stage: 'blank', tut: { ph: 'done' }, seen: { steer:1, jump:1, hold:1, burst:1, roll:1, pound:1, missile:1, item:1, orb:1, rocket:1, airdash:1, look:1 } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        async def wait(js, t=240000): await pg.wait_for_function(js, timeout=t, polling=60)
        async def shot(name): await pg.evaluate("__T.renderer.render = window.__o; 0"); await pg.wait_for_timeout(700); await pg.screenshot(path=f'{WS}/ui/rk_{name}.png'); await pg.evaluate("__T.renderer.render = () => {}; 0")
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await wait('typeof __T === "object"'); await pg.wait_for_timeout(1500)
        await pg.evaluate("(() => { const r = __T.renderer; window.__o = r.render.bind(r); r.render = () => {}; })(); 0")
        if part == 'rocket':
            await pg.evaluate("document.getElementById('homePlay').click()"); await wait("__T.tut && __T.tut.step === 0")
            await pg.evaluate("(() => { let n = 0; while (__T.TUT_STEPS[__T.tut.step].id !== 'orb' && n++ < 30) __T.tutNext(); })(); 0"); await wait("__T.orb.on", 60000)
            await pg.evaluate("(() => { const P = __T.P; if (P.st === 'hide') __T.exitPot(P, true); P.x = __T.orb.x; P.z = __T.orb.z; })(); 0"); await wait("!!__T.P.rocket", 60000)
            await wait("__T.P.rocket && __T.P.rocket.ph === 'hover'", 60000)
            await pg.evaluate("(() => { window.__land = null; let had = false, last = null; const L = () => { const P = __T.P, H = __T.H; if (P.rocket) { had = true; last = [+P.x.toFixed(2), +P.z.toFixed(2), +P.y.toFixed(2), P.rocket.gy, P.rocket.ph]; } else if (had && !window.__land) window.__land = { p: last, pAfter: [+P.x.toFixed(2), +P.z.toFixed(2), +P.y.toFixed(2)], h: [+H.x.toFixed(2), +H.z.toFixed(2), +H.y.toFixed(2)], hst: H.st, hair: H.air, imm: +H.immuneT.toFixed(2), roll: +(H.rollT || 0).toFixed(2), dash: +(H.dashT || 0).toFixed(2), giant: H.giantT, kos: P.kos, ml: __T.matchLeft }; requestAnimationFrame(L); }; requestAnimationFrame(L); })(); 0")
            d = "(() => { const P = __T.P, H = __T.H; return [P.rocket ? P.rocket.ph : null, +Math.hypot(H.x - P.x, H.z - P.z).toFixed(1), __T.tut.driveMode, __T.H.st]; })()"
            best = 99; shotd = False
            for i in range(30):
                v = await pg.evaluate(d); print('  ', v)
                if v[0] is None: break
                if v[1] < best: best = v[1]
                if v[1] < 3 and v[0] == 'hover' and not shotd: await shot('cross'); shotd = True; print('   boost', await pg.evaluate("__T.useSlam(__T.P)"))
                await pg.wait_for_timeout(250)
            print('closest to the crosshair', best)
            await wait("!__T.P.rocket", 60000); await pg.wait_for_timeout(400); print('after the landing', await pg.evaluate("[__T.H.st, __T.TUT_STEPS[__T.tut.step].id, __T.P.kos]")); print('landing', await pg.evaluate("JSON.stringify(window.__land)"))
        else:
            await pg.evaluate("window.__mus = []; const m = __T.AU.music; __T.AU.music = function (k) { window.__mus.push([k, __T.tal ? __T.tal.phase : null, __T.tal ? +__T.tal.t.toFixed(2) : null]); return m.apply(this, arguments); }; 0")
            await pg.evaluate("document.getElementById('homePlay').click()"); await wait("__T.state === 'play'")
            for i in range(80):
                if await pg.evaluate("!!(__T.tutTip && __T.tutTip.key === 'protip')"): break
                await pg.evaluate("(() => { if (__T.P.st === 'hide') __T.exitPot(__T.P, true); })(); 0"); await pg.wait_for_timeout(1500)
            await pg.wait_for_timeout(500)
            print('protip', await pg.evaluate("[__T.tutTip.text, +__T.runT.toFixed(1), (() => { const g = document.querySelector('.tutgest'); return g && !g.hidden ? g.dataset.g : null; })(), document.getElementById('tut').dataset.pos, __T.store.slingTips]")); await shot('protip')
            await pg.evaluate("(() => { const P = __T.P; if (P.st === 'hide') __T.exitPot(P, true); __T.startCharge(P); P.charge = 0.8; __T.fling(P, 0.8); })(); 0"); await pg.wait_for_timeout(500); print('after a fling', await pg.evaluate("[__T.tutTip && __T.tutTip.key, __T.store.flings, __T.P.flung]"))
            await pg.evaluate("(() => { const P = __T.P; for (let i = 0; i < 16; i++) { const x = P.x + (i % 4 - 1.5) * 3.2, z = P.z + (i / 4 | 0) * 3.2 - 4.8; __T.addSplat(x, Math.max(0, __T.surfaceUnder(x, z, P.y + 3, true)), z, 0, 3, __T.clock, false, true, 0); } __T.flushTrail(); window.__instant = false; __T.matchLeft = 0.05; })(); 0"); await wait("__T.state === 'dead'", 90000); await wait("!!__T.tal", 60000)
            await wait("__T.tal && __T.tal.phase >= 5", 120000); await pg.wait_for_timeout(300); print('music at the dab fly', await pg.evaluate("JSON.stringify(window.__mus)"))
            await wait("!document.getElementById('victory').hidden", 120000); await pg.wait_for_timeout(1500); print('music by the winner screen', await pg.evaluate("JSON.stringify(window.__mus)"))
        print('errors', errs); await b.close()
asyncio.run(run(sys.argv[1]))
