"""The app's Game folder, served the way the app serves it (its own files only, no internet): boots, its own fonts load, the version line,
a 1v1 starts and a rival's name tag shows; every error and every request that tried to leave collected."""
import asyncio, functools
from playwright.async_api import async_playwright
print = functools.partial(print, flush=True)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, has_touch=True, is_mobile=True)
        out = []
        async def route(r):
            if r.request.url.startswith('http://localhost:8766/'): await r.continue_()
            else: out.append(r.request.url[:100]); await r.abort()
        await ctx.route('**/*', route)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{ jump: 1, hold: 1, steer: 1, item: 1, orb: 1, roll: 1, pound: 1, missile: 1, burst: 1 }, drops: 0, runs: 5, xp: 400, mode: 'duel', tut: { ph: 'done', strokes: 1, comms: 1, m3: 2 } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:200])); pg.on('console', lambda m: m.type == 'error' and errs.append('console: ' + m.text[:160]))
        await pg.goto('http://localhost:8766/index.html', timeout=240000)
        await pg.wait_for_function("document.getElementById('boot') && document.getElementById('boot').classList.contains('gone')", timeout=400000)
        await pg.wait_for_timeout(1500)
        print('fonts', await pg.evaluate("Promise.all(['400 20px \"Bowlby One\"', '900 12px Figtree', '600 12px Figtree'].map(f => document.fonts.load(f).then(r => r.length > 0)))"))
        print('version line', await pg.evaluate("document.querySelector('.ver').textContent"))
        await pg.screenshot(path='/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/ui/ios251_menu.png')
        # into a match: Play, then the 1v1 event
        await pg.evaluate("document.getElementById('homePlay').click()"); await pg.wait_for_timeout(1500)
        ev = await pg.evaluate("[...document.querySelectorAll('button, [role=button]')].filter(b => b.offsetParent && /1v1/i.test(b.textContent)).map(b => b.textContent.trim().slice(0, 40))")
        print('event buttons', ev)
        await pg.evaluate("(() => { const b = [...document.querySelectorAll('button, [role=button]')].find(b => b.offsetParent && /1v1/i.test(b.textContent)); if (b) b.click(); })()")
        try:
            await pg.wait_for_function("document.getElementById('hud') && !document.getElementById('hud').classList.contains('off')", timeout=300000)
            print('in a match')
            await pg.wait_for_timeout(9000)
            print('tags', await pg.evaluate("[...document.querySelectorAll('.ntag')].map(t => [t.textContent, t.hidden, t.style.opacity])"))
            await pg.screenshot(path='/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/ui/ios251_match.png')
        except Exception as e: print('no match:', str(e)[:120])
        print('left the app:', out[:6]); print('errors', errs[:6]); await b.close()
asyncio.run(main())
