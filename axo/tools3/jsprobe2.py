# like jsprobe, but prints every console message that looks like a shader / program error (full text)
import asyncio, sys, json
from playwright.async_api import async_playwright
async def main(url, exprs):
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width': 200, 'height': 200}); msgs = []
        pg.on('pageerror', lambda e: msgs.append('PAGEERROR ' + str(e)[:3000])); pg.on('console', lambda m: msgs.append(m.type + ' ' + m.text[:6000]))
        await pg.goto(url, timeout=300000); await pg.wait_for_function('window.ready', timeout=300000)
        for e in exprs:
            try: r = await pg.evaluate(e); print(json.dumps(r) if not isinstance(r, str) else r)
            except Exception as ex: print('ERR', str(ex)[:1500])
        await b.close()
        for m in msgs:
            if any(k in m for k in ('ERROR', 'Error', 'error:', 'PAGEERROR', 'WebGLProgram')): print(m[:6000]); print('----')
if __name__ == '__main__': asyncio.run(main(sys.argv[1], sys.argv[2:]))
