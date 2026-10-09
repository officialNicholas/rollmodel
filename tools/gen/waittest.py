# the menu waits for its recording instead of playing the synth first; with no recording to be had, the synth fills in
import asyncio
from playwright.async_api import async_playwright
JS = r"""async ([base, wait]) => {
  window.MUSIC_BASE = base; window.MUSIC_STYLE = 'spooky';
  const src = document.querySelector('script').textContent; // makeAudio reads MUSIC_BASE when built
  const sr = 48000, oc = new OfflineAudioContext(2, sr * 7, sr), A = makeAudio(); A._build(oc); A._offset(1);
  A.music('menu'); await new Promise(r => setTimeout(r, wait)); A._pump(6);
  const buf = await oc.startRendering(), L = buf.getChannelData(0); let ss = 0; for (let i = sr; i < L.length; i++) ss += L[i] * L[i];
  return { playing: A._trk() || null, rms: +(10 * Math.log10(ss / (L.length - sr) + 1e-12)).toFixed(1) }; }"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); errs = []
        for base, wait, label in [('../music_out/', 0, 'recording, right away'), ('../music_out/', 2500, 'recording, after it decodes'), ('../nothing_here/', 2500, 'no recording')]:
            pg = await b.new_page(); pg.on('pageerror', lambda e: errs.append(str(e)))
            await pg.goto('http://127.0.0.1:8765/aud/audiotest.html'); await pg.wait_for_function('window.ready === true')
            print(label, await pg.evaluate(JS, [base, wait])); await pg.close()
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
