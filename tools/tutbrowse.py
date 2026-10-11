"""The onboarding after the shop lesson: in the shop, Ol' Bloop says take a look around (no dim, no hand on Back) and steps aside after a few
seconds; leaving the shop on your own goes on to the locker step. usage: tutbrowse.py [tag]"""
import asyncio, sys, functools
from playwright.async_api import async_playwright
print = functools.partial(print, flush=True)
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
TAG = sys.argv[1] if len(sys.argv) > 1 else 'a'
STATE = "(() => ({ tip: __T.tutTip && __T.tutTip.key, text: __T.tutTip && __T.tutTip.text, dim: document.getElementById('tutDim').className, hand: !document.querySelector('.thand') || getComputedStyle(document.querySelector('.thand')).display }))()"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 430, 'height': 790}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{}, drops: 40, runs: 1, owned: ['flower','fangs'], bought: ['flower','fangs'], tut: { ph: 'locker' } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); ev = pg.evaluate
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000, polling=100); await pg.wait_for_timeout(2500)
        print('lobby', await ev(STATE))
        await ev("document.getElementById('dabsBtn').click()"); await pg.wait_for_timeout(1500)
        print('shop 1.5s', await ev(STATE)); await pg.screenshot(path=f'{WS}/ui/browse_{TAG}_1.png')
        await pg.wait_for_timeout(4000); print('shop 5.5s', await ev(STATE)); await pg.screenshot(path=f'{WS}/ui/browse_{TAG}_2.png')
        await ev("document.getElementById('shopBack').click()"); await pg.wait_for_timeout(1500)
        print('after back', await ev(STATE)); await pg.screenshot(path=f'{WS}/ui/browse_{TAG}_3.png')
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
