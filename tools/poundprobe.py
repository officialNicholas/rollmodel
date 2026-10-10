"""The pound lesson: no tip and no slow-mo until the rival comes close, then the coach tip with slow-mo."""
import asyncio
from playwright.async_api import async_playwright
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 780})
        await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{}, drops: 0 })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        async def wait(js, t=600000): await pg.wait_for_function(js, timeout=t, polling=200)
        st = "[__T.tutTip && __T.tutTip.key, +__T.tut.slowK.toFixed(2), +__T.tut.st.toFixed(1), +Math.hypot(__T.H.x - __T.P.x, __T.H.z - __T.P.z).toFixed(1), document.getElementById('tut').hidden]"
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await wait('typeof __T === "object"'); await pg.wait_for_timeout(1500)
        await pg.evaluate("(() => { const r = __T.renderer, o = r.render.bind(r); let k = 0; window.__o = o; r.render = () => {}; })()")
        await pg.evaluate("document.getElementById('homePlay').click()"); await wait("__T.tut && __T.tut.step === 0")
        await pg.evaluate("(() => { let n = 0; while (__T.TUT_STEPS[__T.tut.step].id !== 'pound' && n++ < 20) __T.tutNext(); })()")
        await pg.wait_for_timeout(800); await pg.keyboard.press('e'); await pg.wait_for_timeout(600); await pg.keyboard.down('ArrowLeft')
        for i in range(40):
            v = await pg.evaluate("[" + st[1:-1] + ", __T.tut.sub, __T.tut.poundIn, __T.TUT_STEPS[__T.tut.step].id, __T.state, +__T.runT.toFixed(1), __T.H.st, __T.P.st, +__T.H.spd.toFixed(1), !!__T.H.charging, __T.H.ai.path && __T.H.ai.path.length, __T.H.ai.pi, [+__T.H.x.toFixed(1), +__T.H.z.toFixed(1), +__T.H.y.toFixed(1)], [+__T.P.x.toFixed(1), +__T.P.z.toFixed(1), +__T.P.y.toFixed(1)]]"); print('t', i, v, flush=True)
            if v[0] == 'pound': break
            if v[0] == 'burst': await pg.keyboard.press('e')
            await pg.wait_for_timeout(1000)
        await wait("__T.tutTip && __T.tutTip.key === 'pound'"); print('tip', await pg.evaluate(st), await pg.evaluate('__T.tutTip.text')); await pg.evaluate('__T.renderer.render = window.__o; 0'); await pg.wait_for_timeout(2500); await pg.screenshot(path=S + '/ws/ui/pound_tip.png')
        print('errors', errs); await b.close()
asyncio.run(main())
