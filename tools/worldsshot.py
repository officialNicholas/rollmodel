"""The canvases gallery: opened from the home screen, stepped to each new painting (the Sludge Sewer, the Fishing Raft), shot each time.
usage: worldsshot.py page tag"""
import asyncio, sys, functools
from playwright.async_api import async_playwright
print = functools.partial(print, flush=True)
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
PAGE, TAG = sys.argv[1], sys.argv[2]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__noVote = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{ jump: 1, hold: 1, steer: 1, item: 1, orb: 1 }, drops: 0, runs: 5, mode: 'duel', tut: { ph: 'done', strokes: 1, comms: 1 } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200])); ev = pg.evaluate
        await pg.goto('http://localhost:8765/' + PAGE, timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000, polling=100); await pg.wait_for_timeout(2500)
        await ev("__T.ev(`openWorlds()`)"); await pg.wait_for_timeout(1500)
        names = await ev("[...document.querySelectorAll('.world')].map(w => w.dataset.s)"); print('tiles', names)
        for sid in ['sewer', 'raft']:
            await ev(f"__T.ev(`(() => {{ const open = worldBtns.filter(b => b.dataset.s !== 'next'), ti = open.findIndex(b => b.dataset.s === '{sid}'); for (let k = 0; k < 12 && stageSel !== '{sid}'; k++) stepWorld(ti > open.findIndex(b => b.dataset.s === stageSel) ? 1 : -1); return stageSel; }})()`)")
            await pg.wait_for_timeout(1400); await pg.screenshot(path=f'{WS}/ui/gw_{TAG}_{sid}.png')
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
