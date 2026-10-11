"""v223 in the lesson match: the basin lesson's basin (how far, on screen) and its swipe-up finger; the finale after Ol' Bloop's card: ten
seconds, rollers close by in view, the orb in front with about four seconds left, the rocket's landing as the last moment.
usage: tut223.py basin|finale"""
import asyncio, os, sys, functools
from playwright.async_api import async_playwright
print = functools.partial(print, flush=True)
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'; SEC = sys.argv[1]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': int(os.environ.get('VW', 360)), 'height': int(os.environ.get('VH', 660))}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__tut = true; window.__skipIntro = false; window.__noReveal = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{}, drops: 0 })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); ev = pg.evaluate
        async def wait(js, t=400000): await pg.wait_for_function(js, timeout=t, polling=60)
        async def shot(n): await pg.screenshot(path=f'{WS}/ui/t223_{n}.png')
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await wait('typeof __T === "object"'); await pg.wait_for_timeout(800)
        await ev("document.getElementById('homePlay').click()"); await wait("__T.state === 'play'"); await wait("__T.tut && __T.tut.step === 0"); await wait("__T.H.st === 'play' && !__T.H.air")
        async def goto(sid):
            await ev("(() => { __T.tut.gap = 0; let n = 0; while (__T.TUT_STEPS[__T.tut.step].id !== '" + sid + "' && n++ < 20) __T.tutNext(); })()")
            await ev("if (__T.P.st === 'hide') __T.useSlam(__T.P)"); await wait("__T.P.st === 'play' && !__T.P.air")
        inview = "(x, y, z) => { const v = new __T.THREE.Vector3(x, y, z).project(__T.camera); return v.z < 1 && Math.abs(v.x) < 1 && Math.abs(v.y) < 1; }"
        if SEC == 'basin':
            await goto('basin')
            await pg.wait_for_timeout(300); print('basin comes up at', await ev("(() => { const q = __T.tut.potQ, P = __T.P; if (!q || !q.next) return 'none raised (the nearest one is used)'; const s = q.next, iv = " + inview + "; return [+Math.hypot(s[0] - P.x, s[2] - P.z).toFixed(1), iv(s[0], s[1] + 0.4, s[2])]; })()"))
            await wait("__T.tutTip && __T.tutTip.key === 'basin'"); t0 = await ev("__T.runT"); await shot('basin_tip'); await ev("__T.P.yaw += Math.PI")  # (heading away from it)
            await wait("document.querySelector('.tutgest') && document.querySelector('.tutgest').dataset.g === 'swipe' && !document.querySelector('.tutgest').hidden || __T.P.st === 'hide'")
            print('swipe finger after', round(await ev("__T.runT") - t0, 2), 's', await ev("[__T.P.st, document.querySelector('.tutgest').dataset.g, __T.tutTip && __T.tutTip.key]")); await pg.wait_for_timeout(300); await shot('basin_swipe')
        if SEC == 'finale':
            await goto('rest')
            # (you out on open floor facing open floor, the rival well away: what a player usually has around them by now)
            print('placed', await ev("""(() => { const T = __T, P = T.P, H = T.H, A = T.ARENA - 3, ok = (x, z) => Math.abs(x) < A && Math.abs(z) < A && T.surfaceUnder(x, z, 0.3) === 0 && !T.blockedAt(x, z, 0) && !T.pots.some(p => Math.hypot(p.x - x, p.z - z) < 2.5);
              for (let gx = -A; gx <= A; gx += 1.5) for (let gz = -A; gz <= A; gz += 1.5) { if (!ok(gx, gz)) continue; for (let k = 0; k < 8; k++) { const a = k * Math.PI / 4; let clear = true; for (let d = 0.5; d <= 8 && clear; d += 0.5) { const x = gx + Math.sin(a) * d, z = gz + Math.cos(a) * d; for (const s of [-1.2, 0, 1.2]) if (!ok(x + Math.cos(a) * s, z - Math.sin(a) * s)) clear = false; }
                if (clear) { P.x = gx; P.z = gz; P.y = 0; P.yaw = a; P.air = false; P.vy = 0; P.st = 'play'; P.stroke++; T.camYaw = a; H.x = -gx; H.z = -gz; H.stroke++; return [gx, gz, +a.toFixed(2)]; } } }
              return null; })()"""))
            await wait("!document.getElementById('tutGo').hidden"); print('card: clock', await ev("+__T.matchLeft.toFixed(2)")); await shot('fin_card')

            await ev("document.getElementById('tgGo').click()"); await pg.wait_for_timeout(200)
            print('rollers:', await ev("(() => { const P = __T.P, iv = " + inview + "; return __T.powers.filter(q => q.type === 'roller').map(q => [+Math.hypot(q.x - P.x, q.z - P.z).toFixed(1), iv(q.x, q.y + 0.4, q.z)]); })()"), 'clock', await ev("+__T.matchLeft.toFixed(2)"))
            await pg.wait_for_timeout(600); await shot('fin_rollers')
            if os.environ.get('ORBNOW'):  # (straight to the last seconds: the orb's moment, closely)
                await ev("__T.matchLeft = 4.3"); rows = []
                for i in range(160):
                    rows.append(await ev("[+__T.matchLeft.toFixed(2), __T.orb.on, __T.orb.on ? +Math.hypot(__T.orb.x - __T.P.x, __T.orb.z - __T.P.z).toFixed(2) : null, __T.orb.on ? +__T.orb.k.toFixed(2) : null, __T.orb.on ? +(__T.orb.pull || 0).toFixed(2) : null, __T.P.st, __T.P.air, +__T.P.spd.toFixed(1), +__T.P.yaw.toFixed(2), __T.P.rocket ? __T.P.rocket.ph : null, __T.orb.on ? [+__T.orb.x.toFixed(1), +__T.orb.z.toFixed(1), +__T.orb.y.toFixed(2)] : null, [+__T.P.x.toFixed(1), +__T.P.z.toFixed(1)]]"))
                    if rows[-1][9] or not rows[-1][0]: break
                    await pg.wait_for_timeout(40)
                for r in rows[::3]: print('  ', r)
                print('errors', errs[:4]); await b.close(); return
            await wait("__T.matchLeft < 8.4"); await ev("(() => { const P = __T.P, i = __T.powers.findIndex(q => q.type === 'roller'); if (!P.held && !P.power && i >= 0) { const q = __T.powers[i]; __T.scene.remove(q.g); __T.powers.splice(i, 1); P.held = 'roller'; } })()")  # (a roller picked up)
            await wait("__T.tutTip && __T.tutTip.key === 'finuse'", 60000); print('roller tip at', await ev("+__T.matchLeft.toFixed(2)")); await ev("__T.P.held = null; __T.P.power = { type: 'roller', t: 9 }")
            prev = None; landed = False
            for i in range(3000):
                r = await ev("[+__T.matchLeft.toFixed(2), __T.state + '/' + __T.P.st, __T.orb.on, __T.orb.on ? +Math.hypot(__T.orb.x - __T.P.x, __T.orb.z - __T.P.z).toFixed(1) : null, __T.P.rocket ? __T.P.rocket.ph : null, __T.tutTip && __T.tutTip.key, __T.P.power && __T.P.power.type]")
                key = r[1:3] + [r[4], r[5]]
                if prev is None or key != prev:
                    print('  ', r)
                    if r[2] and not (prev and prev[1]): print('   orb in view', await ev("(" + inview + ")(__T.orb.x, __T.orb.y, __T.orb.z)")); await shot('fin_orb')
                    if prev and prev[2] == 'dive' and r[4] is None and not landed: landed = True; await shot('fin_land')
                prev = key
                if not r[1].startswith('play'): break
                await pg.wait_for_timeout(50)
        print('errors', errs[:4]); await b.close()
asyncio.run(main())
