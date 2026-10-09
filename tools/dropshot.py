import asyncio
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', mode:'duel', seen:{steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,look:1}, owned:['hat','pirate','patch'], bought:['hat'], drops: 90, look:{head:'hat'} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(2500)
        await pg.screenshot(path=f'{WS}/ui/d9_lobby.png')
        await pg.evaluate("document.getElementById('lookBtn').click()"); await pg.wait_for_timeout(2500); await pg.screenshot(path=f'{WS}/ui/d9_locker.png')
        await pg.evaluate("document.querySelector('.ltile[data-w=\"pirate\"]').click()"); await pg.wait_for_timeout(500); await pg.screenshot(path=f'{WS}/ui/d9_broke.png')
        print('after broke tap', await pg.evaluate("[__T.store ? __T.store.drops : 'n/a', document.getElementById('lkBalN').textContent, document.getElementById('lookNote').textContent]"))
        await pg.evaluate("__T.store.drops = 200; document.querySelector('#lookCats .lcat').click()"); await pg.wait_for_timeout(400)
        await pg.evaluate("document.querySelector('.ltile[data-w=\"pirate\"]').click()"); await pg.wait_for_timeout(900); await pg.screenshot(path=f'{WS}/ui/d9_bought.png')
        print('chip', await pg.evaluate("(() => { const e = document.getElementById('lkBal'), r = e.getBoundingClientRect(), c = getComputedStyle(e); return [e.className, Math.round(r.left) + ',' + Math.round(r.top) + ' ' + Math.round(r.width) + 'x' + Math.round(r.height), c.display, c.opacity, c.visibility, c.scale, e.parentElement.className, [...e.parentElement.children].map(x => x.id + ':' + Math.round(x.getBoundingClientRect().width)).join(' ')]; })()"))
        print('after buy', await pg.evaluate("[document.getElementById('lkBalN').textContent, document.getElementById('lookNote').textContent, JSON.parse(localStorage.getItem('paint-world-red.v1')).bought, JSON.parse(localStorage.getItem('paint-world-red.v1')).look]"))
        await pg.evaluate("document.getElementById('lookDone').click()"); await pg.wait_for_timeout(600)
        await pg.evaluate("document.getElementById('homePlay').click()"); await pg.wait_for_function("__T.state === 'play'", timeout=30000); await pg.wait_for_timeout(1500)
        await pg.evaluate("(() => { const P = __T.P; for (let i = 0; i < 16; i++) { const x = P.x + (i % 4 - 1.5) * 3.2, z = P.z + (i / 4 | 0) * 3.2 - 4.8; __T.addSplat(x, Math.max(0, __T.surfaceUnder(x, z, P.y + 3, true)), z, 0, 3, __T.clock, false, true, 0); } __T.flushTrail(); __T.matchLeft = 0.4; })()")
        await pg.wait_for_function("!!__T.vic", timeout=40000, polling=200); await pg.wait_for_timeout(1500)
        await pg.tap('#victory'); await pg.wait_for_function("!document.getElementById('end').hidden", timeout=10000); await pg.wait_for_timeout(2500); await pg.screenshot(path=f'{WS}/ui/d9_end.png')
        print('results', await pg.evaluate("[document.getElementById('dropGain').textContent, JSON.parse(localStorage.getItem('paint-world-red.v1')).drops]"))
        print('errors', errs[:4]); await b.close()
asyncio.run(main())
