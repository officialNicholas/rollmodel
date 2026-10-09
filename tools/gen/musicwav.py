# render each version of the song in stereo, as it plays in a match, for listening
import asyncio, base64, wave, sys
import numpy as np
from playwright.async_api import async_playwright
U = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/aud/audiotest.html'
JS = r"""async ([style, mode, sec]) => {
  window.MUSIC_STYLE = style;
  const sr = 44100, oc = new OfflineAudioContext(2, Math.floor(sr * (sec + 1)), sr), A = makeAudio(); A._build(oc); A._offset(1); A.music(mode); A._pump(sec - 1.2);
  const buf = await oc.startRendering(), i0 = sr, n = buf.length - i0, L = buf.getChannelData(0).subarray(i0), R = buf.getChannelData(1).subarray(i0), m = new Float32Array(n * 2);
  for (let i = 0; i < n; i++) { m[2 * i] = L[i]; m[2 * i + 1] = R[i]; }
  const u8 = new Uint8Array(m.buffer); let s = ''; for (let i = 0; i < u8.length; i += 0x8000) s += String.fromCharCode.apply(null, u8.subarray(i, i + 0x8000)); return btoa(s); }"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
        pg = await b.new_page(); await pg.goto(U); await pg.wait_for_function('window.ready === true')
        for style, mode, sec in [('tropical', 'play', 36), ('pop', 'play', 36), ('spooky', 'play', 36)]:
            a = np.frombuffer(base64.b64decode(await pg.evaluate(JS, [style, mode, sec])), dtype=np.float32)
            fade = int(44100 * 1.2); a = a.copy(); env = np.linspace(1, 0, fade); a[-fade * 2::2] *= env; a[-fade * 2 + 1::2] *= env
            w = wave.open(f'aud/listen_{style}_{mode}.wav', 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(44100); w.writeframes((np.clip(a, -1, 1) * 32767).astype('<i2').tobytes()); w.close()
            print('ok', style, mode, flush=True)
        await b.close()
asyncio.run(main())
