import asyncio, sys
from playwright.async_api import async_playwright
U = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/pc_w.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        for gfx in ['hi', 'perf']:
            ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, has_touch=True, is_mobile=True)
            await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ name: 'Nick', gfx: '" + gfx + "', seen: {look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1} })); } catch (e) {}")
            pg = await ctx.new_page(); msgs = []
            pg.on('console', lambda m: m.type in ('warning', 'error') and msgs.append(m.type + ': ' + m.text[:220]))
            pg.on('pageerror', lambda e: msgs.append('PAGEERROR: ' + str(e)[:300]))
            await pg.goto(U); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=60000); await pg.wait_for_timeout(1500)
            await pg.evaluate("(() => { const T = __T; for (const th of ['island', 'blank', 'garden', 'crypt', 'cathedral', 'manor']) { T.genWorld(77, { themes: [th] }); T.mapUsed = false; T.start(); for (let i = 0; i < 30; i++) { T.step(0.016); T.visuals(0.016, 0.016); } T.renderFrame(); T.state = 'menu'; T.showMenu(); } })()")
            await pg.wait_for_timeout(500)
            uniq = []
            for m in msgs:
                if m not in uniq: uniq.append(m)
            print(gfx, 'REV', await pg.evaluate("THREE.REVISION"), len(msgs)); [print('  ', m) for m in uniq[:20]]
            await ctx.close()
        await b.close()
asyncio.run(main())
