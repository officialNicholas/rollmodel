"""v182: the canvas page has no mode tabs or difficulty row during onboarding, and has them once it's done."""
import asyncio
from playwright.async_api import async_playwright
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
async def run(p, ph, W, H, tag):
    b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
    ctx = await b.new_context(viewport={'width': W, 'height': H})
    await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'" + ('land' if W > H else 'port') + "', name:'Dusk', seen:{}, drops: 0, tut: { ph: '" + ph + "' } })); } catch (e) {}")
    pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
    await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(2500)
    await pg.evaluate("document.getElementById('stageBtn').click()"); await pg.wait_for_timeout(2500)
    vis = "id => { const e = document.getElementById(id); return !!e && e.getClientRects().length > 0 && getComputedStyle(e).display !== 'none'; }"
    print(ph, tag, await pg.evaluate("[__T.tutPh(), !document.getElementById('mWorld').hidden, (" + vis + ")('modes'), (" + vis + ")('stages'), (" + vis + ")('startBtn')]"))
    await pg.screenshot(path=S + '/ws/ui/modes_' + ph + '_' + tag + '.png'); print('errors', errs); await b.close()
async def main():
    async with async_playwright() as p:
        await run(p, 'vote', 390, 780, 'port'); await run(p, 'vote', 844, 390, 'land'); await run(p, 'done', 390, 780, 'port')
asyncio.run(main())
