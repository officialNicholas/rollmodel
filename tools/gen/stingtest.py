# the results moment, offline: the sting over the start of the win or lost song, written out to listen to, with levels
import asyncio, base64, wave, sys
import numpy as np
from playwright.async_api import async_playwright
JS = r"""async ([kind, sec]) => {
  window.MUSIC_STYLE = 'pop';
  const sr = 48000, oc = new OfflineAudioContext(2, Math.floor(sr * (sec + 1.2)), sr), A = makeAudio(); A._build(oc); A._offset(1);
  const key = kind === 'win' ? 'win' : 'lost';
  A.music('play'); for (let i = 0; i < 300 && !(A._trk('win') && A._trk('lost')); i++) await new Promise(r => setTimeout(r, 50));
  A.music('end'); A.sting(kind); const on = A.music(key);
  const buf = await oc.startRendering(), L = buf.getChannelData(0), R = buf.getChannelData(1), db = x => +(20 * Math.log10(Math.max(1e-9, x))).toFixed(1);
  const seg = (a, b) => { const i0 = Math.floor(a * sr), i1 = Math.min(L.length, Math.floor(b * sr)); let ss = 0, pk = 0; for (let i = i0; i < i1; i++) { ss += L[i] * L[i] + R[i] * R[i]; pk = Math.max(pk, Math.abs(L[i]), Math.abs(R[i])); } return [db(Math.sqrt(ss / (2 * (i1 - i0)))), db(pk)]; };
  const m = new Float32Array(L.length * 2); for (let i = 0; i < L.length; i++) { m[2 * i] = L[i]; m[2 * i + 1] = R[i]; }
  const u8 = new Uint8Array(m.buffer); let s = ''; for (let i = 0; i < u8.length; i += 0x8000) s += String.fromCharCode.apply(null, u8.subarray(i, i + 0x8000));
  return { on, sting: seg(1, 2.2), after: seg(3, 1 + sec), wav: btoa(s) }; }"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required']); pg = await b.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: m.type == 'error' and errs.append(m.text))
        await pg.goto('http://127.0.0.1:8765/aud/audiotest.html'); await pg.wait_for_function('window.ready === true')
        for kind in ['win', 'lose', 'draw']:
            r = await pg.evaluate(JS, [kind, 7]); a = np.frombuffer(base64.b64decode(r.pop('wav')), dtype=np.float32)
            w = wave.open(f'aud/sting_{kind}.wav', 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(48000); w.writeframes((np.clip(a, -1, 1) * 32767).astype('<i2').tobytes()); w.close()
            print(kind, r)
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
