"""The versus card's canvas reel: start a 1v1, let the vote reel spin and land, then shoot it and check the winning picture sits wholly
inside the reel. usage: votereel.py [tag]"""
import asyncio, sys, functools
from playwright.async_api import async_playwright
print = functools.partial(print, flush=True)
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
TAG = sys.argv[1] if len(sys.argv) > 1 else 'a'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        for name, w, h in [('port', 420, 860), ('land', 844, 390)]:
            ctx = await b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=2, has_touch=True, is_mobile=True)
            await ctx.add_init_script("window.__instant = false; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'" + ('land' if w > h else 'port') + "', name:'Dusk', seen:{}, drops: 0, runs: 3, mode: 'duel', tut: { ph: 'done' } })); } catch (e) {}")
            pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); ev = pg.evaluate
            await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000, polling=100); await pg.wait_for_timeout(1500)
            await ev("(() => { const st = window.setTimeout; window.setTimeout = (f, d, ...x) => d === 1900 ? 0 : st(f, d, ...x); })()")  # (the landed reel stays up)
            await ev("__T.mode = 'duel'; __T.applyMode(); __T.start()")
            await pg.wait_for_function("!!document.querySelector('#vreel .vcard.win')", timeout=400000, polling=100); await pg.wait_for_timeout(900)
            info = await ev("""(() => { const r = document.getElementById('vreel').getBoundingClientRect(), c = document.querySelector('#vreel .vcard.win').getBoundingClientRect(), v = document.getElementById('vvote').getBoundingClientRect();
              return { reel: [Math.round(r.top), Math.round(r.bottom), Math.round(r.height)], win: [Math.round(c.top), Math.round(c.bottom), Math.round(c.width), Math.round(c.height)], room: [Math.round(c.top - r.top), Math.round(r.bottom - c.bottom)], panel: [Math.round(v.top), Math.round(v.bottom)], vh: innerHeight }; })()""")
            print(name, info)
            await pg.screenshot(path=f'{WS}/ui/reel_{TAG}_{name}.png'); print('errors', errs[:3]); await ctx.close()
        await b.close()
asyncio.run(main())
