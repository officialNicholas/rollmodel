# evaluate one JS expression in a page (after ready) and write the result (string) to a file
import asyncio, sys
from playwright.async_api import async_playwright
async def main(url, expr_file, out):
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width': 200, 'height': 200})
        await pg.goto(url, timeout=300000); await pg.wait_for_function('window.ready', timeout=300000)
        r = await pg.evaluate(open(expr_file).read()); open(out, 'w').write(r if isinstance(r, str) else str(r)); await b.close()
if __name__ == '__main__': asyncio.run(main(sys.argv[1], sys.argv[2], sys.argv[3]))
