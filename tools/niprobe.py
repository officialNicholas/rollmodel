"""v181: the lesson's gift reveals Flower + Fangs on the New items! screen with the shop's real renders, then the shop flow still works."""
import asyncio, sys
from playwright.async_api import async_playwright
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
W, H, tag = (390, 780, 'port') if (sys.argv[1:] or ['port'])[0] == 'port' else (844, 390, 'land')
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': W, 'height': H})
        await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'" + tag + "', name:'Dusk', seen:{}, drops: 0 })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        async def wait(js, t=300000): await pg.wait_for_function(js, timeout=t, polling=200)
        tip = "[__T.tutPh(), __T.tutTip && __T.tutTip.key, __T.tutTip && __T.tutTip.text]"
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await wait('typeof __T === "object"'); await pg.wait_for_timeout(1500)
        await pg.evaluate("(() => { const r = __T.renderer; window.__o = r.render.bind(r); r.render = () => {}; })()")
        await pg.evaluate("document.getElementById('homePlay').click()"); await wait("__T.tut && __T.tut.step === 0")
        await pg.evaluate("(() => { let n = 0; while (__T.TUT_STEPS[__T.tut.step].id !== 'rest' && n++ < 20) __T.tutNext(); })()")
        print('after flower step', await pg.evaluate("[JSON.stringify(__T.newItemV), __T.OWNED.has('flower'), __T.OWNED.has('fangs')]"))
        await wait("!document.getElementById('tutGo').hidden", 60000); await pg.evaluate("document.getElementById('tgGo').click()"); await pg.wait_for_timeout(500)
        await pg.evaluate("__T.P.kos = 2; __T.matchLeft = 0.05; 0"); await wait("__T.state === 'dead'", 60000)
        await pg.evaluate("__T.renderer.render = window.__o; 0")
        await wait("!document.getElementById('tutWin').hidden", 120000); await pg.wait_for_timeout(2600); print('tutwin', await pg.evaluate("document.getElementById('twRew').textContent")); await pg.evaluate("document.getElementById('twNext').click()")
        await wait("!document.getElementById('victory').hidden", 120000); await wait("__T.vic && __T.vic.t >= 1", 120000); await pg.evaluate("document.getElementById('victory').click()")
        await wait("!document.getElementById('newItem').hidden", 120000); await pg.wait_for_timeout(3200)
        print('newitem', await pg.evaluate("[document.getElementById('niKick').textContent, document.getElementById('niName').textContent, document.getElementById('niWhere').textContent, document.getElementById('niTry').textContent, [...document.querySelectorAll('#niBadges .nibadge')].map(b => b.querySelector('img') ? 'img' : 'svg')]"), await pg.evaluate(tip))
        await pg.screenshot(path=S + '/ws/ui/ni_two_' + tag + '.png')
        await pg.evaluate("document.getElementById('niTry').click()"); await wait("__T.state === 'menu' && !document.getElementById('shop').hidden", 120000); await pg.wait_for_timeout(1500)
        print('shop', await pg.evaluate(tip), await pg.evaluate("__T.store.drops"))
        await pg.evaluate("document.getElementById('shopGrid').querySelector('.shitem[data-w=\"flower\"]').click()"); await pg.wait_for_timeout(1800); print('fangs', await pg.evaluate(tip), await pg.evaluate("[__T.store.drops, JSON.stringify(__T.store.tut.price)]"))
        await pg.evaluate("document.getElementById('shopGrid').querySelector('.shitem[data-w=\"fangs\"]').click()"); await pg.wait_for_timeout(1800); print('bought', await pg.evaluate(tip), await pg.evaluate("__T.store.drops"))
        print('errors', errs); await b.close()
asyncio.run(main())
