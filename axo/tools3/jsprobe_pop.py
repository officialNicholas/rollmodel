# evaluate a JS file in the preview after injecting popdetect.js; optional "pre" JS string run first; writes the string result to a file
#   python3 -I jsprobe_pop.py URL probe.js out.txt [pre-js]
import asyncio, sys, os
from playwright.async_api import async_playwright
HERE = os.path.dirname(os.path.abspath(__file__))
async def main(url, expr_file, out, pre=''):
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width': 200, 'height': 200}); errs = []; pg.on('pageerror', lambda e: errs.append(str(e)[:300]))
        await pg.goto(url, timeout=300000); await pg.wait_for_function('window.ready', timeout=300000)
        await pg.add_script_tag(content=open(os.path.join(HERE, 'popdetect.js')).read())
        if pre: await pg.evaluate(pre)
        r = await pg.evaluate(open(expr_file).read()); open(out, 'w').write((r if isinstance(r, str) else str(r)) + ('\nERR ' + ' | '.join(errs) if errs else '')); await b.close()
if __name__ == '__main__': asyncio.run(main(*sys.argv[1:]))
