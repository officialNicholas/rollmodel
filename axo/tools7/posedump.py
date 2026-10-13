# Dump the crawl mesh's posed dual quaternions from a lab page after a scenario (the runtime's own pose), to check the skinning offline.
#   python3 -I posedump.py <lab dir> <out.json> '<js scenario>'
import asyncio, json, sys
from playwright.async_api import async_playwright
async def main(lab, out, js):
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist']); pg = await b.new_page(viewport={'width': 400, 'height': 300})
        await pg.goto(f'http://localhost:8767/fable4/{lab}/index.html'); await pg.wait_for_function('window.LAB && LAB.ready', timeout=120000)
        await pg.evaluate("LAB.set('idle'); LAB.step(120)"); await pg.evaluate('(async () => { ' + js + ' })()')
        d = await pg.evaluate("(() => { const M = LAB.I.ax.P.m.crawl; return { dq: Array.from(M.dq), names: M.names, mesh: LAB.I.ax.A.mesh, root: LAB.I.ax.A.pose.root.toArray() }; })()")
        json.dump(d, open(out, 'w')); await b.close()
asyncio.run(main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else ''))
