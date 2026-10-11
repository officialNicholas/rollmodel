"""v215 with a phone's notch insets (emulated): the match HUD, the events page and Settings, to check nothing else lost its place now that
the page no longer pads for the notch (the game's own bars do)."""
import asyncio
from playwright.async_api import async_playwright
OUT = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/lab'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 430, 'height': 790}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Glossy', seen:{steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,look:1,items:1}, runs: 9, xp: 300, drops: 120, tut: { ph: 'done' } })); } catch (e) {}")
        pg = await ctx.new_page(); cdp = await ctx.new_cdp_session(pg); await cdp.send('Emulation.setSafeAreaInsetsOverride', {'insets': {'top': 59, 'bottom': 34, 'left': 0, 'right': 0}})
        errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8765/pc_h.html', timeout=300000); await pg.wait_for_function('typeof __T === "object" && !!__T.VP && !!__T.VP.slime', timeout=300000, polling=1000); await pg.wait_for_timeout(2500)
        await pg.evaluate("document.getElementById('homePlay').click()"); await pg.wait_for_timeout(1500); await pg.screenshot(path=f'{OUT}/ss_events.png')
        await pg.evaluate("document.getElementById('evBack') && document.getElementById('evBack').click()"); await pg.wait_for_timeout(1000)
        await pg.evaluate("document.getElementById('hamBtn').click()"); await pg.wait_for_timeout(700); await pg.evaluate("document.getElementById('smSet').click()"); await pg.wait_for_timeout(1000); await pg.screenshot(path=f'{OUT}/ss_settings.png')
        await pg.keyboard.press('Escape'); await pg.wait_for_timeout(600)
        await pg.evaluate("__T.start()"); await pg.wait_for_function("__T.state === 'play'", timeout=240000, polling=500); await pg.wait_for_timeout(2500); await pg.screenshot(path=f'{OUT}/ss_match.png')
        print('errors', errs[:4]); await b.close()
asyncio.run(main())
