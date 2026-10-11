import asyncio, json, sys
from shot import *
st = sys.argv[1]
async def main():
    async with async_playwright() as p:
        b, pg, errs = await open_page(p, 'http://localhost:8765/axo2/preview.html?manual', 300, 300)
        await pg.evaluate(f'axo.setState("{st}"); axo.step(1/60, 60)')
        r = json.loads(await pg.evaluate('JSON.stringify(axo.outliers(0.6))')); print('outliers', len(r))
        for o in r[:8]: print(o)
        await b.close()
asyncio.run(main())
