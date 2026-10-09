import asyncio, json, base64, sys
import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy import signal
from playwright.async_api import async_playwright
U = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/aud/audiotest.html'
ITEMS = [('fx', 'splat', [1], 0.6), ('fx', 'jump', [], 0.4), ('fx', 'slam', [], 1.2), ('fx', 'fling', [1], 0.5), ('fx', 'bonk', [1], 0.4), ('fx', 'power', [], 1.2), ('fx', 'fanfare', [], 2.8), ('fx', 'lose', [], 2.8), ('fx', 'grow', [], 1.6), ('mus', 'play', None, 8.5), ('mus', 'menu', None, 8.5)]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(); await pg.goto(U); await pg.wait_for_function('window.ready === true')
        fig, axs = plt.subplots(len(ITEMS), 1, figsize=(12, 2.0 * len(ITEMS)))
        for ax, (kind, name, args, sec) in zip(axs, ITEMS):
            if kind == 'fx': r = await pg.evaluate("([n, a, s]) => renderFx(n, a, s, true)", [name, args, sec])
            else: r = await pg.evaluate("([m, s]) => renderMusic(m, null, s, true)", [name, sec])
            x = np.frombuffer(base64.b64decode(r['wav']), dtype=np.float32); sr = int(r['sr'])
            wavfile.write(f'aud/{name}.wav', sr, (np.clip(x, -1, 1) * 32767).astype(np.int16))
            f, t, S = signal.spectrogram(x, sr, nperseg=512, noverlap=384)
            ax.pcolormesh(t, f, 10 * np.log10(S + 1e-12), shading='auto', vmin=-110, vmax=-30, cmap='magma'); ax.set_ylim(0, 8000); ax.set_ylabel(name, rotation=0, labelpad=30)
        plt.tight_layout(); plt.savefig('aud/spec.png', dpi=70)
        await b.close()
asyncio.run(main())
