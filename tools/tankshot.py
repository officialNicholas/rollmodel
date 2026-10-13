import asyncio, sys, json
from playwright.async_api import async_playwright
PAGE, TAG = sys.argv[1], sys.argv[2]
WS = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 390, 'height': 844}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.__tut = true; window.__noVote = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', stage:'island', seen:{look:1,steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1}, drops: 50, runs: 9, flings: 50, tut: { ph: 'done' } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto('http://localhost:8765/' + PAGE, timeout=300000); await pg.wait_for_function('typeof __T === "object"', timeout=300000)
        await pg.evaluate("__T.start()"); await pg.wait_for_function("__T.state === 'play'", timeout=300000)
        await pg.evaluate("(() => { __T.renderer.render = () => {}; __T.ev('inShadow = () => false'); window.__hold = ''; setInterval(() => { if (__hold) __T.ev(__hold); }, 50); })()")
        shots = []
        for name, js in [('low', "P.paint = 0.15; P.dry = false; P.dryT = 0; setWx('clear', 1000); P.giantT = 0;"), ('heat', "P.paint = 0.6; setWx('sun', 1000); P.sunGrace = 0; P.st = 'play'; P.dry = false; P.dryT = 0; P.giantT = 0;"), ('giant', "setWx('clear', 1000); P.giantT = 8; P.paint = 0.9;"), ('chip', "P.paint = 0.6; setWx('sun', 1000); P.sunGrace = 0; P.st = 'play'; P.dry = false; P.dryT = 0; P.giantT = 0;")]:
            await pg.evaluate(f"(() => {{ window.__hold = {json.dumps(js)}; __T.ev(__hold); }})()"); await pg.wait_for_timeout(900)
            await pg.evaluate("(() => { for (const a of document.getAnimations()) { a.pause(); a.currentTime = 220; } })()")
            el = 'wx' if name == 'chip' else 'bar'
            r = await pg.evaluate(f"(() => {{ const b = document.getElementById('{el}').getBoundingClientRect(); return [b.left, b.top, b.width, b.height]; }})()")
            pad = 30; clip = {'x': max(0, r[0] - pad), 'y': max(0, r[1] - pad), 'width': r[2] + 2 * pad, 'height': r[3] + 2 * pad}
            await pg.screenshot(path=f'{WS}/ui/tank_{TAG}_{name}.png', clip=clip); shots.append(name)
            await pg.evaluate("(() => { for (const a of document.getAnimations()) a.play(); })()")
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
