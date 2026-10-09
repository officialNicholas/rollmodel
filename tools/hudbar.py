import asyncio
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
SPLAT = "(n, team, dx) => { const P = __T.P; for (let i = 0; i < n; i++) { const x = P.x + dx + (i % 4 - 1.5) * 2.6, z = P.z + (i / 4 | 0) * 2.6 - 3.9; __T.addSplat(x, Math.max(0, __T.surfaceUnder(x, z, P.y + 3, true)), z, 0, 2.6, __T.clock, false, true, team); } __T.flushTrail && __T.flushTrail(); }"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        for w, h, tag, mode in [(844, 390, 'land', 'duel'), (390, 780, 'port', 'trio')]:
            ctx = await b.new_context(viewport={'width': w, 'height': h}, device_scale_factor=2, has_touch=True, is_mobile=True)
            await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'" + ('land' if w > h else 'port') + "', name:'Dusk', mode:'" + mode + "', seen:{steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,look:1} })); } catch (e) {}")
            pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200]))
            await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(1500)
            await pg.evaluate("document.getElementById('homePlay').click()"); await pg.wait_for_function("__T.state === 'play'", timeout=30000); await pg.wait_for_timeout(1500)
            clip = {'x': 0, 'y': 0, 'width': w, 'height': 110 if w > h else 150}
            await pg.evaluate("(" + SPLAT + ")(8, 0, 0)"); await pg.wait_for_timeout(1200); await pg.screenshot(path=f'{WS}/ui/bar_{tag}_1.png', clip=clip)
            print(tag, 'you only', await pg.evaluate("[__T.teamCov(0).toFixed(1), __T.teamCov(1).toFixed(1), document.getElementById('tugYou').style.width]"))
            await pg.evaluate("(" + SPLAT + ")(4, 1, 7)"); await pg.wait_for_timeout(350); await pg.screenshot(path=f'{WS}/ui/bar_{tag}_2.png', clip=clip)
            await pg.wait_for_timeout(1500); await pg.screenshot(path=f'{WS}/ui/bar_{tag}_3.png', clip=clip)
            if mode == 'trio': await pg.evaluate("(" + SPLAT + ")(3, 2, -7)"); await pg.wait_for_timeout(1500); await pg.screenshot(path=f'{WS}/ui/bar_{tag}_4.png', clip=clip)
            print(tag, 'both', await pg.evaluate("[__T.teamCov(0).toFixed(1), __T.teamCov(1).toFixed(1), __T.teamCov(2).toFixed(1), document.getElementById('tugYou').style.width, document.getElementById('tugCpu').style.width]"), errs[:2])
            await ctx.close()
        await b.close()
asyncio.run(main())
