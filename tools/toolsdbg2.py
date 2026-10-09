import asyncio
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        for w, h, tag, inset in [(390, 780, 'port', 0), (390, 780, 'notch', 59), (844, 390, 'land', 0)]:
            ctx = await b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=2, has_touch=True, is_mobile=True)
            await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'" + ('land' if w > h else 'port') + "', name:'Dusk', seen:{steer:1,look:1}, xp: 140 })); } catch (e) {}")
            pg = await ctx.new_page(); await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000)
            if inset: await pg.add_style_tag(content=".corner{top:%dpx !important}.mhome.lobby{padding-top:%dpx !important}.mhome.lobby .ltools{margin-top:0 !important}" % (inset, inset))
            await pg.wait_for_timeout(2500)
            print(tag, await pg.evaluate("[['gear', document.getElementById('setBtn').getBoundingClientRect().top], ['sound', document.getElementById('soundBtn').getBoundingClientRect().top], ['name', document.getElementById('nameBtn').getBoundingClientRect().top]]"))
            if tag == 'port': await pg.screenshot(path=f'{WS}/ui/gear_port.png', clip={'x': 250, 'y': 0, 'width': 140, 'height': 70})
            await ctx.close()
        await b.close()
asyncio.run(main())
