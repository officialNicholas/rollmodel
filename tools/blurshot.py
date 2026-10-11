"""v203: Ol' Bloop's tips dim with a blur in the lobby, and without one in the shop and the locker"""
import asyncio
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
DIM = "(() => { const d = document.getElementById('tutDim'), cs = getComputedStyle(d); return [__T.tutTip && __T.tutTip.key, d.className, cs.backdropFilter || cs.webkitBackdropFilter, cs.backgroundColor]; })()"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        for w, h, tag in [(430, 932, 'port'), (844, 390, 'land')]:
            for ph in ['shop', 'locker']:
                ctx = await b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=2, has_touch=True, is_mobile=True)
                own = "[]" if ph == 'shop' else "['fangs','flower']"
                await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'" + ('land' if w > h else 'port') + "', name:'Dusk', runs: 1, drops: 60, owned: " + own + ", tut: { ph: '" + ph + "' }, seen: { look: 1 } })); } catch (e) {}")
                pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
                await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000)
                lob = 'shop' if ph == 'shop' else 'locker'
                await pg.wait_for_function(f"__T.tutTip && __T.tutTip.key === '{lob}'", timeout=240000); await pg.wait_for_timeout(1500)
                print(tag, 'lobby', await pg.evaluate(DIM)); await pg.screenshot(path=f'{WS}/ui/blur_{tag}_lobby_{ph}.png')
                await pg.evaluate("document.getElementById('" + ('dabsBtn' if ph == 'shop' else 'lookBtn') + "').click()")
                want = 'buyflower' if ph == 'shop' else 'face'
                await pg.wait_for_function(f"__T.tutTip && __T.tutTip.key === '{want}'", timeout=60000); await pg.wait_for_timeout(1800)
                print(tag, ph, await pg.evaluate(DIM), errs); await pg.screenshot(path=f'{WS}/ui/blur_{tag}_{ph}.png'); await ctx.close()
        await b.close()
asyncio.run(main())
