import asyncio
from playwright.async_api import async_playwright
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 780}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__instant = false; window.__skipIntro = false; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', mode:'duel', seen:{steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,look:1}, owned:['hat','lashes'], look:{head:'hat',lash:'lashes',iris:'violet'} })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(3000)
        await pg.evaluate("document.getElementById('homePlay').click()")
        await pg.wait_for_function("__T.state === 'play' && __T.clock > 2.5", timeout=120000, polling=500)
        await pg.screenshot(path=f'{WS}/ui/vs_after_intro.png'); print('after', await pg.evaluate("(() => { const g = id => document.getElementById(id); return [__T.state, __T.clock, g('iris').hidden, g('irisHole') && g('irisHole').style.cssText, getComputedStyle(g('iris')).opacity, g('iris').className, g('vsx').hidden, g('menu').hidden]; })()"), 'errors', errs[:3])
        await b.close()
asyncio.run(main())
