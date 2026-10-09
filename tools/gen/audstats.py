import asyncio, json, sys, base64
import numpy as np
from playwright.async_api import async_playwright
U = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/aud/audiotest.html'
FX = [('ui', []), ('nope', []), ('jump', []), ('land', [1]), ('land', [0.3]), ('splat', [1]), ('splat', [0.4]), ('slam', []), ('quake', []), ('burst', [1]), ('fling', [1]), ('fling', [0.3]), ('whoosh', []), ('brake', []), ('notch', [2]), ('enter', []), ('glug', [0.5]), ('pop', []), ('power', []), ('orb', []), ('grow', []), ('shrink', []), ('die', ['pound']), ('die', ['sun']), ('fall', []), ('squish', []), ('bonk', [1]), ('bonk', [0.3]), ('spot', []), ('ready', []), ('lead', [True]), ('lead', [False]), ('danger', []), ('low', []), ('count', [3]), ('tick', [4]), ('horn', []), ('fanfare', []), ('lose', []), ('draw', []), ('thunder', []), ('heatWarn', []), ('heatOn', []), ('dusk', []), ('splashWater', []), ('sprinkle', [1]), ('sink', []), ('rumble', []), ('rise', []), ('flip', [])]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
        pg = await b.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: m.type == 'error' and errs.append(m.text))
        await pg.goto(U); await pg.wait_for_function('window.ready === true')
        rows = []
        for name, args in FX:
            r = await pg.evaluate("([n, a]) => renderFx(n, a, 4.0)", [name, args])
            rows.append((name + ('(' + ','.join(map(str, args)) + ')' if args else ''), r))
        for nm, r in rows: print(f"{nm:18s} peak {r['peak']:6.1f}  rms {r['rms']:6.1f}  maxST {r['maxST']:6.1f}  until {r['audibleUntil']:4.2f}s")
        for mode, mood in [('menu', None), ('play', None), ('play', [True, False, False, False]), ('play', [False, True, False, False]), ('play', [False, False, True, False])]:
            r = await pg.evaluate("([m, md]) => renderMusic(m, md, 12, false)", [mode, mood])
            print(f"music {mode:5s} {str(mood):28s} peak {r['peak']:6.1f}  rms {r['rms']:6.1f}  maxST {r['maxST']:6.1f}")
        for nm, js in [('roll 5', "A.roll(5, 0)"), ('roll 2', "A.roll(2, 0)"), ('rain 1', "A.rain(1)"), ('sizzle 1', "A.sizzle(1)"), ('charge .8', "A.chargeStart(); A.chargeSet(0.8)")]:
            r = await pg.evaluate("async (js) => { const sr = 44100, oc = new OfflineAudioContext(2, sr * 3, sr), A = makeAudio(); A._build(oc); A._offset(0); eval(js); for (let i = 0; i < 40; i++) {} return stats(await oc.startRendering(), false, 1); }", js)
            print(f"loop {nm:10s} peak {r['peak']:6.1f}  rms {r['rms']:6.1f}  maxST {r['maxST']:6.1f}")
        r = await pg.evaluate("() => renderMix('play', [[0.5, 'jump'], [0.9, 'land', [0.6]], [1.4, 'splat', [1]], [2.0, 'fling', [0.8]], [2.6, 'bonk', [1]], [3.2, 'slam'], [4.5, 'splat', [0.5]], [5.0, 'tick', [3]], [5.4, 'tick', [4]], [6.0, 'power']], 7, false)")
        print('mix play+fx', r)
        print('errors', errs[:4]); await b.close()
asyncio.run(main())
