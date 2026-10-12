"""A close look at the face in the locker (the eye show close-up) and in the lobby, for the decal contrast. usage: faceshot.py page tag"""
import asyncio, sys, functools
from playwright.async_api import async_playwright
print = functools.partial(print, flush=True)
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
PAGE = sys.argv[1]; TAG = sys.argv[2]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__noVote = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{}, drops: 0, runs: 5, tut: { ph: 'done', strokes: 1, comms: 1 } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); ev = pg.evaluate
        await pg.goto('http://localhost:8765/' + PAGE, timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000, polling=100); await pg.wait_for_timeout(9000)
        await pg.screenshot(path=f'{WS}/ui/face_{TAG}_lobby.png', clip={'x': 60, 'y': 300, 'width': 270, 'height': 300})
        await ev("__T.openLook()"); await pg.wait_for_timeout(12000)
        await pg.screenshot(path=f'{WS}/ui/face_{TAG}_locker.png', clip={'x': 45, 'y': 150, 'width': 300, 'height': 330})
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
