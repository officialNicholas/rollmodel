"""v250 gallery art: the canvas vote page stepped to Palette Island, the Blank Canvas and the Season 1 frame (the 'All three' art), then
the season's own grid. usage: galart250.py [page]"""
import asyncio, sys, functools
from playwright.async_api import async_playwright
print = functools.partial(print, flush=True)
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'; PAGE = sys.argv[1] if len(sys.argv) > 1 else 'pc_h.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__noVote = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{ jump: 1, hold: 1, steer: 1, item: 1, orb: 1 }, drops: 0, runs: 5, stage: 'island', mode: 'duel', tut: { ph: 'done', strokes: 1, comms: 1 } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200])); ev = pg.evaluate
        await pg.goto('http://localhost:8765/' + PAGE, timeout=900000); await pg.wait_for_function('typeof __T === "object"', timeout=900000, polling=100)
        await ev("(() => { const r = __T.renderer; r.render = () => {}; })(); 0"); await pg.wait_for_timeout(1500)
        await ev("__T.ev('openWorlds()')"); await pg.wait_for_timeout(1200)
        for sid in ['island', 'blank', 'season']:
            await ev(f"__T.ev(`(() => {{ const b = worldBtns.find(x => x.dataset.s === '{sid}'); centerWorld(b, false); }})()`)"); await pg.wait_for_timeout(900)
            await pg.screenshot(path=f'{WS}/ui/ga250_{sid}.png')
        await ev("__T.ev('openSeason()')"); await pg.wait_for_timeout(900); await pg.screenshot(path=f'{WS}/ui/ga250_grid.png')
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
