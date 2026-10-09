import asyncio, json
from playwright.async_api import async_playwright
U = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/aud/audiotest.html'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(); await pg.goto(U); await pg.wait_for_function('window.ready === true')
        for o in [{'f': 1000, 'dur': 0.5, 'hold': 0.3, 'v': 0.1}, {'f': 1000, 'dur': 0.06, 'v': 0.1}, {'f': 100, 'dur': 0.5, 'hold': 0.3, 'v': 0.1}, {'f': 1000, 'dur': 0.5, 'hold': 0.3, 'v': 0.5}]:
            r = await pg.evaluate("async (o) => { const sr = 44100, oc = new OfflineAudioContext(2, sr * 2, sr), A = makeAudio(); A._build(oc); A._tone(o); const buf = await oc.startRendering(); return stats(buf); }", o)
            print(o, r)
        r = await pg.evaluate("async () => { const sr = 44100, oc = new OfflineAudioContext(2, sr * 2, sr); const o = oc.createOscillator(); const g = oc.createGain(); g.gain.value = 0.1; o.frequency.value = 1000; o.connect(g); g.connect(oc.destination); o.start(0); o.stop(0.5); return stats(await oc.startRendering()); }")
        print('raw 0.1 sine', r)
        await b.close()
asyncio.run(main())
