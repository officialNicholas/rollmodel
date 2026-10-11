import asyncio, json, sys
from playwright.async_api import async_playwright
URL = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:8811/v6/preview.html?manual'
JS = r'''() => { const A = axo.A, P = axo.P, I = A.I; const r = {};
  for (const w of ['stand', 'crawl']) { const M = P.m[w]; const L = n => +M.rest[I[n]].distanceTo(M.rest[I[n === 'thigh.L' ? 'shin.L' : n === 'shin.L' ? 'foot.L' : n === 'upperarm.L' ? 'forearm.L' : n === 'forearm.L' ? 'hand.L' : n === 'thigh.R' ? 'shin.R' : n === 'shin.R' ? 'foot.R' : n === 'upperarm.R' ? 'forearm.R' : 'hand.R']]).toFixed(3);
    r[w] = { thighL: L('thigh.L'), shinL: L('shin.L'), thighR: L('thigh.R'), shinR: L('shin.R'), uarmL: L('upperarm.L'), farmL: L('forearm.L'), uarmR: L('upperarm.R'), farmR: L('forearm.R') };
    r[w].rest = {}; for (const n of ['hips','thigh.L','shin.L','foot.L','toes.L','thigh.R','shin.R','foot.R','toes.R','upperarm.L','forearm.L','hand.L','upperarm.R','forearm.R','hand.R','head','neck','chest']) r[w].rest[n] = M.rest[I[n]].toArray().map(v => +v.toFixed(3)); }
  const pos = P.fk('crawl', A.LS); r.LS = {}; for (const n of ['hips','thigh.L','shin.L','foot.L','toes.L','thigh.R','shin.R','foot.R','toes.R','upperarm.L','forearm.L','hand.L','upperarm.R','forearm.R','hand.R','head','neck','chest','tail1','tail6']) r.LS[n] = pos[I[n]].toArray().map(v => +v.toFixed(3));
  r.crawlHand = A.crawlHand.toArray(); r.crawlFoot = A.crawlFoot.toArray(); r.H = A.H; r.standFeet = [A.standFeet.L.toArray(), A.standFeet.R.toArray()];
  return r; }'''
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width': 200, 'height': 200}); await pg.goto(URL); await pg.wait_for_function('window.ready')
        r = await pg.evaluate(JS); print(json.dumps(r, indent=0)); await b.close()
asyncio.run(main())
