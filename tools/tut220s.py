"""v220 in the lesson match, one section per run (dodge | item | ball): the rival brought into view for the dodge and its pound's
moment with the deep vignette; the roller's pacing and the quick swipe tip; the old jelly ball for a long slingshot and a roll out of a
basin. usage: tut220s.py <section>"""
import asyncio, os, sys, functools
from playwright.async_api import async_playwright
print = functools.partial(print, flush=True)
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'; SEC = sys.argv[1]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': int(os.environ.get('VW', 430)), 'height': int(os.environ.get('VH', 790))}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__tut = true; window.__skipIntro = false; window.__noReveal = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{}, drops: 0 })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        async def wait(js, t=240000): await pg.wait_for_function(js, timeout=t, polling=100)
        async def shot(n): await pg.screenshot(path=f'{WS}/ui/t220_{n}.png')
        ev = pg.evaluate
        dist = "+Math.hypot(__T.H.x - __T.P.x, __T.H.z - __T.P.z).toFixed(1)"
        seen = "(() => { const v = new __T.THREE.Vector3(__T.H.x, __T.H.y + 0.3, __T.H.z).project(__T.camera); return v.z < 1 && Math.abs(v.x) < 1 && Math.abs(v.y) < 1; })()"
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await wait('typeof __T === "object"'); await pg.wait_for_timeout(1000)
        await ev("document.getElementById('homePlay').click()"); await wait("__T.state === 'play'"); await wait("__T.tut && __T.tut.step === 0"); await wait("__T.H.st === 'play' && !__T.H.air")
        async def goto(sid):
            await ev("(() => { __T.tut.gap = 0; let n = 0; while (__T.tut && __T.TUT_STEPS[__T.tut.step].id !== '" + sid + "' && n++ < 20) __T.tutNext(); })()")
            await ev("if (__T.P.st === 'hide') __T.useSlam(__T.P)"); await wait("__T.P.st === 'play' && !__T.P.air")
            print('at', await ev("[__T.TUT_STEPS[__T.tut.step].id, +__T.runT.toFixed(1)]"))
        if SEC == 'dodge':
            await goto('pound'); await ev("__T.tut.poundIn = true")
            # the rival on open ground well away from you, out of sight (as if it had wandered off)
            print('rival put at', await ev("""(() => { const T = __T, P = T.P, H = T.H, A = T.ARENA - 2, V = T.THREE.Vector3;
              for (const r of [13, 11, 15, 9]) for (let k = 0; k < 24; k++) { const a = P.yaw + Math.PI + (k % 2 ? 1 : -1) * Math.floor((k + 1) / 2) * 0.26, x = P.x + Math.sin(a) * r, z = P.z + Math.cos(a) * r;
                if (Math.abs(x) > A || Math.abs(z) > A || T.surfaceUnder(x, z, 0.3) !== 0 || T.blockedAt(x, z, 0) || T.pots.some(p => Math.hypot(p.x - x, p.z - z) < 2.5)) continue;
                const q = new V(x, 0.3, z).project(T.camera); if (q.z < 1 && Math.abs(q.x) < 1.1 && Math.abs(q.y) < 1.1) continue;
                H.x = x; H.z = z; H.y = 0; H.air = false; H.vy = 0; H.stroke++; if (H.ai) { H.ai.plan = null; H.ai.path = null; } return [+x.toFixed(1), +z.toFixed(1), r]; }
              return null; })()"""), 'dist', await ev(dist))
            await ev("(() => { __T.tut.gap = 0; let n = 0; while (__T.TUT_STEPS[__T.tut.step].id !== 'dodge' && n++ < 20) __T.tutNext(); })()"); print('at dodge', await ev(dist), await ev(seen))
            prev = None
            for i in range(600):
                r = await ev("[+__T.runT.toFixed(2), " + dist + ", " + seen + ", __T.H.slam, __T.tutTip && __T.tutTip.key, __T.tut.slowK, document.getElementById('tutSlow').className, __T.P.st]")
                if prev and abs(r[1] - prev[1]) > 2.5: print('   moved:', prev[1], '->', r[1], 'in view', r[2]); await shot('dodge_in')
                if r[3] and not (prev and prev[3]): print('   its pound starts:', r)
                if r[4] == 'dodgenow': print('   swipe now:', r); await shot('dodge_now'); break
                if i % 40 == 0: print('   ', r)
                prev = r; await pg.wait_for_timeout(100)
        if SEC == 'item':
            await goto('item'); t0 = await ev("__T.runT"); rows = []
            for i in range(600):
                rows.append(await ev("[+(__T.runT - " + str(t0) + ").toFixed(2), __T.powers.filter(q => q.type === 'roller').length, __T.tutTip && __T.tutTip.key]")); await pg.wait_for_timeout(100)
                if rows[-1][0] > 3: break
            print('roller (t, rollers, tip):', [r for k, r in enumerate(rows) if k == 0 or rows[k - 1][1:] != r[1:]])
            await shot('item'); await ev("__T.P.held = 'roller'"); await wait("__T.tutTip && __T.tutTip.key === 'use'"); await ev("__T.P.held = null; __T.P.paint = 1; __T.P.power = { type: 'roller', t: 9 }; __T.banner('Roller!', 'Wide stripes. Paint refilled');")
            t1 = await ev("__T.runT"); rows = []; shot_done = False
            for i in range(900):
                rows.append(await ev("[+(__T.runT - " + str(t1) + ").toFixed(2), performance.now() < __T.bannerUntil, document.getElementById('tutPraise').classList.contains('on'), __T.tutTip && __T.tutTip.key, __T.tut.slowK]"))
                if rows[-1][3] == 'rroll' and not shot_done: shot_done = True; await pg.wait_for_timeout(300); await shot('rroll')
                if rows[-1][0] > 7: break
                await pg.wait_for_timeout(100)
            print('after using it (t, banner, praise, tip, slow):', [r for k, r in enumerate(rows) if k == 0 or rows[k - 1][1:] != r[1:]])
        if SEC == 'ball':
            await goto('free3')
            await ev("__T.flingIt(__T.P, 1)"); rows = []
            for i in range(40):
                rows.append(await ev("[+__T.P.vy.toFixed(1), !!__T.VP.balled, __T.VP.oldBlob.visible, __T.VP.slime.root.visible]"))
                if len(rows) > 1 and rows[-1][1] and not rows[-2][1]: await pg.wait_for_timeout(120); await shot('ball')
                if len(rows) > 3 and not rows[-1][1] and rows[-4][1]: await pg.wait_for_timeout(60); await shot('ball_out')
                await pg.wait_for_timeout(40)
            print('fling (vy, balled, jelly shown, axolotl shown):', [r for k, r in enumerate(rows) if k == 0 or rows[k - 1][1:] != r[1:]])
            await wait("(__T.P.st === 'play' && !__T.P.air) || __T.P.st === 'hide'"); await pg.wait_for_timeout(500)
            if await ev("__T.P.st === 'hide'"): print('basin: respawned in one')
            else: print('basin:', await ev("(() => { const P = __T.P, p = __T.pots.reduce((a, q) => !a || Math.hypot(q.x - P.x, q.z - P.z) < Math.hypot(a.x - P.x, a.z - P.z) ? q : a, null); if (!p) return null; p.st = 'up'; __T.enterPot(P, p); return [P.st, +Math.hypot(p.x - P.x, p.z - P.z).toFixed(1)]; })()"))
            await pg.wait_for_timeout(1500); await ev("__T.exitPot(__T.P, true)"); rows = []
            for i in range(30):
                rows.append(await ev("[+__T.P.rollOutT.toFixed(2), !!__T.VP.balled, __T.VP.oldBlob.visible, __T.VP.slime.root.visible]"))
                if i == 3: await shot('rollout')
                await pg.wait_for_timeout(40)
            print('roll out of a basin (rollOutT, balled, jelly, axolotl):', [r for k, r in enumerate(rows) if k == 0 or rows[k - 1][1:] != r[1:]])
        print('errors', errs[:5]); await b.close()
asyncio.run(main())
