import asyncio, json, sys
from playwright.async_api import async_playwright
URL = sys.argv[1]
JS = r'''() => { const A = axo.A, P = axo.P, I = A.I; axo.A.motion.speed = 1; axo.setState('crawl'); axo.step(1/60, 120); const out = [];
  for (let f = 0; f < 60; f++) { axo.step(1/60, 1); const pos = P.fk('crawl', A.pose); const row = [f, +(((A.gait) / (2 * Math.PI)) % 1).toFixed(3)];
    for (const [en, up, lo] of [['hand.L', 'upperarm.L', 'forearm.L'], ['hand.R', 'upperarm.R', 'forearm.R'], ['foot.L', 'thigh.L', 'shin.L'], ['foot.R', 'thigh.R', 'shin.R']]) {
      const M = P.m.crawl, L1 = M.rest[I[lo]].distanceTo(M.rest[I[up]]), L2 = M.rest[I[en]].distanceTo(M.rest[I[lo]]); const c = A.pose.contacts[en]; const d = c.t.distanceTo(pos[I[up]]);
      row.push(+(d / (L1 + L2)).toFixed(3)); }
    out.push(row); }
  return out; }'''
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width': 200, 'height': 200}); await pg.goto(URL); await pg.wait_for_function('window.ready')
        r = await pg.evaluate(JS); print('frame phase  reach: handL handR footL footR')
        for row in r: print(row)
        await b.close()
asyncio.run(main())
