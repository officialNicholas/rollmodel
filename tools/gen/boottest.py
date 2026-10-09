# the loading screen: shots while it loads, the bar's position each time, and that it hands over to the menu cleanly
import asyncio, time
from playwright.async_api import async_playwright
SP = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', seen: {look:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300])); pg.on('console', lambda m: m.type in ('error', 'warning') and errs.append(m.type + ': ' + m.text[:200]))
        t0 = time.time(); await pg.goto(SP + 'pc_t.html', wait_until='commit', timeout=240000)
        k = 0; last = None
        while time.time() - t0 < 200:
            try:
                r = await pg.evaluate("() => { const f = document.getElementById('bootFill'), b = document.getElementById('boot'); if (!f) return null; const tr = getComputedStyle(f).transform; const m = tr && tr !== 'none' ? new DOMMatrixReadOnly(tr).m41 / f.offsetWidth : -1; return { pos: +(1 + m).toFixed(2), msg: document.getElementById('bootMsg').textContent, gone: b.classList.contains('gone'), T: typeof __T === 'object', st: typeof __T === 'object' ? __T.state : null }; }")
            except Exception as e:
                r = str(e)[:80]
            if r != last: print(round(time.time() - t0, 1), r); last = r
            if k < 6 and isinstance(r, dict) and r and not r['gone']: await pg.screenshot(path=f'st/boot_{k}.png', timeout=180000); k += 1
            if isinstance(r, dict) and r and r['gone']: break
            await asyncio.sleep(0.25)
        await asyncio.sleep(1); await pg.screenshot(path='st/boot_menu.png', timeout=180000)
        print('errors', errs[:8]); await b.close()
asyncio.run(main())
