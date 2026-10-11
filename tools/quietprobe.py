"""v201: no lobby character lines during the onboarding, and they come back once it is done"""
import asyncio
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
async def run(ph):
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 780}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', runs: " + ('0' if ph == 'match' else '3') + ", tut: { ph: '" + ph + "' }, seen: {} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000)
        await pg.evaluate("(() => { const r = __T.renderer; window.__o = r.render.bind(r); r.render = () => {}; })(); window.__said = []; new MutationObserver(() => { const t = document.getElementById('heroSayTxt').textContent; if (t && !document.getElementById('heroSay').hidden) __said.push(t); }).observe(document.getElementById('heroSay'), { attributes: true, childList: true, subtree: true }); 0")
        await pg.wait_for_timeout(16000)
        print(ph, 'lines said in 16 s:', await pg.evaluate("JSON.stringify([...new Set(__said)])"), 'bubble showing:', await pg.evaluate("!document.getElementById('heroSay').hidden"), 'phase:', await pg.evaluate("__T.tutPh()"), 'errors', errs)
        await b.close()
async def main():
    await run('match'); await run('done')
asyncio.run(main())
