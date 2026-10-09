import asyncio, base64, wave, sys
import numpy as np
from playwright.async_api import async_playwright
U = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/aud/audiotest.html'
JS = r"""async ([sec, keep]) => {
  const sr = 44100, oc = new OfflineAudioContext(2, Math.floor(sr * (sec + 1)), sr), A = makeAudio(); A._build(oc); A._offset(1); A.music('menu');
  let nodes = 0; const oo = oc.createOscillator.bind(oc); oc.createOscillator = () => { nodes++; return oo(); };
  A._pump(sec - 2.5);
  const buf = await oc.startRendering(), i0 = sr, n = buf.length - i0, L = buf.getChannelData(0).subarray(i0), R = buf.getChannelData(1).subarray(i0);
  let ss = 0, pk = 0; for (let i = 0; i < n; i++) { ss += L[i] * L[i] + R[i] * R[i]; pk = Math.max(pk, Math.abs(L[i]), Math.abs(R[i])); }
  const o = { rms: +(10 * Math.log10(ss / (2 * n))).toFixed(1), peak: +(20 * Math.log10(pk)).toFixed(1), nodes };
  if (keep) { const m = new Float32Array(n * 2); for (let i = 0; i < n; i++) { m[2 * i] = L[i]; m[2 * i + 1] = R[i]; } const u8 = new Uint8Array(m.buffer); let s = ''; for (let i = 0; i < u8.length; i += 0x8000) s += String.fromCharCode.apply(null, u8.subarray(i, i + 0x8000)); o.wav = btoa(s); }
  return o; }"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
        pg = await b.new_page(); errs = []; pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: m.type == 'error' and errs.append(m.text))
        await pg.goto(U); await pg.wait_for_function('window.ready === true')
        r = await pg.evaluate(JS, [41, True])
        a = np.frombuffer(base64.b64decode(r.pop('wav')), dtype=np.float32).copy()
        fade = int(44100 * 2.5); env = np.linspace(1, 0, fade); a[-fade * 2::2] *= env; a[-fade * 2 + 1::2] *= env
        w = wave.open('aud/listen_menu.wav', 'wb'); w.setnchannels(2); w.setsampwidth(2); w.setframerate(44100); w.writeframes((np.clip(a, -1, 1) * 32767).astype('<i2').tobytes()); w.close()
        print(r, errs[:3]); await b.close()
asyncio.run(main())
