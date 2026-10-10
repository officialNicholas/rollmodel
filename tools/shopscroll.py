import asyncio, sys
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
async def run(W, H, tag):
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': W, 'height': H}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{steer:1,look:1}, owned:[], bought:[], drops:0, look:{head:null, eyes:'edgy', iris:'violet'} })); } catch (e) {}")
        pg = await ctx.new_page()
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(1500)
        await pg.evaluate("for (const e of document.querySelectorAll('.shw')) {} document.getElementById('dabsBtn').click()"); await pg.wait_for_timeout(1500)
        # a bigger font, as a phone that renders text larger would show it
        await pg.evaluate("for (const e of document.querySelectorAll('.shw')) e.style.fontSize = '14px'; for (const e of document.querySelectorAll('.shn')) e.style.fontSize = '17px';"); await pg.wait_for_timeout(300)
        print(tag, await pg.evaluate("(() => { const g = document.getElementById('shopGrid'), sh = document.getElementById('shop'); return { gridScrollW: g.scrollWidth, gridClientW: g.clientWidth, shopScrollW: sh.scrollWidth, shopClientW: sh.clientWidth, docW: document.documentElement.scrollWidth, vw: innerWidth, card: Math.round(document.querySelector('.shitem').getBoundingClientRect().width) }; })()"))
        await pg.screenshot(path=f'{WS}/ui/shop_scroll_{tag}.png'); await b.close()
for W, H, tag in [(393, 852, 'phone'), (320, 568, 'narrow')]: asyncio.run(run(W, H, tag))
