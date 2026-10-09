import asyncio
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        for w, h, tag in [(844, 390, 'iph'), (630, 790, 'wide')]:
            ctx = await b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=2, has_touch=True, is_mobile=True)
            await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'" + ('land' if w > h else 'port') + "', name:'Dusk', mode:'duel', seen:{steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,look:1}, owned:['hat'], look:{head:'hat'} })); } catch (e) {}")
            pg = await ctx.new_page(); await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(1500)
            if tag == 'wide':
                await pg.evaluate("window.__instant = false; document.getElementById('homePlay').click()"); await pg.wait_for_timeout(900); await pg.screenshot(path=f'{WS}/ui/hud_{tag}_vs.png'); await ctx.close(); continue
            await pg.evaluate("document.getElementById('homePlay').click()"); await pg.wait_for_function("__T.state === 'play'", timeout=30000); await pg.wait_for_timeout(2000)
            await pg.evaluate("__T.wxPhase = 'warn'; __T.wxLeft = 2"); await pg.wait_for_timeout(500)
            print(tag, await pg.evaluate("(() => { const s = document.querySelector('.score'); const r = s.getBoundingClientRect(), c = getComputedStyle(s); const pr = s.parentElement, pc = getComputedStyle(pr); return [Math.round(r.width) + 'x' + Math.round(r.height), 'h=' + c.height + ' maxh=' + c.maxHeight + ' disp=' + c.display + ' rows=' + c.gridTemplateRows + ' ov=' + c.overflow, 'parent ' + pr.className + ' ' + pc.display + ' ' + pc.height + ' rows=' + pc.gridTemplateRows + ' align=' + pc.alignItems, [...s.children].map(e => e.className + ':' + Math.round(e.getBoundingClientRect().height)).join(' ')]; })()"))
            await pg.screenshot(path=f'{WS}/ui/hud_{tag}.png'); await ctx.close()
        await b.close()
asyncio.run(main())
