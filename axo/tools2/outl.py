import asyncio, json
from shot import *
async def main():
    async with async_playwright() as p:
        b, pg, errs = await open_page(p, 'http://localhost:8765/axo2/preview.html?manual', 300, 300)
        await pg.evaluate('axo.setState("crawl"); axo.step(1/60, 120)')
        r = await pg.evaluate('JSON.stringify(axo.outliers(0.45))'); r = json.loads(r); print('outliers', len(r))
        from collections import Counter; c = Counter()
        for o in r[:40]: print(o)
        for o in r: c[o['bones'][0].split(':')[0]] += 1
        print(c.most_common(10)); print(errs[:3]); await b.close()
asyncio.run(main())
