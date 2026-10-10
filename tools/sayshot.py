import asyncio
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 393, 'height': 852}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{steer:1,look:1}, owned:[], bought:[], drops:300, look:{head:null, eyes:'edgy', iris:'violet'} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(2500)
        await pg.evaluate("__T.heroSpeak('The critics are watching.')"); await pg.wait_for_timeout(900)
        r = await pg.evaluate("(() => { const e = document.getElementById('heroSay'), q = e.getBoundingClientRect(); return [e.className, e.style.getPropertyValue('--tx'), Math.round(q.left), Math.round(q.top), Math.round(q.width), Math.round(q.height)]; })()"); print('say', r, errs[:2])
        x, y, w, h = r[2], r[3], r[4], r[5]
        await pg.screenshot(path=f'{WS}/ui/say_bubble.png', clip={'x': max(0, x - 40), 'y': max(0, y - 30), 'width': min(393, w + 80), 'height': h + 120})
        await b.close()
asyncio.run(main())
