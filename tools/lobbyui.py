"""The lobby after How to play moved into Settings, with the Commissions refresh timer: the lobby, the Commissions card, Settings, the guide
opened from Settings and closed back to it; portrait and landscape. Also checks the countdown's text in the last hour (a mocked clock)."""
import asyncio, json, sys
from playwright.async_api import async_playwright
OUT = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axoshots'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        for w, h, t in [(390, 844, 'p'), (844, 390, 'l')]:
            ctx = await b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=2, has_touch=True, is_mobile=True)
            await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'" + ('land' if w > h else 'port') + "', name:'Dusk', seen:{look:1}, runs: 9, tut: { ph: 'done' } })); } catch (e) {}")
            pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); pg.on('console', lambda m: errs.append(m.text[:200]) if m.type == 'error' and 'Failed to load' not in m.text and 'ERR_FAILED' not in m.text else None)
            await pg.goto('http://localhost:8765/pc_h.html', timeout=300000); await pg.wait_for_function('typeof __T === "object" && !!__T.VP && !!__T.VP.slime', timeout=300000, polling=1000); await pg.wait_for_timeout(2500)
            await pg.screenshot(path=f'{OUT}/lu_{t}_lobby.png')
            print(t, 'timer', await pg.evaluate("[document.getElementById('commTimer').textContent, document.getElementById('commArc').getAttribute('stroke-dasharray'), document.getElementById('commBtn').getAttribute('aria-label'), !!document.getElementById('howBtn')]"))
            await pg.evaluate("document.getElementById('commBtn').click()"); await pg.wait_for_timeout(900); await pg.screenshot(path=f'{OUT}/lu_{t}_comm.png')
            await pg.evaluate("document.getElementById('commClose').click()"); await pg.wait_for_timeout(500)
            await pg.evaluate("document.getElementById('setBtn').click()"); await pg.wait_for_timeout(900); await pg.screenshot(path=f'{OUT}/lu_{t}_set.png')
            await pg.evaluate("document.getElementById('howOpen').click()"); await pg.wait_for_timeout(900); await pg.screenshot(path=f'{OUT}/lu_{t}_how.png')
            print(t, 'how open', await pg.evaluate("[document.getElementById('howModal').hidden, document.getElementById('setModal').hidden]"))
            await pg.evaluate("document.getElementById('howClose').click()"); await pg.wait_for_timeout(600)
            print(t, 'how closed', await pg.evaluate("[document.getElementById('howModal').hidden, document.getElementById('setModal').hidden, document.activeElement && document.activeElement.id]"))
            await pg.keyboard.press('Escape'); await pg.wait_for_timeout(400)
            print(t, 'after escape', await pg.evaluate("[document.getElementById('setModal').hidden]"))
            if t == 'p':
                # the last hour: minutes and seconds (the clock moved to 23:55:04 local)
                await pg.evaluate("(() => { const R = Date; const n = new R(); const fake = new R(n.getFullYear(), n.getMonth(), n.getDate(), 23, 55, 4).getTime(), off = fake - R.now(); window.Date = class extends R { constructor(...a) { if (a.length) super(...a); else super(R.now() + off); } static now() { return R.now() + off; } }; })()")
                await pg.wait_for_timeout(2200); await pg.screenshot(path=f'{OUT}/lu_{t}_lasthour.png', clip={'x': 0, 'y': 120, 'width': 200, 'height': 330})
                print(t, 'last hour', await pg.evaluate("document.getElementById('commTimer').textContent"))
            print(t, 'errors', errs[:5]); await ctx.close()
        await b.close()
asyncio.run(main())
