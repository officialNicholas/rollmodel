"""v178: no badge row over the lesson tips; the +5 still pops under the score."""
import asyncio
from playwright.async_api import async_playwright
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 780})
        await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{}, drops: 0 })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        async def wait(js, t=300000): await pg.wait_for_function(js, timeout=t, polling=200)
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await wait('typeof __T === "object"'); await pg.wait_for_timeout(1500)
        await pg.evaluate("(() => { const r = __T.renderer; window.__o = r.render.bind(r); r.render = () => {}; })()")
        await pg.evaluate("document.getElementById('homePlay').click()"); await wait("__T.tut && __T.tut.step === 0")
        await pg.evaluate("(() => { let n = 0; while (__T.TUT_STEPS[__T.tut.step].id !== 'sling' && n++ < 20) __T.tutNext(); })()"); await pg.wait_for_timeout(1500)
        await pg.evaluate("__T.tutReward('move'); 0"); await pg.wait_for_timeout(150)
        print('state', await pg.evaluate("[__T.tutTip && __T.tutTip.text, getComputedStyle(document.getElementById('tutPips')).display, document.getElementById('tutPips').classList.contains('on'), (document.querySelector('.tutplus') || {}).textContent, __T.tut.bonus]"))
        await pg.evaluate("__T.renderer.render = window.__o; 0"); await pg.wait_for_timeout(1500); await pg.screenshot(path=S + '/ws/ui/pips_gone.png')
        print('errors', errs); await b.close()
asyncio.run(main())
