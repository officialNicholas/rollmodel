import asyncio, sys, json, time
from playwright.async_api import async_playwright
async def main(mode, diff):
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        ctx = await b.new_context(viewport={'width': 844, 'height': 390}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("try { localStorage.setItem('paint-world-red.v1', JSON.stringify({ orient:'land', name:'Dusk', seen:{steer:1,jump:1,hold:1,roll:1,missile:1,pound:1,burst:1,orb:1,look:1,items:1}, mode:'" + mode + "', runs: 3, stage:'island', diff:'" + diff + "' })); } catch (e) {}")
        pg = await ctx.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:400]))
        cdp = await ctx.new_cdp_session(pg); await cdp.send('Debugger.enable'); paused = []
        cdp.on('Debugger.paused', lambda ev: paused.append(ev))
        await pg.goto('http://localhost:8765/pc_h.html', timeout=240000); await pg.wait_for_function('typeof __T === "object"', timeout=240000); await pg.wait_for_timeout(1500)
        await pg.evaluate("document.getElementById('homePlay').click()"); await pg.wait_for_function("__T.state === 'play'", timeout=60000)
        print('mode', await pg.evaluate("[__T.mode, __T.ACTIVE.length, __T.diff]")); last = None
        for i in range(40):
            try:
                r = await asyncio.wait_for(pg.evaluate("(() => { let err = null; try { for (let k = 0; k < 150; k++) { __T.step(0.016); if (__T.state !== 'play') break; } } catch (e) { err = String(e.stack || e).slice(0, 400); } return [+__T.runT.toFixed(1), __T.state, __T.P.st, __T.H.st, __T.H2 && __T.H2.st, __T.orb.on, __T.powers.length, __T.wx, err]; })()"), timeout=25)
                print(i, r); last = r
                if r[8] or r[1] != 'play': break
            except asyncio.TimeoutError:
                print('HUNG after', last); await cdp.send('Debugger.pause'); await asyncio.sleep(2)
                if paused:
                    for f in paused[0]['callFrames'][:14]: print('  frame', f['functionName'], f['location']['lineNumber'] + 1, f['location']['columnNumber'])
                else: print('no pause event')
                break
        print('errors', errs[:5]); await b.close()
asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else 'trio', sys.argv[2] if len(sys.argv) > 2 else 'medium'))
