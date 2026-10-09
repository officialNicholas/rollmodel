import asyncio, sys
from playwright.async_api import async_playwright
U = 'file:///tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/aud/'
JS = """async ([mode, mood]) => {
  const proto = BaseAudioContext.prototype, names = Object.getOwnPropertyNames(proto).filter(n => n.startsWith('create')), cnt = {};
  const orig = {}; for (const n of names) { orig[n] = proto[n]; proto[n] = function () { cnt[n] = (cnt[n] || 0) + 1; return orig[n].apply(this, arguments); }; }
  const sr = 44100, oc = new OfflineAudioContext(2, sr * 2, sr), A = makeAudio(); A._build(oc); for (const k in cnt) cnt[k] = 0;
  A._offset(1); A.music(mode); if (mood) A.mood.apply(null, mood); A._pump(1 + 33.1);
  for (const n of names) proto[n] = orig[n];
  let tot = 0; for (const k in cnt) tot += cnt[k]; return { perSec: +(tot / 33.1).toFixed(1), cnt };
}"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for page in sys.argv[1:]:
            pg = await b.new_page(); await pg.goto(U + page); await pg.wait_for_function('window.ready === true')
            for mode, mood in [('menu', None), ('play', None), ('play', [True, True, False, False])]:
                r = await pg.evaluate(JS, [mode, mood]); print(page, mode, mood, r['perSec'], {k: v for k, v in r['cnt'].items() if v})
            await pg.close()
        await b.close()
asyncio.run(main())
