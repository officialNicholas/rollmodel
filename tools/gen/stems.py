import asyncio, sys, base64, numpy as np
from scipy.io import wavfile
from playwright.async_api import async_playwright
sys.path.insert(0, 'gen'); from loud import lufs, phone
U = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/aud/'
DR = ['kick', 'clap', 'snap', 'hat', 'shaker', 'crash', 'tom', 'swell', 'riser', 'impact']
LEAD = ['bell', 'theremin', 'arp', 'power']
GROUPS = {'drums': DR, 'bass': ['bass'], 'chords': ['stab', 'pad', 'drone'], 'lead': LEAD}
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for page in sys.argv[1:]:
            pg = await b.new_page(); await pg.goto(U + page); await pg.wait_for_function('window.ready === true')
            for mode in ['menu', 'play']:
                row = []
                for gname, keep in [('all', None)] + list(GROUPS.items()):
                    mute = [] if keep is None else [k for g in GROUPS.values() for k in g if k not in keep]
                    r = await pg.evaluate("([m, mu]) => renderMusic(m, null, 16, 'stereo', mu)", [mode, mute])
                    x = np.frombuffer(base64.b64decode(r['wav']), dtype=np.float32).reshape(-1, 2).astype(np.float64); sr = r['sr']
                    row.append(f"{gname} {lufs(x, sr):6.1f}/{lufs(phone(x, sr), sr):6.1f}")
                print(f"{page:9s} {mode:5s} " + ' | '.join(row))
            await pg.close()
        await b.close()
asyncio.run(main())
