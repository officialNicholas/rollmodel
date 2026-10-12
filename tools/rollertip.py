"""The lesson's roller tip: after the roller is in hand, when the tip comes against where the rival is (distance, ahead, on screen), with a
shot at the moment it shows. usage: rollertip.py [page] [tag]"""
import asyncio, sys, functools
print = functools.partial(print, flush=True)
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
PAGE = sys.argv[1] if len(sys.argv) > 1 else 'pc_h.html'; TAG = sys.argv[2] if len(sys.argv) > 2 else 'a'
SEEN = "(() => { const P = __T.P, H = __T.H; if (!H) return null; const dx = H.x - P.x, dz = H.z - P.z, d = Math.hypot(dx, dz), fw = (Math.sin(P.yaw) * dx + Math.cos(P.yaw) * dz) / Math.max(d, 1e-3); return [+d.toFixed(1), +fw.toFixed(2)]; })()"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__tut = true; window.__noVote = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{}, drops: 0, runs: 0, tut: { ph: 'match' } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); ev = pg.evaluate
        wait = lambda f, t=240000: pg.wait_for_function(f, timeout=t, polling=100)
        await pg.goto('http://localhost:8765/' + PAGE, timeout=240000); await wait('typeof __T === "object"'); await pg.wait_for_timeout(1500)
        await ev("__T.start()"); await wait("__T.state === 'play' && __T.tut && __T.tut.step !== undefined", 400000)
        await wait("__T.tut && __T.tut.outAt !== undefined", 400000); await wait("__T.tut.step === 0", 400000); await pg.wait_for_timeout(500)
        await ev("(() => { __T.tut.gap = 0; let n = 0; while (__T.tut && __T.TUT_STEPS[__T.tut.step].id !== 'item' && n++ < 20) __T.tutNext(); })()"); print('at', await ev("__T.TUT_STEPS[__T.tut.step].id"))
        await wait("__T.powers.filter(q => q.type === 'roller').length > 0", 400000); await ev("__T.P.held = 'roller'"); await wait("__T.tutTip && __T.tutTip.key === 'use'", 400000); await ev("__T.useHeld(__T.P)")
        t0 = await ev("__T.runT"); shown = None
        for i in range(300):
            r = await ev("[+(__T.runT - " + str(t0) + ").toFixed(2), __T.TUT_STEPS[__T.tut.step].id, __T.tutTip && __T.tutTip.key, " + SEEN + ", __T.tut.driveMode, __T.tut.rTip, __T.P.power && +__T.P.power.t.toFixed(1), __T.lineClear(__T.P, __T.H.x, __T.H.z, __T.P.y), __T.tutRivalSeen(9), __T.tut.rSeen, __T.tut.rIn]")
            if i % 3 == 0 or (r[2] == 'rroll' and shown is None): print(r, await ev("(() => { const H = __T.H, v = new THREE.Vector3(H.x, H.y + 0.3, H.z).project(__T.camera); return [+v.x.toFixed(2), +v.y.toFixed(2), +v.z.toFixed(3), __T.H.st]; })()"))
            if r[2] == 'rroll' and shown is None: shown = r; await pg.screenshot(path=f'{WS}/ui/rt_{TAG}_tip.png'); print('tip text', await ev("document.getElementById('tutCall').textContent"))
            if shown and r[2] != 'rroll': break
            await pg.wait_for_timeout(150)
        print('shown', shown, 'errors', errs[:3]); await b.close()
asyncio.run(main())
