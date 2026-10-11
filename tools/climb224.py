"""v224: the climb out of the basin at the start of a match, from the game's own camera: shots through the countdown."""
import asyncio, os, functools
from playwright.async_api import async_playwright
print = functools.partial(print, flush=True)
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': int(os.environ.get('VW', 360)), 'height': int(os.environ.get('VH', 640))}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__skipIntro = false; window.__noReveal = true; window.__introKind = 'climb'; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{}, drops: 0, runs: 3, tut: { ph: 'done' } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); ev = pg.evaluate
        async def wait(js, t=400000): await pg.wait_for_function(js, timeout=t, polling=30)
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await wait('typeof __T === "object"'); await pg.wait_for_timeout(800)
        await ev("__T.mode = 'duel'; __T.applyMode(); __T.beginMatch()")
        await wait("__T.P.introCrawl"); print('crawl:', await ev("(() => { const C = __T.P.introCrawl; return [C.s0, C.rw2, C.s1, C.T, C.rw, !!C.path].map(v => typeof v === 'number' ? +v.toFixed(2) : v); })()"))
        for i, k in enumerate([0.05, 0.25, 0.45, 0.6, 0.75, 0.9, 1.05, 1.2, 1.4, 1.65, 1.95, 2.3]):
            await wait(f"!__T.P.introCrawl || __T.P.introCrawl.t >= {k}")
            info = await ev("[__T.P.introCrawl ? +__T.P.introCrawl.t.toFixed(2) : 'out', __T.P.introCrawl ? +__T.P.introCrawl.s.toFixed(2) : null, +__T.introT.toFixed(2), __T.state]")
            await pg.screenshot(path=f'{WS}/ui/climb_{i:02d}.png'); print(i, info)
            if info[0] == 'out' and i > 6: break
        print('errors', errs[:4]); await b.close()
asyncio.run(main())
