import asyncio
from shot import *
async def main():
    async with async_playwright() as p:
        b, pg, errs = await open_page(p, 'http://localhost:8765/axo2/preview.html?manual', 300, 300)
        print(await pg.evaluate('JSON.stringify({stand: {abs: axo.S.meta.headAbs, mid: axo.S.meta.headMid, H: axo.S.meta.headH, r: axo.S.meta.headr}, crawl: {abs: axo.C.meta.headAbs, mid: axo.C.meta.headMid, H: axo.C.meta.headH, r: axo.C.meta.headr}, probe: [axo.look.rigs.stand.probeDist, axo.look.rigs.crawl.probeDist]})'))
        await b.close()
asyncio.run(main())
