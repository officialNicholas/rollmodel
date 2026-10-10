import asyncio, sys
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 1180, 'height': 700}, device_scale_factor=1)
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200])); pg.on('console', lambda m: errs.append('C:' + m.text[:160]) if m.type == 'error' else None)
        await pg.goto('http://localhost:8765/pc_h.html', wait_until='commit', timeout=240000)
        for i in range(8):
            try:
                await pg.wait_for_timeout(1500)
                st = await pg.evaluate("(() => { const b = document.getElementById('boot'); if (!b) return 'noboot'; const c = document.getElementById('bootC'); const f = document.getElementById('bootFill'); return [b.className, document.getElementById('bootMsg') && document.getElementById('bootMsg').textContent, window.__bootP, c && c.width, f && getComputedStyle(f).display, getComputedStyle(document.querySelector('.bootbar')).width]; })()")
                await pg.screenshot(path=f'{WS}/ui/bootreal_{i}.png', timeout=5000); print(i, st, errs[-2:])
            except Exception as e: print(i, 'x', str(e)[:80])
        await b.close()
asyncio.run(main())
