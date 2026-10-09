import asyncio
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        for w, h in [(630, 790), (820, 1100), (390, 780)]:
            ctx = await b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=1)
            await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name:'Dusk', seen:{steer:1} })); } catch (e) {}")
            pg = await ctx.new_page(); await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(1500)
            print(w, h, await pg.evaluate("(() => { const a = document.querySelector('.ocard[data-o=port] .oart'), i = a.querySelector('img'); const ca = getComputedStyle(a), ci = getComputedStyle(i); return ['oart ' + ca.height + ' disp=' + ca.display, 'img ' + i.getBoundingClientRect().width.toFixed(0) + 'x' + i.getBoundingClientRect().height.toFixed(0) + ' h=' + ci.height + ' ar=' + ci.aspectRatio + ' nat=' + i.naturalWidth + 'x' + i.naturalHeight + ' complete=' + i.complete]; })()"))
            await pg.screenshot(path=f'{WS}/ui/orient_{w}.png'); await ctx.close()
        await b.close()
asyncio.run(main())
