import asyncio, sys, base64, numpy as np
from playwright.async_api import async_playwright
sys.path.insert(0, 'gen'); from loud import lufs, phone, bands
U = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/aud/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for page in sys.argv[1:]:
            pg = await b.new_page(); await pg.goto(U + page); await pg.wait_for_function('window.ready === true')
            for mode in ['menu', 'play']:
                r = await pg.evaluate("([m]) => renderMusic(m, null, 34, 'stereo', [])", [mode])
                x = np.frombuffer(base64.b64decode(r['wav']), dtype=np.float32).reshape(-1, 2).astype(np.float64); sr = r['sr']
                print(f"{page:9s} {mode:5s} LUFS {lufs(x, sr):6.1f} phone {lufs(phone(x, sr), sr):6.1f} peak {r['peak']:5.1f} side {r['side']:6.1f} bands " + ' '.join(f'{v:6.1f}' for v in bands(x, sr)), flush=True)
            await pg.close()
        await b.close()
asyncio.run(main())
