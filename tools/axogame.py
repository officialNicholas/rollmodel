"""The axolotl in the game: the lobby, then a match a few seconds in (the player's view), and close-ups of the player and a rival.
usage: axogame.py [tag] [stage]"""
import asyncio, json, sys
from playwright.async_api import async_playwright
OUT = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/axoshots'
TAG = sys.argv[1] if len(sys.argv) > 1 else 'a'; ST = sys.argv[2] if len(sys.argv) > 2 else 'studio'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 430, 'height': 754}, device_scale_factor=2)
        await ctx.add_init_script("window.__tut = true; try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'port', name:'Dusk', seen:{look:1}, runs: 9, tut: { ph: 'done' } })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:400])); pg.on('console', lambda m: errs.append('CONSOLE ' + m.text[:300]) if m.type == 'error' or 'axolotl' in m.text or 'slime' in m.text else None)
        await pg.goto('http://localhost:8765/pc_h.html', timeout=300000)
        for i in range(150):
            if await pg.evaluate("typeof __T === 'object' && !!__T.VP && !!__T.VP.slime"): break
            await pg.wait_for_timeout(2000)
        info = await pg.evaluate("(() => { const I = __T.VP.slime; return { kind: I.kind, axoReady: __T.AXOC && __T.AXOC.S.ready, slimeReady: __T.SLIME.S.ready, state: __T.state }; })()")
        print('boot', json.dumps(info), errs[:5])
        await pg.wait_for_timeout(2500); await pg.screenshot(path=f'{OUT}/{TAG}_lobby.png')
        await pg.evaluate(f"__T.setStage('{ST}'); __T.start()")
        for i in range(150):
            if await pg.evaluate("__T.state === 'play'"): break
            await pg.wait_for_timeout(1000)
        await pg.wait_for_timeout(2500); await pg.screenshot(path=f'{OUT}/{TAG}_play1.png')
        await pg.wait_for_timeout(3000); await pg.screenshot(path=f'{OUT}/{TAG}_play2.png')
        st = await pg.evaluate("(() => { const I = __T.VP.slime, A = I.ax && I.ax.A; return A ? { mesh: A.mesh, state: A.state, speed: +A.motion.speed.toFixed(2), turn: +A.motion.turn.toFixed(2), vis: I.root.visible, Pspd: +__T.P.spd.toFixed(2) } : null; })()")
        print('play', json.dumps(st), 'errors', errs[:8])
        await b.close()
asyncio.run(main())
