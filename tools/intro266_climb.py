#!/usr/bin/env python3
"""v266 checks, stepped at 30 fps: the head down in the paint (and its tail under the sand) from the pop to the cards, each face close up
there, then the climb out frame by frame, and standing by the drum through the name and confirm cards."""
import asyncio, json, os, sys
from playwright.async_api import async_playwright
SHIM = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'intro264_ending.py')).read().split('SHIM = """')[1].split('"""')[0]
OUT = sys.argv[1]; MODE = sys.argv[2] if len(sys.argv) > 2 else 'port'; VP = (390, 780) if MODE == 'port' else (780, 390)
FACES = os.environ.get('FACES', '1') == '1'
os.makedirs(OUT, exist_ok=True)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/opt/pw-browsers/chromium', args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist', '--autoplay-policy=no-user-gesture-required'])
        ctx = await b.new_context(viewport={'width': VP[0], 'height': VP[1]}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__tapGate = false; try { localStorage.clear(); } catch (e) {}")
        pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)[:400]))
        pg.on('console', lambda m: errs.append('console ' + m.text[:300]) if m.type == 'error' and '404' not in m.text else None)
        await pg.goto('http://localhost:8773/_intro_test.html', timeout=600000)
        await pg.wait_for_function('typeof __T === "object"', timeout=600000, polling=500)
        await pg.wait_for_timeout(1500)
        if await pg.evaluate("!document.getElementById('orient').hidden"):
            await pg.evaluate("document.querySelector('#orient .ocard[data-o=\"%s\"]').click(); document.getElementById('orientOk').click()" % MODE); await pg.wait_for_timeout(800)
        for i in range(200):
            if await pg.evaluate("__T.ev('!!(FL && FL.live)')"): break
            await pg.wait_for_timeout(200)
        await pg.evaluate(SHIM); await pg.wait_for_timeout(200)
        ph = lambda: pg.evaluate("__T.ev('JSON.stringify(FL.peek())')")
        n = [0]
        async def steps(k, save=None):
            for _ in range(k):
                await pg.evaluate('__step(1000 / 30)'); n[0] += 1
                if save: await pg.screenshot(path=f'{OUT}/{save}_{n[0]:04d}.jpg', type='jpeg', quality=80, scale='css')
        async def until(phase, pt, save=None, every=1):
            while True:
                await steps(1); q = json.loads(await ph())
                if save and q['ph'] == save[0] and n[0] % every == 0: await pg.screenshot(path=f'{OUT}/{save[1]}_{n[0]:04d}.jpg', type='jpeg', quality=80, scale='css')
                if q['ph'] == phase and q['pt'] >= pt: return q
        await until('barrel', 6.9, ('barrel', 'pop'), 3)   # (the drum thumps, tips; it pours; the eyes come up and look about)
        await until('iris', 1.2, ('barrel', 'pop'), 3)
        # each face, close, down in the paint
        if FACES:
            for f in ['neutral', 'smirk', 'focus', 'curious', 'glee', 'startle', 'doze', 'content', 'happy']:
                await pg.evaluate("__T.ev(\"FL.X().I.face('%s', 3); 1\")" % f); await steps(14)
                await pg.screenshot(path=f'{OUT}/face_{f}.png', clip={'x': 60, 'y': 180, 'width': 270, 'height': 260})
        await pg.evaluate("document.querySelector(\".flopt[data-i='violet']\").click()"); await steps(20)
        await pg.evaluate("document.querySelector('#flIrisGo').click()"); await steps(30)
        await pg.evaluate("document.querySelector(\".flopt[data-s='round']\").click()")
        for k in range(8): await steps(8); await pg.screenshot(path=f'{OUT}/proud_{k}.png', clip={'x': 60, 'y': 180, 'width': 270, 'height': 260})
        await pg.evaluate("document.querySelector('#flStyleGo').click()"); await steps(30)
        await pg.evaluate("document.querySelector(\".flopt[data-c='red']\").click()"); await steps(30, 'paint')
        await pg.evaluate("document.querySelector('#flPaintGo').click()")
        await until('name', 0.6, ('form', 'form'), 1)
        await steps(20, 'name')
        await pg.fill('#flNameIn', 'Pip'); await pg.evaluate("document.querySelector('#flNameGo').click()")
        await until('confirm', 1.5, ('confirm', 'confirm'), 3)
        print('done', n[0], await ph(), flush=True); print('ERRORS', errs[:6]); await b.close()
asyncio.run(main())
