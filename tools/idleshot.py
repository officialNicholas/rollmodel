import asyncio
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        for eyes in ['round', 'edgy', 'dot']:
            ctx = await b.new_context(viewport={'width': 390, 'height': 780}, device_scale_factor=2, has_touch=True, is_mobile=True)
            await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{steer:1,look:1}, owned:['hat'], bought:['hat'], look:{eyes:'" + eyes + "',iris:'violet'} })); } catch (e) {}")
            pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200])); logs = []; pg.on('console', lambda m: logs.append(m.text[:300]) if m.type == 'error' and 'CORS' not in m.text and 'ERR_FAILED' not in m.text else None)
            await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(1500)
            await pg.evaluate("document.getElementById('lookBtn').click()")
            if eyes == 'round':
                await pg.wait_for_timeout(1250); await pg.screenshot(path=f'{WS}/ui/land_0.png', clip={'x': 0, 'y': 0, 'width': 390, 'height': 360})
                await pg.wait_for_timeout(250); await pg.screenshot(path=f'{WS}/ui/land_1.png', clip={'x': 0, 'y': 0, 'width': 390, 'height': 360})
            await pg.wait_for_timeout(3200); await pg.screenshot(path=f'{WS}/ui/eyes_{eyes}.png', clip={'x': 40, 'y': 60, 'width': 310, 'height': 300})
            if eyes == 'round':
                for act, wait in [('hands', 1300), ('peek', 1300), ('wag', 700), ('listen', 1200), ('face', 900), ('bounce', 600)]:
                    await pg.evaluate("window.__idleForce = '" + act + "'; __T && 0")
                    await pg.wait_for_function("(() => { const t = document.getElementById('lookTitle'); return true; })()")
                    await pg.wait_for_timeout(4200 + wait); await pg.screenshot(path=f'{WS}/ui/idle_{act}.png', clip={'x': 40, 'y': 40, 'width': 310, 'height': 330})
                await pg.evaluate("window.__idleForce = null")
                await pg.evaluate("document.getElementById('lookDone').click()"); await pg.wait_for_timeout(500)
                await pg.evaluate("document.getElementById('stageBtn').click()"); await pg.wait_for_timeout(800); await pg.screenshot(path=f'{WS}/ui/gal_title.png', clip={'x': 0, 'y': 0, 'width': 390, 'height': 140})
            print(eyes, 'errors', errs[:3], logs[:2]); await ctx.close()
        await b.close()
asyncio.run(main())
