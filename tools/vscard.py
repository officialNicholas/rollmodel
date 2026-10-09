import asyncio, sys
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
LAND = '--land' in sys.argv; MODE = 'trio' if '--trio' in sys.argv else 'duel'; TAG = sys.argv[1]
VP = {'width': 780, 'height': 360} if LAND else {'width': 390, 'height': 780}
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport=VP, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__instant = false; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'" + ('land' if LAND else 'port') + "', name:'Dusk', mode:'" + MODE + "', seen:{steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,look:1}, owned:['witch','lashes','pirate','tophat','tiara','hat','halo','fangs','patch','glasses','flower','bowtie'], look:{head:'hat',lash:'lashes',iris:'violet'} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(3500)
        await pg.screenshot(path=f'{WS}/ui/{TAG}_lobby.png')
        await pg.evaluate("document.getElementById('homePlay').click()"); await pg.wait_for_timeout(500); await pg.screenshot(path=f'{WS}/ui/{TAG}_vs0.png'); await pg.wait_for_timeout(800); await pg.screenshot(path=f'{WS}/ui/{TAG}_vs.png'); print(await pg.evaluate("[__T.state, document.getElementById('vsx').hidden, document.getElementById('nameModal') && document.getElementById('nameModal').hidden, document.getElementById('vsRow').children.length]"))
        await pg.wait_for_function("__T.state === 'play'", timeout=30000); await pg.wait_for_timeout(2500); await pg.screenshot(path=f'{WS}/ui/{TAG}_play.png')
        print(TAG, 'errors', errs[:4]); await b.close()
asyncio.run(main())
