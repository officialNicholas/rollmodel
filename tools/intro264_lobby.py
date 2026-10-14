#!/usr/bin/env python3
"""v264 lobby entrance probe: a new player, the intro jumped straight to its hand-over (FL.handoff, test build only), then the lobby entrance stepped at 30 fps, every frame saved. Usage: intro264_lobby.py <out dir> [port|land] (NF=frames)"""
import asyncio, json, os, sys
from playwright.async_api import async_playwright
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
SHIM = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'intro264_ending.py')).read().split('SHIM = """')[1].split('"""')[0]
OUT = sys.argv[1]; MODE = sys.argv[2] if len(sys.argv) > 2 else 'port'; VP = (390, 780) if MODE == 'port' else (780, 390)
SAVE = json.dumps({"name": "Pip", "color": "purple", "look": {"eyes": "edgy", "iris": "blue"}, "introDone": 1, "tut": {"ph": "match"}, "orient": MODE})
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path='/opt/pw-browsers/chromium', args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist', '--autoplay-policy=no-user-gesture-required'])
        ctx = await b.new_context(viewport={'width': VP[0], 'height': VP[1]}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__tapGate = false; try { localStorage.clear(); } catch (e) {}")
        pg = await ctx.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append('PAGEERR ' + str(e)[:400]))
        await pg.goto('http://localhost:8773/_intro_test.html', timeout=600000)
        await pg.wait_for_function('typeof __T === "object"', timeout=600000, polling=500)
        await pg.wait_for_timeout(6000)
        if await pg.evaluate("!document.getElementById('orient').hidden"):
            await pg.evaluate("document.querySelector('#orient .ocard[data-o=\"%s\"]').click(); document.getElementById('orientOk').click()" % MODE); await pg.wait_for_timeout(1500)
        print('state', await pg.evaluate("__T.ev('state')"), 'FL', await pg.evaluate("__T.ev('typeof FL + \" \" + !!(FL && FL.after)')"), flush=True)
        for i in range(100):
            if await pg.evaluate("__T.ev('FL.live')"): break
            await pg.wait_for_timeout(200)
        await pg.wait_for_timeout(1500); print('live', await pg.evaluate("__T.ev('FL.live')"), flush=True)
        await pg.evaluate(SHIM); await pg.wait_for_timeout(200)
        await pg.evaluate("__T.ev('FL.handoff(); 1')")
        FR = OUT + '/lobby_' + MODE; os.makedirs(FR, exist_ok=True)
        for n in range(1, int(os.environ.get("NF", "80"))):
            await pg.evaluate('__step(1000 / 30)')
            await pg.screenshot(path=f'{FR}/f{n:04d}.jpg', type='jpeg', quality=85)
            s = await pg.evaluate("__T.ev('JSON.stringify({ fr: renderer.info.render.frame, jt: FL.jin ? +FL.jin.t.toFixed(2) : null, rq: window.__rq.length, jin: FL.jin ? FL.jin.ph : null, ball: FL.jin ? !!FL.jin.ball : null, li: lookIntro ? +lookIntro.t.toFixed(2) : null, parts: poolList.reduce((a, q) => a + q.items.length, 0), shake: +shake.toFixed(3) })')")
            if n % 3 == 0 or n < 3: print(n, s, flush=True)
        print('ERRORS', errs, flush=True); await b.close()
asyncio.run(main())
