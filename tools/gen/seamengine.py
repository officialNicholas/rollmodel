# the loop played by the game's own audio engine, past its seam: any click shows as a spike in the very highs at the jump
import asyncio, base64, numpy as np, json
from scipy import signal
from playwright.async_api import async_playwright
JS = r"""async ([style, sec]) => {
  window.MUSIC_STYLE = style;
  const sr = 48000, oc = new OfflineAudioContext(2, Math.floor(sr * (sec + 1)), sr), A = makeAudio(); A._build(oc); A._offset(1);
  const key = ({ spooky: 'halloween', tropical: 'island', pop: 'blank' })[style];
  A.music('play'); for (let i = 0; i < 200 && !A._trk(key); i++) await new Promise(r => setTimeout(r, 50));
  A.music('play'); A._pump(sec);
  const buf = await oc.startRendering(), L = buf.getChannelData(0), R = buf.getChannelData(1), m = new Float32Array(L.length);
  for (let i = 0; i < L.length; i++) m[i] = 0.5 * (L[i] + R[i]);
  const u8 = new Uint8Array(m.buffer); let s = ''; for (let i = 0; i < u8.length; i += 0x8000) s += String.fromCharCode.apply(null, u8.subarray(i, i + 0x8000));
  return btoa(s); }"""
async def main():
    meta = json.load(open('music_out/loops.json'))
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required']); pg = await b.new_page()
        await pg.goto('http://127.0.0.1:8765/aud/audiotest.html'); await pg.wait_for_function('window.ready === true')
        for style, key in (('spooky', 'halloween'), ('tropical', 'island'), ('pop', 'blank')):
            M = meta[key]; sec = M['b'] + 6
            x = np.frombuffer(base64.b64decode(await pg.evaluate(JS, [style, sec])), dtype=np.float32).astype(np.float64)
            sr = 48000; bh, ah = signal.butter(4, 9000 / (sr / 2), 'high'); hx = np.abs(signal.filtfilt(bh, ah, x))
            # find when the song started (first sound after the 1 s offset), so the jump's time is known
            st = np.where(np.abs(x) > 1e-3)[0][0] / sr
            tj = st + M['b'] - M['a'] * 0 ; # the source reaches loopEnd at st + b
            i = int((st + M['b']) * sr); w = int(0.03 * sr)
            near = hx[i - w:i + w].max(); typ = np.percentile(hx[int((st + 5) * sr):int((st + M['b'] - 1) * sr)], 99.9)
            print(f'{key}: started {st:.3f}s, jump at {st + M["b"]:.2f}s: highs peak {near:.4f} vs 99.9th pct elsewhere {typ:.4f}')
        await b.close()
asyncio.run(main())
