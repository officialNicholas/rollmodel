import asyncio, sys, base64, numpy as np
from playwright.async_api import async_playwright
sys.path.insert(0, 'gen'); from loud import lufs, phone
U = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/aud/'
ALL = ['kick', 'clap', 'snap', 'hat', 'shaker', 'crash', 'tom', 'swell', 'riser', 'impact', 'bass', 'stab', 'pad', 'drone', 'bell', 'theremin', 'arp', 'power']
SOLO = {'menu': [['kick'], ['shaker'], ['snap'], ['bass'], ['pad'], ['bell'], ['theremin'], ['swell']], 'play': [['kick'], ['clap'], ['hat'], ['crash', 'swell', 'riser', 'impact'], ['tom'], ['bass'], ['stab'], ['pad'], ['bell'], ['theremin'], ['arp']]}
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        page = sys.argv[1]; sec = 34
        pg = await b.new_page(); await pg.goto(U + page); await pg.wait_for_function('window.ready === true')
        for mode in ['menu', 'play']:
            r = await pg.evaluate("([m]) => renderMusic(m, null, 34, 'stereo', [])", [mode])
            x = np.frombuffer(base64.b64decode(r['wav']), dtype=np.float32).reshape(-1, 2).astype(np.float64); sr = r['sr']
            A, Ap = lufs(x, sr), lufs(phone(x, sr), sr)
            out = [f"ALL {A:6.1f}/{Ap:6.1f}"]
            for keep in SOLO[mode]:
                mute = [k for k in ALL if k not in keep]
                r = await pg.evaluate("([m, mu]) => renderMusic(m, null, 34, 'stereo', mu)", [mode, mute])
                x = np.frombuffer(base64.b64decode(r['wav']), dtype=np.float32).reshape(-1, 2).astype(np.float64)
                out.append(f"{'+'.join(keep)[:10]} {lufs(x, sr) - A:+5.1f}/{lufs(phone(x, sr), sr) - Ap:+5.1f}")
            print(mode, ' | '.join(out))
        await b.close()
asyncio.run(main())
