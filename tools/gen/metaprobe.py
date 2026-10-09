import asyncio, json
from playwright.async_api import async_playwright
SP = '/tmp/claude-0/-home-user-rollmodel/5c52352e-692f-5301-ac55-ec4d2c708f3e/scratchpad/ws/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-gl=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist'])
        pg = await b.new_page(viewport={'width': 360, 'height': 640})
        await pg.goto('file://' + SP + 'pc_t.html', timeout=300000); await pg.wait_for_function('typeof __T === "object" && __T.VP && __T.VP.slime', polling=200, timeout=300000)
        r = await pg.evaluate("""() => { const S = __T.SLIME.S, m = S.meta.slime; const g = S.geo.slime; const pos = g.attributes.position.array; let mn=[1e9,1e9,1e9], mx=[-1e9,-1e9,-1e9]; for (let i=0;i<pos.length;i+=3) for (let k=0;k<3;k++){ mn[k]=Math.min(mn[k],pos[i+k]); mx[k]=Math.max(mx[k],pos[i+k]); }
          return { meta: m, keys: Object.keys(m), bbox: [mn, mx], attrs: Object.keys(g.attributes), nv: pos.length/3 }; }""")
        print(json.dumps(r, indent=1)[:3000])
        await b.close()
asyncio.run(main())
