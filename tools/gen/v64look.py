import asyncio, json
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: 'hi', mode: 'duel', color: 'pink', stage: 'blank', owned: ['pirate','patch','flower','tophat','bowtie','tiara','lashes','hat','halo','fangs'], look: { head: 'tiara', lash: 'lashes', neck: 'bowtie' }, seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,rocket:1,dry:1} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append('PAGE ' + str(e)[:300])); pg.on('console', lambda m: m.type == 'error' and 'ERR_' not in m.text and errs.append(m.text[:300]))
        await pg.goto('file://' + SP + 'pc_t.html', timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000); await pg.wait_for_timeout(1800)
        await pg.evaluate("() => { const T = __T; window.__noLoop = true; T.openLook(); for (let i = 0; i < 200; i++) T.visuals(1 / 60, 1 / 60); T.clock = 10.176; for (let i = 0; i < 4; i++) T.visuals(0.0005, 0.0005); T.renderFrame(); }")
        await pg.screenshot(path=SP + 'st/v64_look.png'); print('errors', errs[:4]); await b.close()
asyncio.run(main())
