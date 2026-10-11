"""The locker with things worn (a flower at the side, fangs, lashes) on the character, close: the hat must sit on the head's top.
usage: lockerhat.py [tag]"""
import asyncio, sys, functools
from playwright.async_api import async_playwright
print = functools.partial(print, flush=True)
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
TAG = sys.argv[1] if len(sys.argv) > 1 else 'a'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 800}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{}, drops: 40, runs: 3, owned: ['flower','fangs','bunny','tophat'], tut: { done: true } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); ev = pg.evaluate
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000, polling=100)
        await pg.wait_for_timeout(2500); await ev("__T.openLook()"); await pg.wait_for_timeout(9000)
        for i, look in enumerate([{'side': 'flower', 'mouth': 'fangs'}, {'head': 'bunny'}, {'head': 'tophat', 'lash': 'long'}]):
            await ev("(l) => { const L = __T.myLook; L.side = l.side || null; L.mouth = l.mouth || null; L.head = l.head || null; L.lash = l.lash || null; __T.renderLook(); }", look); await pg.wait_for_timeout(2500)
            await pg.screenshot(path=f'{WS}/ui/lockerhat_{TAG}_{i}.png'); print(i, look, await ev("Object.assign({}, __T.myLook)"))
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
