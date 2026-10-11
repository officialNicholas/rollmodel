"""The onboarding's shop step through a turn of the phone: the tip on the flower, the phone turned sideways, the shop scrolled to the
bottom, turned back upright. The flower should be back in view, inside the tip's window, and buyable. usage: tutrotate.py [tag]"""
import asyncio, sys, functools
from playwright.async_api import async_playwright
print = functools.partial(print, flush=True)
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
TAG = sys.argv[1] if len(sys.argv) > 1 else 'a'
STATE = """(() => { const f = document.querySelector('.shitem[data-w="flower"]'), r = f && f.getBoundingClientRect(), g = document.getElementById('shopGrid'), d = document.getElementById('tutDim');
  return { tip: __T.tutTip && __T.tutTip.key, flower: r && [Math.round(r.top), Math.round(r.bottom)], vh: innerHeight, scroll: g && Math.round(g.scrollTop), win: d.dataset.w, cls: d.className }; })()"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 430, 'height': 790}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__tut = true; window.__noRotate = false; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{}, drops: 40, runs: 1, owned: [], tut: { ph: 'shop', price: { flower: 10 } } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); ev = pg.evaluate
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000, polling=100); await pg.wait_for_timeout(2500)
        await ev("document.getElementById('dabsBtn').click()"); await pg.wait_for_timeout(2500)
        print('start', await ev(STATE))
        await pg.set_viewport_size({'width': 790, 'height': 430}); await pg.wait_for_timeout(1500)
        await ev("document.getElementById('shopGrid').scrollTop = 99999"); await pg.wait_for_timeout(400)
        print('sideways', await ev(STATE)); await pg.screenshot(path=f'{WS}/ui/tutrot_{TAG}_side.png')
        await pg.set_viewport_size({'width': 430, 'height': 790}); await ev("document.getElementById('shopGrid').scrollTop = 99999"); await pg.wait_for_timeout(1500)
        st = await ev(STATE); print('upright', st); await pg.screenshot(path=f'{WS}/ui/tutrot_{TAG}_back.png')
        ok = st['flower'] and 0 <= st['flower'][0] and st['flower'][1] <= st['vh']; print('flower in view:', ok)
        if ok:  # tap it where the tip's window is
            await ev("(() => { const f = document.querySelector('.shitem[data-w=\"flower\"]'), r = f.getBoundingClientRect(), x = r.left + r.width / 2, y = r.top + r.height / 2, t = document.elementFromPoint(x, y); window.__hit = t && (t.closest('.shitem') || {}).dataset; })()")
            print('tap lands on', await ev("window.__hit && window.__hit.w"))
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
