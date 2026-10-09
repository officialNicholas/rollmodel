import asyncio
from playwright.async_api import async_playwright
SP = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("const __raf = window.requestAnimationFrame.bind(window); let __first = true; window.requestAnimationFrame = f => { if (__first) { __first = false; return setTimeout(() => {}, 1e9); } return __raf(f); };")
        pg = await ctx.new_page(); await pg.goto(SP + 'pc_t.html', timeout=240000); await asyncio.sleep(2.5)
        await pg.screenshot(path='st/boot_creep.png', timeout=60000)
        await pg.evaluate("() => { document.getElementById('bootMsg').textContent = 'Mixing the paint'; const f = document.getElementById('bootFill'); f.style.animation = 'none'; f.style.transform = 'translateX(-30%)'; }"); await asyncio.sleep(0.3)
        await pg.screenshot(path='st/boot_mid.png', timeout=60000); await b.close()
asyncio.run(main())
