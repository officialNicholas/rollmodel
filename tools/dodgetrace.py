"""trace each rival pound in the dodge lesson with no input from you: where you were, what the tip said, and how it ended"""
import asyncio
from playwright.async_api import async_playwright
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{}, drops: 0 })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        async def wait(js, t=300000): await pg.wait_for_function(js, timeout=t, polling=50)
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await wait('typeof __T === "object"'); await pg.wait_for_timeout(1500)
        await pg.evaluate("(() => { const r = __T.renderer; window.__o = r.render.bind(r); r.render = () => {}; })(); 0")
        await pg.tap('#homePlay'); await wait("__T.tut && __T.tut.step === 0")
        await pg.evaluate("(() => { let n = 0; while (__T.TUT_STEPS[__T.tut.step].id !== 'dodge' && n++ < 20) __T.tutNext(); })(); 0")
        await pg.evaluate("""(() => { window.__log = []; let was = false, wst = 'play'; const L = () => { const P = __T.P, H = __T.H, t = __T.tut; if (__T.TUT_STEPS[t.step].id !== 'dodge') return;
          if (P.st === 'hide') __T.exitPot(P, true);
          const s = [+t.st.toFixed(2), H.slam ? 'SLAM' : '-', +(H.slam ? H.slamEta - H.slamT : 0).toFixed(2), +Math.hypot(H.x - P.x, H.z - P.z).toFixed(2), P.air, +(P.y).toFixed(2), +(H.y).toFixed(2), P.st, t.sub, t.slowK];
          if (H.slam !== was || P.st !== wst) __log.push(s.join(' ')); else if (H.slam && __log.length < 400) __log.push('  ' + s.join(' ')); was = H.slam; wst = P.st; requestAnimationFrame(L); }; requestAnimationFrame(L); })(); 0""")
        await pg.keyboard.down('ArrowLeft'); await wait("__T.TUT_STEPS[__T.tut.step].id !== 'dodge'", 600000)
        for l in await pg.evaluate("__log"): print(l)
        print('errors', errs); await b.close()
asyncio.run(main())
