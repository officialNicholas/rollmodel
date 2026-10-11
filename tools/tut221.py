"""v221: a lesson's praise and the next tip never on screen together. Forced: a praise held on (as if behind a banner) holds the next
lesson back until it's gone. Natural: landing in the basin, the praise, then "Full tank! Tap POUND to burst out" after it."""
import asyncio, os, functools
from playwright.async_api import async_playwright
print = functools.partial(print, flush=True)
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': int(os.environ.get('VW', 430)), 'height': int(os.environ.get('VH', 790))}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__tut = true; window.__skipIntro = false; window.__noReveal = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{}, drops: 0 })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); ev = pg.evaluate
        async def wait(js, t=300000): await pg.wait_for_function(js, timeout=t, polling=50)
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await wait('typeof __T === "object"'); await pg.wait_for_timeout(800)
        await ev("document.getElementById('homePlay').click()"); await wait("__T.state === 'play'"); await wait("__T.tut && __T.tut.step === 0"); await wait("__T.H.st === 'play' && !__T.H.air")
        state = "[Math.round(performance.now()), +__T.runT.toFixed(2), document.getElementById('tutPraise').classList.contains('on'), !!document.getElementById('tutPraise')._pend, __T.tutTip && __T.tutTip.key, __T.TUT_STEPS[__T.tut.step].id, +(__T.tut.gap || 0).toFixed(2)]"
        # forced: the praise held up (as if behind a banner) for 1.5 s; the next lesson must wait for it
        await ev("__T.tut.steered = true; __T.tut.jumped = true;"); await wait("__T.tut.gap > 0"); await ev("document.getElementById('tutPraise')._pend = true")
        rows = []
        for i in range(400):
            r = await ev(state); rows.append(r)
            if i == 30: await ev("document.getElementById('tutPraise')._pend = false")
            if r[5] != 'move': break
            await pg.wait_for_timeout(50)
        held = [r for r in rows if r[3]]; print('forced: held', len(held), 'samples, step stayed', set(r[5] for r in held), '; moved on at', rows[-1][:2], 'praise on', rows[-1][2])
        # natural: into the basin
        await ev("(() => { __T.tut.gap = 0; let n = 0; while (__T.TUT_STEPS[__T.tut.step].id !== 'basin' && n++ < 20) __T.tutNext(); })()")
        await wait("__T.tutTip && __T.tutTip.key === 'basin'"); await pg.wait_for_timeout(300)
        print('basin:', await ev("(() => { const P = __T.P, ps = __T.pots.filter(p => __T.potUp(p) && !p.occ); const p = ps.sort((a, b) => Math.hypot(a.x - P.x, a.z - P.z) - Math.hypot(b.x - P.x, b.z - P.z))[0]; if (!p) return 'no basin'; __T.enterPot(P, p); return P.st; })()"))
        rows = []; shot = False
        for i in range(800):
            r = await ev(state); rows.append(r)
            if r[2] and not shot: shot = True; await ev("document.getElementById('tutPraise').getAnimations().forEach(a => { a.pause(); a.currentTime = 450; })"); await pg.screenshot(path=f'{WS}/ui/t221_praise.png'); await ev("document.getElementById('tutPraise').getAnimations().forEach(a => a.play())")  # (held mid-way for the picture only)
            if r[4] == 'burst': await pg.wait_for_timeout(200); await pg.screenshot(path=f'{WS}/ui/t221_burst.png'); rows.append(await ev(state)); break
            await pg.wait_for_timeout(40)
        t0 = rows[0][0]; ch = [[r[0] - t0] + r[1:] for k, r in enumerate(rows) if k == 0 or rows[k - 1][2:6] != r[2:6]]
        print('natural (ms, runT, praise, pending, tip, step, gap):'); [print('  ', c) for c in ch]
        both = [r for r in rows if r[2] and r[4]]; print('praise and a tip together:', len(both))
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
