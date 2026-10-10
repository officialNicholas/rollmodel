"""The orientation chooser: no focus ring on touch, tidy spacing, portrait and landscape."""
import asyncio, sys
from playwright.async_api import async_playwright
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
async def run(p, W, H, tag):
    b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
    ctx = await b.new_context(viewport={'width': W, 'height': H}, device_scale_factor=2, has_touch=True, is_mobile=True)
    await ctx.add_init_script("window.__tut = true; try { localStorage.removeItem('paint-world-red.v1'); } catch (e) {}")
    pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
    await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000)
    await pg.wait_for_function("!document.getElementById('orient').hidden", timeout=120000); await pg.wait_for_timeout(1500)
    print(tag, await pg.evaluate("(() => { const b = document.getElementById('orientOk'), cs = getComputedStyle(b); const r = e => { const q = document.querySelector(e).getBoundingClientRect(); return [Math.round(q.top), Math.round(q.bottom)]; }; return [document.activeElement && document.activeElement.id, cs.outlineStyle, cs.outlineWidth, document.documentElement.className, r('.otitle'), r('.osub'), r('.ocards'), r('#orientOk')]; })()"))
    await pg.screenshot(path=S + '/ws/ui/orient_' + tag + '.png'); print('errors', errs); await b.close()
async def main():
    async with async_playwright() as p:
        await run(p, 390, 780, 'port'); await run(p, 844, 390, 'land')
asyncio.run(main())
