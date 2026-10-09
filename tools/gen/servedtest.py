# the page as published: served over http next to its files, the pack fetched (not inlined)
import asyncio, sys
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', mode: 'trio', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; reqs = []
        pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300])); pg.on('console', lambda m: errs.append(m.type + ' ' + m.text[:200]) if m.type in ('error', 'warning') and 'GPU stall' not in m.text and 'fonts.g' not in m.text else None)
        pg.on('requestfinished', lambda r: reqs.append(r.url.split('/')[-1]))
        await pg.goto('http://127.0.0.1:8765/paint-the-canvas.html', timeout=240000)
        await pg.wait_for_timeout(20000)
        print('requests', [r for r in reqs if r.endswith(('.pack', '.js', '.mp3'))])
        await pg.screenshot(path='/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/served.png', timeout=120000)
        # the boot screen may ask for a tap; tap it, then look at the menu
        try: await pg.mouse.click(195, 600)
        except Exception as e: print('tap', e)
        await pg.wait_for_timeout(8000)
        await pg.screenshot(path='/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/served2.png', timeout=120000)
        await pg.evaluate("() => { const b = document.getElementById('lookBtn'); if (b) b.click(); }")
        await pg.wait_for_timeout(12000)
        await pg.screenshot(path='/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/served3.png', timeout=120000)
        print('errors', errs[:8]); await b.close()
asyncio.run(main())
