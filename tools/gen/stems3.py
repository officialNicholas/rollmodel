import asyncio, sys, base64, numpy as np
from playwright.async_api import async_playwright
sys.path.insert(0, 'gen'); from loud import lufs, phone, kw
U = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/aud/'
ALL = ['kick', 'clap', 'snap', 'hat', 'shaker', 'crash', 'tom', 'swell', 'riser', 'impact', 'bass', 'stab', 'pad', 'drone', 'bell', 'theremin', 'arp', 'power']
SOLO = {'menu': [['kick'], ['shaker'], ['snap'], ['bass'], ['pad'], ['bell'], ['theremin'], ['swell']], 'play': [['kick'], ['clap'], ['hat'], ['crash', 'swell', 'riser', 'impact'], ['tom'], ['bass'], ['stab'], ['pad'], ['bell'], ['theremin'], ['arp']]}
def en(x, sr):   # ungated K-weighted energy, full range and phone band, in dB
    a = kw(x, sr); b = kw(phone(x, sr), sr)
    return 10 * np.log10((a ** 2).mean() * 2 + 1e-15), 10 * np.log10((b ** 2).mean() * 2 + 1e-15)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        page = sys.argv[1]; sec = float(sys.argv[2]) if len(sys.argv) > 2 else 34
        pg = await b.new_page(); await pg.goto(U + page); await pg.wait_for_function('window.ready === true')
        for mode in ['menu', 'play']:
            r = await pg.evaluate("([m, s]) => renderMusic(m, null, s, 'stereo', [])", [mode, sec])
            x = np.frombuffer(base64.b64decode(r['wav']), dtype=np.float32).reshape(-1, 2).astype(np.float64); sr = r['sr']
            A, Ap = en(x, sr)
            out = [f"ALL {lufs(x, sr):6.1f}/{lufs(phone(x, sr), sr):6.1f}LUFS"]
            for keep in SOLO[mode]:
                mute = [k for k in ALL if k not in keep]
                r = await pg.evaluate("([m, mu, s]) => renderMusic(m, null, s, 'stereo', mu)", [mode, mute, sec])
                x = np.frombuffer(base64.b64decode(r['wav']), dtype=np.float32).reshape(-1, 2).astype(np.float64)
                e, ep = en(x, sr)
                out.append(f"{'+'.join(keep)[:8]} {e - A:+5.1f}/{ep - Ap:+5.1f}")
            print(page, mode, ' | '.join(out), flush=True)
        await b.close()
asyncio.run(main())
