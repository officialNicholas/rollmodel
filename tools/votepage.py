"""The canvas vote page: open it (versus mode, a Halloween canvas voted for) and shoot it at a few phone sizes. usage: votepage.py [tag]"""
import asyncio, sys, functools
from playwright.async_api import async_playwright
print = functools.partial(print, flush=True)
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
TAG = sys.argv[1] if len(sys.argv) > 1 else 'a'
SIZES = [('tall', 460, 845, 'port'), ('small', 375, 667, 'port'), ('land', 844, 390, 'land')]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        for name, w, h, orient in SIZES:
            ctx = await b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=2, has_touch=True, is_mobile=True)
            await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'" + orient + "', name:'Dusk', seen:{}, drops: 17, runs: 3, mode: 'vs', stage: 'cathedral', tut: { done: true } })); } catch (e) {}")
            pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); ev = pg.evaluate
            await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000, polling=100)
            await pg.wait_for_timeout(2500); await ev("document.getElementById('stageBtn').click()"); await pg.wait_for_timeout(3000)
            info = await ev("""(() => { const q = s => { const e = document.querySelector(s); if (!e) return null; const r = e.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.top), Math.round(r.width), Math.round(r.height)]; };
              const sel = document.querySelector('.world[aria-pressed="true"] .frame'); const g = document.getElementById('stagePick').getBoundingClientRect(); const fr = sel && sel.getBoundingClientRect();
              return { title: q('#worldTitle'), gallery: q('#stagePick'), frame: fr && [Math.round(fr.left), Math.round(fr.top), Math.round(fr.width), Math.round(fr.height)], frameMidY: fr && Math.round(fr.top + fr.height / 2 - g.top - g.height / 2), dots: q('#gDots'), foot: q('.wfoot'), vote: (document.querySelector('.wfoot .snote:not([hidden])') || {}).textContent }; })()""")
            print(name, info)
            await pg.screenshot(path=f'{WS}/ui/vote_{TAG}_{name}.png'); print('errors', errs[:3]); await ctx.close()
        await b.close()
asyncio.run(main())
