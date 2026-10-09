import asyncio
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        for w, h, tag in [(390, 780, 'port'), (844, 390, 'land')]:
            ctx = await b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=2, has_touch=True, is_mobile=True)
            await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'" + ('land' if w > h else 'port') + "', name:'Dusk', mode:'duel', stage:'cathedral', seen:{jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,look:1} })); } catch (e) {}")
            pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
            await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(1000)
            await pg.evaluate("document.getElementById('homePlay').click()"); await pg.wait_for_function("__T.state === 'play'", timeout=30000); await pg.wait_for_timeout(1200)
            await pg.evaluate("__T.banner('Paint it orange!', 'The Cathedral', true); __T.hint('steer', 'Drag to steer', 6)"); await pg.wait_for_timeout(900)
            print(tag, await pg.evaluate("(() => { const q = s => { const r = document.querySelector(s).getBoundingClientRect(); return [r.top|0, r.bottom|0]; }; return { strip: q('.score'), banner: q('.banner .plate'), hint: q('.hint span'), hintOn: document.querySelector('.hint').className }; })()"), errs[:2])
            await pg.screenshot(path=f'{WS}/ui/tip_{tag}.png'); await ctx.close()
        await b.close()
asyncio.run(main())
