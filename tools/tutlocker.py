"""The onboarding's locker step: in the shop (locker step) the tip points at Back; in the locker, dressed, Ol' Bloop says take a look around
(nothing dimmed, no hand), steps aside after a few seconds, and closing the locker goes on to the next step. usage: tutlocker.py [page] [tag]"""
import asyncio, sys, functools
from playwright.async_api import async_playwright
print = functools.partial(print, flush=True)
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
PAGE = sys.argv[1] if len(sys.argv) > 1 else 'pc_h.html'; TAG = sys.argv[2] if len(sys.argv) > 2 else 'a'
STATE = "(() => ({ ph: __T.tutPh ? __T.tutPh() : null, tip: __T.tutTip && __T.tutTip.key, text: __T.tutTip && __T.tutTip.text, dim: document.getElementById('tutDim').className }))()"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 430, 'height': 790}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{}, drops: 40, runs: 1, owned: ['flower','fangs'], bought: ['flower','fangs'], look: { mouth: 'fangs', side: 'flower' }, tut: { ph: 'locker' } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); ev = pg.evaluate
        await pg.goto('http://localhost:8765/' + PAGE, timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000, polling=100); await pg.wait_for_timeout(3000)
        print('lobby', await ev(STATE))
        await ev("document.getElementById('dabsBtn').click()"); await pg.wait_for_timeout(1500); print('shop', await ev(STATE)); await pg.screenshot(path=f'{WS}/ui/tlk_{TAG}_shop.png')
        await ev("document.getElementById('shopBack').click()"); await pg.wait_for_timeout(1500); print('back', await ev(STATE))
        await ev("document.getElementById('lookBtn').click()"); await pg.wait_for_timeout(1800); print('locker 1.8s', await ev(STATE)); await pg.screenshot(path=f'{WS}/ui/tlk_{TAG}_locker.png')
        await pg.wait_for_timeout(4000); print('locker 5.8s', await ev(STATE)); await pg.screenshot(path=f'{WS}/ui/tlk_{TAG}_locker2.png')
        await ev("document.getElementById('lookDone').click()"); await pg.wait_for_timeout(2500); print('closed', await ev(STATE)); await pg.screenshot(path=f'{WS}/ui/tlk_{TAG}_after.png')
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
