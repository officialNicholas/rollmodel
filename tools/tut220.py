"""v220 lesson pacing in a real run of the lesson match: the first tip's wait after the basin, a lesson's praise on its own before the next
tip, the rival brought into view for the pound and the dodge, the roller's pacing and its swipe tip, the slow motion's vignette, and the
old jelly ball standing in for the axolotl on a long slingshot."""
import asyncio, os, json, functools
print = functools.partial(print, flush=True)
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
os.makedirs(WS + '/ui', exist_ok=True)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 430, 'height': 790}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__tut = true; window.__skipIntro = false; window.__noReveal = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{}, drops: 0 })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        async def wait(js, t=90000): await pg.wait_for_function(js, timeout=t, polling=100)
        async def shot(n): await pg.screenshot(path=f'{WS}/ui/t220_{n}.png')
        ev = pg.evaluate
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await wait('typeof __T === "object"', 240000); await pg.wait_for_timeout(1200)
        await ev("document.getElementById('homePlay').click()"); await wait("__T.state === 'play'", 120000)
        # 1. the first tip waits a second and a half after you're out of the basin
        await wait("__T.tut && __T.tut.outAt !== undefined", 60000); out = await ev("__T.tut.outAt")
        await wait("__T.tut.step === 0", 30000); print('1. out of the basin at', round(out, 2), 'move tip at', round(await ev("__T.runT"), 2), await ev("[__T.tutTip && __T.tutTip.key, __T.tut.slowK]")); await pg.wait_for_timeout(500); await shot('move')
        # 2. a lesson done: the praise alone, then the next tip
        await ev("__T.tut.steered = true; __T.tut.jumped = true;"); await wait("__T.tut.gap > 0", 10000)
        rows = []
        for i in range(14):
            rows.append(await ev("[+__T.runT.toFixed(2), __T.TUT_STEPS[__T.tut.step].id, +(__T.tut.gap || 0).toFixed(2), __T.tutTip && __T.tutTip.key, document.getElementById('tutPraise').classList.contains('on'), __T.tut.slowK]"))
            if i == 2: await shot('praise')
            await pg.wait_for_timeout(150)
        print('2. praise then next:', rows[0], rows[3], rows[-1])
        async def goto(sid):
            await ev("(() => { __T.tut.gap = 0; let n = 0; while (__T.tut && __T.TUT_STEPS[__T.tut.step].id !== '" + sid + "' && n++ < 20) __T.tutNext(); })()")
            print('   at', await ev("__T.TUT_STEPS[__T.tut.step].id"))
        async def far():  # out of the basin if the lesson left you in one; then the rival on open ground well away, out of sight
            await ev("if (__T.P.st === 'hide') __T.useSlam(__T.P)"); await wait("__T.P.st === 'play' && !__T.P.air", 120000)
            print('   rival put at', await ev("""(() => { const T = __T, P = T.P, H = T.H, A = T.ARENA - 2, V = T.THREE.Vector3;
              for (const r of [13, 11, 15, 9]) for (let k = 0; k < 24; k++) { const a = P.yaw + Math.PI + (k % 2 ? 1 : -1) * Math.floor((k + 1) / 2) * 0.26, x = P.x + Math.sin(a) * r, z = P.z + Math.cos(a) * r;
                if (Math.abs(x) > A || Math.abs(z) > A || T.surfaceUnder(x, z, 0.3) !== 0 || T.blockedAt(x, z, 0) || T.pots.some(p => Math.hypot(p.x - x, p.z - z) < 2.5)) continue;
                const q = new V(x, 0.3, z).project(T.camera); if (q.z < 1 && Math.abs(q.x) < 1.1 && Math.abs(q.y) < 1.1) continue;
                H.x = x; H.z = z; H.y = 0; H.air = false; H.vy = 0; H.stroke++; if (H.ai) { H.ai.plan = null; H.ai.path = null; } return [+x.toFixed(1), +z.toFixed(1), r]; }
              return null; })()"""))
        dist = "+Math.hypot(__T.H.x - __T.P.x, __T.H.z - __T.P.z).toFixed(1)"
        seen = "(() => { const v = new __T.THREE.Vector3(__T.H.x, __T.H.y + 0.3, __T.H.z).project(__T.camera); return v.z < 1 && Math.abs(v.x) < 1 && Math.abs(v.y) < 1; })()"
        await wait("__T.H.st === 'play' && !__T.H.air", 300000)
        # 3. the pound: the rival brought into view, the tip once it's in the pound's reach
        await goto('pound'); await pg.wait_for_timeout(300); await far(); d0 = await ev(dist)
        await wait(dist.replace('+', '') + " < 8", 300000); print('3. pound: rival', d0, '->', await ev(dist), 'in view', await ev(seen)); await pg.wait_for_timeout(200); await shot('pound_in')
        await wait("__T.tutTip && __T.tutTip.key === 'pound'", 300000); print('   pound tip with the rival at', await ev(dist), 'slow', await ev("__T.tut.slowK"), 'vignette', await ev("document.getElementById('tutSlow').className")); await shot('pound_tip')
        # 4. the dodge: the rival in view, its pound coming, the moment to swipe (the deep vignette)
        await goto('dodge'); await pg.wait_for_timeout(300); await far(); d0 = await ev(dist)
        await wait(dist.replace('+', '') + " < 8.5", 300000); print('4. dodge: rival', d0, '->', await ev(dist), 'in view', await ev(seen))
        await wait("__T.H.slam", 300000); print('   its pound starts at', await ev(dist), 'in view', await ev(seen))
        await wait("__T.tutTip && __T.tutTip.key === 'dodgenow'", 300000); print('   swipe now:', await ev("[__T.tut.slowK, document.getElementById('tutSlow').className]")); await shot('dodge_now')
        # 5. the roller: a breath, it pops up, its tip a moment later; once a roller, the quick swipe tip at full speed
        await goto('item'); t0 = await ev("__T.runT"); rows = []
        for i in range(400):
            rows.append(await ev("[+(__T.runT - " + str(t0) + ").toFixed(2), __T.powers.filter(q => q.type === 'roller').length, __T.tutTip && __T.tutTip.key]")); await pg.wait_for_timeout(120)
            if rows[-1][0] > 3.2: break
        print('5. roller:', [r for k, r in enumerate(rows) if k % 3 == 0 or (k and (rows[k - 1][1] != r[1] or rows[k - 1][2] != r[2]))])
        await ev("__T.P.held = 'roller'"); await wait("__T.tutTip && __T.tutTip.key === 'use'", 120000); await ev("__T.useHeld(__T.P)")
        t1 = await ev("__T.runT"); rows = []
        for i in range(600):
            rows.append(await ev("[+(__T.runT - " + str(t1) + ").toFixed(2), performance.now() < __T.bannerUntil, document.getElementById('tutPraise').classList.contains('on'), __T.tutTip && __T.tutTip.key, __T.tut.slowK]")); await pg.wait_for_timeout(120)
            if rows[-1][0] > 6: break
            if rows[-1][3] == 'rroll' and not any(r[3] == 'rroll' for r in rows[:-1]): await shot('rroll')
        ch = [r for k, r in enumerate(rows) if k == 0 or rows[k - 1][1:] != r[1:]]
        print('   after using it (t, banner, praise, tip, slow):', ch)
        # 6. a long slingshot: the old jelly ball in the axolotl's place
        await goto('free3'); await pg.wait_for_timeout(600); await wait("!__T.P.air && __T.P.st === 'play'", 120000)
        await ev("__T.flingIt(__T.P, 1)"); rows = []
        for i in range(14):
            rows.append(await ev("[+__T.P.vy.toFixed(1), !!__T.VP.balled, __T.VP.oldBlob.visible, __T.VP.slime.root.visible]"))
            if i == 2: await shot('ball')
            await pg.wait_for_timeout(70)
        print('6. fling (vy, balled, jelly shown, axolotl shown):', rows)
        print('errors', errs[:5]); await b.close()
asyncio.run(main())
