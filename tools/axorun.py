"""The axolotl running a match: the player steered in a wide arc (keys), shots from the play camera every so often, and the frame
times. usage: axorun.py [tag] [stage] [secs]"""
import asyncio, json, sys
from playwright.async_api import async_playwright
OUT = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axoshots'
TAG = sys.argv[1] if len(sys.argv) > 1 else 'r'; ST = sys.argv[2] if len(sys.argv) > 2 else 'blank'; SECS = float(sys.argv[3]) if len(sys.argv) > 3 else 12
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 430, 'height': 754}, device_scale_factor=2)
        await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{look:1}, runs: 9, tut: { ph: 'done' } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:400]))
        await pg.goto('http://localhost:8765/pc_h.html', timeout=300000)
        for i in range(150):
            if await pg.evaluate("typeof __T === 'object' && !!__T.VP && !!__T.VP.slime"): break
            await pg.wait_for_timeout(2000)
        await pg.evaluate(f"__T.setStage('{ST}'); __T.start()")
        for i in range(150):
            if await pg.evaluate("__T.state === 'play'"): break
            await pg.wait_for_timeout(1000)
        await pg.wait_for_timeout(1500)
        await pg.keyboard.down('ArrowLeft'); n = 0; t = 0
        while t < SECS:
            await pg.wait_for_timeout(1500); t += 1.5; n += 1
            if n % 3 == 0: await pg.keyboard.up('ArrowLeft'); await pg.keyboard.down('ArrowRight')
            if n % 3 == 1 and n > 1: await pg.keyboard.up('ArrowRight'); await pg.keyboard.down('ArrowLeft')
            await pg.screenshot(path=f'{OUT}/{TAG}_{n:02d}.png')
            st = await pg.evaluate("(() => { const I = __T.VP.slime, A = I.ax && I.ax.A; return { mesh: A.mesh, state: A.state, sp: +A.motion.speed.toFixed(2), turn: +A.motion.turn.toFixed(2), Pspd: +__T.P.spd.toFixed(1), air: __T.P.air }; })()")
            print(n, json.dumps(st))
        await pg.keyboard.up('ArrowLeft'); await pg.keyboard.up('ArrowRight')
        print('errors', errs[:6])
        await b.close()
asyncio.run(main())
