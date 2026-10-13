import asyncio, sys
from playwright.async_api import async_playwright
PAGE, TAG, GFX, NEW = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4] == '1'
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__tut = true; window.__noVote = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', gfx:'%s', stage:'island', seen:{look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1}, drops: 50, runs: 9, flings: 50, tut: { ph: 'done' } })); } catch (e) {}" % GFX)
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8765/' + PAGE, timeout=300000); await pg.wait_for_function('typeof __T === "object"', timeout=300000)
        await pg.evaluate("__T.ev('genWorld(4242, { themes: stageThemes() }); mapUsed = false; warmRender();')")
        await pg.evaluate("__T.start()"); await pg.wait_for_function("__T.state === 'play'", timeout=300000)
        await pg.evaluate("setInterval(() => __T.ev(\"P.paint = 0.9; P.dry = false; P.dryT = 0; setWx('clear', 1000);\"), 50)")
        await pg.wait_for_timeout(1200)
        await pg.evaluate("__T.ev('hitEdge(H)')")
        if NEW: await pg.evaluate("setInterval(() => __T.ev('EDGE.hitT0 = performance.now() / 1000 - 0.3'), 20)")
        else:
            await pg.wait_for_timeout(200)
            await pg.evaluate("(() => { for (const a of document.getAnimations()) if (a.animationName === 'hitsplat') { a.pause(); a.currentTime = 300; } })()")
        await pg.wait_for_timeout(1500); await pg.screenshot(path=f'{WS}/ui/hit_{TAG}.png')
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
