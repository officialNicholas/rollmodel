# pretend to be the iPhone shell: an older phone gets Performance, Low Power Mode and heat ease things off, keepAwake messages arrive
import asyncio
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
async def run(b, native, label):
    ctx = await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=3, has_touch=True, is_mobile=True)
    await ctx.add_init_script("window.__msgs = []; window.webkit = { messageHandlers: { device: { postMessage: m => window.__msgs.push(m) }, haptic: { postMessage: () => {} } } }; window.__NATIVE = " + native + "; localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} }));")
    pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)))
    await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=60000); await pg.wait_for_timeout(800)
    r = await pg.evaluate("[__T.GFX, __T.renderer.getPixelRatio(), __T.post ? [__T.post.bloom, __T.post.dof] : null]")
    await pg.evaluate("(() => { __T.freshMap(); __T.mapUsed = false; __T.start(); })()"); await pg.wait_for_timeout(600)
    await pg.evaluate("(() => { window.__NATIVE.thermal = 2; window.dispatchEvent(new CustomEvent('nativechange')); })()"); await pg.wait_for_timeout(300)
    r2 = await pg.evaluate("[__T.renderer.getPixelRatio(), __T.post ? [__T.post.bloom, __T.post.dof] : null, JSON.stringify(window.__msgs)]")
    print(label, 'start:', r, 'hot:', r2, errs[:2]); await ctx.close()
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        await run(b, "{ platform: 'ios', model: 'iPhone16,1', tier: 3, lowPower: false, thermal: 0 }", 'iPhone 15 Pro')
        await run(b, "{ platform: 'ios', model: 'iPhone14,5', tier: 2, lowPower: true, thermal: 0 }", 'iPhone 13 low power')
        await run(b, "{ platform: 'ios', model: 'iPhone12,1', tier: 1, lowPower: false, thermal: 0 }", 'iPhone 11')
        await b.close()
asyncio.run(main())
