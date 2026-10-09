import asyncio, base64
import numpy as np
from playwright.async_api import async_playwright
U = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/aud/audiotest.html'
JS = r"""async ([sec, mute]) => {
  const sr = 44100, oc = new OfflineAudioContext(2, Math.floor(sr * (sec + 1)), sr), A = makeAudio(); A._build(oc); A._offset(1); A._mute(mute); A.music('menu'); A._pump(sec - 1);
  const buf = await oc.startRendering(), i0 = sr, n = buf.length - i0, L = buf.getChannelData(0).subarray(i0), R = buf.getChannelData(1).subarray(i0), m = new Float32Array(n);
  for (let i = 0; i < n; i++) m[i] = (L[i] + R[i]) * 0.5; const u8 = new Uint8Array(m.buffer); let s = ''; for (let i = 0; i < u8.length; i += 0x8000) s += String.fromCharCode.apply(null, u8.subarray(i, i + 0x8000)); return btoa(s); }"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(); await pg.goto(U); await pg.wait_for_function('window.ready === true')
        allv = ['ether', 'choir', 'sub', 'glass', 'air', 'swell']
        for keep in allv:
            a = np.frombuffer(base64.b64decode(await pg.evaluate(JS, [12, [k for k in allv if k != keep]])), dtype=np.float32)
            f = np.fft.rfftfreq(len(a), 1/44100); P = np.abs(np.fft.rfft(a))**2
            print(f"{keep:6s} rms {20*np.log10(np.sqrt((a**2).mean())+1e-12):6.1f}  bands", [round(10*np.log10(P[(f>=lo)&(f<hi)].sum()+1e-12) - 10*np.log10(len(a)) ,1) for lo,hi in [(20,150),(150,500),(500,2000),(2000,6000),(6000,20000)]])
        await b.close()
asyncio.run(main())
