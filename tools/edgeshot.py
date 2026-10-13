"""The screen-edge effects, shot: plain, low paint, burning in the sun, a hit (early and late). usage: edgeshot.py page tag gfx(hi|perf)"""
import asyncio, sys, json
from playwright.async_api import async_playwright
PAGE, TAG, GFX = sys.argv[1], sys.argv[2], sys.argv[3]
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
        print('gfx', await pg.evaluate("__T.GFX"), 'post', await pg.evaluate("!!__T.post"))
        await pg.evaluate("(() => { __T.ev('inShadow = () => false'); window.__hold = ''; setInterval(() => { if (__hold) __T.ev(__hold); }, 50); })()")
        async def shot(name, js, wait=1800):
            await pg.evaluate(f"(() => {{ window.__hold = {json.dumps(js)}; __T.ev(__hold); }})()"); await pg.wait_for_timeout(wait)
            await pg.screenshot(path=f'{WS}/ui/edge_{TAG}_{name}.png')
        await shot('plain', "P.paint = 0.9; P.dry = false; P.dryT = 0; setWx('clear', 1000);")
        await shot('low', "P.paint = 0.15; P.dry = false; P.dryT = 0;")
        await shot('heat', "P.paint = 0.6; setWx('sun', 1000); P.sunGrace = 0; P.st = 'play'; P.dry = false; P.dryT = 0;", 2500)
        await pg.evaluate("(() => { window.__hold = \"P.paint = 0.9; setWx('clear', 1000); P.dry = false; P.dryT = 0;\"; })()"); await pg.wait_for_timeout(1500)
        await pg.evaluate("__T.ev('hitEdge(H)')"); await pg.wait_for_timeout(120); await pg.screenshot(path=f'{WS}/ui/edge_{TAG}_hit1.png')
        await pg.wait_for_timeout(400); await pg.screenshot(path=f'{WS}/ui/edge_{TAG}_hit2.png')
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
