import asyncio, json
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width': 360, 'height': 640})
        await pg.goto('file://' + SP + 'pc_t.html', timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000)
        r = await pg.evaluate("""() => { const S = __T.SLIME.S, out = {}; for (const k in S.geo) { const g = S.geo[k], A = g.attributes; out[k] = { pos: Array.from(A.position.array), nor: Array.from(A.normal.array), uv: Array.from(A.uv.array), rig: A.rig ? Array.from(A.rig.array) : null, rigN: A.rig ? A.rig.itemSize : 0, rig2: A.rig2 ? Array.from(A.rig2.array) : null, rig2N: A.rig2 ? A.rig2.itemSize : 0, idx: g.index ? Array.from(g.index.array) : null }; } return { geo: out, meta: S.meta }; }""")
        json.dump(r, open(SP + 'rx/geo.json', 'w'))
        print({k: len(v['pos'])//3 for k, v in r['geo'].items()}, list(r['meta'].keys()))
        await b.close()
asyncio.run(main())
