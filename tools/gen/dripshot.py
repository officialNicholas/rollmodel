import asyncio, sys
from playwright.async_api import async_playwright
U='file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_t.html'
TIMES = [0.55, 0.7, 0.85, 1.0, 1.1, 1.2, 1.3, 1.45, 1.6, 1.8, 2.2]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader','--enable-webgl','--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', color: 'purple', seen: {look:1}, look: { eyes: 'happy', head: 'halo', back: 'wings', mouth: 'fangs' } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: m.type=='error' and 'ERR_' not in m.text and errs.append(m.text))
        await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=30000); await pg.wait_for_timeout(800)
        await pg.evaluate("(()=>{ for (let i=0;i<120;i++) __T.visuals(0.016, 0.016); __T.renderFrame(); })()")
        await pg.evaluate("window.__noLoop = true;")
        await pg.click('#lookBtn'); await pg.wait_for_timeout(50)
        t = 0.0
        for T in TIMES:
            n = round((T - t) / 0.016); t += n * 0.016
            await pg.evaluate(f"(()=>{{ for (let i=0;i<{n};i++) __T.visuals(0.016, 0.016); __T.flushTrail(); __T.renderFrame(); }})()")
            await pg.screenshot(path=f'ui/drip_{int(T*100):03d}.png')
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
