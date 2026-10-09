import asyncio, json
from playwright.async_api import async_playwright
JS = r"""async ([mode, style, sec]) => {
  window.MUSIC_STYLE = style;
  const sr = 48000, oc = new OfflineAudioContext(2, Math.floor(sr * (sec + 1)), sr), A = makeAudio(); A._build(oc); A._offset(1);
  const key = mode === 'menu' ? 'menu' : mode === 'play' ? ({ spooky: 'halloween', tropical: 'island', pop: 'blank' })[style] : mode;
  A.music(mode); for (let i = 0; i < 200 && !A._trk(key); i++) await new Promise(r => setTimeout(r, 50));
  const ok = A._trk(key); A.music(mode); A._pump(sec);
  const buf = await oc.startRendering(), L = buf.getChannelData(0), R = buf.getChannelData(1), i0 = Math.floor(sr * 18); let ss = 0, pk = 0;
  for (let i = i0; i < L.length; i++) { ss += L[i] * L[i] + R[i] * R[i]; pk = Math.max(pk, Math.abs(L[i]), Math.abs(R[i])); }
  return { key, decoded: ok, playing: A._trk(), rms: +(10 * Math.log10(ss / (2 * (L.length - i0)))).toFixed(1), peak: +(20 * Math.log10(pk)).toFixed(1) }; }"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required']); pg = await b.new_page(); errs = []
        pg.on('pageerror', lambda e: errs.append(str(e))); pg.on('console', lambda m: m.type == 'error' and errs.append(m.text))
        await pg.goto('http://127.0.0.1:8765/aud/audiotest.html'); await pg.wait_for_function('window.ready === true')
        for mode, style in [('play', 'spooky'), ('play', 'tropical'), ('play', 'pop')]:
            print(mode, style, await pg.evaluate(JS, [mode, style, 50]))
        print('errors', errs[:3]); await b.close()
asyncio.run(main())
