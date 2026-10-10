import asyncio
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 780}, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{steer:1}, runs: 1, drops: 0, owned: ['flower','fangs'], bought: ['flower','fangs'], tut: { ph: 'locker' } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        tip = "[__T.tutPh(), __T.tutTip && __T.tutTip.key, __T.tutTip && __T.tutTip.text, document.getElementById('tut').dataset.pos, document.getElementById('tutDim').className, document.getElementById('tutHand').hidden]"
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(1200)
        print('lobby', await pg.evaluate(tip))
        await pg.evaluate("document.getElementById('lookBtn').click()"); await pg.wait_for_timeout(1500); print('locker', await pg.evaluate(tip))
        await pg.evaluate("document.getElementById('lc-face').click()"); await pg.wait_for_timeout(900); print('face', await pg.evaluate(tip))
        await pg.evaluate("document.getElementById('lookRail').querySelector('.ltile[data-w=\"fangs\"]').click()"); await pg.wait_for_timeout(900); print('fangs on', await pg.evaluate(tip)); await pg.screenshot(path=f'{WS}/ui/lock_head.png')
        await pg.evaluate("document.getElementById('lc-head').click()"); await pg.wait_for_timeout(900); print('head tab', await pg.evaluate(tip)); await pg.screenshot(path=f'{WS}/ui/lock_flower.png')
        await pg.evaluate("document.getElementById('lookRail').querySelector('.ltile[data-w=\"flower\"]').click()"); await pg.wait_for_timeout(900); print('worn', await pg.evaluate(tip), await pg.evaluate("JSON.parse(localStorage.getItem('paint-world-red.v1')).look"))
        await pg.evaluate("document.getElementById('lookDone').click()"); await pg.wait_for_timeout(1500); print('pick', await pg.evaluate(tip))
        await pg.evaluate("document.getElementById('stageBtn').click()"); await pg.wait_for_timeout(1500); print('start', await pg.evaluate(tip)); await pg.screenshot(path=f'{WS}/ui/lock_start.png')
        s0 = await pg.evaluate("__T.stageSel"); el = await pg.query_selector('#stagePick .world:not([aria-pressed="true"])'); 
        bb = await pg.evaluate("(() => { const n = [...document.querySelectorAll('#worldNext, .wnext, [aria-label*=\"Next\"]')].find(e => e.offsetParent); if (!n) return null; const r = n.getBoundingClientRect(); return [r.left + r.width / 2, r.top + r.height / 2]; })()")
        hit = await pg.evaluate("(() => { const out = []; for (const [x, y] of [[361, 390], [195, 330], [30, 390]]) { const e = document.elementFromPoint(x, y); out.push((e.id || e.className || e.tagName).toString().slice(0, 40)); } return out; })()"); print('top elements at arrow/painting/left', hit)
        if bb: await pg.mouse.click(bb[0], bb[1]); await pg.wait_for_timeout(6000)
        print('picked', s0, '->', await pg.evaluate("__T.stageSel"), 'via', bb); print('errors', errs[:3]); await b.close()
asyncio.run(main())
