import asyncio, sys, json
from playwright.async_api import async_playwright
sys.path.insert(0, '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/tools')
from h254 import *
async def main():
    async with async_playwright() as p:
        b = await launch(p); ctx, pg, errs = await boot(b, sys.argv[1], dict(SAVE, mode=sys.argv[2]), dpr=int(sys.argv[3]))
        await pg.evaluate("__T.start()"); await pg.wait_for_function("__T.state === 'play'", timeout=120000, polling=100); await pg.wait_for_timeout(2500)
        r = await pg.evaluate("""(() => { const q = s => { const e = document.querySelector(s); if (!e) return null; const r = e.getBoundingClientRect(); return [s, Math.round(r.x), Math.round(r.y), Math.round(r.width), Math.round(r.height), getComputedStyle(e).display, getComputedStyle(e).visibility]; };
          const out = ['#stage', '#cv', '#hud', '#iris', '.iris', '#menu', '#end', '#vsx', '#reveal', '#slamBtn', '#bar'].map(q);
          const top = document.elementFromPoint(195, 150); out.push(['top@195,150', top && (top.id || top.className)]); const c = document.getElementById('cv'); out.push(['cv size', c.width, c.height, innerWidth, innerHeight, devicePixelRatio]); return out; })()""")
        for x in r: print(x)
        await pg.screenshot(path=f'{OUT}/rects_{sys.argv[2]}_{sys.argv[3]}.png'); print(errs[:3]); await b.close()
asyncio.run(main())
