import asyncio
from playwright.async_api import async_playwright
U = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/aud/audiotest.html'
JS = r"""async ([dur, comp]) => { const sr = 44100, oc = new OfflineAudioContext(2, sr * 1, sr); const o = oc.createOscillator(); const g = oc.createGain(); o.frequency.value = 1000;
  const t = 0.004, a = 0.004, v = 0.1; g.gain.setValueAtTime(0, t); g.gain.linearRampToValueAtTime(v, t + a); g.gain.setTargetAtTime(0, t + a, Math.max(0.004, dur / 5));
  o.connect(g); let d = oc.destination; if (comp) { const c = oc.createDynamicsCompressor(); c.threshold.value = -16; c.knee.value = 8; c.ratio.value = 3; c.attack.value = 0.005; c.release.value = 0.2; c.connect(oc.destination); d = c; } g.connect(d); o.start(t); o.stop(t + a + dur + 0.03);
  return stats(await oc.startRendering()); }"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(); await pg.goto(U); await pg.wait_for_function('window.ready === true')
        for dur in [0.06, 0.2, 0.5]:
            for comp in [False, True]:
                print(dur, comp, await pg.evaluate(JS, [dur, comp]))
        await b.close()
asyncio.run(main())
