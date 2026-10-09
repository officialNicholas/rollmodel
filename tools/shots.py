import asyncio, sys, json, os
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
U = 'http://localhost:8765/pc_h.html'
OUT = sys.argv[1] if len(sys.argv) > 1 else WS + '/ui/cur'
LAND = '--land' in sys.argv; FIRST = '--first' in sys.argv
os.makedirs(OUT, exist_ok=True)
VP = {'width': 780, 'height': 360} if LAND else {'width': 390, 'height': 780}
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport=VP, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ seen: {steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1}, name:'Dusk'" + ('' if FIRST else ", orient:'" + ('land' if LAND else 'port') + "'") + " })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: m.type == 'error' and errs.append(m.text[:200]))
        await pg.goto(U, timeout=240000); await pg.wait_for_function('typeof __T === "object"', polling=100, timeout=240000)
        await pg.wait_for_timeout(2500)
        async def shot(n):
            await pg.screenshot(path=f'{OUT}/{n}.png'); print('shot', n)
        if FIRST:
            await shot('00_orient'); await pg.evaluate("document.querySelector('.ocard[data-o=" + ('land' if LAND else 'port') + "]').click()"); await pg.wait_for_timeout(400); await shot('00_orient_pick'); await pg.evaluate("document.getElementById('orientOk').click()"); await pg.wait_for_timeout(900)
        await shot('01_home')
        for sel, n, back in [('#setBtn', '02_settings', '#setDone'), ('#howBtn', '03_how', '#howClose'), ('#nameBtn', '04_name', None)]:
            if await pg.evaluate(f"!!document.querySelector('{sel}')"):
                await pg.evaluate(f"document.querySelector('{sel}').click()"); await pg.wait_for_timeout(600); await shot(n)
                if back: await pg.evaluate(f"document.querySelector('{back}').click()")
                else: await pg.evaluate("document.getElementById('nameOk').click()")
                await pg.wait_for_timeout(500)
        if await pg.evaluate("!!document.getElementById('lookBtn')"):
            await pg.evaluate("document.getElementById('lookBtn').click()"); await pg.wait_for_timeout(1500); await shot('05_look')
            await pg.evaluate("document.getElementById('lookDone').click()"); await pg.wait_for_timeout(800)
        if await pg.evaluate("!!document.getElementById('homePlay')"):
            await pg.evaluate("document.getElementById('stageBtn').click()"); await pg.wait_for_timeout(900); await shot('06_world')
            await pg.evaluate("document.getElementById('worldBack').click()"); await pg.wait_for_timeout(600)
            await pg.evaluate("document.getElementById('homePlay').click()"); await pg.wait_for_timeout(400)
            if await pg.evaluate("!document.getElementById('nameModal').hidden"):
                await pg.fill('#nameInput', 'Dusk'); await pg.tap('#nameOk')
        await pg.wait_for_function("__T.state === 'play'", timeout=20000); await pg.wait_for_timeout(2500)
        await shot('07_hud')
        await pg.evaluate("__T.P.paint = 0.34"); await pg.wait_for_timeout(450); await shot('07b_tank')
        await pg.evaluate("document.getElementById('pauseBtn').click()"); await pg.wait_for_timeout(600); await shot('08_pause'); await pg.evaluate("document.getElementById('resumeBtn').click()"); await pg.wait_for_timeout(300)
        await pg.evaluate("(() => { const P = __T.P; for (let i = 0; i < 16; i++) { const x = P.x + (i % 4 - 1.5) * 3.2, z = P.z + (i / 4 | 0) * 3.2 - 4.8; __T.addSplat(x, Math.max(0, __T.surfaceUnder(x, z, P.y + 3, true)), z, 0, 3, __T.clock, false, true, 0); } __T.flushTrail(); __T.matchLeft = 0.4; })()")
        await pg.wait_for_function("!!__T.vic", timeout=30000, polling=200); await pg.wait_for_timeout(1800); await shot('09_victory')
        await pg.tap('#victory'); await pg.wait_for_function("!document.getElementById('end').hidden", timeout=10000); await pg.wait_for_timeout(1500); await shot('10_end')
        print('errors', errs[:5]); await b.close()
asyncio.run(main())
