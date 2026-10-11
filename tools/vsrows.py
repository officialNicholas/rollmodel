"""v193: the fight card on an upright screen: fighters in full-width rows, shot on the face (duel and 3-way), landscape unchanged."""
import asyncio
from playwright.async_api import async_playwright
S = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad'
async def run(p, W, H, mode, tag):
    b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
    ctx = await b.new_context(viewport={'width': W, 'height': H}, device_scale_factor=2, has_touch=True, is_mobile=True)
    await ctx.add_init_script("window.__instant = false; window.__skipIntro = false; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'" + ('land' if W > H else 'port') + "', name:'Pixel', mode: '" + mode + "', seen:{look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1}, drops: 50, runs: 3, tut: { ph: 'done' } })); } catch (e) {}")
    pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
    await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(2500)
    await pg.evaluate("document.getElementById('homePlay').click()"); await pg.wait_for_function("!document.getElementById('vsx').hidden", timeout=60000)
    await pg.wait_for_function("[...document.querySelectorAll('#vsRow .vbox')].every(b => b.querySelector('canvas'))", timeout=60000); await pg.wait_for_timeout(900)
    print(tag, await pg.evaluate("[document.getElementById('vsRow').className, [...document.querySelectorAll('#vsRow .vcol')].map(c => { const r = c.getBoundingClientRect(); return [Math.round(r.left), Math.round(r.top), Math.round(r.width), Math.round(r.height)]; })]"))
    await pg.screenshot(path=S + '/ws/ui/vsrows_' + tag + '.png'); print('errors', errs); await b.close()
async def main():
    async with async_playwright() as p:
        await run(p, 390, 780, 'duel', 'duel'); await run(p, 390, 780, 'trio', 'trio'); await run(p, 844, 390, 'duel', 'land')
asyncio.run(main())
