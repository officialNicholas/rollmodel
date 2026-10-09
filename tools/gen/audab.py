# renders the music from an audio test page: stats, wavs and a spectrogram
import asyncio, sys, base64, json
import numpy as np
from scipy.io import wavfile
from playwright.async_api import async_playwright
page = sys.argv[1]; tag = sys.argv[2]; sec = float(sys.argv[3]) if len(sys.argv) > 3 else 20
U = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/aud/' + page
CASES = [('menu', None), ('play', None), ('play', [True, False, False, False]), ('play', [False, True, False, False]), ('play', [False, False, True, False])]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: m.type == 'error' and errs.append(m.text))
        await pg.goto(U); await pg.wait_for_function('window.ready === true')
        print('build ms', round(await pg.evaluate('buildTime()'), 1), round(await pg.evaluate('buildTime()'), 1))
        for mode, mood in CASES:
            keep = 'stereo' if mood is None else False
            r = await pg.evaluate("([m, md, s, k]) => renderMusic(m, md, s, k)", [mode, mood, sec, keep])
            if keep:
                x = np.frombuffer(base64.b64decode(r.pop('wav')), dtype=np.float32).reshape(-1, 2); sr = int(r.pop('sr')); r.pop('ch')
                wavfile.write(f'aud/{tag}_{mode}.wav', sr, (np.clip(x, -1, 1) * 32767).astype(np.int16))
            print(f"{mode:5s} {str(mood):28s}", json.dumps(r))
        r = await pg.evaluate("() => renderMix('play', [[0.5, 'jump'], [0.9, 'land', [0.6]], [1.4, 'splat', [1]], [2.0, 'fling', [0.8]], [2.6, 'bonk', [1]], [3.2, 'slam'], [4.5, 'splat', [0.5]], [5.0, 'tick', [3]], [5.4, 'tick', [4]], [6.0, 'power']], 7, false)")
        print('mix play+fx', json.dumps(r))
        print('errors', errs[:4]); await b.close()
asyncio.run(main())
