import asyncio, json
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(); await pg.goto('http://127.0.0.1:8765/aud/decodetest.html'); await pg.wait_for_function('window.ready === true')
        r = await pg.evaluate('run()'); print(json.dumps(r, indent=0)); await b.close()
asyncio.run(main())
